#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Colour datatype. Contains storage for the given colour as a set of decimals,
plus conversions from RGBA to other systems.

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
from decimal import Decimal

from cached_property import cached_property
from dataclasses import dataclass


@dataclass(repr=True)
class Colour:
    _r: Decimal
    _g: Decimal
    _b: Decimal
    _a: Decimal

    @property
    def rgb(self):
        return self._r, self._g, self._b

    @property
    def rgba(self):
        return self._r, self._g, self._b, self._a

    @property
    def argb(self):
        return self._a, self._r, self._g, self._b

    @property
    def abgr(self):
        return self._a, self._b, self._g, self._r

