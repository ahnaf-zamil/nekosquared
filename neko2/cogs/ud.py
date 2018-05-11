#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Urban Dictionary support.

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

from discomaton import book

from neko2.shared import traits, commands
from neko2.shared import string


urban_random = 'http://api.urbandictionary.com/v0/random'
urban_search = 'http://api.urbandictionary.com/v0/define'


class UrbanDictionaryCog(traits.CogTraits):
    """Urban dictionary cog."""
    @staticmethod
    def _format_urban_defn(definition: dict) -> discord.Embed:
        """
        Takes an UrbanDictionary word response and formats an embed
        to represent the output, before returning it.
        """

        # Adds ellipses to the end and truncates if a string is too long.
        def dots(string, limit=1024):
            return string if len(string) < limit else string[:limit-3] + '...'

        title = definition['word'].title()
        defn = dots(definition['definition'], 2000)

        # Remove embedded URLS to stop Discord following them.
        defn = defn.replace('https://', '').replace('http://', '')
        # [] signify bold phrases
        defn = defn.replace('[', '**').replace(']', '**')

        # Sanitise backticks and place in a code block if applicable.
        example = dots(definition['example'].replace('`', '’'))
        if example:
            example = f'`{string.trunc(example, 1000)}`'

        author = definition['author']
        yes = definition['thumbs_up']
        no = definition['thumbs_down']
        permalink = definition['permalink']

        embed = discord.Embed(
            title=title,
            description=string.trunc(defn),
            colour=0xFFFF00,
            url=permalink)

        embed.set_author(
            name=f'{author} (\N{HEAVY BLACK HEART} {yes} \N{PILE OF POO} {no})')

        if example:
            embed.add_field(name='Example', value=example)

        if 'tags' in definition and definition['tags']:
            tags = ', '.join(sorted({*definition['tags']}))
            embed.set_footer(text=string.trunc(tags))
        return embed

    @commands.command(
        brief='Looks up a definition on Urban Dictionary',
        examples=['java', ''], aliases=['ud', 'udd', 'urband'])
    async def urban(self, ctx: commands.Context, *, phrase: str=None):
        """If no phrase is given, we pick some random ones to show."""

        conn = await self.acquire_http()

        with ctx.typing():
            # Get the response
            if phrase:
                resp = await conn.get(urban_search, params={'term': phrase})
            else:
                resp = await conn.get(urban_random)

            # Decode the JSON.
            resp = (await resp.json())['list']

        if len(resp) == 0:
            return await ctx.send('No results. You sure that is a thing?',
                                  delete_after=15)

        embeds = [self._format_urban_defn(word) for word in resp]

        # If we have more than one result, make a FSM from the pages.
        if ctx.invoked_with in ('udd', 'urband'):
            await commands.try_delete(ctx)

        book.EmbedBooklet(ctx=ctx, pages=embeds).start()


def setup(bot):
    bot.add_cog(UrbanDictionaryCog())
