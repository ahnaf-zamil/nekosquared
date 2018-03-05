#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Algorithm stuff, and general bits and pieces that don't belong elsewhere, or
that generally operate on a wide variety of data.
"""
import time       # Basic timestamps
import typing     # Type checking


def find(predicate, iterable):
    """
    Attempts to find the first match for the given predicate in the iterable.

    If the element is not found, then ``None`` is returned.
    """
    for el in iterable:
        if predicate(el):
            return el


async def find_async(async_predicate, iterable):
    """
    See ``find``. This operates in the same way, except we await the
    predicate on each call.
    """
    for el in iterable:
        if await async_predicate(el):
            return el


async def find_async_iterator(async_predicate, async_iterator):
    """
    Same as ``find_async``, but treats the iterator as an ``await``able
    object.
    """
    for el in await async_iterator:
        if await async_predicate(el):
            return el


def find_all(predicate, iterable):
    """
    Yields all matches for the predicate across the iterable.
    """
    for el in iterable:
        if predicate(el):
            yield el


def time_it(call, *args, **kwargs) -> (typing.Any, float):
    """
    Times how long it takes to perform a task synchronously.

    :param call: the function to call.
    :param args: the arguments to give the callable.
    :param kwargs: the kwargs to give the callable.
    :returns: a tuple of the return result and the time taken in seconds.
    """
    start = time.time()
    result = call(*args, **kwargs)
    end = time.time()

    return result, end - start


async def time_it_async(coro, *args, **kwargs) -> (typing.Any, float):
    """
    Times how long it takes to perform a task asynchronously.

    :param coro: the coroutine to call.
    :param args: the arguments to give the callable.
    :param kwargs: the kwargs to give the callable.
    :returns: a tuple of the return result and the time taken in seconds.
    """
    start = time.time()
    result = await coro(*args, **kwargs)
    end = time.time()

    return result, end - start
