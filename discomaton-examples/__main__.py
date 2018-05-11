#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
An example bot that demonstrates how to use specific utilities.

===

MIT License

Copyright (c) 2018 Neko404NotFound

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
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
