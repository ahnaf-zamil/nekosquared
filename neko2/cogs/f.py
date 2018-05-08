#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Press F to pay respects.
"""
import asyncio
import traceback
import typing

import dataclasses
import discord

from neko2.shared import commands, alg, morefunctools, collections

# Last for 1 hours otherwise.
F_TIMEOUT = 60**2

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
            c4 = reaction.emoji == '\N{REGIONAL INDICATOR SYMBOL LETTER F}'

            if all((c1, c2, c3, c4)):
                await self.append_to_bucket(b, user)
                message: discord.Message = reaction.message
                await message.remove_reaction(reaction, user)

    @morefunctools.always_background()
    async def destroy_bucket_later(self, channel):
        await asyncio.sleep(F_TIMEOUT)
        await self.buckets[channel].message.clear_reactions()
        del self.buckets[channel]

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

        if bucket.message:
            await bucket.message.edit(embed=embed)
        else:
            bucket.message = await bucket.ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command(brief='Pay your respects.')
    async def f(self, ctx, *, reason=None):
        try:
            await ctx.message.delete()
            bucket = self.buckets.get(ctx.channel)

            # Get the last 10 recent messages. If the bucket message
            # is in there, then update, else, delete the old message if
            # possible and then resend the new one. If the bucket is too
            # old, start anew.
            if bucket:
                msg = bucket.message.id
                most_recent = await ctx.channel.history(limit=10).flatten()
                new_msg = alg.find(lambda m: m.id == msg, most_recent)

                if new_msg:
                    bucket.message = new_msg
                else:
                    try:
                        await bucket.message.delete()
                        bucket.message = None
                    except:
                        del self.buckets[ctx.channel]
                        bucket = None
                    else:
                        return await self.append_to_bucket(bucket, ctx.author)

            if not bucket:
                colour = alg.rand_colour()

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
                self.destroy_bucket_later(self, ctx.channel)
            else:
                await self.append_to_bucket(bucket, ctx.author)
        except BaseException:
            traceback.print_exc()


def setup(bot):
    bot.add_cog(RespectsCog(bot))
