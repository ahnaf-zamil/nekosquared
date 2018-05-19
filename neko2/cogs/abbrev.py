#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Webscrapes websites to get definitions for given abbreviations.

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
from urllib import parse

import bs4
import discord

from discomaton import book
from neko2.shared import alg, commands, traits


def gen_url_acronymn_finder(terms):
    terms = parse.quote(terms)
    return (
        'https://www.acronymfinder.com/~/search/af.aspx?string=exact&Acronym='
        + terms
    )


class AbbrevCog(traits.CogTraits):
    async def fail(self, ctx, query):
        return await ctx.send(f'No results for `{query}`...', delete_after=10)

    @commands.command(
        brief='Looks up definitions for the given abbreviations.',
        aliases=['ab'])
    async def abbrev(self, ctx, *, query):
        url = gen_url_acronymn_finder(query)

        http = await self.acquire_http()

        async with http.get(url) as resp:
            resp.raise_for_status()
            html = await resp.text()

        soup = bs4.BeautifulSoup(html)

        result_tags = soup.find_all(
            name='td',
            attrs={'class': 'result-list__body__rank'})

        if not result_tags:
            return await self.fail(ctx, query)

        # Convert to tuples of abbreviation and definition.
        pairs = []

        for tag in result_tags:
            abbrev = tag.text
            defn = tag.find_next_sibling(
                name='td',
                attrs={'class': 'result-list__body__meaning'})

            definition = defn.text if defn else None
            if definition:
                pairs.append((abbrev, defn))

        if not pairs:
            return await self.fail(ctx, query)

        embeds = []

        def new_embed():
            embeds.append(discord.Embed(title=query,
                                        description='',
                                        colour=alg.rand_colour()))

        new_embed()

        for i, (abbrev, definition) in enumerate(pairs):
            if i and i % 6:
                new_embed()

            embeds[-1].description += f'**{abbrev}**\n\t{definition}\n\n'

        booklet = book.EmbedBooklet(pages=embeds, ctx=ctx)
        booklet.start()


def setup(bot):
    bot.add_cog(AbbrevCog())
