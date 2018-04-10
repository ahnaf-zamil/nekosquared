#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Embed preview cog utility.
"""
import json                                # JSON
import traceback                           # Traceback utils

import discord
from discord import utils                  # OAuth2 URL generation
from neko2.engine import commands          # Commands decorators
from neko2.shared import perms             # Permission help
from neko2.shared import mentionconverter  # Mentioning
from neko2.shared import string            # String helpers



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

    @commands.group(name='inspect', brief='Inspects a given element.',
                    examples=['@User#1234', '#channel', '@Role Name'],
                    invoke_without_command=True)
    async def inspect_group(self,
                            ctx,
                            *,
                            what: mentionconverter.MentionConverter):
        """
        Inspects something by passing a mention. This will not support
        emojis, or anything that is not a valid mention. See the help page
        for all inspection sub-commands if you require parsing a specific
        entity type to be recognised, or cannot mention the entity.
        """
        raise NotImplementedError

    @inspect_group.command(name='role', brief='Inspects a given role.',
                           examples=['@Role Name'])
    async def inspect_role(self, ctx, *, role: discord.Role):
        role: discord.Role
        permissions = perms.Permissions.from_discord_type(role.permissions)

        permissions = sorted(f'`{name}`' for name in permissions.unmask())

        embed = discord.Embed(title=role.name,
                              description=', '.join(permissions),
                              colour=role.colour)

        embed.add_field(name='Can mention?',
                        value=string.yn(role.mentionable))
        embed.add_field(name='Will hoist?',
                        value=string.yn(role.mentionable))
        embed.add_field(name='Externally managed?',
                        value=string.yn(role.managed))
        embed.add_field(name='Created on',
                        value=role.created_at.strftime('%c'))
        embed.add_field(name='Colour', value=f'`{hex(role.colour.value)}`')
        embed.add_field(name='Members with this role',
                        value=string.plur_simple(len(role.members), 'member'))

        if role.position:
            embed.add_field(name='Height',
                            value=f'{string.plur_simple(role.position, "role")}'
                                  ' from the bottom.')
        else:
            embed.add_field(name='Height', value='Bottom-most role.')

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(DiscordUtilCog())
