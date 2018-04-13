#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
A cached Sequel statement that we gather from disk.
"""
import logging

from neko2.shared import ioutil      # in_here


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
