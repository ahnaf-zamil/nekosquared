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
#
# Capture groups:
#     - #1 - numeric value
#     - #2 - optional space (allows us to ignore short phrases if a space
#            exists at the start, for example, to ignore "33 in here" as
#            being 33 inches.
#     - #3 - the unit string.
#
# 23rd April 2018 - Replaced non-match at start and end with positive look
#     behind and positive look ahead assertions. This prevents the word
#     boundary being consumed and then not being present for the next token
#     if multiple units of measurement follow eachother directly. The
#     previous behaviour prevented every other expected consecutive match
#     (e.g. in the string 1.3m 2.3m 3.3m 4.3m) to be ignored as the boundary
#     was consumed and not present for the second/fourth/sixth/etc token.
#     EDIT 2: To simplify regex. We pad the input string by a space either
#        side to prevent having to match start and end of string.
raw_unit_pattern = (
    r'(?<=\s)([-+]?(?:(?:\d+)[.]\d+|\d+)(?:[eE][-+]?\d+)?)(\s?)(.+?)(?=\s)'
)

pattern = re.compile(raw_unit_pattern, re.I)


def tokenize(input_string: str) -> typing.Iterator[PotentialValueModel]:
    input_string = ' ' + input_string + ' '
    matches = list(pattern.finditer(input_string))

    for result in matches:
        value = decimal.Decimal(result.group(1))
        space = result.group(2)
        unit_string = result.group(3)

        if not len(space) or len(unit_string) >= 3:
            yield PotentialValueModel(value, unit_string)
