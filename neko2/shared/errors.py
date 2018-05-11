#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Implementations of errors.

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
