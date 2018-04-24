#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Ensures the correct version of Discord.py is installed.
"""
import importlib
import warnings


__all__ = ()


discord = None

try:
    discord = importlib.import_module('discord')
    if discord.version_info.major != 1:
        raise RuntimeError('The wrong version of discord.py is installed. '
                           f'Expected v1.x.x, got {discord.__version__}')
except BaseException as ex:
    warnings.warn(str(ex), type(ex))

del warnings
del discord

