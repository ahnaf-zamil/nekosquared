#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Other random stuff I like.
"""
import discord
from neko2.shared import alg
from neko2.shared import commands


class MiscCog:
    # Only work for Guilds that I am actually in.
    @commands.check(
        lambda c: alg.find(lambda m: m.id == c.bot.owner_id, c.guild.members)
    )
    @commands.command(
        brief="Gets Esp's Nintendo Switch code.", aliases=["sw", "switch"]
    )
    async def nintendoswitch(self, ctx):
        await ctx.send("SW-5006-9390-0438")

    @commands.command(
        brief="Suggest a new feature for Neko3", aliases=["suggestion", "suggestions"]
    )
    async def suggest(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        await ctx.send(f"{member.mention} https://goo.gl/forms/nscqZkCQ423A1iuZ2")


def setup(bot):
    bot.add_cog(MiscCog())
