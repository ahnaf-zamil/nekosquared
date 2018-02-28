#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Bot engine code. This is for general internal bits and bobs pertaining to how
the bot runs. Cogs and extensions may use some of these utilities, but they are
primarily for the main Discord.py bot wrapper.
"""
from .client import *
from .commands import *
from .shutdown import *
