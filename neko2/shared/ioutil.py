#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
IO bits and pieces.

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
import inspect  # Stack frame inspection
import os  # OS path utils

__all__ = ('in_here', 'json', 'yaml', 'get_inode_type')


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
            to zero, inferring to get the file that directly calls this
            function
            itself.
    """
    result, frame = None, None
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

        result = os.path.join(abs_dir_name, *paths)
    
    # This is to prevent cyclic references that screw the interpreter up.
    del frame
    return result


def json(file, *, relative_to_here=True):
    """Loads a JSON file on the fly and returns the data."""
    import json

    if relative_to_here:
        file = in_here(file, nested_by=1)

    with open(file) as fp:
        return json.load(fp)


def yaml(file, *, relative_to_here=True):
    """Loads a YAML file on the fly and returns the data."""
    import yaml

    if relative_to_here:
        file = in_here(file, nested_by=1)

    with open(file) as fp:
        return yaml.load(fp)


def get_inode_type(*paths):
    """
    Returns a string representing the inode type, or none if the inode doesn't
    exist.

    :param paths: the paths to join.
    :return: 'dir', 'link', 'file', None
    """
    path = os.path.join(*paths)

    if not os.path.exists(path):
        return None
    elif os.path.islink(path):
        return 'link'
    elif os.path.isfile(path):
        return 'file'
    elif os.path.isdir(path):
        return 'dir'
    else:
        assert False, f'Unknown inode type for {path}.'
