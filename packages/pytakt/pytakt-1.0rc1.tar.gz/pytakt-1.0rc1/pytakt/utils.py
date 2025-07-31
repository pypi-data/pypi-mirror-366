# coding:utf-8
import math
import random
import os
import re
from fractions import Fraction
from typing import Union

# Copyright (C) 2025  Satoshi Nishimura

__all__ = ['takt_round', 'takt_roundx', 'int_preferred', 'std_time_repr',
           'frac_time_repr', 'TaktWarning', 'NoteDict', 'get_file_type',
           'Ticks', 'Fraction']


Ticks = Union[int, float, Fraction]


def takt_round(x) -> int:
    """
    Round `x` to the nearest integer, the larger if there are two
    possibilities.

    Args:
        x(float): the original value

    Returns:
        Resulting value
    """
    # Python's round() has differnt behavior in V2 and V3
    return int(math.floor(x + .5))


_ROUNDX_EPSILON = 1e-4


def takt_roundx(x, mode) -> int:
    """
    Rounding function to an integer with various rounding modes.

    Args:
        x(float): original value
        mode(str or function): rounding mode represented by one of the
            followings.

            * 'nearestup': The integer closest to `x`.
              If there are two possibilities, the larger one is chosen.
            * 'nearestdown': The integer closest to `x`.
              If there are two possibilities, the smaller one is chosen.
            * 'floor': The largest integer less than or equal to `x`.
            * 'ceil': The smallest integer greater than or equal to `x`.
            * 'down': The largest integer less than or equal to (`x` + 10
              :sup:`-4`) ('floor' with allowing calculation errors).
            * 'up': The smallest integer greater than or equal to (`x` - 10
              :sup:`-4`) ('ceil' with allowing calculation errors).
            * 'random': 'up' or 'down' chosen at random with equal
              probability.
            * function: the function is called with `x` as argument, and
              its return value is the result.

    Returns:
        Result value
    """
    if mode == 'nearestup':
        return int(math.floor(x + .5))
    elif mode == 'nearestdown':
        return int(math.ceil(x - .5))
    elif mode == 'down':
        return int(math.floor(x + _ROUNDX_EPSILON))
    elif mode == 'up':
        return int(math.ceil(x - _ROUNDX_EPSILON))
    elif mode == 'floor':
        return int(math.floor(x))
    elif mode == 'ceil':
        return int(math.ceil(x))
    elif mode == 'random':
        return random.choice((takt_roundx(x, 'up'), takt_roundx(x, 'down')))
    elif callable(mode):
        return mode(x)
    else:
        raise ValueError('%r: Unrecognized rounding mode' % (mode,))


def int_preferred(x) -> Union[int, float, Fraction]:
    """
    If `x` has an integer value, convert it to the 'int' type, otherwise
    return it as it is.

    Args:
        x(int, float, or Fraction): original value

    Returns:
        Resulting value
    """
    try:
        return int(x) if int(x) == x else x
    except (OverflowError, ValueError):
        return x


def std_time_repr(time) -> str:
    """
    Converts `time` to a string with 5 decimal places.

    This function is used when converting an Event or EventList to a string
    with the str function.

    Args:
        time(ticks): value
    """
    if isinstance(time, Fraction):
        time = float(time)
    return repr(round(time, 5))


def frac_time_repr(time) -> str:
    """
    Converts `time` to a string using fractional notation that is as accurate
    and compact as possible.
    Unlike the repr function, the result may contain a conversion error
    up to 1e-8.

    This function is the default time-to-string conversion function
    in :func:`.showtext` when it is not in the raw mode.

    Args:
        time(ticks): value
    """
    if int(time) == time:
        return repr(int(time))
    elif round(time, 5) == time:
        return repr(time)
    else:
        ratio = Fraction(time).limit_denominator(99)
#        if ('%.9e' % ratio) == ('%.9e' % time):
        if abs(ratio - time) < 1e-8:
            # 99.99999999999999のときのように分母が1になることがある。
            return '%d' % ratio.numerator if ratio.denominator == 1 else \
                '%d+%d/%d' % (ratio.numerator // ratio.denominator,
                              ratio.numerator % ratio.denominator,
                              ratio.denominator)
        else:
            return repr(time)


class TaktWarning(UserWarning):
    pass


class NoteDict:
    """
    A dictionary for finding correspondences between events (typically for
    NoteOnEvent and NoteOffEvent).
    By default, it uses (track number, MIDI channel number, MIDI note number)
    as key to find events with the same key. Unlike normal dict, it allows
    multiple elements for the same key.
    """
    def __init__(self):
        self.notedict = {}  # dict of list

    def __repr__(self):
        return f"<NoteDict notedict={self.notedict!r}>"

    def __bool__(self):
        return bool(self.notedict)

    def clear(self):
        self.notedict.clear()

    def copy(self):
        result = NoteDict()
        result.notedict = {k: lst.copy() for (k, lst) in self.notedict.items()}
        return result

    def push(self, key, value):
        self.notedict.setdefault(key, []).append(value)

    def pushuniq(self, key, value):
        self.notedict[key] = (value,)

    def pushnote(self, ev, value):  # evは典型的にはNoteOnEvent
        self.push((ev.tk, ev.ch, ev.n), value)

    __default = object()

    def pop(self, key, default=__default):
        try:
            lst = self.notedict[key]
        except KeyError:
            if default is self.__default:
                raise
            return default
        value = lst.pop(0)  # use FIFO heuristic
        if not lst:
            del self.notedict[key]
        return value

    def popuniq(self, key, default=__default):
        if default is self.__default:
            return self.notedict.pop(key)[0]
        else:
            return self.notedict.pop(key, (default,))[0]

    def popnote(self, ev, default=__default):  # evは典型的にはNoteOffEvent
        return self.pop((ev.tk, ev.ch, ev.n), default)

    def items(self):
        return ((k, v) for (k, lst) in self.notedict.items() for v in lst)

    def keys(self):
        return (k for (k, lst) in self.notedict.items() for v in lst)

    def values(self):
        return (v for lst in self.notedict.values() for v in lst)

    def uniquekeys(self):
        return self.notedict.keys()

    def popitem(self):
        # dict.popitemと異なりFIFOの順序で取り出す
        if not self.notedict:
            raise KeyError('popitem(): notedict is empty')
        else:
            k, lst = next(iter(self.notedict.items()))
            if len(lst) == 1:
                del self.notedict[k]
                return k, lst[0]
            else:
                return k, lst.pop(0)


def get_file_type(path, types=('smf', 'json', 'mxl'), guess=True) -> str:
    """
    Determines whether the file specified by `path` is a standard MIDI file,
    a JSON file, or a MusicXML file.
    First, the extension in the pathname is examined to determine the file
    type.  If it cannot be determined from the pathname, it is inferred from
    the file content (only if guess=True). If it still cannot be determined,
    an exception is raised.

    Args:
        path(str): path name of the file
        types(tuple of str): Acceptable file formats
        guess(bool, optional): If True, guessed from the file content in
            addition to the extension in the pathname.

    Returns:
        'smf' for standard MIDI files, 'json' for JSON files, or 'mxl' for
        MusicXML files.
    """
    _, ext = os.path.splitext(path)
    ext = ext.lower()
    extdict = {}
    for typ in types:
        elist = ('.mid', '.midi', '.smf') if typ == 'smf' else \
                ('.json',) if typ == 'json' else \
                ('.mxl', '.musicxml', '.xml') if typ == 'mxl' \
                else ()
        for x in elist:
            extdict[x] = typ
    try:
        return extdict[ext]
    except KeyError:
        pass

    if guess:
        with open(path, 'rb') as fp:
            header = fp.read(256)
        if 'smf' in types and header[0:4] == b'MThd':
            return 'smf'
        if 'json' in types and \
           re.match(rb'\s*\{\s*"(__event_list__|__tracks__)"', header):
            return 'json'
        if 'mxl' in types and re.match(rb'(?s)<\?xml.*DTD MusicXML', header):
            return 'mxl'
        # Compressed MusicXML is not recongnized.

    raise Exception("Only the following file types supported: "
                    + ' '.join(extdict))
