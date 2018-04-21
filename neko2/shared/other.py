#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Other bits and pieces that do not belong elsewhere.
"""
import typing


def rand_colour() -> int:
    """Gets a random colour."""
    from random import randint
    return randint(0, 0xFFFFFF)
