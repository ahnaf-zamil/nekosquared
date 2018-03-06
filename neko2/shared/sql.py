#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
A cached Sequel statement that we gather from disk.
"""
from neko2.shared import io      # in_here
from neko2.shared import traits  # Logging trait


__all__ = ('SqlQuery',)


class SqlQuery(traits.Scribe):
    """
    This reads a SQL query from disk at the given path and acts as a descriptor
    returning the raw SQL query text.

    This is designed to be embedded in class-scope and then accessed by an
    instance of that class.
    """
    def __init__(self, file_name, *, relative_to_here=True):
        """
        Reads the query from file, and initialises the object.

        :param file_name: file name to open.
        :param relative_to_here: defaults to true. If true, we consider the file
                to be in the same directory as the caller.
        """
        if relative_to_here:
            self._file_name = io.in_here(file_name, nested_by=1)
        else:
            self._file_name = file_name

        with open(self._file_name) as fp:
            self.content = '\n'.join(fp.readlines())

        self.logger.info(f'Deserialized {file_name}')

    def __get__(self, *_):
        """This acts as the descriptor."""
        return self.content
