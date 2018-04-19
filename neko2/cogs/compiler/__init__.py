#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Various code-related compilation tools.
"""
from neko2.cogs.compiler.cmds import CompilerCog


def setup(bot):
    bot.add_cog(CompilerCog())

