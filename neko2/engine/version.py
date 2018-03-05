#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Builtin extension that is loaded to implement a version message.
"""
import discord

import neko2
from neko2.engine import commands


@commands.command()
async def version(ctx):
    author = neko2.__author__
    contrib = neko2.__contributors__
    license = neko2.__license__
    repo = neko2.__repository__
    version = neko2.__version__
    owner = ctx.bot.get_user(ctx.bot.owner_id)
    uptime = ctx.bot.uptime

    desc = '\n'.join([
        f'Contributed to by {", ".join(contrib)}',
        '',
        f'Licensed under {license}',
        '',
        f'Bot user owned by {owner}'
    ])

    embed = discord.Embed(
        title=f'Nekozilla² v{version}',
        description=desc,
        colour=0xc70025,
        url=repo)

    embed.set_author(name=author)

    if uptime >= 60 * 60 * 24:
        uptime /= (60.0 * 60 * 24)
        uptime = round(uptime, 1)
        uptime = f'{uptime} day{"s" if uptime != 1 else ""}'
    elif uptime >= 60 * 60:
        uptime /= (60.0 * 60)
        uptime = round(uptime, 1)
        uptime = f'{uptime} hour{"s" if uptime != 1 else ""}'
    elif uptime >= 60:
        uptime /= 60.0
        uptime = round(uptime, 1)
        uptime = f'{uptime} minute{"s" if uptime != 1 else ""}'
    else:
        uptime = int(uptime)
        uptime = f'{uptime} second{"s" if uptime != 1 else ""}'

    embed.set_footer(text=f'Uptime: {uptime}')

    embed.set_thumbnail(url=ctx.bot.user.avatar_url)

    await ctx.send(embed=embed)


def setup(bot):
    bot.add_command(version)
