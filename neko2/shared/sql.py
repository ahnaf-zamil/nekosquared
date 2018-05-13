#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
A cached Sequel statement that we gather from disk.

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
import logging

from neko2.shared import ioutil  # in_here

__all__ = ('sql_query',)

__logger = logging.getLogger(__name__)


def sql_query(file_name: str, *, relative_to_here=True) -> str:
    """
    Reads the query from file, and initialises the object.

    :param file_name: file name to open.
    :param relative_to_here: defaults to true. If true, we consider the file
            to be in the same directory as the caller.
    """
    if relative_to_here:
        file_name = ioutil.in_here(file_name, nested_by=1)

    if ioutil.get_inode_type(file_name) != 'file':
        in_ty = ioutil.get_inode_type(file_name + '.sql')
        if in_ty == 'file':
            file_name = file_name + '.sql'
        else:
            raise FileNotFoundError(f'Cannot find {file_name}')

    with open(file_name) as fp:
        content = '\n'.join(fp.readlines())

    __logger.info(f'Deserialized {file_name}')

    return content
