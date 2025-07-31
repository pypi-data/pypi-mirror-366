# coding:utf-8
"""
This module defines a set of classes related to events.
Most of these events are based on events defined in Standard MIDI files.
"""
# Copyright (C) 2025  Satoshi Nishimura

import warnings
import numbers
from typing import Union, Tuple
from pytakt.utils import takt_round, int_preferred, std_time_repr, TaktWarning
from pytakt.constants import CONTROLLERS, META_EVENT_TYPES, M_TEXT_LIMIT, \
     M_TEXT, C_BEND, C_KPR, C_CPR, C_PROG, C_TEMPO, C_ALL_NOTES_OFF, \
     M_SEQNO, M_CHPREFIX, M_SMPTE, M_MARK, M_TEMPO, M_TIMESIG, M_KEYSIG, \
     M_EOT, TICKS_PER_QUARTER
from pytakt.pitch import Key
from pytakt.utils import Ticks

__all__ = ['MidiEventError', 'MidiEventWarning', 'midimsg_size',
           'message_to_event']  # extended later


class MidiEventError(Exception): pass
class MidiEventWarning(TaktWarning): pass


class Event(object):
    """ Base class for all types of events.

    Attributes:
        t (ticks): time of the event in ticks
        tk (int): track number (starting from 0)
        dt (ticks): the difference between the notated time and the played
            time; for performances, t plus this value (in ticks)
            is used for timing; the range of the dt value is limited
            (see :const:`pytakt.constants.MAX_DELTA_TIME`).

    Args:
        t(ticks): value of the t attribute
        tk(int): value of the tk attribute
        dt(ticks, optional): value of the dt attribute
        kwargs: additional attributes for the event

    .. rubric:: Arithmetic Rules

    * The equivalence comparison ('==') between events results in true
      only if the classes match and all attribute values are equivalent.
    * If the '|' operator is used with the left operand being a string and
      the right operand being an event, the left operand is ignored and the
      result is the value of the event itself. This is used in showtext()
      to ignore measure numbers, etc. to the left of the '|'.

    """

    __slots__ = ('t',   # time in ticks
                 'tk',  # track number (base-0)
                 'dt',  # time deviation in ticks
                 '__dict__')

    def __init__(self, t, tk, dt=0, **kwargs):
        if not isinstance(t, numbers.Real) or not isinstance(dt, numbers.Real):
            raise TypeError("time must be int, float, or Fraction")
        if not isinstance(tk, numbers.Integral) or tk < 0:
            raise TypeError("track number must be non-negative int")
        (self.t, self.tk, self.dt) = (t, tk, dt)
        self.__dict__.update(kwargs)

    def copy(self) -> 'Event':
        """
        Returns a copied event (shallow copy).
        """
        return self.__class__(self.t, self.tk, self.dt, **self.__dict__)
    __copy__ = copy

    def update(self, **kwargs) -> 'Event':
        """
        Adds or changes attributes according to the assignment description
        in `kwargs`.

        Returns:
            self
        """
        for k, v in kwargs.items():
            setattr(self, k, v)
        return self

    # (ev, val) のようにタプルにしたときにその大小関係が混乱するのでやめた。
    # def __lt__(self, other):
    #     return self.t < other.t
    # def __gt__(self, other):
    #     return self.t > other.t

    def __eq__(self, other):
        return (type(self) is type(other) and
                all(all(getattr(self, key) == getattr(other, key)
                        for key in cls.__slots__)
                    for cls in self.__class__.__mro__ if cls is not object))

    __hash__ = object.__hash__

    def _getattrs(self):
        attrs = [key for key in ('t', 'n', 'mtype', 'xtype', 'L', 'v', 'nv',
                                 'ctrlnum', 'value', 'tk', 'ch')
                 if hasattr(self, key) and key not in self.__dict__]
        if self.dt != 0:
            attrs.append('dt')
        attrs += self.__dict__
        return attrs

    def _valuestr(self, key, timereprfunc):
        value = getattr(self, key)
        if key == 't' or key == 'dt':
            return timereprfunc(value)
        elif key == 'ctrlnum' and value in CONTROLLERS:
            return CONTROLLERS[value]
        elif key == 'mtype' and value in META_EVENT_TYPES:
            return META_EVENT_TYPES[value]
        else:
            return "%r" % (value,)  # %sだとMetaEvent等で値が文字列の場合に問題

    def tostr(self, timereprfunc=std_time_repr) -> str:
        """ Returns a string representation of the event.

        Args:
            timereprfunc(function): Function to convert a value of time to
                a string. By default, it assumes a function that returns
                a representation rounded to 5 decimal places.
        """
        params = ["%s=%s" % (k, self._valuestr(k, timereprfunc))
                  for k in self._getattrs()]
        return "%s(%s)" % (self.__class__.__name__, ', '.join(params))

    def __str__(self):
        return self.tostr()

    def __repr__(self):
        return self.tostr(repr)

    def __ror__(self, other):
        if isinstance(other, str):
            return self
        else:
            return NotImplemented

    def is_pitch_bend(self) -> bool:
        """ Returns true for a Pitch Bend event. """
        return (isinstance(self, CtrlEvent) and self.ctrlnum == C_BEND)
    def is_key_pressure(self) -> bool:
        """ Returns true for a Key Pressure event. """
        return isinstance(self, KeyPressureEvent)
    def is_channel_pressure(self) -> bool:
        """ Returns true for a Channel Pressure event. """
        return (isinstance(self, CtrlEvent) and self.ctrlnum == C_CPR)
    def is_program_change(self) -> bool:
        """ Return true for a Program Change event. """
        return (isinstance(self, CtrlEvent) and self.ctrlnum == C_PROG)
    def is_all_notes_off(self) -> bool:
        """ Returns true for an all-note-off event (#123 control change
            event with a value of 0). """
        return (isinstance(self, CtrlEvent) and
                self.ctrlnum == C_ALL_NOTES_OFF and self.value == 0)
    def is_marker(self) -> bool:
        """ Returns true for a marker event (#6 meta event). """
        return (isinstance(self, MetaEvent) and self.mtype == M_MARK)
    def is_end_of_track(self) -> bool:
        """ Returns true for a track-end event (#47 meta event). """
        return (isinstance(self, MetaEvent) and self.mtype == M_EOT)
    def is_text_event(self) -> bool:
        """ Returns true for text events (#1 to #15 meta events)."""
        return (isinstance(self, MetaEvent) and 1 <= self.mtype <= 15)

    def to_message(self, errhdr='') -> Union[bytes, bytearray]:
        """ Convert an event to a byte sequence.

        Args:
            errhdr(str, optional): header string for error and warning messages
        """
        return b''

    def _get_ch(self, errhdr=''):
        if not isinstance(self.ch, numbers.Integral) or not 1 <= self.ch <= 16:
            raise MidiEventError(errhdr + "event with invalid channel number")
        return min(max(self.ch, 1), 16) - 1

    def _get_n(self, errhdr=''):
        if not isinstance(self.n, numbers.Real):
            raise MidiEventError(errhdr + "event with ill-typed note number")
        n = takt_round(self.n)
        if not 0 <= n <= 127:
            warnings.warn(errhdr + ("Out-of-range note number (n=%r, ch=%r)" %
                          (self.n, self.ch)), MidiEventWarning, stacklevel=2)
        return min(max(n, 0), 127)

    def _get_ctrl_val(self, low, high, errhdr=''):
        if not isinstance(self.value, numbers.Real):
            raise MidiEventError(errhdr + "event with ill-typed control value")
        val = takt_round(self.value)
        if not low <= val <= high:
            warnings.warn(errhdr + ("Out-of-range control value (value=%r, \
ctrlnum=%r, ch=%r)" % (self.value, self.ctrlnum, self.ch)),
                          MidiEventWarning, stacklevel=2)
        return min(max(val, low), high)

    def _get_data_bytes(self, encoding='utf-8'):
        if isinstance(self.value, str):
            return self.value.encode(encoding, errors='surrogateescape')
        else:
            return bytes(self.value)

    def ptime(self) -> Ticks:
        """ Returns the performance time (sum of the t and dt attribute
            values). """
        return self.t + self.dt


class NoteEventClass(Event):
    """
    Base class of NoteEvent, NoteOnEvent, and NoteOffEvent.
    """
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        raise Exception("NoteEventClass is an abstract class")


class NoteEvent(NoteEventClass):
    """
    Class for note events. A note event corresponds to a pair of note-on
    and note-off.

    Attributes:
        ch (int): MIDI channel number (starting from 1)
        n (int or Pitch): MIDI note number
        L (ticks): notated duration in ticks (note value)
        v (int): MIDI velocity
        nv (int or None): MIDI note-off velocity; if this is None, a note-on
            message with zero velocity is used when converted to a MIDI byte
            sequence.
        du (ticks, optional): playing duration in ticks (time difference
            between note-on and note-off in the performance). When this
            attribute is absent, it is assumed to have the same value as
            the L attribute.

    Other Inherited Attributes
        t, tk, dt

    Args:
        t(ticks): value of the t attribute
        n(int or Pitch): value of the n attribute
        L(ticks): value of the L attribute
        v(int, optional): value of the v attribute
        nv(int or None, optional): value of the nv attribute
        du(ticks, optional): value of the du attribute
        tk(int, optional): value of the tk attribute
        ch(int, optional): value of the ch attribute
        dt(ticks, optional): value of the dt attribute
        kwargs: additional attributes for the event
    """

    __slots__ = ('ch',  # MIDI channel number (base-1)
                 'n',   # MIDI note number
                 'L',   # note value in ticks
                 'v',   # MIDI velocity
                 'nv')  # nv: MIDI note-off velocity (possibly None)

    def __init__(self, t, n, L, v=80, nv=None, du=None, tk=1, ch=1, dt=0,
                 **kwargs):
        (self.ch, self.n, self.L, self.v, self.nv) = (ch, n, L, v, nv)
        if du is not None:
            self.du = du
        Event.__init__(self, t, tk, dt, **kwargs)

    def copy(self) -> Event:
        return self.__class__(self.t, self.n, self.L, self.v, self.nv,
                              tk=self.tk, ch=self.ch, dt=self.dt,
                              **self.__dict__)
    __copy__ = copy

    def get_du(self) -> Ticks:
        """ Returns the value of the du attribute (or the value of L if it is
            missing)."""
        return getattr(self, 'du', self.L)

    def offtime(self) -> Ticks:
        """ Returns the notated note-off time (sum of the t and L attribute
            values)."""
        return self.t + self.L

    def pofftime(self) -> Ticks:
        """ Returns the played note-off time. """
        return self.ptime() + self.get_du()

    def to_message(self, errhdr='') -> Union[bytes, bytearray]:
        return NoteOnEvent.to_message(self, errhdr) + \
            NoteOffEvent.to_message(self, errhdr)


class NoteOnEvent(NoteEventClass):
    """ Class for note-on events.

    Attributes:
        ch (int): MIDI channel number (starting from 1)
        n (int or Pitch): MIDI note number
        v (int): MIDI velocity

    Other Inherited Attributes
        t, tk, dt

    Args:
        t(ticks): value of the t attribute
        n(int or Pitch): value of the n attribute
        v(int, optional): value of the v attribute
        tk(int, optional): value of the tk attribute
        ch(int, optional): value of the ch attribute
        dt(ticks, optional): value of the dt attribute
        kwargs: additional attributes for the event
    """

    __slots__ = ('ch',  # MIDI channel number (base-1)
                 'n',   # MIDI note number
                 'v')   # MIDI velocity

    def __init__(self, t, n, v=80, tk=1, ch=1, dt=0, **kwargs):
        (self.ch, self.n, self.v) = (ch, n, v)
        Event.__init__(self, t, tk, dt, **kwargs)

    def copy(self) -> Event:
        return self.__class__(self.t, self.n, self.v,
                              self.tk, self.ch, self.dt, **self.__dict__)
    __copy__ = copy

    def to_message(self, errhdr='') -> Union[bytes, bytearray]:
        if not isinstance(self.v, numbers.Real):
            raise MidiEventError(errhdr + "note-on with ill-typed velocity")
        v = takt_round(self.v)
        if not 1 <= v <= 127:
            warnings.warn(errhdr + ("Out-of-range velocity (v=%r, ch=%r)" %
                          (self.v, self.ch)), MidiEventWarning, stacklevel=2)
        v = min(max(v, 1), 127)
        return b"%c%c%c" % (0x90 | self._get_ch(errhdr),
                            self._get_n(errhdr), v)


class NoteOffEvent(NoteEventClass):
    """ Class for note-off events.

    Attributes:
        ch (int): MIDI channel number (starting from 1)
        n (int or Pitch): MIDI note number
        nv (int or None): MIDI note-off velocity; if this is None, a note-on
            message with zero velocity is used when converted to a MIDI byte
            sequence.

    Other Inherited Attributes
        t, tk, dt

    Args:
        t(ticks): value of the t attribute
        n(int or Pitch): value of the n attribute
        nv(int or None, optional): value of the nv attribute
        tk(int, optional): value of the tk attribute
        ch(int, optional): value of the ch attribute
        dt(ticks, optional): value of the dt attribute
        kwargs: additional attributes for the event
    """

    __slots__ = ('ch',  # MIDI channel number (base-1)
                 'n',   # MIDI note number
                 'nv', )  # nv: MIDI note-off velocity (possibly None)

    def __init__(self, t, n, nv=None, tk=1, ch=1, dt=0, **kwargs):
        (self.ch, self.n, self.nv) = (ch, n, nv)
        Event.__init__(self, t, tk, dt, **kwargs)

    def copy(self) -> Event:
        return self.__class__(self.t, self.n, self.nv,
                              self.tk, self.ch, self.dt, **self.__dict__)
    __copy__ = copy

    def to_message(self, errhdr='') -> Union[bytes, bytearray]:
        if self.nv is None:
            return b"%c%c%c" % (0x90 | self._get_ch(errhdr),
                                self._get_n(errhdr), 0)
        else:
            if not isinstance(self.nv, numbers.Real):
                raise MidiEventError(errhdr +
                                     "note-off with ill-typed velocity")
            nv = takt_round(self.nv)
            if not 0 <= nv <= 127:
                warnings.warn(
                    errhdr + ("Out-of-range note-off velocity (nv=%r, ch=%r)" %
                              (self.nv, self.ch)),
                    MidiEventWarning, stacklevel=2)
            nv = min(max(nv, 0), 127)
            return b"%c%c%c" % (0x80 | self._get_ch(errhdr),
                                self._get_n(errhdr), nv)


class CtrlEvent(Event):
    """
    Class of control events with controller number and control value.
    This includes MIDI Control Change, Program Change, Pitch Bend,
    Channel Pressure, and Key Pressure.
    For Key Pressure, a dedicated subclass is provided, so use its constructor
    when instantiating.

    Attributes:
        ch (int): MIDI channel number (starting from 1)
        ctrlnum (int): controller number, with the following meaning

            * 0 to 127: MIDI control change (`value` is from 0 to 127)
            * 128(C_BEND): MIDI pitch bend (`value` is from -8192 to 8191)
            * 129(C_KPR): MIDI key pressure (see KeyPressureEvent)
            * 130(C_CPR): MIDI channel pressure (`value` is from 0 to 127)
            * 131(C_PROG): MIDI program change (`value` is from 1 to 128)
            * Other: For internal processing.
        value (int, etc.): control value

    Other Inherited Attributes
        t, tk, dt

    Args:
        t(ticks): value of the t attribute
        ctrlnum (int): value of ctrlnum attribute
        value(int, etc.): value of the value attribute
        tk(int, optional): value of the tk attribute
        ch(int, optional): value of the ch attribute
        dt(ticks, optional): value of the dt attribute
        kwargs: additional attributes for the event
    """
    __slots__ = 'ch', 'ctrlnum', 'value'

    def __init__(self, t, ctrlnum, value, tk=1, ch=1, dt=0, **kwargs):
        if not isinstance(ctrlnum, numbers.Integral):
            raise TypeError("controller number must be int")
        if ctrlnum in (C_KPR, C_TEMPO):
            raise ValueError("Use other constructors for that type of event")
        self._init_base(t, ctrlnum, value, tk, ch, dt, **kwargs)

    def _init_base(self, t, ctrlnum, value, tk, ch, dt, **kwargs):
        (self.ch, self.ctrlnum, self.value) = (ch, ctrlnum, value)
        super().__init__(t, tk, dt, **kwargs)

    def copy(self) -> Event:
        return self.__class__(self.t, self.ctrlnum, self.value,
                              self.tk, self.ch, self.dt, **self.__dict__)
    __copy__ = copy

    def to_message(self, errhdr='') -> Union[bytes, bytearray]:
        if self.ctrlnum == C_PROG:
            low, high = 1, 128
        elif self.ctrlnum == C_BEND:
            low, high = -8192, 8191
        else:
            low, high = 0, 127
        val = self._get_ctrl_val(low, high, errhdr)
        if 0 <= self.ctrlnum <= 127:
            return b"%c%c%c" % (0xb0 | self._get_ch(errhdr), self.ctrlnum, val)
        elif self.ctrlnum == C_BEND:
            val += 8192
            return b"%c%c%c" % (0xe0 | self._get_ch(errhdr),
                                val & 0x7f, (val >> 7) & 0x7f)
        elif self.ctrlnum == C_CPR:
            return b"%c%c" % (0xd0 | self._get_ch(errhdr), val)
        elif self.ctrlnum == C_PROG:
            return b"%c%c" % (0xc0 | self._get_ch(errhdr), val - 1)
        else:
            raise MidiEventError(errhdr +
                                 "event with invalid controller number")


class KeyPressureEvent(CtrlEvent):
    """ Class of Key Pressure events.

    Attributes:
        n (int or Pitch): MIDI note number
        value (int or float): control value (0-127)

    Other Inherited Attributes
        t, tk, dt, ch, ctrlnum

    Args:
        t(ticks): value of the t attribute
        n(int or Pitch): value of the n attribute
        value(int, etc.): value of the value attribute
        tk(int, optional): value of the tk attribute
        ch(int, optional): value of the ch attribute
        dt(ticks, optional): value of the dt attribute
        kwargs: additional attributes for the event
    """
    __slots__ = ('n',)

    def __init__(self, t, n, value, tk=1, ch=1, dt=0, **kwargs):
        self.n = n
        super()._init_base(t, C_KPR, value, tk, ch, dt, **kwargs)

    def copy(self) -> Event:
        return self.__class__(self.t, self.n, self.value,
                              self.tk, self.ch, self.dt, **self.__dict__)
    __copy__ = copy

    def _getattrs(self):
        attrs = super()._getattrs()
        attrs.remove('ctrlnum')
        return attrs

    def to_message(self, errhdr='') -> Union[bytes, bytearray]:
        val = self._get_ctrl_val(0, 127, errhdr)
        return b"%c%c%c" % (0xa0 | self._get_ch(errhdr),
                            self._get_n(errhdr), val)


class SysExEvent(Event):
    """ Class for system-exclusive message events.

    Attributes:
        value (bytes, bytearray, or iterable of int):
            The contents of the message explicitly including the leading
            0xf0 and trailing 0xf7.
            It is possible to split a single message into multiple
            SysExEvent's, in which case 0xf0 is placed in the first event and
            0xf7 in the last.

    Other Inherited Attributes
        t, tk, dt

    Args:
        t(ticks): value of the t attribute
        value(bytes, bytearray, or iterable of int):
            value of the value attribute
        tk(int, optional): value of the tk attribute
        dt(ticks, optional): value of the dt attribute
        kwargs: additional attributes for the event
    """
    __slots__ = ('value',)

    def __init__(self, t, value, tk=1, dt=0, **kwargs):
        self.value = value  # should be bytes or list/tupple of int
        super().__init__(t, tk, dt, **kwargs)

    def copy(self) -> Event:
        return self.__class__(self.t, self.value, self.tk, self.dt,
                              **self.__dict__)
    __copy__ = copy

    def to_message(self, errhdr='') -> Union[bytes, bytearray]:
        """ Convert the event to a byte sequence (sequence prefixed with an
            additional 0xf0).

        Args:
            errhdr(str, optional): header string for error and warning messages
        """
        result = bytearray((0xf0,))
        result.extend(self.value)
        return result


class MetaEvent(Event):
    """
    Class for meta events defined in Standard MIDI files.
    This includes text events, key signature events, time signature events,
    tempo change events, and end-of-track events.

    Attributes:
        mtype (int): type of meta event (0-127)
        value (bytes, bytearray, str, Key, int, float, or iterable of int):
            Data of the meta event. If mtype is from 1 to 15, this attribute
            should be of type str. If mtype is M_KEYSIG (key signature event),
            this attribute must be of type Key. If mtype is M_TEMPO (tempo
            change event), this attribute must be of type int or float.
            For other meta events, bytes, bytearray, or iterable of int is
            recommended.

    Other Inherited Attributes
        t, tk, dt

    Args:
        t(ticks): value of the t attribute
        mtype(int): value of the mtype attribute
        value(bytes, bytearray, str, Key, int, float, or iterable of int):
            value of the value attribute
        tk(int, optional): value of the tk attribute
        dt(ticks, optional): value of the dt attribute
        kwargs: additional attributes for the event

    Notes:
        The key signature event, the time signature event, and the tempo
        change event have their own subclasses.
        When instantiating a tempo change event, use the dedicated subclass
        (TempoEvent).
        Although it is possible to create the key and time signature events
        using the constructor of this class, it is more convenient to use
        the constructor of each subclass.
    """

    __slots__ = ('mtype', 'value')

    def __init__(self, t, mtype, value, tk=1, dt=0, **kwargs):
        if not isinstance(mtype, numbers.Integral):
            raise TypeError("meta-event type must be int")
        if mtype == M_TEMPO:
            raise ValueError("Use TempoEvent for create a tempo event")
        elif mtype == M_KEYSIG:
            self.__class__ = KeySignatureEvent
            if not isinstance(value, Key):
                raise TypeError(
                    "value must be a Key object for key-signature event")
        elif mtype == M_TIMESIG:
            self.__class__ = TimeSignatureEvent
        self._init_base(t, mtype, value, tk, dt, **kwargs)

    def _init_base(self, t, mtype, value, tk, dt, **kwargs):
        (self.mtype, self.value) = (mtype, value)
        super().__init__(t, tk, dt, **kwargs)

    def copy(self) -> Event:
        return MetaEvent(self.t, self.mtype, self.value,
                         self.tk, self.dt, **self.__dict__)
    __copy__ = copy

    def to_message(self, errhdr='',
                   encoding='utf-8') -> Union[bytes, bytearray]:
        """ Converts the event to a byte sequence (data in a standard MIDI
        file without length information).

        Args:
            errhdr(str, optional): header string for error and warning messages
            encoding(str): specifies how the text event's string should be
                encoded in the byte sequence.
        """
        try:
            result = bytearray((0xff, self.mtype))
        except (TypeError, ValueError):
            raise MidiEventError(errhdr + "invalid meta event type")
        data_bytes = self._get_data_bytes(encoding)
        if self.mtype == M_SEQNO and len(data_bytes) != 2 or \
           self.mtype == M_CHPREFIX and len(data_bytes) != 1 or \
           self.mtype == M_EOT and len(data_bytes) != 0 or \
           self.mtype == M_TEMPO and len(data_bytes) != 3 or \
           self.mtype == M_SMPTE and len(data_bytes) != 5 or \
           self.mtype == M_TIMESIG and len(data_bytes) != 4 or \
           self.mtype == M_KEYSIG and len(data_bytes) != 2:
            raise MidiEventError(errhdr +
                                 "meta event with inappropriate data length")
        result.extend(data_bytes)
        return result


class KeySignatureEvent(MetaEvent):
    """ Class for key signature events.

    Inherited Attributes
        t, tk, dt, mtype, value

    Args:
        t(ticks): value of the t attribute
        value(Key, int, or str): first argument of the Key constructor
        tk(int, optional): value of the tk attribute
        dt(ticks, optional): value of the dt attribute
        kwargs: additional attribute for the event
    """
    __slots__ = ()

    def __init__(self, t, value, tk=0, dt=0, **kwargs):
        super().__init__(t, M_KEYSIG, Key(value), tk, dt, **kwargs)

    def _getattrs(self):
        attrs = super()._getattrs()
        attrs.remove('mtype')
        return attrs

    def to_message(self, errhdr='',
                   encoding='utf-8') -> Union[bytes, bytearray]:
        return b"\xff%c%c%c" % (M_KEYSIG,
                                self.value.signs & 0xff, self.value.minor)


class TimeSignatureEvent(MetaEvent):
    """ Class for time signature events.

    Inherited Attributes
        t, tk, dt, mtype, value

    Args:
        t(ticks): value of the t attribute
        num(int): value of the numerator
        den(int): value of the denominator
        cc(int, optional): interval between metronome clicks in units of 1/24
            of a quarter note. By default, it is automatically guessed from
            `num` and `den`.
        tk(int, optional): value of the tk attribute
        dt(ticks, optional): value of the dt attribute
        kwargs: additional attributes for the event

    Examples:
        ``TimeSignatureEvent(0, 3, 4)`` for 3/4 time and zero event time.
    """
    __slots__ = ()

    def __init__(self, t, num, den, cc=None, tk=0, dt=0, **kwargs):
        if den <= 0 or den & (den - 1) != 0:
            raise ValueError("TimeSignatureEvent: Bad denominator")
        value = (num, (den - 1).bit_length(),
                 cc if cc is not None else self._guess_cc(num, den), 8)
        value = kwargs.pop('value', value)
        super().__init__(t, M_TIMESIG, bytes(value), tk, dt, **kwargs)

    def _getattrs(self):
        attrs = super()._getattrs()
        attrs.remove('mtype')
        return attrs

    def _guess_cc(self, num, den):
        cc = 96 * (3 if den >= 8 and num in (6, 9, 12) else 1)
        if cc % den != 0:
            cc = 24  # very rare case like 4/64
        else:
            cc //= den
        return cc

    def numerator(self) -> int:
        """ Returns the value of the numerator."""
        return self._get_data_bytes()[0]

    def denominator(self) -> int:
        """ Returns the value of the denominator."""
        return 1 << self._get_data_bytes()[1]

    def num_den(self) -> Tuple[int, int]:
        """ Returns a 2-tuple consisting of the numerator and denominator."""
        data = self._get_data_bytes()
        return (data[0], 1 << data[1])

    def get_cc(self) -> int:
        """ Returns the interval between metronome clicks (in 1/24ths of
            a quarter note)."""
        return self._get_data_bytes()[2]

    def tostr(self, timereprfunc=std_time_repr) -> str:
        if isinstance(self.value, bytes) and self.value[3] == 8:
            num = self.value[0]
            den = 1 << self.value[1]
            params = ["%s=%s" % ('t', self._valuestr('t', timereprfunc)),
                      "num=%r" % num, "den=%r" % den]
            if self.value[2] != self._guess_cc(num, den):
                params.append("cc=%r" % self.value[2])
            attrs = self._getattrs()
            attrs.remove('t')
            attrs.remove('value')
            params.extend("%s=%s" % (k, self._valuestr(k, timereprfunc))
                          for k in attrs)
            return "%s(%s)" % (self.__class__.__name__, ', '.join(params))
        else:
            return super().tostr(timereprfunc)

    def beat_length(self) -> Ticks:
        """ Returns the length of one beat in ticks."""
        data = self._get_data_bytes()
        return int_preferred(TICKS_PER_QUARTER * 4 / (1 << data[1]))

    def measure_length(self) -> Ticks:
        """ Returns the length of one measure in ticks."""
        return self.numerator() * self.beat_length()


class TempoEvent(MetaEvent):
    """ Class for tempo change events.

    Attributes:
        value (int or float):
            tempo value in quarter notes per minute (minimum value is 4)

    Other Inherited Attributes
        t, tk, dt, mtype, value

    Args:
        t(ticks): value of the t attribute
        value(int or float): value of the value attribute
        tk(int, optional): value of the tk attribute
        dt(ticks, optional): value of the dt attribute
        kwargs: additional attributes for the event
    """
    __slots__ = ()

    def __init__(self, t, value, tk=0, dt=0, **kwargs):
        super()._init_base(t, M_TEMPO, value, tk, dt, **kwargs)

    def copy(self) -> Event:
        return self.__class__(self.t, self.value, self.tk, self.dt,
                              **self.__dict__)
    __copy__ = copy

    def _getattrs(self):
        attrs = super()._getattrs()
        attrs.remove('mtype')
        return attrs

    def to_message(self, errhdr='',
                   encoding='utf-8') -> Union[bytes, bytearray]:
        low, high = 4, 1e8
        if not low <= self.value <= high:
            warnings.warn(errhdr +
                          ("Out-of-range tempo value (value=%r)" %
                           (self.value,)), MidiEventWarning, stacklevel=2)
        val = takt_round(6e+7 / min(max(self.value, low), high))
        return b"\xff%c%c%c%c" % (M_TEMPO, (val >> 16) & 0xff,
                                  (val >> 8) & 0xff, val & 0xff)


class LoopBackEvent(Event):
    """ Class for loopback events.

    Attributes:
        value: Arbitrary data to distinguish events

    Other Inherited Attributes
        t, tk, dt

    Args:
        t(ticks): value of the t attribute
        value(str): value of the value attribute
        tk(int, optional): value of the tk attribute
        dt(ticks, optional): value of the dt attribute
        kwargs: additional attribute for the event
    """
    __slots__ = ('value',)

    def __init__(self, t, value, tk=0, dt=0, **kwargs):
        self.value = value
        super().__init__(t, tk, dt, **kwargs)

    def copy(self) -> Event:
        return self.__class__(self.t, self.value, self.tk, self.dt,
                              **self.__dict__)
    __copy__ = copy

    def to_message(self, errhdr='') -> Union[bytes, bytearray]:
        raise Exception(errhdr + "Cannot convert LoopBackEvent to a message")


class XmlEvent(Event):
    """ A class of events describing additional information for staff notation.

    Attributes:
        xtype (str): a string representing the type of information
        value: Content data of information

    Other Inherited Attributes
        t, tk, dt

    Args:
        t(ticks): value of t attribute
        xtype(str): value of the xtype attribute
        value: value of the value attribute
        tk(int, optional): value of the tk attribute
        dt(ticks, optional): value of the dt attribute
        kwargs: additional attribute for the event

    List of valid events
        ========== ============ ============================= ================
        xtype      desc.         value                        optional attrs.
        ========== ============ ============================= ================
        'clef'     clef         'G', 'F', 'C'                 line(int),
                                'percussion', 'TAB',          octave_change
                                'jianpu', 'none'              (int)
        'barline'  bar line     'dashed', 'dotted', 'heavy',
                                'heavy-heavy', 'heavy-light',
                                'light-heavy', 'light-light',
                                'none', 'regular', 'short',
                                'tick', 'double', 'final',
                                'repeat-start', 'repeat-end'
        'chord'    chord symbol Chord
        'text'     generic text str
        ========== ============ ============================= ================
    """
    __slots__ = ('xtype', 'value',)

    def __init__(self, t, xtype, value, tk=1, dt=0, **kwargs):
        self.xtype = xtype
        self.value = value
        super().__init__(t, tk, dt, **kwargs)

    def copy(self) -> Event:
        return self.__class__(self.t, self.xtype, self.value,
                              self.tk, self.dt, **self.__dict__)
    __copy__ = copy

    def to_message(self, errhdr='') -> Union[bytes, bytearray]:
        raise Exception(errhdr + "Cannot convert XmlEvent to a message")


_msg_size_table = (3, 3, 3, 3, 2, 2, 3, 0)


def midimsg_size(status) -> int:
    """ Finds the length of a MIDI message from the status byte of the message.

    Args:
        status(int): MIDI status byte value

    Returns:
        Length of the message
    """
    return (-1 if status < 0x80 or status >= 0x100 else
            _msg_size_table[(status >> 4) & 7] if status <= 0xf0 else
            2 if status in (0xf1, 0xf3) else
            3 if status == 0xf2 else
            1)


def message_to_event(msg, time, tk, encoding='utf-8', errhdr='') -> Event:
    """ Takes a byte sequence in the format returned by the to_message method
    of each class and converts it to an event of the appropriate class (except
    LoopBackEvent).

    Args:
        msg(bytes, bytearray, or iterable of int): Input byte sequence
        time(ticks): time of event
        tk(int): track number
        encoding(str or None): specifies how the string of the text event is
            encoded in the byte sequence; if this is None, the string is
            copied verbatimly from the byte sequence.
        errhdr(str, optional): header string for error and warning messages

    Returns:
        Event created
    """
    ch = (msg[0] & 0xf) + 1
    etype = msg[0] & 0xf0
    if etype == 0x80:
        return NoteOffEvent(time, msg[1], msg[2], tk, ch)
    elif etype == 0x90:
        if msg[2] == 0:
            return NoteOffEvent(time, msg[1], None, tk, ch)
        else:
            return NoteOnEvent(time, msg[1], msg[2], tk, ch)
    elif etype == 0xa0:
        return KeyPressureEvent(time, msg[1], msg[2], tk, ch)
    elif etype == 0xb0:
        return CtrlEvent(time, msg[1], msg[2], tk, ch)
    elif etype == 0xc0:
        return CtrlEvent(time, C_PROG, msg[1] + 1, tk, ch)
    elif etype == 0xd0:
        return CtrlEvent(time, C_CPR, msg[1], tk, ch)
    elif etype == 0xe0:
        return CtrlEvent(time, C_BEND, msg[1] + (msg[2] << 7) - 8192, tk, ch)
    elif msg[0] == 0xf0:
        return SysExEvent(time, bytes(msg[1:]), tk)
    elif msg[0] == 0xff:
        if msg[1] == M_TEMPO:
            usecsPerBeat = (msg[2] << 16) + (msg[3] << 8) + msg[4]
            usecsPerBeat = max(usecsPerBeat, 1)
            return TempoEvent(time, 6e+7 / usecsPerBeat, tk)
        elif M_TEXT <= msg[1] <= M_TEXT_LIMIT:
            if encoding is None:
                return MetaEvent(time, msg[1], bytes(msg[2:]), tk)
            try:
                strvalue = msg[2:].decode(encoding)
            except UnicodeDecodeError:
                # warnings.warn("Unrecognized characters in text events. "
                #               "Please check the 'encoding' argument.",
                #               TaktWarning)
                strvalue = msg[2:].decode(encoding, errors='surrogateescape')
            return MetaEvent(time, msg[1], strvalue, tk)
        elif msg[1] == M_KEYSIG:
            try:
                key = Key(msg[2] - ((msg[2] & 0x80) << 1), msg[3])
            except Exception as e:
                raise e.__class__(errhdr + str(e))
            return MetaEvent(time, msg[1], key, tk)
        else:
            return MetaEvent(time, msg[1], bytes(msg[2:]), tk)
    else:
        warnings.warn(errhdr + ("unrecognized MIDI message: %r" % bytes(msg)),
                      MidiEventWarning, stacklevel=2)
        return SysExEvent(time, bytes(msg), tk)


# Eventとそのサブクラスを自動的に __all__ に含める
__all__.extend([name for name, value in globals().items()
               if name[0] != '_' and isinstance(value, type) and
               issubclass(value, Event)])
