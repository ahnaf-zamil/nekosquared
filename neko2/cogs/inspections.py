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
import urllib.parse

import discord

# Random colours; Permission help; Logging; String helpers; HTTPS
from discomaton.factories import bookbinding
from neko2.shared import collections, scribe, string, traits
from neko2.shared.perms import Permissions
from neko2.shared.converters import *  # Mentioning


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
            await self.inspect_member.callback(self, ctx, member=obj)
        elif isinstance(obj, discord.Role):
            await self.inspect_role.callback(self, ctx, role=obj)
        elif isinstance(obj, discord.Emoji):
            await self.inspect_emoji.callback(self, ctx, emoji=obj)
        elif isinstance(obj, discord.PartialEmoji):
            await ctx.send(f'You should use `{ctx.prefix}char` for Unicode '
                           'emojis.')
        else:
            raise NotImplementedError

    @inspect_group.command(name='allperms',
                           brief='Shows a list of all permission names usable '
                                 'with this bot.')
    async def inspect_allperms(self, ctx):
        await ctx.send('**Permissions that this bot understands:**\n\n' +
                       ', '.join(f'`{p}`'
                                 for p in sorted(Permissions.__members__)))

    # noinspection PyUnresolvedReferences
    @inspect_group.command(name='avatar', brief='Shows the user\'s avatar.',
                           examples=['@user'], aliases=['a', 'av'])
    async def inspect_avatar(self, ctx, *, user: discord.Member = None):
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
    async def inspect_emoji(self, ctx, *, emoji: discord.Emoji=None):
        """
        Note that this will only work for custom emojis.
        If no emoji name is provided, we list all emojis available in this
        guild.
        """
        if emoji:

            desc = f'Created on {emoji.created_at.strftime("%c")}\n\n'

            if emoji.animated:
                desc += 'Animated emoji\n'
            if emoji.require_colons:
                desc += 'Must be wrapped in colons\n'
            if emoji.managed:
                desc += 'Managed as part of a Twitch integration\n'
            if not emoji.roles:
                desc += 'Emoji is usable by everyone here\n'

            rc = emoji.require_colons

            embed = discord.Embed(
                title=rc and f'`:{emoji.name}:`' or f'`{emoji}`',
                description=desc,
                url=emoji.url,
                colour=0xab19cf or emoji.animated and 0xd1851b)

            if emoji.roles:
                embed.add_field(
                    name='Usable by',
                    value=string.trunc(', '.join(map(str, emoji.roles)), 1024))

            embed.set_thumbnail(url=emoji.url)

            embed.set_author(name=f'Emoji in "{emoji.guild}"',
                             icon_url=emoji.url)
            embed.set_footer(text=str(emoji.id),
                             icon_url=emoji.url)
            await ctx.send(embed=embed)
        elif len(ctx.guild.emojis) == 0:
            await ctx.send('This server has no emojis yet...',
                           delete_after=10)
        else:
            binder = bookbinding.StringBookBinder(ctx, max_lines=None)

            def key(e):
                return e.name

            for i, e in enumerate(sorted(ctx.guild.emojis, key=key)):
                binder.add_line(f'`{i + 1:03}`\t{e} \t `{e}`')

            binder.start()

    @inspect_group.command(name='channel', brief='Inspects a given channel.',
                           aliases=['ch', 'c'])
    async def inspect_channel(self, ctx, *,
                              channel: GuildChannelConverter = None):
        """
        Inspects a channel in this guild. If no channel is given, we check
        the current channel.
        """
        channel = channel or ctx.channel

        category = channel.category
        category = category and category.name.upper() or None

        if isinstance(channel, discord.TextChannel):
            try:
                wh_count = len(await channel.webhooks())
            except discord.Forbidden:
                wh_count = 'I need `MANAGE_WEBHOOKS` first!'

            pin_count = len(await channel.pins())

            try:
                invite_count = len(await channel.invites())
            except discord.Forbidden:
                invite_count = 'I need `MANAGE_CHANNELS` first!'

            embed = discord.Embed(
                title=f'`#{channel.name}`',
                colour=alg.rand_colour(),
                description='\n'.join([
                    f'Type: Text channel',
                    f'Created on: {channel.created_at.strftime("%c")}',
                    f'Category: `{category}`',
                    f'NSFW: {string.yn(channel.is_nsfw()).lower()}',
                    f'Pin count: {pin_count}',
                    f'Webhook count: {wh_count}',
                    f'Invitations here: {invite_count}'
                ]))

            if channel.topic:
                embed.add_field(name='Topic',
                                value=string.trunc(channel.topic, 1024),
                                inline=False)

            if len(channel.members) == len(ctx.guild.members):
                embed.add_field(name='Accessible by',
                                value='All ' +
                                      string.plur_simple(len(channel.members),
                                                         'member'))
            elif len(channel.members) > 10:
                embed.add_field(name='Accessible by',
                                value=f'{len(channel.members)} members')
            elif channel.members:
                embed.add_field(name='Accessible by',
                                value=', '.join(
                                    sorted(map(str, channel.members))))
            else:
                embed.add_field(name='Accessible by',
                                value='No one has this role yet!')

            if channel.changed_roles:
                embed.add_field(
                    name='Roles with custom permissions',
                    value=', '.join(str(c) for c in
                                    sorted(channel.changed_roles, key=str)))

        else:
            channel: discord.VoiceChannel = channel

            embed = discord.Embed(
                title=f'`#{channel.name}`',
                colour=alg.rand_colour(),
                description='\n'.join([
                    f'Type: Text channel',
                    f'Created on: {channel.created_at.strftime("%c")}',
                    f'Category: `{category}`',
                    f'Bitrate: {channel.bitrate / 1000:,.2f}kbps',
                    f'User limit: {channel.user_limit or None}'
                ]))

            if len(channel.members) == len(ctx.guild.members):
                embed.add_field(name='Members in this VC',
                                value='All ' +
                                      string.plur_simple(len(channel.members),
                                                         'member'))
            elif len(channel.members) > 10:
                embed.add_field(name='Members in this VC',
                                value=f'{len(channel.members)} members')
            elif channel.members:
                embed.add_field(name='Members in this VC',
                                value=', '.join(
                                    sorted(map(str, channel.members))))
            else:
                embed.add_field(name='Members in this VC',
                                value='No one is in this VC yet!')

        embed.set_author(name=f'Channel #{channel.position + 1}')
        embed.set_footer(text=str(channel.id))
        await ctx.send('Channel inspection', embed=embed)

    @inspect_group.command(name='category', brief='Inspects a given category.',
                           aliases=['ca', 'cat'])
    async def inspect_category(self, ctx, *,
                               category: LowercaseCategoryConverter=None):
        """
        If no category is provided, and we are in a valid category, we will
        inspect that, otherwise, you need to provide me with a valid category
        snowflake or name.
        """
        if category is None:
            if ctx.channel.category is None:
                raise commands.MissingRequiredArgument('category')
            else:
                category = ctx.channel.category

        embed = discord.Embed(
            title=f'`{category.name.upper()}`',
            colour=alg.rand_colour(),
            description='\n'.join([
                f'Created on: {category.created_at.strftime("%c")}',
                f'NSFW: {string.yn(category.is_nsfw()).lower()}',
            ]))

        if category.changed_roles:
            embed.add_field(
                name='Roles with custom permissions',
                value=', '.join(str(c) for c in
                                sorted(category.changed_roles, key=str)))

        channels = sorted(map(lambda c: c.name, category.channels))

        if channels:
            c_string = ''
            for channel in channels:
                if c_string:
                    next_substring = f', `{channel}`'
                else:
                    next_substring = f'`{channel}`'

                if len(c_string + next_substring) < 1020:
                    c_string += next_substring
                else:
                    c_string += '...'

            embed.add_field(name='Channels',
                            value=c_string)
        else:
            embed.add_field(name='Channels',
                            value='No channels yet!')

        embed.set_author(name=f'Category #{category.position + 1}')
        embed.set_footer(text=str(category.id))
        await ctx.send('Category inspection', embed=embed)

    @inspect_group.command(name='member', brief='Inspects a given member.',
                           aliases=['user', 'u', 'm'])
    async def inspect_member(self, ctx, *, member: discord.Member=None):
        """
        If no member is specified, then I will show your profile instead.
        """
        if member is None:
            member = ctx.author

        embed = discord.Embed(title=f'`@{member}`', colour=member.colour)

        desc = '\n'.join((
            f'Display name: `{member.display_name}`',
            f'Joined here on: {member.joined_at.strftime("%c")}',
            f'Joined Discord on: {member.created_at.strftime("%c")}',
            f'Top role: {member.top_role}',
            f'Colour: `#{hex(member.colour.value)[2:].zfill(6)}`',
            'Status: ' + {
                discord.Status.online: 'Online',
                discord.Status.idle: 'Away',
                discord.Status.dnd: 'Busy',
                discord.Status.invisible: 'Hiding',
                discord.Status.offline: 'Offline',
            }.get(member.status, 'On Mars'),
            f'Account type: {member.bot and "Bot" or "Human"}'
        ))
        embed.description = desc
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=str(member.id),
                         icon_url=member.default_avatar_url)

        if member.roles:
            embed.add_field(
                name='Roles',
                value=string.trunc(
                    ', '.join(map(str, reversed(member.roles))), 1024))

        role_perms = Permissions.from_discord_type(member.guild_permissions)
        role_perms = {*role_perms.unmask()}

        chn_perms = member.permissions_in(ctx.channel)
        chn_perms = {*Permissions.from_discord_type(chn_perms).unmask()}

        # Calculate any extra perms granted for this channel only.
        chn_perms.difference_update(role_perms)

        if role_perms:
            role_perms = ', '.join(f'`{p}`' for p in role_perms)
        else:
            role_perms = 'No role permissions granted (somehow)'

        embed.add_field(name='Role-granted permissions',
                        value=role_perms)

        if member.activity:
            # This design is...not the best imho, but it is confusingly
            # defined in the API:
            # This attr can be a Game, Streaming or Activity, but Activity
            # itself can have a `playing` type which denotes a game, so...
            # how do we know which one to expect? Game is not a subtype
            # of activity nor vice versa!
            if isinstance(member.activity, discord.Activity):
                a = member.activity

                attrs = []
                # Less verbose.
                z = attrs.append

                if a.start:
                    z(f'Since: {a.start.strftime("%c")}')
                if a.end:
                    z(f'Until: {a.end.strftime("%c")}')

                if a.details:
                    z(f'Details: {a.details}')

                if a.small_image_text:
                    z(f'Small tooltip: {a.small_image_text}')
                if a.large_image_text:
                    z(f'Large tooltip: {a.large_image_text}')

                if not attrs:
                    z(a.name)
                else:
                    attrs.insert(0, f'Name: {a.name}')

                t = a.type
                t = 'Activity' \
                    if t == discord.ActivityType.unknown \
                    else t.name.title()

                embed.add_field(
                    name=t,
                    value='\n'.join(attrs))
            elif isinstance(member.activity, discord.Game):
                embed.add_field(
                    name='Playing',
                    value=member.activity.name)

            elif isinstance(member.activity, discord.Streaming):
                a = member.activity
                embed.add_field(
                    name='Streaming',
                    value=f'[{a.twitch_name or a.name}]({a.url})\n'
                          f'{a.details or ""}')

        if chn_perms:
            chn_perms = ', '.join(f'`{p}`' for p in chn_perms)
            embed.add_field(name='Additional permissions in this channel',
                            value=chn_perms)

        await ctx.send('Member inspection', embed=embed)

    @inspect_group.command(name='role', brief='Inspects a given role.',
                           examples=['@Role Name'], aliases=['r'])
    async def inspect_role(self, ctx, *, role: discord.Role):
        permissions = Permissions.from_discord_type(role.permissions)

        permissions = sorted(f'`{name}`' for name in permissions.unmask())

        embed = discord.Embed(title=role.name,
                              description=', '.join(permissions),
                              colour=role.colour)

        embed.add_field(name='Can be mentioned?',
                        value=string.yn(role.mentionable))
        embed.add_field(name='Will hoist?',
                        value=string.yn(role.hoist))
        embed.add_field(name='Externally managed?',
                        value=string.yn(role.managed))
        embed.add_field(name='Created on',
                        value=role.created_at.strftime('%c'))
        embed.add_field(name='Colour',
                        value=f'`#{hex(role.colour.value)[2:].zfill(6)}`')

        if len(role.members) == len(ctx.guild.members):
            embed.add_field(name='Members with this role',
                            value='All ' +
                                  string.plur_simple(len(role.members),
                                                     'member'))
        elif len(role.members) > 10:
            embed.add_field(name='Members with this role',
                            value=f'{len(role.members)} members')
        elif role.members:
            embed.add_field(name='Members with this role',
                            value=', '.join(sorted(map(str, role.members))))
        else:
            embed.add_field(name='Members with this role',
                            value='No one has this role yet!')

        embed.add_field(
            name='Location in the hierarchy',
            value=f'{string.plur_simple(role.position, "role")} from the '
                  f'bottom; {len(ctx.guild.roles) - role.position} from '
                  'the top.')

        await ctx.send('Role inspection', embed=embed)

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
        # epoch = 1_420_070_400_000
        epoch = discord.utils.DISCORD_EPOCH
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


def setup(bot):
    bot.add_cog(GuildStuffCog(bot))
