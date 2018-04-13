#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import discord

from neko2.engine import commands
from neko2.shared import traits

class CatCog(traits.HttpPool):
    @commands.command(brief='Gets a random cat!')
    async def cat(self, ctx):
        # This endpoint will redirect us.
        conn = await self.acquire_http()
        resp = await conn.get('http://thecatapi.com/api/images/get')
        url = resp.url
        e = discord.Embed()
        e.set_image(url=url)
        e.set_footer(text='Provided by TheCatAPI')
        await ctx.send(embed=e)
        await resp.release()

def setup(bot):
    bot.add_cog(CatCog())
