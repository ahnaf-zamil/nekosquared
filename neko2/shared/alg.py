#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Algorithm stuff, and general bits and pieces that don't belong elsewhere, or
that generally operate on a wide variety of data.
"""
import asyncio    # Future type
import time       # Basic timestamps
import typing     # Type checking


__all__ = ('find', 'find_async', 'find_async_iterator', 'find_all',
           'time_it', 'time_it_async')


def find(predicate, iterable, default=None):
    """
    Attempts to find the first match for the given predicate in the iterable.

    If the element is not found, then ``None`` is returned.
    """
    for el in iterable:
        if predicate(el):
            return el

    return default


async def find_async(async_predicate, iterable, default=None):
    """
    See ``find``. This operates in the same way, except we await the
    predicate on each call.
    """
    for el in iterable:
        if await async_predicate(el):
            return el

    return default


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
    start = time.monotonic()
    result = call(*args, **kwargs)
    end = time.monotonic()

    return result, end - start


async def time_it_async(coro, *args, **kwargs) -> (typing.Any, float):
    """
    Times how long it takes to perform a task asynchronously.

    Note that this measures time between start and finish. If other coroutines
    are in the queue between these calls, then it will impact the runtime.

    :param coro: the coroutine to call.
    :param args: the arguments to give the callable.
    :param kwargs: the kwargs to give the callable.
    :returns: a tuple of the return result and the time taken in seconds.
    """
    end = 0

    def callback():
        nonlocal end
        end = time.monotonic()

    start = time.monotonic()
    result_fut = asyncio.ensure_future(coro(*args, **kwargs))
    result_fut.add_done_callback(callback)
    result = await result_fut
    return result, end - start
