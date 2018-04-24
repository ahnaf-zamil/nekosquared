#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Python script...
"""
from discord.ext import commands

from discomaton.factories import bookbinding

from . import lipsum


class BookBindingCog:
    @commands.command(brief='Uses multiple calls to set settings.')
    async def bind_book_ex1(self, ctx):
        binder = bookbinding.StringBookBinder(ctx)

        binder.add(lipsum.lorem_ipsum)
        binder.with_prefix('```css')
        binder.with_suffix('```')
        binder.with_respond_to_author_only(False)
        binder.with_timeout(100)
        binder.with_open_on_number(5)
        binder.with_max_lines(7)

        await binder.start()

    @commands.command(brief='Uses call chaining to set settings.')
    async def bind_book_ex2(self, ctx):
        await (
            bookbinding.StringBookBinder(ctx)
                .add(lipsum.lorem_ipsum)
                .with_prefix('```css')
                .with_suffix('```')
                .with_respond_to_author_only(False)
                .with_timeout(100)
                .with_open_on_number(5)
                .with_max_lines(7)
        ).start()

    @commands.command(brief='Uses a huuuuge constructor to set settings.')
    async def bind_book_ex3(self, ctx):
        binder = bookbinding.StringBookBinder(
            ctx,
            max_lines=7,
            start_page=5,
            timeout=100,
            only_author=True,
            prefix='```css',
            suffix='```')

        binder.add(lipsum.lorem_ipsum)

        await binder.start()

    @commands.command(brief='Shows that you can build separately.')
    async def bind_book_ex4(self, ctx):
        binder = bookbinding.StringBookBinder(
            ctx,
            max_lines=7,
            start_page=5,
            timeout=100,
            only_author=True,
            prefix='```css',
            suffix='```')

        binder.add(lipsum.lorem_ipsum)

        booklet = binder.build()

        # Run async without waiting.
        booklet.start()
        await ctx.send('This is async.')

    @commands.command(brief='Demos the intelliadd functionality.')
    async def bind_book_ex5(self, ctx):
        binder = bookbinding.StringBookBinder(
            ctx,
            max_lines=7,
            start_page=5,
            timeout=100,
            only_author=True,
            prefix='```css',
            suffix='```')

        super_long_string = ''

        i = 0
        for i in range(0, 10_000, max(i // 10, 1)):
            super_long_string += '. '
            super_long_string += f'{(i//26 + 1) * chr(ord("a") + (i % 26)):}'

        binder.add(super_long_string)

        booklet = binder.build()

        # Run async without waiting.
        booklet.start()
        await ctx.send('This uses intelligent pagination now, and has been '
                       'rewritten from scratch!')
