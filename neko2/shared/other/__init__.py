#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Other more bespoke utilities used throughout the bot, such as fuzzy string
pattern matching, fake type implementations, et cetera.

Uncategorised bits and bobs can go here directly.
"""
from . import excuses
from . import fuzzy
from . import orderedset


def rand_colour() -> int:
    """Gets a random colour."""
    from random import randint
    return randint(0, 0xFFFFFF)
