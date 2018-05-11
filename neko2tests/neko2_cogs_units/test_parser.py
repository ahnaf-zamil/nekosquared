#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Tests the parser to ensure that works.

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
import unittest

from neko2.cogs.units.models import *
from neko2.cogs.units.conversions import _models
from neko2.cogs.units.lex import *
from neko2.cogs.units.parser import *


# This relies on the lexer working. Meh. Shit unit tests are shit. I got it.
class TestParser(unittest.TestCase):
    def setUp(self):
        """
        Initialise test data.
        """
        self.variants_tests = {
            ('33cm', ValueModel('33', find_unit_by_str('centimeters'))),
            ('33e78cm', ValueModel('33e78', find_unit_by_str('centimeters'))),
            ('-33cm', ValueModel('-33', find_unit_by_str('centimeters'))),
            ('+33cm', ValueModel('33', find_unit_by_str('centimeters'))),
            ('-33e78cm', ValueModel('-33e78', find_unit_by_str('centimeters'))),
            ('+33e78cm', ValueModel('33e78', find_unit_by_str('centimeters'))),
            ('33.1234cm', ValueModel('33.1234', find_unit_by_str('centimeters'))),
            ('-33.1234cm', ValueModel('-33.1234', find_unit_by_str('centimeters'))),
            ('33cm', ValueModel('33', find_unit_by_str('centimeters'))),
            ('33cm', ValueModel('33', find_unit_by_str('centimeters')))
        }

    def test_variants(self):
        """
        Tests variants of the same unit get tokenize and parsed
        correctly
        """
        for input, output in self.variants_tests:
            token = list(tokenize(input))
            self.assertEqual(1, len(token), 'Tokenizer is iffy.')
            token = token.pop()
            value = list(parse(token))
            self.assertEqual(1, len(value), 'Parser is iffy.')
            value = value.pop()
            self.assertEqual(output, value)
