#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Builtin extension that is loaded to implement a custom help method.
"""
from neko2.engine import commands       # Command decorators


@commands.command()
async def help(ctx, *, query: str=None):
    raise NotImplementedError


def setup(bot):
    # Remove any existing help command first.
    bot.remove_command('help')
    bot.add_command(help)
