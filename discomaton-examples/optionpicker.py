#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Option picker usage.
"""

import discord
from discord.ext import commands

from discomaton import userinput


class ColourModel:
    def __init__(self, hex_str):
        self.value = int(hex_str, 16)
        self.string = hex_str

    def __str__(self):
        return self.string


class OptionPickerCog:
    @commands.command(brief='Shows option picker usage.')
    async def option_picker(self, ctx):
        options = [ColourModel(c) for c in [
            '0x32834d', '0x9a2db', '0x4e066c', '0xf32a10', '0xf36d3a',
            '0x80f1f1', '0xa9e335', '0x42561f', '0x805fd3', '0xda0440',
            '0xe4b9b2', '0x58fa97', '0x2602fa', '0x4d670f', '0xfe0e2',
            '0xdd292e', '0x11624f', '0xa86a5d', '0x35d888', '0x407563',
            '0x7830f7', '0x7c3dc0', '0xe7f33c', '0x3246cf', '0xce608b',
            '0xf12873', '0xc25fd6', '0xd55a16', '0xc89c93', '0xac987',
            '0x56040c', '0x2a22f8', '0x3a80ec', '0x89a8d8', '0x40da23',
            '0xf593f4', '0xcbffeb', '0x8244d0', '0xe767b', '0xc367c0',
            '0xf815bd', '0x1ced2b', '0x551989', '0x6d5d7', '0xa42e9d',
            '0xf075fd', '0x34d909', '0xc3e825', '0xa962e6', '0x8493cd',
            '0x383f52', '0xe3d6e5', '0xbd7430', '0x780247', '0xffe713',
            '0x63cb25', '0xc67d1e', '0xd2dcd2', '0x19382d', '0x39cb61',
            '0xd053c3', '0xa9190a', '0x95d35f', '0x358c01', '0xe4010c',
            '0x901d2', '0xec6154', '0x27cbd4', '0x94e5b1', '0x88b843',
            '0xe33acf', '0xfe95a0', '0xea0dfe', '0x8b4ffc', '0x99edf4',
            '0x2458e3', '0x905467', '0x93be7a', '0x4c4506', '0xd29c45',
            '0x5e0052', '0x7891ec', '0xd05918', '0xc29b88', '0xa1f473',
            '0x6432b2', '0xf46e51', '0xd3c570', '0xfe226', '0x3ec64b',
            '0xdd9c37', '0xd616a9', '0x2073cd', '0x79af64', '0x8635e0',
            '0x2c650f', '0x9fb98e', '0x9cd6fa', '0xb88f51', '0x6485ab'
        ]]

        result = await userinput.option_picker(ctx, *options, timeout=15)

        if result:
            await ctx.send(
                embed=discord.Embed(
                    title=str(result),
                    colour=result.value),
                delete_after=15)
        else:
            await ctx.send('No result', delete_after=5)
