#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Parser logic.
"""
import typing

from neko2.cogs.units.conversions import find_unit_by_str
from neko2.cogs.units.models import ValueModel, PotentialValueModel


def _parse(input_model: PotentialValueModel) -> typing.Optional[ValueModel]:
    """Parses a single value.s"""
    unit_type = find_unit_by_str(input_model.unit)
    if unit_type is not None:
        return ValueModel(input_model.value, unit_type)


def parse(input_model: PotentialValueModel,
          *input_models: PotentialValueModel) -> typing.Iterator[ValueModel]:
    """
    Takes one or more input models that may be a measurement, and attempts
    to parse them, returning an iterator across all parsed results, and ignoring
    any that turn out to be invalid.
    """
    # Parse the potential models.
    for pm in (input_model, *input_models):
        parsed = _parse(pm)
        if parsed is not None:
            yield parsed
