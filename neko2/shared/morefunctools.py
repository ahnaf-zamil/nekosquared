#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Utilities for monkey-patching classes and functions. This is to be used
as a drop-in for functools, which gets imported.
"""
import asyncio
import functools as _functools
from functools import *

__all__ = (*dir(_functools), 'old_wraps')


old_wraps = _functools.wraps


# noinspection PyBroadException
def wraps(what):
    """
    For implicitly monkey patching a class onto another class with a
    decorator. This is similar to the ``functools.wraps`` but for classes.

    This also will work with functions and coroutine types.
    """
    if isinstance(what, type):
        def decorator(new_klass: type):
            for attr in ('__name__',
                         '__qualname__',
                         '__module__',
                         '__class__',
                         '__doc__'):
                try:
                    setattr(new_klass,
                            attr,
                            getattr(what, attr, None))
                except BaseException:
                    pass
            return new_klass
        return decorator
    else:
        def decorator(fn: callable):
            for attr in ('__name__',
                         '__doc__'):
                try:
                    setattr(fn,
                            attr,
                            getattr(what, attr, None))
                except BaseException:
                    pass
            return fn
        return decorator


class ClassProperty:
    """
    A property that belongs to the class it is defined in, rather than the
    object instances themselves.
    """
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, _, owner):
        return self.getter(owner)


class SingletonMeta(type):
    """
    Metaclass to enforce the singleton pattern.

    !!!!!!!!!!!!!!THIS IS NOT THREAD SAFE!!!!!!!!!!!!!!
    """
    _cache = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._cache:
            inst = super(SingletonMeta, cls).__call__(*args, **kwargs)
            cls._cache[cls] = inst

        return cls._cache[cls]


def always_background(loop: asyncio.AbstractEventLoop=None):
    """
    Decorates a coroutine and ensures that whenever we invoke it, we
    actually end up creating a task in the background. This is a neat
    little drop-in that will essentially allow both await and normal
    calling, to ensure compatibility.

    :param loop: the event loop to delegate on. Uses the default if
        unspecified.
    """
    def decorator(coro):
        @wraps(coro)
        class AlwaysInvokeAsTaskInBackground:
            __slots__ = ()

            def __call__(self, *args, **kwargs):
                """Invokes as a task."""
                nonlocal loop

                if loop is None:
                    loop = asyncio.get_event_loop()

                task = loop.create_task(coro(*args, **kwargs))

                # Enables awaiting, optionally.
                return task

        return AlwaysInvokeAsTaskInBackground()
    return decorator
