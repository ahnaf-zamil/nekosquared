#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""Utilities for monkey-patching classes."""


def patches(original_kass):
    """
    For implicitly monkey patching a class onto another class with a
    decorator. This is similar to the ``functools.wraps`` but for classes.
    """
    def decorator(new_klass: type):
        for attr in ('__name__',
                     '__qualname__',
                     '__module__',
                     '__class__',
                     '__doc__'):
            # noinspection PyBroadException
            try:
                setattr(new_klass, attr, getattr(original_kass, attr, None))
            except BaseException:
                pass
        return new_klass
    return decorator
