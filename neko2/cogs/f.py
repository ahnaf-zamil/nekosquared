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


@dataclasses.dataclass()
class F:
    members: collections.MutableOrderedSet
    message: discord.Message
    colour: int


class RespectsCog:
    def __init__(self, bot):
        self.bot = bot

        self.buckets: typing.Dict[
            typing.Tuple[discord.Guild, discord.TextChannel], F
        ] = {}

        self.bucket_lock = asyncio.Lock()

    # noinspection PyUnusedLocal
    @commands.cooldown(1, 600, commands.BucketType.user)
    @commands.command(brief='Pay your respects.')
    async def f(self, ctx):
        prefix = ctx.prefix + ctx.invoked_with

        with await self.bucket_lock:
            try:
                guild_channel = (ctx.guild, ctx.channel)
                if guild_channel not in self.buckets:

                    colour = other.rand_colour()

                    message = await ctx.send(
                        embed=discord.Embed(
                            description=f'{ctx.author} paid their respects.',
                            colour=colour))

                    f_bucket = F(collections.MutableOrderedSet({ctx.author}),
                                 message,
                                 colour)

                    self.buckets[guild_channel] = f_bucket

                    async def destroy_bucket_later(_guild_channel):
                        await asyncio.sleep(F_TIMEOUT)
                        with await self.bucket_lock:
                            del self.buckets[_guild_channel]

                    self.bot.loop.create_task(
                        destroy_bucket_later(guild_channel))

                else:
                    await ctx.message.delete()
                    bucket = self.buckets[guild_channel]
                    bucket.members.add(ctx.author)

                    members = bucket.members[:15]

                    first = members[:-1]
                    last = members[-1]

                    first = list(map(str, first))
                    last = str(last) if last else ''

                    message = (
                        ', '.join(first) + f' and {last} ' +
                        'paid their respects')

                    embed = discord.Embed(
                        description=message,
                        colour=bucket.colour)

                    await bucket.message.edit(embed=embed)
            except BaseException:
                pass


def setup(bot):
    bot.add_cog(RespectsCog(bot))
