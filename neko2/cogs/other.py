#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Other random stuff I like.
"""
from neko2.shared import alg
from neko2.shared import commands


class MiscCog:
    # Only work for Guilds that I am actually in.
    @commands.check(lambda c: alg.find(lambda m: m.id == c.bot.owner_id, 
                                       c.guild.members))
    @commands.command(brief='Gets Esp\'s Nintendo Switch code.', aliases=['sw', 'switch'])
    async def nintendoswitch(self, ctx):
        await ctx.send('SW-5006-9390-0438')


def setup(bot):
    bot.add_cog(MiscCog())
