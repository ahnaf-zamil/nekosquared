#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
IO bits and pieces.
"""
import inspect
import os

__all__ = ('in_here',)


def in_here(*paths, nested_by=0):
    """
    Gets the absolute path of the path relative to the file you called this
    function from. This works by inspecting the current stack and extracting
    the caller module, then getting the parent directory of the caller as an
    absolute path.

    :param paths: each path fragment to format.
    :param nested_by: how many function calls to consider this call nested in.
            This is important if you call this as part of an outer utility,
            as we have to inspect the stack to get the file name. This defaults
            to zero, inferring to get the file that directly calls this function
            itself.
    """
    try:
        frame = inspect.stack()[1 + nested_by]
    except IndexError:
        raise RuntimeError('Could not find a stack record. Interpreter has '
                           'been shot.')
    else:
        module = inspect.getmodule(frame[0])
        assert hasattr(module, '__file__'), 'No __file__ attr, whelp.'

        file = module.__file__

        dir_name = os.path.dirname(file)
        abs_dir_name = os.path.abspath(dir_name)

        return os.path.join(abs_dir_name, *paths)
