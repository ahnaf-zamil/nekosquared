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


class CommandExecutionError(RuntimeError):
    """
    Should be raised if something goes wrong in a command. Deriving from
    this ensures the correct type of error message is shown to the user.

    This should send the raw message to the user in any error handler
    implementation.
    """
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message
