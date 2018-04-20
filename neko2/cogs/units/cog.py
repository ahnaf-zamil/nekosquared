#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Listens to messages on all channels, and tests if any substrings can be found
that appear to be units of measurement.

A reaction is then added to the corresponding message for a given period of
time. Interacting with it will trigger the main layer of logic in this
extension.

On a positive hit, we convert those into an SI representation and then back to
every commonly used possibility.
"""
import decimal
import re
import typing

from .models import *

# Regex to match a unit of measurement. This essentially looks for a word
# boundary, followed by a valid IEEE floating point representation of a number,
# followed by a single optional space. The last section matches a unit of
# measurement such
raw_unit_pattern = (
    r'(?:\s|^)([-+]?(?:(?:\d+)\.\d+|\d+)(?:[eE][-+]?\d+)?) ?([-°^"/\w]+)(?:\b)')

pattern = re.compile(raw_unit_pattern, re.I)


def tokenize(input_string: str) -> typing.Iterator[PotentialValueModel]:
    matches = pattern.finditer(input_string)

    for result in matches:
        value = decimal.Decimal(result.group(1))
        unit_string = result.group(2)
        yield PotentialValueModel(value, unit_string)
