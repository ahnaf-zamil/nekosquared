#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
An abstract implementation of an asynchronous auto-serialized dictionary.

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
import abc
import typing


class AbstractASDict(abc.ABC, typing.Dict[typing.Any, typing.Any]):
    def __init__(self):
        super().__init__()

    async def get(self, k: typing.Any, default: typing.Any = None):
        """
        Accesses the given element or returns the default if nothing
        is found.
        """
        try:
            return self[k]
        except KeyError:
            return default

    @abc.abstractmethod
    def __getitem__(self, key: typing.Any) -> typing.Awaitable[typing.Any]:
        """
        Asynchronously gets the item.
        """
        pass

    @abc.abstractmethod
    def __setitem__(self,
                    key: typing.Any,
                    value: typing.Any) -> typing.Awaitable[typing.Any]:
        """
        Asynchronously mutates the item.
        :param key: the key.
        :param value: the value.
        :return: a coroutine or future to await.
        """
        pass
