#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Hard coded model definitions. These are singletons, and are evil... if you alter
them. They should not be altered however, so there should never be a problem.
"""
from typing import Optional, Iterator

from neko2.shared import alg
from .models import *


__all__ = ('get_category', 'get_compatible_models', 'find_unit_by_str')


_models = {
    UnitCollectionModel(
        UnitCategoryModel.DISTANCE,
        UnitModel.new_si('meter', 'metre', 'meters', 'metres', 'm'),
        UnitModel.new_cv('0.3048', 'foot', 'feet', 'ft'),
        UnitModel.new_cv('1000', 'kilometer', 'kilometre', 'kilometers',
                         'kilometres', 'km'),
        UnitModel.new_cv('1609.34', 'mile', 'miles', 'mi'),
        UnitModel.new_cv('0.9144', 'yard', 'yards', 'yd'),
        UnitModel.new_cv('0.0254', 'inch', 'inchs', 'inches', 'in'),
        UnitModel.new_cv('1852', 'nautical mile', 'nautical miles', 'nmi'),
        UnitModel.new_cv('0.01', 'centimeter', 'centimetre', 'centimeters',
                         'centimetres', 'cm'),
        UnitModel.new_cv('0.001', 'millimeter', 'millimetre', 'millimeters',
                         'millimetres', 'mm')
    )
}


def get_category(category: UnitCategoryModel) -> Optional[UnitCollectionModel]:
    """
    Gets the given collection of measurement quantities for the given
    dimensionality of measurement.
    """
    res = alg.find(lambda c: c.unit_type == category, _models)
    return res


def get_compatible_models(model: UnitModel,
                          ignore_self: bool=False,
                          ignore_si: bool=False) -> Iterator[UnitModel]:
    """Yields any compatible models with the given model, including itself."""
    if ignore_self or ignore_si:
        for pm in get_category(model.unit_type):
            if ignore_self and pm == model:
                continue
            elif ignore_si and model.is_si:
                continue
            else:
                yield pm

    else:
        yield from get_category(model.unit_type)


def find_unit_by_str(input_string: str) -> Optional[UnitModel]:
    """
    Attempts to find a match for the given input string. Returns None if
    nothing is resolved.
    """
    input_string = input_string.lower()

    for category in _models:
        for model in category:
            if input_string in model.names:
                return model
