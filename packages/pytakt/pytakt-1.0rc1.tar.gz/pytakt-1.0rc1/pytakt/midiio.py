# coding:utf-8
"""
This module defines functions for real-time MIDI input/output and timers.

.. rubric:: Devices

In Pytakt, devices to send MIDI messages (MIDI interface or application port)
are called output devices, and devices to receive MIDI messages are called
input devices. A list of available devices can be found with the
:func:`show_devices` function. Each device is assigned an integer device
number.

There is a special device called the loopback device (not shown in
:func:`show_devices`). The loopback device is an output device and moreover
an input device, and can receive messages sent to them by itself.
It is normally used for sending and receiving LoopBackEvent's, but can also be
used for other events.

To use a device, it must be opened in advance. However, the loopback device is
always available and does not need to be opened.

For input and output each, there is a currently selected device.
The initial choice of this is platform specific. However, by setting the
environment variables PYTAKT_OUTPUT_DEVICE and PYTAKT_INPUT_DEVICE to a string
recognized by :func:`find_output_device` or :func:`find_input_device`, the
initial choice can be changed.

.. rubric:: Input and Output Queues

Inside the module, there is a queue for storing messages, which are byte
sequences converted from events with :meth:`.Event.to_message`, for input
and output each. Each message is given a timestamp and a track number.
When an event is sent to an output device via the :func:`queue_event` function,
the event is converted to a message, placed in the output queue, and then
kept until the sending time before it is actually sent to the device.
Messages from input devices are first placed in the input queue, where they
are kept until retrieved by the :func:`recv_event` function. There is no limit
on the size of the queues.

.. rubric:: Timer

The module has a timer that indicates the time since the module was imported.
The unit of time is the tick (a floating-point value equal to 1/480th of a
quarter note), and the relationship between seconds and ticks is determined
by two values: tempo (beats per minute, BPM) and tempo scale, with the
following formula:

    ticks = seconds * tempo * tempo_scale / 60 * 480

By default, the tempo is set to 125 BPM and the tempo scale is set to 1,
thus establishing the relationship 1 tick = 1 msec.
Tempo can be changed dynamically by sending a :class:`.TempoEvent` to any of
the output devices, and the tempo scale can be changed by calling the
:func:`set_tempo_scale` function.
"""
# Copyright (C) 2025  Satoshi Nishimura

import os
import itertools
from typing import List, Optional
import pytakt.cmidiio as _cmidiio
from pytakt.event import NoteEvent, NoteEventClass, CtrlEvent, SysExEvent, \
     MetaEvent, TempoEvent, LoopBackEvent, Event, message_to_event
from pytakt.pitch import Pitch
from pytakt.constants import TICKS_PER_QUARTER
from pytakt.score import Score, EventList, EventStream, RealTimeStream, Tracks
from pytakt.mml import mml
from pytakt.timemap import _current_tempo_value

__all__ = ['DEV_DUMMY', 'DEV_LOOPBACK']  # extended later


try:
    # Windows の jupyter notebook では、interrupt動作を行ってもカーネルプロセス
    # へシグナル(SIGINT)が送られない。下のコードは、かわりに送られる Windows
    # イベントに対して、その受信ハンドラに細工をすることで、recv_message を
    # 停止させるようにしている。
    os.environ['JPY_INTERRUPT_EVENT']
    from ipykernel import parentpoller
    import _thread

    def _jupyter_interrupt():
        _cmidiio._interrupt_recv_message()
        _thread.interrupt_main()

    parentpoller.interrupt_main = _jupyter_interrupt
except (KeyError, ModuleNotFoundError, ImportError):
    pass


DEV_DUMMY = -1
DEV_LOOPBACK = -2


_output_devnum = DEV_DUMMY
_input_devnum = DEV_DUMMY


_loopback_events = {}  # 送出されてから受信されるまでLoopBackEventを保管
_loopback_count = itertools.count()


def current_output_device() -> int:
    """ Returns the device number of the currently selected output device. """
    return _output_devnum


def current_input_device() -> int:
    """ Returns the device number of the currently selected input device. """
    return _input_devnum


def _find_device(dev, devices):
    if isinstance(dev, str):
        devlist = dev.split(';')
    elif isinstance(dev, list) or isinstance(dev, tuple):
        devlist = dev
    else:
        devlist = (dev,)
    for d in devlist:
        devnum = None
        if isinstance(d, int):
            devnum = d
        elif isinstance(d, str):
            if d.strip() == '':
                continue
            try:
                devnum = int(d)
            except ValueError:
                try:
                    devnum = [i for i, devname in enumerate(devices)
                              if devname.find(d) != -1][0]
                except IndexError:
                    pass
        if devnum is not None and DEV_DUMMY <= devnum < len(devices):
            return devnum
    raise ValueError("No such device: %r" % (dev,)) from None


def find_output_device(dev) -> int:
    """
    Get the output device number based on a device description.

    Args:
        dev(int, str, list, tuple): Device description. If it is an integer,
            it is recognized as the device number. If it is a string
            representing an integer, it is converted to an integer, which is
            then recognized as the device number. For other forms of a string,
            it means a device where the string matches all or part of its
            device name (and whichever has the smallest device number if there
            are multiple matched devices).
            The string may be multiple device descriptions separated by
            semicolons, in which case the first one whose existence is
            confirmed is valid.
            If the argument is a list or tuple where each element is an
            integer or a string without a semicolon, it is examined starting
            from the first element in the same manner as a single element,
            and the first device whose existence is confirmed becomes valid.
            If no device is found, an exception is raised.

    Returns:
        Output device number

    Examples:
        - ``find_output_device(1)``
        - ``find_output_device('1')``
        - ``find_output_device('TiMidity; MIDI Mapper')``
        - ``find_output_device([2, 0])``
    """
    return _find_device(dev, output_devices())


def output_devices() -> List[str]:
    """ Get a list of the device names of all the output devices. """
    return _cmidiio.output_devices()


def set_output_device(dev) -> None:
    """ Specifies `dev` as the currently selected output device.

    Args:
        dev: Device description recognized by :func:`find_output_device`.
    """
    global _output_devnum
    _output_devnum = find_output_device(dev)


def open_output_device(dev=None) -> None:
    """
    Open the output device `dev`.
    This may take a little time depending on the device.

    Args:
        dev: Target output device. If None, the currently selected output
            device is used; otherwise, the target device is the result of
            calling :func:`find_output_device` with this as an argument.
    """
    devnum = _output_devnum if dev is None else find_output_device(dev)
    _cmidiio._open_output_device(devnum)


def close_output_device(dev=None) -> None:
    """ Close the output device `dev`.

    Args:
        dev: Target output device. If None, the currently selected output
            device is used; otherwise, the target device is the result of
            calling :func:`find_output_device` with this as argument.
    """
    devnum = _output_devnum if dev is None else find_output_device(dev)
    _cmidiio._close_output_device(devnum)


def is_opened_output_device(dev) -> bool:
    """ Returns true if the output device `dev` is opened, or false otherwise.

    Args:
        dev: Device description that can be recognized by
            :func:`find_output_device`.
    """
    return _cmidiio._is_opened_output_device(find_output_device(dev))


def find_input_device(dev) -> int:
    """
    Get the input device number based on a device description.

    Args:
        dev(int, str, list, tuple): Device description in the same format as
            :func:`find_output_device`.
    """
    return _find_device(dev, input_devices())


def input_devices() -> List[str]:
    """ Get a list of the device names of all the input devices. """
    return _cmidiio.input_devices()


def set_input_device(dev) -> None:
    """ Specifies `dev` as currently selected input device.

    Args:
        dev: Device description recognized by :func:`find_intput_device`.
    """
    global _input_devnum
    _input_devnum = find_input_device(dev)


def open_input_device(dev=None) -> None:
    """ Open the input device `dev`.

    The input device inserts received messages into the input queue only while
    it is open, and discards messages while it is closed. To avoid unintended
    message accumulation in the input queue, openings should be limited to the
    necessary period of time.

    Args:
        dev: Target input device. If None, the currently selected input device
            is used; otherwise, the target device is the result of calling
            :func:`find_input_device` with this as an argument.
    """
    devnum = _input_devnum if dev is None else find_input_device(dev)
    _cmidiio._open_input_device(devnum)


def close_input_device(dev=None) -> None:
    """ Close the input device `dev`.

    Args:
        dev: Target input device. If None, the currently selected input device
            is used; otherwise, the target device is the result of calling
            :func:`find_input_device` with this as argument.
    """

    devnum = _input_devnum if dev is None else find_input_device(dev)
    _cmidiio._close_input_device(devnum)


def is_opened_input_device(dev) -> bool:
    """ Returns true if the input device `dev` is opened, or false otherwise.

    Args:
        dev: Device description that can be recognized by
            :func:`find_input_device`.
    """
    return _cmidiio._is_opened_input_device(find_input_device(dev))


def show_devices() -> None:
    """ Show the list of all the available devices. """
    odev = output_devices()
    for i, devname in enumerate(odev):
        print(" %c %c[%d] %s" % ('>' if i == _output_devnum else ' ',
                                 '*' if is_opened_output_device(i) else ' ',
                                 i, devname))
    if not odev:
        print("  Not available")
    print("\nMIDI Input Devices:")
    idev = input_devices()
    for i, devname in enumerate(idev):
        print(" %c %c[%d] %s" % ('>' if i == _input_devnum else ' ',
                                 '*' if is_opened_input_device(i) else ' ',
                                 i, devname))
    if not idev:
        print("  Not available")
    print("\n'*': opened   '>': currently selected")


def current_time() -> float:
    """ Returns the current time.

    Returns:
        Time in ticks, being 0 when the module was imported.
    """
    return _cmidiio.current_time()


def _current_tempo() -> float:
    """ Returns the current tempo.

    Returns:
        Tempo value (beats per minute).
    """
    return _cmidiio.current_tempo()


def _set_tempo(bpm) -> None:
    """ Changes the current tempo.

    Args:
        bpm(float): Tempo value (beats per minute)
    """
    t = current_time()
    _cmidiio.queue_message(DEV_DUMMY, t, 0, TempoEvent(t, bpm).to_message())


def current_tempo_scale() -> float:
    """ Returns the current tempo scale value.

    Returns:
        Tempo scale value
    """
    return _cmidiio.current_tempo_scale()


def set_tempo_scale(tempo_scale) -> None:
    """ Changes the tempo scale value.

    Args:
        tempo_scale(float): tempo scale value (non-negative)
    """
    _cmidiio.set_tempo_scale(tempo_scale)


def queue_event(ev, time=None, devnum=None) -> None:
    """
    Converts an event to a message (a sequence of bytes) and places the message
    with its sending time and track number on the output queue. The message is
    sent to the output device when the sending time is reached.
    There is no blocking (waiting for output) in this function.

    Note: When queuing a TempoEvent for a tempo change, the sending time must
    not be earlier than the current time.

    Args:
        ev(Event): The event to queue. This is converted to a message by the
            :meth:`.Event.to_message` method and placed on the output queue.
            If `ev` is a NoteEvent, two messages, one for note-on and the other
            for note-off, are placed (the sending time of note-off is that of
            note-on plus the value of the 'du' attribute if it exists or
            the L attribute otherwise).
            Even if the event is updated after calling this function, the
            queued message is not affected.
        time(ticks, optional): Specifies the time (in ticks) at which the
            message is sent. If not specified, the value of the 't' attribute
            of `ev` is used.
        devnum(int, optional): Specifies the output device number to which
            the message will be sent. If not specified, the currently selected
            output device is used.
            If `ev` is a LoopBackEvent, the message is always sent to the
            loopback device regardless of this value.
    """
    if time is None:
        time = ev.t
    if isinstance(ev, LoopBackEvent):
        seqno = next(_loopback_count)
        # 他の種類のメッセージは先頭バイトが0x80以上なので区別可能。
        _cmidiio.queue_message(DEV_LOOPBACK, time, ev.tk, str(seqno).encode())
        _loopback_events[seqno] = ev
    else:
        if devnum is None:
            devnum = _output_devnum
        if isinstance(ev, NoteEvent):
            _cmidiio.queue_message(devnum, time, ev.tk, ev.to_message()[0:3])
            _cmidiio.queue_message(devnum, time + ev.get_du(),
                                   ev.tk, ev.to_message()[3:])
        else:
            _cmidiio.queue_message(devnum, time, ev.tk, ev.to_message())


def recv_ready() -> bool:
    """
    Returns true if there is a message on the input queue, or false otherwise.
    If this value is true, it is guaranteed that the next call to
    :func:`recv_event` will not be blocked.
    """
    return _cmidiio.recv_ready()


def recv_event() -> Optional[Event]:
    """
    Receives a message from an input device and returns it as an event.
    All the opened input devices are subject for receiving.
    If there is no message in the input queue, it enters a blocking state
    and waits for the input.
    Execution is resumed whtn a message arrives or a keyboard interrupt
    is received.

    If a message from the loopback device and a message from a normal input
    device arrive almost at the same time, the order of receiving may be
    different from the order of event times.

    System messages other than exclusive messages are ignored and cannot be
    received.

    Returns:
        The event converted from the received message. Its 't' attribute value
        is the time the message was received. Returns None when a keyboard
        interrupt is received.
    """
    # 今のところ、recv_eventではdevnumの情報を得る手段がない。
    # devnumからtkへのdict指定してtkに反映させるようにしたら良いかもしれない。
    (devnum, ticks, tk, msg) = _cmidiio.recv_message()
    if not msg:
        return None  # keyboard interrupt while receiving
    elif msg[0] < 0x80:
        try:
            return _loopback_events.pop(int(msg.decode()))
        except KeyError:
            raise Exception("Received a corrupted loop-back event")
    else:
        ev = message_to_event(msg, ticks, tk)
        if hasattr(ev, 'n'):
            ev.n = Pitch(ev.n)
        return ev


def cancel_events(tk=-1, devnum=None) -> None:
    """
    Performs the following two operations on the specified track of the
    specified device.

        1. Delete all messages in the output queue.
        2. Sends messages to turn off the notes being played and the sustain
           pedal in use.

    Args:
        tk(int, optional):
            Specifies the target track number. A value of -1 means all tracks.
        devnum(int, optional):
            Specifies the target output device number. If not specified,
            the currently selected output device is used.
            The loopback device cannot be specified.
    """
    if devnum is DEV_LOOPBACK:
        # 実は今の実装でもまだ送出時刻に達していないものに限り削除できるが、
        # 削除されるかどうかが不確定なのは役立ちそうもない。
        raise Exception("Loop-back events cannot be canceled")
    _cmidiio.cancel_messages(_output_devnum if devnum is None else devnum, tk)


def stop() -> None:
    """
    Deletes all messages in the input and output queues, as well as sends
    messages to turn off the notes being played and the sustain pedal in use.
    In addition, it will send the MIDI message below to all channels of all
    opened output devices, attempting to completely stop all sound from the
    synthesizers.

        - All notes off (control change #123)
        - Sustain pedal control with value 0 (control change #64)
        - All sounds off (control change #120)

    This function is automatically called when a keyboard interrupt is
    received with this module imported.
    """
    _cmidiio.stop()
    _loopback_events.clear()


# もたつきを防ぐため先読みする時間幅。少なくとも MAX_DELTA_TIME*2 より大きい
# 必要がある。
_QUEUE_LOOK_AHEAD = TICKS_PER_QUARTER * 16

_METRONOME_TRACK = 65536


def _play_rec(score, rec=False, outdev=None, indev=None, metro=None,
              monitor=False):
    # score が EventStream である場合、playやrecordがリターンするのは
    # Keybordinterruptのみ。
    devnum = _output_devnum if outdev is None else find_output_device(outdev)
    indevnum = DEV_DUMMY
    if rec:
        indevnum = _input_devnum if indev is None else find_input_device(indev)
    open_output_device(devnum)  # may take some seconds
    open_input_device(indevnum)
    if score is None:
        score = EventList()
        isstream = False
    else:
        isstream = isinstance(score, EventStream)
        if isstream and score.is_consumed():
            raise Exception('play: Input stream has already been consumed')
        if not isstream:
            score = Tracks([score,
                            EventList([LoopBackEvent(score.get_duration(),
                                                     'done')], 0)])
    if metro:
        score = score & metro.mapev(
            lambda ev: ev.copy().update(tk=_METRONOME_TRACK))
    event_stream = score.ConnectTies().stream()
    tempo_scale_save = current_tempo_scale()
    recevlist = EventList()

    def resume_tempo_scale():
        nonlocal tempo_scale_save
        if tempo_scale_save is not None:
            set_tempo_scale(tempo_scale_save)
        tempo_scale_save = None

    done = False

    if isinstance(score, RealTimeStream):
        toffset = score.starttime
    else:
        # 出だしのもたつきを防ぐため、tempo_scale を 0 にする。
        set_tempo_scale(0)
        while current_tempo_scale() > 0:
            pass  # スレッドが切り替わって tempo-scale が更新されるまで待つ
        toffset = current_time()

    try:
        while True:
            try:
                ev = next(event_stream)
                # qt はキューに入れるべきシステム時刻
                qt = ev.t - _QUEUE_LOOK_AHEAD + toffset
            except StopIteration as e:
                if isstream:
                    queue_event(LoopBackEvent(e.value, 'done'),
                                e.value + toffset)
                ev = None
            if isinstance(score, RealTimeStream):
                if ev is None:
                    done = True
            else:
                if ev is None or qt >= current_time():
                    resume_tempo_scale()
                    if ev is not None:
                        queue_event(LoopBackEvent(qt, 'next'))
                    while True:
                        rev = recv_event()
                        if isinstance(rev, LoopBackEvent):
                            if rev.value == 'next':
                                break
                            elif rev.value == 'done':
                                recevlist.duration = rev.t
                                cancel_events(_METRONOME_TRACK, devnum)
                                done = True
                                break
                        elif rec:
                            if monitor:
                                queue_event(rev, devnum=devnum)
                            recevlist.append(rev)
            if done:
                break
            if isinstance(ev, (NoteEventClass, CtrlEvent, MetaEvent,
                               SysExEvent, LoopBackEvent)):
                queue_event(ev, ev.t + ev.dt + toffset, devnum)

    except KeyboardInterrupt:
        stop()
        recevlist.duration = current_time() - toffset
        # The following print() avoids command-line corruption by '^C'
        print(f"{'record' if rec else 'play'} interrupted")
    finally:
        resume_tempo_scale()
        close_input_device(indevnum)

    if rec:
        for ev in recevlist:
            ev.t = max(0, ev.t - toffset)
        return recevlist


def play(score, dev=None) -> None:
    """
    Plays a score. Messages are sent to the output device in sequence
    according to the events contained in the score. This function does not
    return until the time corresponding to the duration of the score has
    elapsed, or until a keyboard interrupt is received.

    Args:
        score(Score): Score to be played. It may be an infinite-length score.
        dev: Target output device. If None, the currently selected output
            device is used; otherwise, the target device is the result of
            calling :func:`find_output_device` with this as argument.
            If the specified device is not opened, it will be opened
            automatically.
    """
    # scoreにMML文字列を渡せるようにしないのは、MML中でPython関数を
    # 呼んだときに関数スコープの問題を生じやすいから。
    _play_rec(score, False, dev)


def record(indev=None, play=None, outdev=None,
           metro=None, monitor=False) -> EventList:
    """
    Records a performance from an input device and returns an event list.
    It is also possible to record with a score being played back.
    This function does not return until the time corresponding to the duration
    of the playback score has elapsed, or until a keyboard interrupt is
    received.

    Args:
        indev: Target input device. If None, the currently selected input
            device is used; otherwise, the target device is the result of
            calling :func:`find_input_device` with this as the argument.
            If the specified device is not opened, it will be opened
            automatically. Also, it will be closed when returning from this
            function.
            If another input device other than this device is already open,
            events from that device will be recorded as well.
        play(Score, optional): The score to be played back simultaneously.
            It may be an infinite-length score.
        outdev: The output device for playback. If None, the currently selected
            output device is used; otherwise, the target device is the result
            of calling :func:`find_output_device` with this as the argument.
        metro(str, bool or Score, optional):
            If specified, a metronome will be sounded. The default metronome
            assumes that a GM standard rhythmic instrument is assigned to
            MIDI channel 10.
            This argument can be a string representing a time signature,
            such as "3/4", True (equivalent to "4/4"), or a score to play
            the metronome sound
            (e.g., ``record(metro=mml("ch=10 {A5 {Ab5* Ab5}/3 }@@"))``).
        monitor(bool, optional):
            If True, sends messages from the input device to the output device.

    Returns:
        Recorded score
    """
    try:
        if metro is True:
            metro = '4/4'
        if isinstance(metro, str):
            d = [int(s) for s in metro.split('/')]
            if len(d) == 2 and d[0] > 0 and \
               d[1] in (1, 2, 4, 8, 16, 32, 64, 128):
                metro = mml('ch=10 L%d {A5 %s}@@' % (d[1], 'Ab5' * (d[0]-1)))
            else:
                raise ValueError()
        elif metro is not None and not isinstance(metro, Score):
            raise ValueError()
    except ValueError:
        raise ValueError("Unrecognized 'metro' argument") from None

    return _play_rec(play, True, outdev, indev, metro, monitor)


def listen(dev=None) -> RealTimeStream:
    devnum = _input_devnum if dev is None else find_input_device(dev)
    open_input_device(devnum)
    toffset = current_time()

    def _listen():
        try:
            while True:
                ev = recv_event()
                if not isinstance(ev, LoopBackEvent):
                    ev.update(t=ev.t-toffset)
                yield ev
        except KeyboardInterrupt:
            print("listen interrupted")
            stop()
            return current_time() - toffset
        finally:
            close_input_device(devnum)

    return RealTimeStream(_listen(), toffset)


def monitor(dev=None) -> None:
    """
    Displays the sequence of events from the input device.
    This function does not return until it receives a keyboard interrupt.

    Args:
        dev: Target input device. If None, the currently selected input
            device is used; otherwise, the target device is the result of
            calling :func:`find_input_device` with this as the argument.
            If the specified device is not opened, it will be opened
            automatically. Also, it will be closed when returning from this
            function.
    """
    devnum = _input_devnum if dev is None else find_input_device(dev)
    open_input_device(devnum)
    try:
        while True:
            print(recv_event())
    except KeyboardInterrupt:
        pass
    finally:
        close_input_device(devnum)


# モジュールで定義された関数を自動的に __all__ に含める
__all__.extend([name for name, value in globals().items()
                if name[0] != '_' and callable(value) and
                value.__module__ == 'pytakt.midiio'])


# current output device は、PYTAKT_OUTPUT_DEVICE 環境変数が定義されていれば
# その値 (-1 でも可) になり、そうでなければ default output deivce になる。
set_output_device(os.environ['PYTAKT_OUTPUT_DEVICE']
                  if 'PYTAKT_OUTPUT_DEVICE' in os.environ
                  else _cmidiio.default_output_device())


# current input device は、PYTAKT_INPUT_DEVICE 環境変数が定義されていれば
# その値 (-1 でも可) になり、そうでなければ default input deivce になる。
set_input_device(os.environ['PYTAKT_INPUT_DEVICE']
                 if 'PYTAKT_INPUT_DEVICE' in os.environ
                 else _cmidiio.default_input_device())


# midiioモジュールのインポートより前に設定されたいたテンポを引き継ぐ
_set_tempo(_current_tempo_value)
