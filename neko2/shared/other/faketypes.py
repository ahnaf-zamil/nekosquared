#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Type hinting bits and pieces.
"""
import typing


class ClientSessionT:
    """
    Fake client session object which provides some type hinting support.

    This makes my IDE experience a bit nicer. Sue me.
    """
    class ResponseT:
        status: str
        reason: str

        async def read(self) -> typing.AnyStr:
            pass

        async def text(self) -> str:
            pass

        async def json(self) -> typing.Union[
                list, dict, str, int, float, bool, None]:
            pass

    # noinspection PyTypeChecker
    def __init__(self) -> typing.NoReturn:
        raise NotImplementedError

    async def get(self, url: str, params: dict=None, **kwargs) -> ResponseT:
        pass

    async def post(self, url: str, params: dict=None, **kwargs) -> ResponseT:
        pass

    async def request(self,
                      method: str,
                      url: str,
                      params: dict=None,
                      **kwargs) -> ResponseT:
        pass
