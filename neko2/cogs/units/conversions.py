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


# Last name should be abbreviation. First should be singular and second should
# be plural.
_models = {
    UnitCollectionModel(
        UnitCategoryModel.DISTANCE,
        UnitModel.new_si('meter', 'meters', 'metre', 'metres', 'm'),
        UnitModel.new_cv('0.3048', 'foot', 'feet', 'ft'),
        UnitModel.new_cv('1000', 'kilometer', 'kilometre', 'kilometers',
                         'kilometres', 'km', exclude_from_conversions=True),
        UnitModel.new_cv('1609.34', 'mile', 'miles', 'mi'),
        UnitModel.new_cv('0.9144', 'yard', 'yards', 'yd'),
        UnitModel.new_cv('0.0254', 'inch', 'inches', 'inchs', 'in'),
        UnitModel.new_cv('1852', 'nautical mile', 'nautical miles', 'nmi'),
        UnitModel.new_cv('0.01', 'centimeter', 'centimetre', 'centimeters',
                         'centimetres', 'cm', exclude_from_conversions=True),
        UnitModel.new_cv('0.001', 'millimeter', 'millimetre', 'millimeters',
                         'millimetres', 'mm', exclude_from_conversions=True),
        UnitModel.new_cv('1.496e+11', 'astronomical unit', 'astronomical units',
                         'AU'),
        UnitModel.new_cv('9.461e+15', 'light-year', 'light-years',
                         'light year', 'light years', 'ly'),
        UnitModel.new_cv('3.086e+16', 'parsec', 'parsecs', 'pc')
    ),

    UnitCollectionModel(
        UnitCategoryModel.TIME,
        UnitModel.new_si('second', 'seconds', 's'),
        UnitModel.new_cv('60', 'minute', 'minutes'),
        UnitModel.new_cv('3600', 'hour', 'hours', 'h'),
        UnitModel.new_cv('86400', 'day', 'days', 'dy', 'dys'),
        UnitModel.new_cv('604800', 'week', 'weeks', 'wk', 'wks'),
        UnitModel.new_cv('2592000', 'month', 'months', 'mon', 'mons'),
        UnitModel.new_cv('31536000', 'year', 'years', 'yr', 'yrs'),
        UnitModel.new_cv('3.336e-11', 'jiffy', 'jiffies',
                         exclude_from_conversions=True),
        UnitModel.new_cv('5.391e-44', 'plank time', 'tP',
                         exclude_from_conversions=True)
    ),

    UnitCollectionModel(
        UnitCategoryModel.SPEED
    ),

    UnitCollectionModel(
        UnitCategoryModel.ACCELERATION
    ),

    UnitCollectionModel(
        UnitCategoryModel.AREA
    ),

    UnitCollectionModel(
        UnitCategoryModel.VOLUME
    ),

    # Includes mass for the benefit of the doubt.
    UnitCollectionModel(
        UnitCategoryModel.FORCE
    ),
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
            if pm.exclude_from_conversions:
                continue
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
            if input_string in (n.lower() for n in model.names):
                return model
