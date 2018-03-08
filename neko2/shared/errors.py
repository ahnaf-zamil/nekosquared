#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Implementations of errors.
"""


__all__ = ('HttpError', 'NotFound')


class HttpError(RuntimeError):
    def __init__(self, response):
        self.response = response

    @property
    def reason(self) -> str:
        return self.response.reason

    @property
    def status(self) -> int:
        return self.response.status

    def __str__(self):
        return f'{self.status}: {self.reason}'


class NotFound(RuntimeError):
    def __init__(self, message=None):
        self.message = message if message else "No valid result was found"

    def __str__(self):
        return self.message
