#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Tests the parser to ensure that works.
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
