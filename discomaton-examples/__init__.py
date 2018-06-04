#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Examples for how to use this library.

This defines the setup function to load each cog.

===

MIT License

Copyright (c) 2018 Neko404NotFound

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import discord

import discomaton
from . import bookbinders, books, optionpicker

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
            f"Created by {__author__} as an example for Discomaton "
            f"v{__version__}. Licensed under {__license__}."
        )

    @bot.listen()
    async def on_ready():
        await bot.change_presence(activity=discord.Game(name=__repository__[8:]))
