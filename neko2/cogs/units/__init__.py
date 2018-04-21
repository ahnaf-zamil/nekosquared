#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Unit conversion system v2.
"""
from . import cog


def setup(bot):
    bot.add_cog(cog.UnitCog(bot))
