#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Press F to pay respects.
"""
import asyncio
import typing

import dataclasses
import discord
from neko2.shared import commands, other, collections

# We remember responses for 1 hour before allowing them to time out.
F_TIMEOUT = 60 ** 2


# Set to True to enable `f' being a valid trigger for the command without
# a prefix.
ENABLE_NAKED = False

# Set to True to enable responding to reactions to the original trigger
# response
ENABLE_REACT = True


@dataclasses.dataclass()
class F:
    members: collections.MutableOrderedSet
    message: discord.Message
    colour: int


class RespectsCog:
    def __init__(self, bot):
        self.bot = bot
        self.buckets: typing.Dict[discord.TextChannel, F] = {}

    if ENABLE_NAKED:
        async def on_message(self, message):
            if message.content.lower() == 'f' and message.guild:
                message.content = self.bot.command_prefix + 'f'
                ctx = await self.bot.get_context(message)
                try:
                    await self.f.invoke(ctx)
                finally:
                    return

    if ENABLE_REACT:
        async def on_reaction_add(self,
                                  reaction: discord.Reaction,
                                  user: discord.Member):
            if user == self.bot.user:
                return

            channel = reaction.message.channel
            b = self.buckets.get(channel)
            
            if b is None:
                return

            c1 = b.message.id == reaction.message.id
            c2 = reaction.message.guild is not None
            c3 = user not in b.members

            if c1 and c2 and c3:
                await self.append_to_bucket(b, user)
                message: discord.Message = reaction.message
                await message.remove_reaction(reaction, user)

    @staticmethod
    async def append_to_bucket(bucket, user):
        bucket.members.add(user)

        members = bucket.members[:15]

        first = members[:-1]
        last = members[-1]

        first = list(map(str, first))
        last = str(last) if last else ''

        if len(members) > 1:
            message = (
                    ', '.join(first) + f' and {last} ' +
                    'paid their respects')
        else:
            message = (
                f'{last} paid their respects.')

        embed = discord.Embed(
            description=message,
            colour=bucket.colour)

        await bucket.message.edit(embed=embed)

    @other.always_background()
    async def destroy_bucket_later(self, channel):
        await asyncio.sleep(F_TIMEOUT)
        if ENABLE_REACT:
            await self.buckets[channel].message.clear_reactions()

        del self.buckets[channel]

    @commands.guild_only()
    @commands.command(brief='Pay your respects.')
    async def f(self, ctx, *, reason=None):
        try:
            await ctx.message.delete()

            if ctx.channel not in self.buckets:

                colour = other.rand_colour()

                if reason is None:
                    message = await ctx.send(
                        embed=discord.Embed(
                            description=f'{ctx.author} paid their respects.',
                            colour=colour))
                else:
                    message = await ctx.send(
                        embed=discord.Embed(
                            description=f'{ctx.author} paid their respects for'
                                        f' {reason}'))

                if ENABLE_REACT:
                    await message.add_reaction(
                        '\N{REGIONAL INDICATOR SYMBOL LETTER F}')

                f_bucket = F(collections.MutableOrderedSet({ctx.author}),
                             message,
                             colour)

                self.buckets[ctx.channel] = f_bucket

                await self.destroy_bucket_later(ctx.channel)
            else:
                bucket = self.buckets[ctx.channel]
                await self.append_to_bucket(bucket, ctx.author)
        except BaseException:
            pass


def setup(bot):
    bot.add_cog(RespectsCog(bot))
