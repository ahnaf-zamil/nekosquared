#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Algorithm stuff, and general bits and pieces that don't belong elsewhere, or
that generally operate on a wide variety of data.

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
import asyncio  # Future type
import time  # Basic timestamps
import typing  # Type checking

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
    result_fut = asyncio.get_event_loop().create_task(coro(*args, **kwargs))
    result_fut.add_done_callback(callback)
    result = await result_fut
    return result, end - start


def rand_colour() -> int:
    """Gets a random colour."""
    from random import randint
    return randint(0, 0xFFFFFF)
