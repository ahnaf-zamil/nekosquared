#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Various useful operations to use in guilds.

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
from datetime import datetime  # Timestamp stuff
from typing import Union
import urllib.parse

import discord

# Random colours; Permission help; Logging; String helpers; HTTPS
from neko2.shared import alg, collections, perms, scribe, string, traits
from neko2.shared.mentionconverter import *  # Mentioning


class GuildStuffCog(traits.CogTraits, scribe.Scribe):
    def __init__(self, bot):
        self.bot = bot

    # noinspection PyMethodMayBeStatic
    async def __local_check(self, ctx):
        """Only allows these to be called in Guilds."""
        return ctx.guild

    @commands.group(name='inspect', brief='Inspects a given element.',
                    examples=['@User#1234', '#channel', '@Role Name'],
                    invoke_without_command=True,
                    aliases=['in'])
    async def inspect_group(self, ctx, *,
                            obj: MentionOrSnowflakeConverter):
        """
        Inspects something by passing a mention. This will not support
        emojis, or anything that is not a valid mention. See the help page
        for all inspection sub-commands if you require parsing a specific
        entity type to be recognised, or cannot mention the entity.
        """
        if isinstance(obj, int):
            await self.inspect_snowflake.callback(self, ctx, obj)
        elif isinstance(obj, discord.Member):
            await self.inspect_member(self, ctx, member=obj)
        elif isinstance(obj, discord.Role):
            await self.inspect_role.callback(self, ctx, role=obj)
        elif isinstance(obj, discord.Emoji):
            await self.inspect_emoji.callback(self, ctx, emoji=obj)
        elif isinstance(obj, discord.PartialEmoji):
            await ctx.send(f'You should use `{ctx.prefix}char` for Unicode '
                           'emojis.')
        else:
            raise NotImplementedError

    # noinspection PyUnresolvedReferences
    @inspect_group.command(name='avatar', brief='Shows the user\'s avatar.',
                           examples=['@user'], aliases=['a', 'av'])
    async def inspect_avatar(self, ctx, *, user: discord.Member=None):
        """
        If no avatar is specified, then the guild avatar is captured
        instead!
        """
        if user:
            avatar_url = user.avatar_url
            url_obj = urllib.parse.urlparse(avatar_url)
            avatar_url = f'{url_obj[0]}://{url_obj[1]}{url_obj[2]}?size=2048'
            embed = discord.Embed(
                title=f'`@{user}`\'s avatar',
                colour=getattr(user, 'colour', 0))
            embed.set_image(url=avatar_url)
            await ctx.send('Member avatar inspection', embed=embed)
        else:
            embed = discord.Embed(
                colour=alg.rand_colour())
            embed.set_image(url=ctx.guild.icon_url)
            await ctx.send('Guild avatar inspection', embed=embed)

    @inspect_group.command(name='emoji', brief='Inspects an emoji.',
                           aliases=['e'])
    async def inspect_emoji(self, ctx, *, emoji: discord.Emoji):
        """Note that this will only work for custom emojis."""
        desc = f'Created on {emoji.created_at.strftime("%c")}\n\n'

        if emoji.animated:
            desc += 'Animated emoji\n'
        if emoji.require_colons:
            desc += 'Must be wrapped in colons\n'
        if emoji.managed:
            desc += 'Managed as part of a Twitch integration\n'
        if not emoji.roles:
            desc += 'Emoji is usable by everyone here\n'

        embed = discord.Embed(
            title=emoji.require_colons and f'`:{emoji.name}:`' or f'`{emoji}`',
            description=desc,
            url=emoji.url,
            colour=0xab19cf or emoji.animated and 0xd1851b)

        if emoji.roles:
            embed.add_field(
                name='Usable by',
                value=string.trunc(', '.join(map(str, emoji.roles)), 1024))

        embed.set_thumbnail(url=emoji.url)

        embed.set_author(name=f'Emoji in "{emoji.guild}"', icon_url=emoji.url)
        embed.set_footer(text=str(emoji.id), icon_url=emoji.url)

        await ctx.send(embed=embed)

    @inspect_group.command(name='member', brief='Inspects a given member.',
                           aliases=['user', 'u', 'm'])
    async def inspect_member(self, ctx, *, member: discord.Member):
        member: Union[discord.Member, discord.User]

        embed = discord.Embed(title=f'`@{member}`', colour=member.colour)

        desc = '\n'.join((
            f'Display name: `{member.display_name}`',
            f'Joined on: {member.joined_at.strftime("%c")}',
            f'Top role: {member.top_role}',
            f'Colour: `#{hex(member.colour.value)[2:]}`',
        ))
        embed.description = desc

        embed.set_thumbnail(url=member.avatar_url)

        embed.set_footer(text=str(member.id),
                         icon_url=member.default_avatar_url)

        embed.add_field(
            name='Account type',
            value=('Bot' if member.bot else 'User') + ' account')

        if member.roles:
            embed.add_field(
                name='Roles',
                value=string.trunc(
                    ', '.join(map(str, reversed(member.roles))), 1024))

        await ctx.send('Member inspection', embed=embed)

    @inspect_group.command(name='snowflake', brief='Deciphers a snowflake.',
                           examples=['439802699144232960'],
                           aliases=['s', 'sf'])
    async def inspect_snowflake(self, ctx, *snowflakes: int):
        """You can pass up to 10 snowflakes at once."""
        if not len(snowflakes):
            return

        # Filters out duplicates.
        snowflakes = collections.OrderedSet(snowflakes)

        embed = discord.Embed(colour=alg.rand_colour())

        # Discord epoch from the Unix epoch in ms
        # Essentially the number of milliseconds since epoch
        # at 1st January 2015
        epoch = 1_420_070_400_000
        for s in snowflakes[:10]:

            timestamp = ((s >> 22) + epoch) / 1000
            creation_time = datetime.utcfromtimestamp(timestamp)

            worker_id = (s & 0x3E0000) >> 17
            process_id = (s & 0x1F000) >> 12
            increment = s & 0xFFF

            string = '\n'.join((
                f'`{creation_time} UTC`',
                f'Worker ID: `{worker_id}`',
                f'Process ID: `{process_id}`',
                f'Increment: `{increment}`'))

            # Attempt to resolve the snowflake in all caches where possible
            # and non-intrusive to do so.

            if s == getattr(ctx.bot, 'client_id', None):
                string += '\n- My client ID'

            if s == ctx.bot.user.id:
                string += '\n- My user ID'
            elif s == ctx.bot.owner_id:
                string += '\n- My owner\'s ID'
            elif alg.find(lambda u: u.id == s, ctx.guild.members):
                string += '\n- A member in this guild'
            elif alg.find(lambda u: u.id == s, ctx.bot.users):
                string += '\n- A user'

            if alg.find(lambda e: e.id == s, ctx.guild.emojis):
                string += '\n- Emoji in this guild'
            elif alg.find(lambda e: e.id == s, ctx.bot.emojis):
                string += '\n- Emoji in another guild'

            if alg.find(lambda c: c.id == s, ctx.guild.categories):
                string += '\n- Category in this guild'

            if alg.find(lambda r: r.id == s, ctx.guild.roles):
                string += '\n- Role in this guild'

            if s == ctx.channel.id:
                string += '\n- ID for this channel'
            elif alg.find(lambda c: c.id == s, ctx.guild.text_channels):
                string += '\n- Text channel in this guild'
            elif alg.find(lambda c: c.id == s, ctx.guild.voice_channels):
                string += '\n- Voice channel in this guild'
            elif alg.find(lambda c: c.id == s, ctx.bot.get_all_channels()):
                string += '\n- Text or voice channel in another guild'

            if s == ctx.guild.id:
                string += '\n- ID for this guild'
            elif alg.find(lambda g: g.id == s, ctx.bot.guilds):
                string += '\n- ID for another guild I am in'

            embed.add_field(name=str(s), value=string)

        await ctx.send('Snowflake inspection', embed=embed)

    @inspect_group.command(name='role', brief='Inspects a given role.',
                           examples=['@Role Name'], aliases=['r'])
    async def inspect_role(self, ctx, *, role: discord.Role):
        permissions = perms.Permissions.from_discord_type(role.permissions)

        permissions = sorted(f'`{name}`' for name in permissions.unmask())

        embed = discord.Embed(title=role.name,
                              description=', '.join(permissions),
                              colour=role.colour)

        embed.add_field(name='Can mention?',
                        value=string.yn(role.mentionable))
        embed.add_field(name='Will hoist?',
                        value=string.yn(role.hoist))
        embed.add_field(name='Externally managed?',
                        value=string.yn(role.managed))
        embed.add_field(name='Created on',
                        value=role.created_at.strftime('%c'))
        embed.add_field(name='Colour',
                        value=f'`#{hex(role.colour.value)[2:]}`')
        embed.add_field(name='Members with this role',
                        value=string.plur_simple(len(role.members), 'member'))

        if role.position:
            embed.add_field(
                name='Height',
                value=f'{string.plur_simple(role.position, "role")}'
                      ' from the bottom.')
        else:
            embed.add_field(name='Height', value='Bottom-most role.')

        await ctx.send('Role inspection', embed=embed)


def setup(bot):
    bot.add_cog(GuildStuffCog(bot))
