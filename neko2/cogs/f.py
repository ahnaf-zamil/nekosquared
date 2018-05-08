#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Press F to pay respects.
"""
import asyncio
import typing

import dataclasses
import discord

from neko2.shared import commands, alg, morefunctools, collections

# Timeout to reset after regardless
F_TIMEOUT = 6 * 60 * 60

# Set to True to enable `f' being a valid trigger for the command without
# a prefix.
ENABLE_NAKED = False

# Set to True to enable responding to reactions to the original trigger
# response
ENABLE_REACT = True


@dataclasses.dataclass()
class F:
    initial_ctx: commands.Context
    members: collections.MutableOrderedSet
    message: discord.Message
    colour: int
    reason: typing.Optional[str] = None


ReasonChannel = typing.Tuple[discord.TextChannel, str]


class RespectsCog:
    def __init__(self, bot):
        self.bot = bot
        self.buckets: typing.Dict[ReasonChannel, F] = {}

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
            try:
                b = alg.find(lambda k: k[0] == channel, list(self.buckets.keys()))
            except:
                # Debuggling.
                import traceback
                traceback.print_exc()
                return

            if b:
                b = self.buckets[b]

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

        if bucket.message:
            await bucket.message.edit(embed=embed)
        else:
            bucket.message = await bucket.initial_ctx.send(embed=embed)

        if ENABLE_REACT:
            await bucket.message.add_reaction(
                '\N{REGIONAL INDICATOR SYMBOL LETTER F}')

    @morefunctools.always_background()
    async def destroy_bucket_later(self, channel):
        await asyncio.sleep(F_TIMEOUT)
        if ENABLE_REACT:
            await self.buckets[channel].message.clear_reactions()
        del self.buckets[channel]

    @commands.guild_only()
    @commands.command(brief='Pay your respects.')
    async def f(self, ctx, *, reason=''):
        try:
            await ctx.message.delete()

            reason_low = reason.strip().lower()

            bucket = self.buckets.get((ctx.channel, reason_low))

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

            if not bucket or reason_low != bucket.reason.strip().lower():

                colour = alg.rand_colour()

                if not reason:
                    message = await ctx.send(
                        embed=discord.Embed(
                            description=f'{ctx.author} paid their respects.',
                            colour=colour))
                else:
                    message = await ctx.send(
                        embed=discord.Embed(
                            description=f'{ctx.author} paid their respects for'
                                        f' {reason}'))

                self.destroy_bucket_later(self, ctx.channel)

                f_bucket = F(ctx,
                             collections.MutableOrderedSet({ctx.author}),
                             message,
                             colour,
                             reason)

                self.buckets[(ctx.channel, reason_low)] = f_bucket

                if ENABLE_REACT:
                    await message.add_reaction(
                        '\N{REGIONAL INDICATOR SYMBOL LETTER F}')
            else:
                await self.append_to_bucket(bucket, ctx.author)

                if ENABLE_REACT:
                    await bucket.message.add_reaction(
                        '\N{REGIONAL INDICATOR SYMBOL LETTER F}')
        except BaseException as ex:
            raise


def setup(bot):
    bot.add_cog(RespectsCog(bot))
