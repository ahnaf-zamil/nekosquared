#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

from neko2.shared import commands


class ChattyCog:
    @commands.command(brief='Take a wild guess.')
    async def say(self, ctx, *, message):
        try:
            await ctx.message.delete()
            await ctx.send(message)
        finally:
            return
            

def setup(bot):
    bot.add_cog(ChattyCog())
