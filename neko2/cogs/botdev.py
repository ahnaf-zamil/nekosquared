#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Bits and bobs helpful when making Discord bots I guess.

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

from discord import utils

from neko2.shared import commands, perms


class BotUtils:
    @commands.group(name='botdev', brief='A collection of useful tools for '
                                         'bot developers.',
                    invoke_without_command=True)
    async def botdev_group(self, ctx, *, child):
        ctx.message.content = f'{ctx.bot.command_prefix}help botdev'
        ctx = await ctx.bot.get_context(ctx.message)
        await ctx.bot.invoke(ctx)

    @botdev_group.command(
        name='invite',
        brief='Generates an OAuth invite URL from a given snowflake client ID',
        help='Valid options: ```' +
             ', '.join(perms.Permissions.__members__.keys()) +
             '```')
    async def generate_invite(self, ctx, client_id: str, *permissions: str):
        perm_bits = 0

        for permission in permissions:
            if permission.upper() not in perms.Permissions.__members__.keys():
                return await ctx.send(f'{permission} is not recognised.')
            else:
                perm_bits |= perms.Permissions[permission.upper()]

        await ctx.send(
            utils.oauth_url(
                client_id,
                permissions=perm_bits if hasattr(perm_bits, 'value') else None,
                guild=ctx.guild
            ))


def setup(bot):
    bot.add_cog(BotUtils())
