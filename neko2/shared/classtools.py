#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Utilities for monkey-patching classes.
"""


__all__ = ('patches',)


def patches(what):
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
                # noinspection PyBroadException
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
                # noinspection PyBroadException
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
    """Metaclass to enforce the singleton pattern."""
    _cache = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._cache:
            inst = super(SingletonMeta, cls).__call__(*args, **kwargs)
            cls._cache[cls] = inst

        return cls._cache[cls]
