#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Hard coded model definitions. These are singletons, and are evil... if you alter
them. They should not be altered however, so there should never be a problem.
"""
from decimal import Decimal
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
        UnitModel.new_cv('1.496e+11', 'AU', 'AU', 'astronomical unit',
                         'astronomical units', 'AU'),
        UnitModel.new_cv('9.461e+15', 'light-year', 'light-years',
                         'light year', 'light years', 'ly'),
        UnitModel.new_cv('3.086e+16', 'parsec', 'parsecs', 'pc')
    ),

    # UnitCollectionModel(
    #     UnitCategoryModel.TIME,
    #     UnitModel.new_si('second', 'seconds', 's'),
    #     UnitModel.new_cv('60', 'minute', 'minutes'),
    #     UnitModel.new_cv('3600', 'hour', 'hours', 'h'),
    #     UnitModel.new_cv('86400', 'day', 'days', 'dy', 'dys'),
    #     UnitModel.new_cv('604800', 'week', 'weeks', 'wk', 'wks'),
    #     UnitModel.new_cv('2592000', 'month', 'months', 'mon', 'mons'),
    #     UnitModel.new_cv('31536000', 'year', 'years', 'yr', 'yrs'),
    #     UnitModel.new_cv('3.336e-11', 'jiffy', 'jiffies',
    #                      exclude_from_conversions=True),
    #    UnitModel.new_cv('5.391e-44', 'plank time', 'tP',
    #                      exclude_from_conversions=True)
    # ),

    UnitCollectionModel(
        UnitCategoryModel.SPEED,
        UnitModel.new_si('meter per second', 'meters per second',
                         'metres per second', 'metre per second',
                         'ms^-1', 'm/s'),
        UnitModel.new_cv('3.6', 'kilometer per hour', 'kilometers per hour',
                         'kilometres per hour', 'kilometre per hour',
                         'kmh', 'kmph', 'kmh^-1', 'km/hr', 'km/h'),
        UnitModel.new_cv('2.23694', 'mile per hour', 'miles per hour',
                         'mi/h', 'mph'),
        UnitModel.new_cv('3.28084', 'foot per second', 'feet per second',
                         'fts^-1', 'ftsec^-1', 'ft/sec', 'ft/s'),
        UnitModel.new_cv('1.94384', 'knot', 'knots', 'kts', 'kt')
    ),

    UnitCollectionModel(
        UnitCategoryModel.VOLUME,
        UnitModel.new_si('meter³', 'meters³', 'm^3', 'm³'),
        UnitModel.new_cv('0.001', 'liter', 'litre', 'liters', 'litres', 'l'),
        UnitModel.new_cv('1e-6', 'milliliter', 'milliliters', 'millilitre',
                         'millilitres', 'ml', exclude_from_conversions=True),
        UnitModel.new_cv('1e-5', 'centiliter', 'centiliters', 'centilitre',
                         'centilitres', 'cl', exclude_from_conversions=True),
        UnitModel.new_cv('1e-6', 'centimeters³', 'cm³', 'cm^3', 'cc'),
        UnitModel.new_cv('0.000568261', 'pints', 'pint', 'UKpnt' 'pnt'),
        UnitModel.new_cv('0.00454609', 'gallons', 'gallon', 'UKgal', 'gal'),
        UnitModel.new_cv('0.000473176', 'US pints', 'US pint', 'USpnt'),
        UnitModel.new_cv('0.00378541', 'US gal', 'USgal'),
        UnitModel.new_cv('0.0283168', 'feet³', 'foot³', 'feet^3', 'foot^3',
                         'ft^3'),
        UnitModel.new_cv('1.6387e-5', 'inches³', 'inch³', 'inchs³', 'in^3'
                         'inches^3', 'inch^3', 'inchs^3', 'in³'),
    ),

    # Includes mass for the benefit of the doubt.
    UnitCollectionModel(
        UnitCategoryModel.FORCE_MASS,
        UnitModel.new_si('newton', 'newtons', 'kgms^-2', 'kg/ms^2', 'N'),
        UnitModel.new_cv('0.101936799180', 'kilogram', 'kilograms',
                         'kilogrammes', 'kg'),
        UnitModel.new_cv('4.44822', 'pound force', 'lbf'),
        UnitModel.new_cv('0.04623775433027025', 'pound', 'pounds', 'lb'),
        UnitModel.new_cv('0.6473285606237836', 'stone', 'stone', 'stones',
                         'st'),
        UnitModel.new_cv('101.93679918', 'tonne', 'T'),
    ),

    UnitCollectionModel(
        UnitCategoryModel.DATA,
        UnitModel.new_si('byte', 'bytes', 'B'),
        UnitModel.new_cv('1e3', 'kilobyte', 'kilobytes', 'kB'),
        UnitModel.new_cv('1e6', 'megabyte', 'megabytes', 'MB'),
        UnitModel.new_cv('1e9', 'gigabyte', 'gigabytes', 'GB'),
        UnitModel.new_cv('1e12', 'terabyte', 'terabytes', 'TB'),
        UnitModel.new_cv('1e15', 'petabyte', 'petabytes', 'PB'),
        UnitModel.new_cv('1024', 'kibibyte', 'kibibytes', 'kiB'),
        UnitModel.new_cv('1048576', 'mebibyte', 'mebibytes', 'MiB'),
        UnitModel.new_cv('1073741824', 'gibibyte', 'gibibytes', 'GiB'),
        UnitModel.new_cv('1099511627776', 'tebibyte', 'tebibytes', 'TiB'),
        UnitModel.new_cv('1125899906842624', 'pebibyte', 'pebibytes', 'PiB'),
        UnitModel.new_cv('0.125', 'bit', 'bits'),
        UnitModel.new_cv('0.5', 'nibble', 'nibbles'),
        UnitModel.new_cv('7.35e7', 'Gangnam Style playing on Youtube at 1080p',
                         'Gangnam Styles playing on Youtube at 1080p'),
    ),

    UnitCollectionModel(
        UnitCategoryModel.TEMPERATURE,
        UnitModel.new_si('\ufff0K', '\ufff0K', 'kelvin'),
        UnitModel(
            lambda c: c + Decimal('273.15'),
            lambda k: k - Decimal('273.15'),
            '°C', '°C', 'celsius', 'centigrade', 'oC', 'C'),
        UnitModel(
            lambda f: Decimal('5') * (f + Decimal('459.67')) / Decimal('9'),
            lambda k: (k * (Decimal('9') / Decimal('5'))) - Decimal('459.67'),
            '°F', '°F', 'fahrenheit', 'oF', 'F'),
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
