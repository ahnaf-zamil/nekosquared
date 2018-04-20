#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Hard coded model definitions.
"""
from .models import *


_models = {
    UnitCollectionModel(
        UnitCategoryModel.DISTANCE,
        UnitModel.new_si('meter', 'metre', 'meters', 'metres', 'm'),
        UnitModel.new_cv('0.3048', 'foot', 'feet', 'ft'),
        UnitModel.new_cv('1000', 'kilometer', 'kilometre', 'kilometers',
                         'kilometres', 'km'),
        UnitModel.new_cv('0.9144', 'yard', 'yards', 'yd'),
        UnitModel.new_cv('0.0254', 'inch', 'inchs', 'inches', 'in'),
        UnitModel.new_cv('1852', 'nautical mile', 'nautical miles', 'nmi'),
        UnitModel.new_cv('0.01', 'centimeter', 'centimetre', 'centimeters',
                         'centimetres', 'cm')
    )
}