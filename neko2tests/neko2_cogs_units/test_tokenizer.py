#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Tests the tokeniser behaves as expected
"""
# noinspection PyUnresolvedReferences
import decimal
import unittest

from neko2.cogs.units.lex import *


d = decimal.Decimal


class TokenizerTests(unittest.TestCase):
    def test_none(self):
        """Tests input with no valid tokens"""
        for test in ('',
                     ' ',
                     '\n'
                     'hello world',
                     '-40',
                     '92 235',
                     'lorem ipsum dolorq sit amet 9',
                     'xxyyzz',
                     'a9'):
            result = list(tokenize(test))
            self.assertFalse(result)

    def test_ints(self):
        """Tests positive and negative integer measurements"""
        for input, output in (('5 cm', (d('5'), 'cm')),
                              ('10 q', (d('10'), 'q')),
                              ('20 miles', (d('20'), 'miles')),
                              ('-5 cm', (d('-5'), 'cm')),
                              ('-10q', (d('-10'), 'q')),
                              ('-20 miles', (d('-20'), 'miles'))):
            result = list(tokenize(input))
            self.assertEqual(1, len(result), input)
            result = result[0]
            value, unit = output
            self.assertEqual(result.value, value, input)
            self.assertEqual(result.unit, unit, input)

    def test_floats(self):
        """Tests positive and negative float measurements"""
        for input, output in (('5.1124 cm', (d('5.1124'), 'cm')),
                              ('10.97291q', (d('10.97291'), 'q')),
                              ('20.32482346868246859846196419 miles', (d('20.32482346868246859846196419'), 'miles')),
                              ('-5.1124 cm', (d('-5.1124'), 'cm')),
                              ('-10.97291q', (d('-10.97291'), 'q')),
                              ('-20.32482346868246859846196419 miles', (d('-20.32482346868246859846196419'), 'miles'))):
            result = list(tokenize(input))
            self.assertEqual(1, len(result), input)
            result = result[0]
            value, unit = output
            self.assertEqual(result.value, value, input)
            self.assertEqual(result.unit, unit, input)

    def test_exponents(self):
        """Tests positive and negative exponent-integer float measurements"""
        for input, output in (('5e68 cm', (d('5e68'), 'cm')),
                              ('10e+9632q', (d('10e9632'), 'q')),
                              ('20e-9 miles', (d('20e-9'), 'miles')),
                              ('-5e68 cm', (d('-5e68'), 'cm')),
                              ('-10e+9632q', (d('-10e9632'), 'q')),
                              ('-20e-9 miles', (d('-20e-9'), 'miles'))):
            result = list(tokenize(input))
            self.assertEqual(1, len(result), input)
            result = result[0]
            value, unit = output
            self.assertEqual(result.value, value, input)
            self.assertEqual(result.unit, unit, input)

    def test_float_exponents(self):
        """Tests positive and negative float measurements"""
        for input, output in (('5.1124e69 cm', (d('5.1124e69'), 'cm')),
                              ('10.97291e+9999q', (d('10.97291e+9999'), 'q')),
                              ('20.32482346868246859846196419e-124 miles', (d('20.32482346868246859846196419e-124'), 'miles')),
                              ('5.1124e69 cm', (d('5.1124e69'), 'cm')),
                              ('10.97291e+9999q', (d('10.97291e+9999'), 'q')),
                              ('20.32482346868246859846196419e-124 miles', (d('20.32482346868246859846196419e-124'), 'miles'))):
            result = list(tokenize(input))
            self.assertEqual(1, len(result), input)
            result = result[0]
            value, unit = output
            self.assertEqual(result.value, value, input)
            self.assertEqual(result.unit, unit, input)

