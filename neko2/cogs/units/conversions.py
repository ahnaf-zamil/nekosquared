#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Hard coded model definitions. These are singletons, and are evil... if you alter
them. They should not be altered however, so there should never be a problem.
"""
from typing import Optional, Iterator

from neko2.shared import alg
from .models import *


_models = {
    UnitCollectionModel(
        UnitCategoryModel.DISTANCE,
        UnitModel.new_si('meter', 'metre', 'meters', 'metres', 'm'),
        UnitModel.new_cv('0.3048', 'foot', 'feet', 'ft'),
        UnitModel.new_cv('1000', 'kilometer', 'kilometre', 'kilometers', 'kilometres', 'km'),
        UnitModel.new_cv('0.9144', 'yard', 'yards', 'yd'),
        UnitModel.new_cv('0.0254', 'inch', 'inchs', 'inches', 'in'),
        UnitModel.new_cv('1852', 'nautical mile', 'nautical miles', 'nmi'),
        UnitModel.new_cv('0.01', 'centimeter', 'centimetre', 'centimeters', 'centimetres', 'cm')
    )
}


def get_category(category: UnitCategoryModel) -> Optional[UnitCollectionModel]:
    """
    Gets the given collection of measurement quantities for the given
    dimensionality of measurement.
    """
    return alg.find(lambda c: c.unit_type == category, _models)


def get_compatible_models(model: UnitModel,
                          ignore_self: bool=False) -> Iterator[UnitModel]:
    """Yields any compatible models with the given model, including itself."""
    if ignore_self:
        for pm in get_category(model.unit_type):
            if pm is not model:
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
