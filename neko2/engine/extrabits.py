#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Extra bits and pieces used by the engine internally.
"""
from neko2.shared import traits


class InternalCogType(traits.CogTraits):
    """
    Marks a class as being an internal cog. This allows us to ignore
    it when unloading all cogs, otherwise we lose the ability to
    reload extensions later.
    """
    def __init__(self, bot):
        self.bot = bot
