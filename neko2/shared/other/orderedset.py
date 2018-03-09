#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Implementation of an ordered set data type.
"""
import collections
import typing

__all__ = ('OrderedSet', 'MutableOrderedSet')


# noinspection PyProtectedMember
class OrderedSet(collections.Set):
    """
    A set data-type that maintains insertion order. This implementation
    is immutable for the most part.
    """
    def __init__(self, iterable: typing.Iterable=None):
        """Initialise the set."""

        # This implementation is just a dictionary that only utilises the keys.
        # We use the OrderedDict implementation underneath.
        if iterable:
            self._dict = collections.OrderedDict({k: None for k in iterable})
        else:
            self._dict = collections.OrderedDict()

    def __contains__(self, x: object) -> bool:
        """Return true if the given object is present in the set."""
        return x in self._dict

    def __len__(self) -> int:
        """Get the length of the set."""
        return len(self._dict)

    def __iter__(self) -> typing.Iterator[typing._T_co]:
        """Return an iterator across the set."""
        return iter(self._dict)

    def __getitem__(self, index: int) -> typing._T:
        """Access the element at the given index in the set."""
        return list(self._dict.keys())[index]

    def __str__(self) -> str:
        """Get the string representation of the set."""
        return f'{{{",".join(repr(k) for k in self)}}}'

    __repr__ = __str__


# noinspection PyProtectedMember
class MutableOrderedSet(OrderedSet, collections.MutableSet):
    """An ordered set that allows mutation."""
    def add(self, x: typing._T) -> None:
        """Adds a new element to the set."""
        self._dict[x] = None

    def discard(self, x: typing._T) -> None:
        """Removes an element from the set."""
        self._dict.pop(x)
