#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Embed preview cog utility.
"""
import json                           # JSON
import traceback                      # Traceback utils
from discord import embeds            # Embeds
from discord import utils             # OAuth2 URL generation
from neko2.engine import commands     # Commands decorators
from neko2.shared import perms


class DiscordUtilCog:
    @commands.command(
        name='geninvite',
        brief='Generates an OAuth invite URL from a given snowflake client ID',
        help='Valid options: ```' +
             ', '.join(perms.Permissions.__members__.keys()) +
             '```')
    async def generate_invite(self, ctx, client_id: str, *permissions: str):
        perm_bits = 0

        for permission in permissions:
            if permission not in perms.Permissions:
                return await ctx.send(f'{permission} is not recognised.')
            else:
                perm_bits |= perms.Permissions[permission]

        await ctx.send(
            utils.oauth_url(
                client_id,
                permissions=perms.Permissions.to_discord_type(perm_bits),
                guild=ctx.guild
            ))


def setup(bot):
    bot.add_cog(DiscordUtilCog())
