#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Embed preview cog utility.
"""
import asyncio                             # Async bits and bobs

import discord
from discord import utils                  # OAuth2 URL generation
from neko2.shared import perms, commands  # Permission help
from neko2.shared import mentionconverter  # Mentioning
from neko2.shared import string            # String helpers
from neko2.shared import scribe            # Logging
from neko2.shared import traits            # HTTPS


class DiscordUtilCog(traits.CogTraits, scribe.Scribe):
    def __init__(self, bot):
        self.bot = bot

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

    async def on_ready(self):
        """
        Starts a coroutine background worker to periodically change the
        bot status if Discord is playing up.
        """
        self.maybe_spawn_status_worker()

    def maybe_spawn_status_worker(self):
        task = getattr(self, '_status_task', None)
        if not task or task.done() or task.cancelled():
            task = asyncio.ensure_future(self.check_status())
            setattr(self, '_status_task', task)
            setattr(self, '_discord_down', False)

    async def check_status(self):
        """
        Checks Discord's status each minute. If an issue occurs with their
        systems, we change the bot's status to reflect this, otherwise, the
        bot will just say "watching for n.help".
        """
        while self.bot.is_ready():
            try:
                conn = await self.acquire_http(self.bot)
                # We use unresolved as status does not seem to provide
                # information about outages. Source: tried it when discord
                # went down and it said "all systems operational" despite the
                # main page saying "major service outage."
                resp = await conn.get(
                    'https://status.discordapp.com/api/v2'
                    '/incidents/unresolved.json')
                assert resp.status == 200, resp.reason
                data = await resp.json()

                # https://status.discordapp.com/api#incidents-unresolved
                problems = data.get('incidents')
                if problems:
                    problem = problems.pop(0)
                    name = problem['name']
                    await self.bot.change_presence(
                        activity=discord.Activity(
                            type=discord.ActivityType.watching,
                            name=f'Discord: {name}'),
                        status=discord.Status.dnd)
                    setattr(self, '_discord_down', True)
                else:
                    # Only change presence if discord has just gone
                    # back up again. This way, we can allow other cogs
                    # to change the message if they fancy.
                    if getattr(self, '_discord_down'):
                        await self.bot.change_presence(
                            activity=discord.Activity(
                                type=discord.ActivityType.watching,
                                name=f'for {self.bot.command_prefix}help'),
                            status=discord.Status.online)
                        setattr(self, '_discord_down', False)
            except BaseException as ex:
                self.logger.warning('Background checker for Discord status: ' +
                                    type(ex).__qualname__ + ': ' + str(ex))
            finally:
                await asyncio.sleep(60)


def setup(bot):
    bot.add_cog(DiscordUtilCog(bot))
