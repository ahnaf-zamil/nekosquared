#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Examples for how to use this library.

This defines the setup function to load each cog.
"""
import discord

import discomaton
from . import books
from . import bookbinders
from . import optionpicker


__author__ = discomaton.__author__
__license__ = discomaton.__license__
__version__ = discomaton.__version__
__repository__ = discomaton.__repository__


def setup(bot):
    # Call each cog here.
    bot.add_cog(books.BookCog())
    bot.add_cog(bookbinders.BookBindingCog())
    bot.add_cog(optionpicker.OptionPickerCog())

    @bot.command()
    async def version(ctx):
        await ctx.send(
            f'Created by {__author__} as an example for Discomaton '
            f'v{__version__}. Licensed under {__license__}.'
        )

    @bot.listen()
    async def on_ready():
        await bot.change_presence(
            activity=discord.Game(name=__repository__[8:]))
