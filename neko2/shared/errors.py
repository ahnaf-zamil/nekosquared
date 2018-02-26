#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Implementations of errors.
"""


class HttpError(RuntimeError):
    def __init__(self, response):
        self.response = response

    @property
    def reason(self) -> str:
        return self.response.reason

    @property
    def status_code(self) -> int:
        return self.response.status_code

    def __str__(self):
        return f'{self.status_code}: {self.reason}'
