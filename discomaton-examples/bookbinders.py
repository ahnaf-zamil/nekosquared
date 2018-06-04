#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Cogs

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
from discord.ext import commands

from discomaton.factories import bookbinding
from . import lipsum


class BookBindingCog:
    @commands.command(brief="Uses multiple calls to set settings.")
    async def bind_book_ex1(self, ctx):
        binder = bookbinding.StringBookBinder(ctx)

        binder.add(lipsum.lorem_ipsum)
        binder.with_prefix("```css")
        binder.with_suffix("```")
        binder.with_respond_to_author_only(False)
        binder.with_timeout(100)
        binder.with_open_on_number(5)
        binder.with_max_lines(7)

        await binder.start()

    @commands.command(brief="Uses call chaining to set settings.")
    async def bind_book_ex2(self, ctx):
        await (
            bookbinding.StringBookBinder(ctx)
            .add(lipsum.lorem_ipsum)
            .with_prefix("```css")
            .with_suffix("```")
            .with_respond_to_author_only(False)
            .with_timeout(100)
            .with_open_on_number(5)
            .with_max_lines(7)
        ).start()

    @commands.command(brief="Uses a huuuuge constructor to set settings.")
    async def bind_book_ex3(self, ctx):
        binder = bookbinding.StringBookBinder(
            ctx,
            max_lines=7,
            start_page=5,
            timeout=100,
            only_author=True,
            prefix="```css",
            suffix="```",
        )

        binder.add(lipsum.lorem_ipsum)

        await binder.start()

    @commands.command(brief="Shows that you can build separately.")
    async def bind_book_ex4(self, ctx):
        binder = bookbinding.StringBookBinder(
            ctx,
            max_lines=7,
            start_page=5,
            timeout=100,
            only_author=True,
            prefix="```css",
            suffix="```",
        )

        binder.add(lipsum.lorem_ipsum)

        booklet = binder.build()

        # Run async without waiting.
        booklet.start()
        await ctx.send("This is async.")

    @commands.command(brief="Demos the intelliadd functionality.")
    async def bind_book_ex5(self, ctx):
        binder = bookbinding.StringBookBinder(
            ctx,
            max_lines=7,
            start_page=5,
            timeout=100,
            only_author=True,
            prefix="```css",
            suffix="```",
        )

        super_long_string = ""

        i = 0
        for i in range(0, 10_000, max(i // 10, 1)):
            super_long_string += ". "
            super_long_string += f'{(i//26 + 1) * chr(ord("a") + (i % 26)):}'

        binder.add(super_long_string)

        booklet = binder.build()

        # Run async without waiting.
        booklet.start()
        await ctx.send(
            "This uses intelligent pagination now, and has been "
            "rewritten from scratch!"
        )
