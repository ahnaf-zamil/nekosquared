#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Parser logic.

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
import typing

from neko2.cogs.units.conversions import find_unit_by_str
from neko2.cogs.units.models import PotentialValueModel, ValueModel


def _parse(input_model: PotentialValueModel) -> typing.Optional[ValueModel]:
    """Parses a single value.s"""
    unit_type = find_unit_by_str(input_model.unit)
    if unit_type is not None:
        return ValueModel(input_model.value, unit_type)


def parse(input_model: PotentialValueModel,
          *input_models: PotentialValueModel) -> typing.Iterator[ValueModel]:
    """
    Takes one or more input models that may be a measurement, and attempts
    to parse them, returning an iterator across all parsed results,
    and ignoring
    any that turn out to be invalid.
    """
    # Parse the potential models.
    for pm in (input_model, *input_models):
        parsed = _parse(pm)
        if parsed is not None:
            yield parsed
