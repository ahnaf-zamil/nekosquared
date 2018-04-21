#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Tokenizer logic.
"""
import decimal
import re
import typing

from neko2.cogs.units.models import PotentialValueModel
from .conversions import *


__all__ = ('tokenize',)


# Regex to match a unit of measurement. This essentially looks for a word
# boundary, followed by a valid IEEE floating point representation of a number,
# followed by a single optional space. The last section matches a unit of
# measurement that starts with a non-space and non-digit value.
raw_unit_pattern = (
    r'(?:\s|^)([-+]?(?:(?:\d+)\.\d+|\d+)(?:[eE][-+]?\d+)?)\s?'
    r'([^\s0-9].*)(?:\b)')

pattern = re.compile(raw_unit_pattern, re.I)


def tokenize(input_string: str) -> typing.Iterator[PotentialValueModel]:
    matches = pattern.finditer(input_string)

    for result in matches:
        value = decimal.Decimal(result.group(1))
        unit_string = result.group(2)
        yield PotentialValueModel(value, unit_string)
