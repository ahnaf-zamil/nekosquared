#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Shows the bot ping.
"""
from neko2.engine import commands


@commands.command()
async def ping(ctx):
    """
    Checks whether the bot is online and responsive or not.
    """
    await ctx.send(f'Pong! ({ctx.bot.latency * 1000:.2f}ms)')


def setup(bot):
    bot.add_command(ping)
