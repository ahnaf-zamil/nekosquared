#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Press F to pay respects.
"""
import discord


class RespectsCog:
    async def on_message(self, message):
        try:
            if message.content.lower() == 'f':
                await message.delete()
                await message.channel.send(embed=discord.Embed(
                    title=f'{message.author} paid their respects.',
                    colour=0x551a8b
                ))
        except:
            pass


def setup(bot):
    bot.add_cog(RespectsCog())
