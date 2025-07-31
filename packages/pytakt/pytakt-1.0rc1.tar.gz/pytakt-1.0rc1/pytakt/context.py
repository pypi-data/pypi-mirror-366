# coding:utf-8
"""
This module defines the Context class and its associated functions.
"""
# Copyright (C) 2025  Satoshi Nishimura

import numbers
import os
import threading
from typing import List, Tuple, Any
from pytakt.utils import int_preferred
from pytakt.constants import L4

__all__ = ['Context', 'context', 'newcontext']


thread_local = threading.local()


class Context(object):
    """
    The Context class object (context) is a collection of parameters that
    are referenced by functions defined in the sc module as well as the mml()
    function.

    Contexts can be switched by using the 'with' syntax. For example::

        mycontext = Context(ch=2, v=50)
        with mycontext:
            ...

    will activate mycontext within the 'with' block, and return to the
    original context upon exiting the block.

    It is possible to change the value of the context's attribute by
    ``mycontext.ch=3`` for example, but you must use the addattr() method
    to add a new attribute.

    The functions defined in the sc module and the mml() function can also
    be used as methods of the Context class, allowing context-specific score
    generation (e.g. ``mycontext.note(C4)``, ``mycontext.mml('CDE')``, etc.).

    To ensure safe use in multi-threaded environments, the currently active
    context is managed separately for each thread. When a new thread is
    created, its context is always the default context (the context obtained
    by Context()).

    Attributes:
        dt (ticks): Specifies the value of the dt attribute (difference
            between the notated time and played time) of generated events.
        tk (int): Specifies the value of the tk attribute (track number) of
            generated events.
        ch (int): Specifies the value of the ch attribute (MIDI channel
            number) of generated events.
        v (int): Specifies the value of the v attribute (velocity) of
            generated NoteEvent events.
        nv (int or None): Specifies the value of the nv attribute (note-off
            velocity) of generated NoteEvent events.
        L (ticks): Specifies the value of the L attribute of generated
            NoteEvent events.
            This corresponds to the note value in ticks in the score.
            It is also used to specify the length of rests in the rest()
            function.
        duoffset(ticks or function): Holds the offset value of the playing
            duration of the note (the difference between note-on and note-off
            times in the performance, aka. gate time).
            Optionally, a function to get that value from the value of
            the L attribute can be specified.
            Together with **durate** below, it is used to determine
            the playing duration of a note.
        durate(int or float): The value added to the playing duration
            as a percentage of the note value. The playing duration is
            determined by the following equation together with the
            **duoffset** above.

                note duration at play = **duoffset** + **L** * **durate** \
/ 100 (when **duoffset** is an int/float)

                note duration at play = **duoffset(L)** + **L** * **durate** \
/ 100 (when **duoffset** is a function)

            If the note duration at play is negative, it is corrected to 0.

            The note() function sets the above value to the du attribute of
            NoteEvent (or omitted if the value is the same as the L attribute
            value).
        o (int): An integer representing the octave (4 being the octave
            starting from the middle C).
            This is used only by the mml() function.
        key (Key, int, or str): Specifies the key for automatic sharpening or
            flattening. It can be a :class:`.Key` object or
            the first argument of the Key() constructor.
            This is only used by the mml() function.
        effectors (list of callable objects): A list of callable objects
            for score conversion; callables (typically Effector instances)
            in this list are applied to the return value of the mml()
            function or that of the functions in the sc module, in sequence
            from the first element of the list to the last.

    .. rubric:: Pseudo-attributes

    In order to facilitate the specification of the playing duration of notes,
    the following two pseudo-attributes are provided.
    These can be read and written in the same way as normal instance
    attributes, but they are not registered as attributes.

    **du**
        Represents the note duration at play.
        Reading **du** yields the note duration at play (see the expression
        shown in the **durate** item above).
        Writing a value `x` to **du** sets **duoffset** to `x` and
        simultaneously sets **durate** to 0 (or 100 if `x` is negative).

        Examples:
            ``note(C4, du=120)``: Fixes the note duration at play to 120 ticks.

            ``note(C4, du=-30)``: sets the playing duration to 30 ticks less
            than the L attribute value and thus keeps the gap between notes
            to 30 ticks.

        Type:: ticks

    **dr**
        Represents the percentage of the duration at play to the note value.
        Reading **dr** yields the value of the **durate** attribute.
        Writing a value to **dr** sets **durate** to that value and
        simultaneously sets **duoffset** to 0.

        Examples:
            ``note(C4, dr=50)`` : sets the playing duration to 50% of
            the note value (simulating so-called "staccato" playing).

        Type:: int or float

    Args:
        dt, L, v, nv, duoffset, durate, tk, ch, o, key:
            Specifies attribute values of the same name.
        effectors:
            Specifies the value of the 'effectors' attribute.
            A copy of the list is assigned to the attribute.
        kwargs: specifies additional attributes for the context.
    """
    __slots__ = ('dt', 'tk', 'ch', 'v', 'nv', 'L', 'duoffset', 'durate',
                 'o', 'key', 'effectors', '_outer_context', '__dict__')
    _newtrack_count = 1

    def __init__(self, dt=0, L=L4, v=80, nv=None, duoffset=0, durate=100,
                 tk=1, ch=1, o=4, key=0, effectors=[], **kwargs):
        self.dt = dt
        self.L = L
        self.v = v
        self.nv = nv
        self.duoffset = duoffset
        self.durate = durate
        self.tk = tk
        self.ch = ch
        self.o = o
        self.key = key
        self.effectors = effectors.copy()
        self._outer_context = None
        self.__dict__.update(kwargs)

    def copy(self) -> 'Context':
        """
        Returns a duplicated context. For the 'effectors' attribute value,
        the list is duplicated. For other attributes, a shallow copy is made.
        """
        return self.__class__(self.dt, self.L, self.v, self.nv,
                              self.duoffset, self.durate, self.tk, self.ch,
                              self.o, self.key,
                              self.effectors, **self.__dict__)
    __copy__ = copy

    def __getattr__(self, name):
        if name == 'du':
            duo = self.duoffset if isinstance(self.duoffset, numbers.Real) \
                  else self.duoffset(self.L)
            return int_preferred(max(0, duo + self.L * self.durate / 100))
        elif name == 'dr':
            return self.durate
        else:
            return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name in self.__slots__ or name in self.__dict__:
            object.__setattr__(self, name, value)
        elif name == 'du':
            self.duoffset = value
            self.durate = (100 if isinstance(value, numbers.Real) and value < 0
                           else 0)
        elif name == 'dr':
            self.duoffset = 0
            self.durate = value
        else:
            raise AttributeError(
                'No such attribute %r. Use addattr() to add a new attribute.'
                % name)

    def addattr(self, name, value=None) -> None:
        """
        Adds a new attribute to the context.

        Args:
            name(str): name of the attribute
            value(any): initial value of the attribute
        """
        object.__setattr__(self, name, value)

    def has_attribute(self, name) -> bool:
        """
        Returns true if `name` is an attribute of the context.
        Differs from hasattr(self, name) in that it does not target
        method names.

        Args:
            name(str): name of the attribute
        """
        return name in (*self.__slots__, 'du', 'dr', *self.__dict__)

    def reset(self) -> None:
        """
        Returns all the attribute values to their initial values
        (i.e., default constructor argument values).
        """
        self.__dict__.clear()
        self.__init__()

    def keys(self) -> List[str]:
        """
        Returns a list of attribute names.
        """
        attrs = []
        attrs += self.__slots__
        attrs.remove('__dict__')
        attrs.remove('_outer_context')
        attrs += self.__dict__
        return attrs

    def items(self) -> List[Tuple[str, Any]]:
        """
        Returns a list of attribute name/value pairs.
        """
        return [(key, getattr(self, key)) for key in self.keys()]

    def update(self, **kwargs) -> 'Context':
        """
        Change attribute values according to the assignment description
        in `kwargs`.

        Returns:
            self
        """
        for k, v in kwargs.items():
            setattr(self, k, v)
        return self

    def __repr__(self):
        attrs = ["%s=%r" % (k, getattr(self, k)) for k in self.keys()]
        return "<Context: " + str.join(" ", attrs) + ">"

    @staticmethod
    def _push(ctxt):
        ctxt._outer_context = context()
        thread_local.current_context = ctxt

    @staticmethod
    def _pop():
        ctxt = context()
        if ctxt._outer_context is None:
            raise RuntimeError("pop on empty context stack")
        thread_local.current_context = ctxt._outer_context

    # example:
    #  with newcontext(ch=2): note(C4)
    def __enter__(self):
        Context._push(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        Context._pop()

    def do(self, func, *args, **kwargs) -> Any:
        """ Execute the function `func` in this context and return
        its return value.

        Args:
            args, kwargs: arguments passed to `func`.

        Examples:
            ``somecontext.do(lambda: note(C4) + note(D4))``
        """
        with self:
            return func(*args, **kwargs)

    def attach(self, func) -> 'Context':
        """
        Inserts the score conversion function `func` at the beginning of
        the list in the 'effectors' attribute.

        Returns:
            self

        Examples:
            >>> horn_in_F = newcontext().attach(Transpose(-Interval('P5')))
            >>> horn_in_F.note(C4)
            EventList(duration=480, events=[
                NoteEvent(t=0, n=F3, L=480, v=80, nv=None, tk=1, ch=1)])
        """
        self.effectors.insert(0, func)
        return self

    def detach(self) -> 'Context':
        """
        Deletes the first element of the list in the 'effectors' attribute.

        Returns:
            self
        """
        self.effectors.pop(0)
        return self


# 理想を言えば context をグローバル変数としたいが、python では import
# するときにグローバル変数のコピーが行われるので、モジュール内から global文で
# もって書き換えることができない。

def context() -> Context:
    """
    Returns the currently active context.
    """
    pass


# 上の context() の定義だと、 'context().attr = value' を誤って、
# 'context.attr = value' と書いたときにエラーにならないので、
# 下の定義に変更している (autodocのために元のも残してある)。
class _context_function(object):
    __slots__ = ()

    def __call__(self) -> Context:
        if not hasattr(thread_local, 'current_context'):
            thread_local.current_context = Context()
        return thread_local.current_context


if '__SPHINX_AUTODOC__' not in os.environ:
    context = _context_function()


def newcontext(**kwargs) -> Context:
    """
    Returns a copy of the currently active context with attribute values
    changed according to the assignment description in `kwargs`.
    Equivalent to ``context().copy().update(**kwargs)``.
    """
    ctxt = context().copy()
    ctxt.update(**kwargs)
    return ctxt


# def newtrack(**kwargs):
#     ctxt = newcontext(**kwargs)
#     ctxt.tk = Context._newtrack_count
#     Context._newtrack_count += 1
#     return ctxt


# def withcontext(ctxt, func):
#     with ctxt:
#         return func()
