#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
An abstract implementation of an asynchronous auto-serialized dictionary.
"""
import abc
import typing


class AbstractASDict(abc.ABC, typing.Dict[typing.Any, typing.Any]):
    def __init__(self):
        super().__init__()

    async def get(self, k: typing.Any, default: typing.Any=None):
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
