#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Implementation of an ordered set data type.

===

MIT License

Copyright (c) 2018 Neko404NotFound

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import collections
import typing

from cached_property import cached_property

__all__ = ('OrderedSet', 'MutableOrderedSet', 'Stack', 'TwoWayDict')

SetType = typing.TypeVar('SetType')


class OrderedSet(collections.Set, typing.Generic[SetType]):
    """
    A set data-type that maintains insertion order. This implementation
    is immutable for the most part.
    """

    def __init__(self, iterable: typing.Iterable = None):
        """Initialise the set."""

        # This implementation is just a dictionary that only utilises the keys.
        # We use the OrderedDict implementation underneath.
        if iterable:
            self._dict = collections.OrderedDict({k: None for k in iterable})
        else:
            self._dict = collections.OrderedDict()

    def __contains__(self, x: SetType) -> bool:
        """Return true if the given object is present in the set."""
        return x in self._dict

    def __len__(self) -> int:
        """Get the length of the set."""
        return len(self._dict)

    def __iter__(self) -> typing.Iterator[SetType]:
        """Return an iterator across the set."""
        return iter(self._dict)

    def __getitem__(self, index: int) -> SetType:
        """Access the element at the given index in the set."""
        return list(self._dict.keys())[index]

    def __str__(self) -> str:
        """Get the string representation of the set."""
        return f'{{{",".join(repr(k) for k in self)}}}'

    __repr__ = __str__


# noinspection PyProtectedMember
class MutableOrderedSet(OrderedSet, collections.MutableSet):
    """An ordered set that allows mutation."""

    def add(self, x: SetType) -> None:
        """Adds a new element to the set."""
        self._dict[x] = None

    def discard(self, x: SetType) -> None:
        """Removes an element from the set."""
        self._dict.pop(x)


FifoFiloType = typing.TypeVar('FifoFiloType')


class _FifoFiloBase(collections.Sequence, typing.Generic[FifoFiloType]):
    """
    Underlying implementation of either a FIFO/LILO or FILO/LIFO datatype.
    This is exposed as a Queue or Stack subtype.
    """

    def __init__(self,
                 items: typing.Optional[typing.Sequence[FifoFiloType]] =
                 None) \
            -> None:
        """
        Initialise the stack.
        :param items: the items to add to the stack initially.
        """
        self._deque = []
        if items:
            self._deque.extend(items)

    def __getitem__(self, index: int) -> FifoFiloType:
        """
        Get the item at the given index in the stack. Zero implies
        the bottom of the stack (first in).
        """
        return self._deque[index]

    def __setitem__(self, index: int, value: object) -> None:
        """
        Sets the value of the item in the given position in the stack.
        :param index: the index to edit at.
        :param value: the value to edit at.
        """
        self._deque[index] = value

    def __len__(self) -> int:
        """Get the stack length."""
        return len(self._deque)

    def __iter__(self) -> typing.Iterator[FifoFiloType]:
        """Get an iterator across the stack."""
        return iter(self._deque)

    def __contains__(self, x: object) -> bool:
        """Determine if the given object is in the stack."""
        return x in self._deque

    def __reversed__(self) -> None:
        """Gets the reversed representation of the stack."""
        self._deque = list(reversed(self._deque))

    def __str__(self) -> str:
        """Gets the string representation of the stack."""
        return str(self._deque)

    def __repr__(self) -> str:
        """Gets the string representation of the stack."""
        return repr(self._deque)

    def __bool__(self) -> bool:
        """Returns true if the stack is non-empty."""
        return bool(self._deque)

    def __hash__(self):
        return hash(id(self))


class Stack(_FifoFiloBase):
    """First-in-Last-out."""

    def push(self, x: FifoFiloType) -> FifoFiloType:
        """Pushes the item onto the stack and returns it."""
        self._deque.append(x)
        return x

    def pop(self) -> FifoFiloType:
        """Pops from the stack."""
        return self._deque.pop()


class Queue(_FifoFiloBase):
    """First-in-first out"""

    def enqueue(self, x: FifoFiloType) -> FifoFiloType:
        """Pushes the item onto the Queue and returns it."""
        self._deque.append(x)
        return x

    def dequeue(self) -> FifoFiloType:
        """Pops from the front of the queue."""
        return self._deque.pop(0)

    # I hate inconsistent naming.


class Deque(Queue, Stack):
    """Implementation of both a Stack and a Queue in one."""

    def shift(self):
        """Shifts from the front."""
        return self._deque.pop(0)

    def unshift(self, x: FifoFiloType):
        """Un-shifts the given element to the start of the deque."""
        self._deque.insert(0, x)
        return x


class TwoWayDict(collections.OrderedDict):
    """
    A map that supports being reversed, and caches it's value to speed up
    reversal whilst maintaining some level of integrity.

    Note that value types that are iterable will be reversed in a way that
    enforces each value in the list is a separate key.

    To comply with Python3.7, this is Ordered by default.
    """

    @cached_property
    def _reversed_representation(self) -> dict:
        rev = collections.OrderedDict()

        for k, v in self.items():
            if hasattr(v, '__iter__') and not isinstance(v, str):
                for sv in v:
                    rev[sv] = k
            else:
                rev[v] = k
        return rev

    def __reversed__(self) -> dict:
        return self._reversed_representation

    def __setitem__(self, key, value):
        if '_reversed_representation' in self.__dict__:
            del self.__dict__['_reversed_representation']
        return super().__setitem__(key, value)
