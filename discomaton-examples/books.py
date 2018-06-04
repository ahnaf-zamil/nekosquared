#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Basic book cogs.

These do what they say on the tin, and basically demonstrate ways to use the
book types.

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
from random import randint

from discord import embeds
from discord.ext import commands

from discomaton import book
from discomaton.util import pag
from . import lipsum


class BookCog:
    @commands.command(brief="Demonstrates a basic book made from strings.")
    async def string_book(self, ctx, everyone_can_edit=False):
        """
        Produces multiple pages, and displays them to the author only.

        Notice that page numbering is added automatically, but ONLY if there
        is enough room on a page to do so.
        """

        # Generate our pages first. This is so that Discord doesn't complain
        # of messages being too large. This is just a reference to Danny's
        # paginator implementation for now.
        paginator = pag.RapptzPaginator(prefix="", suffix="")

        for line in lipsum.lorem_ipsum.splitlines():
            paginator.add_line(line)

        # Create our book state machine
        b = book.StringBooklet(
            pages=paginator.pages,
            ctx=ctx,
            timeout=100,
            only_author=not everyone_can_edit,
        )

        await b.start()

    @commands.command(brief="Shows a single page book.")
    async def single_page_string_book(self, ctx, everyone_can_edit=False):
        """
        See `string_book`. The difference here is that only a single page of
        content is output, which should affect the buttons that show up.
        """
        # Generate our pages first. This is so that Discord doesn't complain
        # of messages being too large.
        paginator = pag.RapptzPaginator(prefix="", suffix="")

        for line in lipsum.lorem_about_500.splitlines():
            paginator.add_line(line)

        # Create our book state machine
        b = book.StringBooklet(
            pages=paginator.pages,
            ctx=ctx,
            timeout=100,
            only_author=not everyone_can_edit,
        )

        await b.start()

    @commands.command(brief="Demonstrates a basic book made from strings.")
    async def string_book_lines(self, ctx, everyone_can_edit=False):
        """
        Produces multiple pages, and displays them to the author only.

        This uses our custom derived implementation of Rapptz paginator that
        also limits the max number of lines to show per page.

        Notice that page numbering is added automatically, but ONLY if there
        is enough room on a page to do so.
        """

        # Generate our pages first. This is so that Discord doesn't complain
        # of messages being too large. This is just a reference to Danny's
        # paginator implementation for now.
        paginator = pag.Paginator(prefix="", suffix="", max_lines=10)

        for line in lipsum.lorem_ipsum.splitlines():
            paginator.add_line(line)

        # Create our book state machine
        b = book.StringBooklet(
            pages=paginator.pages,
            ctx=ctx,
            timeout=100,
            only_author=not everyone_can_edit,
        )

        await b.start()

    @commands.command(brief="Demonstrates a basic book made from embeds.")
    async def embed_book(self, ctx, everyone_can_edit=False):
        """
        Produces multiple pages, and displays them to the author only.
        """
        # Generate our pages first. This is so that Discord doesn't complain
        # of messages being too large. This is just a reference to Danny's
        # paginator implementation for now.
        paginator = pag.RapptzPaginator(prefix="", suffix="", max_size=2048)

        for line in lipsum.lorem_ipsum.splitlines():
            paginator.add_line(line)

        embed_pages = []
        for page in paginator.pages:
            embed_pages.append(
                embeds.Embed(
                    title="Just an example",
                    description=page,
                    colour=randint(0, 0xFFFFFF),
                )
            )

        # Create our book state machine
        b = book.EmbedBooklet(
            pages=embed_pages, ctx=ctx, timeout=100, only_author=not everyone_can_edit
        )

        await b.start()
