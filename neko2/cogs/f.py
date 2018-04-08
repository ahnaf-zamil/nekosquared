#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Press F to pay respects.
"""
import discord
from neko2.engine import commands


class RespectsCog:
    async def on_message(self, message, **kwargs):
        try:
            if message.content.lower() == 'f' or 'for_what' in kwargs:
                await message.delete()

                text = f'{message.author} paid their respects'
                if kwargs.get("for_what"):
                    text += f' for {kwargs["for_what"]}.'
                else:
                    text += '.'

                resp = await message.channel.send(embed=discord.Embed(
                    title=text,
                    colour=0x551a8b
                ))
                await resp.add_reaction(
                    '\N{REGIONAL INDICATOR SYMBOL LETTER F}')
        except:
            raise

    @commands.command(brief='Pay your respects.',
                      examples=['me', 'you', 'the in-laws', 'the police'])
    async def f(self, ctx, *, what=None):
        prefix = ctx.prefix + ctx.invoked_with
        await self.on_message(
            ctx.message,
            for_what=ctx.message.clean_content[len(prefix):].lstrip())


def setup(bot):
    bot.add_cog(RespectsCog())
