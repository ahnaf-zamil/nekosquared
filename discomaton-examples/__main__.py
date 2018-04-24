#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
An example bot that demonstrates how to use specific utilities.
"""
import logging
import sys
import traceback

import discord
from discord.ext import commands


logging.basicConfig(level='INFO')

try:
    token = sys.argv[1]
    client_id = sys.argv[2]
except IndexError:
    raise RuntimeError('Please give your token as the first argument, and the '
                       'client ID as the second.') from None

bot = commands.Bot(command_prefix=';;')


@bot.listen()
async def on_command_error(ctx: commands.Context, error: BaseException):
    # Removes the outer discord.py wrapper error.
    if getattr(error, '__cause__', None) is not None:
        outer_error, error = error, error.__cause__
    else:
        outer_error = error

    traceback.print_exception(
        type(outer_error),
        outer_error,
        outer_error.__traceback__)

    # noinspection PyBroadException
    try:
        await ctx.send(f'**Error occurred:**\n`{type(error).__qualname__}`:'
                       f' {error}')
    except BaseException:
        pass

bot.load_extension('examples')
logging.info(discord.utils.oauth_url(client_id))
bot.run(token)
