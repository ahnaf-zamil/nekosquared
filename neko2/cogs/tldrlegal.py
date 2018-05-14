#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Uses webscraping to search tldrlegal for human-readable information on
software licenses, et cetera.

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
from typing import List, Tuple

import bs4
from dataclasses import dataclass
import discord

from discomaton import option_picker
from neko2.shared import alg, commands, string, traits

base_url = 'https://tldrlegal.com/'


@dataclass()
class License:
    name: str
    brief: str
    can: List[Tuple[str, str]]
    cant: List[Tuple[str, str]]
    must: List[Tuple[str, str]]
    url: str


class TldrLegalCog(traits.CogTraits):
    @staticmethod
    def get_results_from_html(html: str) -> List[Tuple[str, str]]:
        """
        Parses the given HTML as search results for TLDR legal, returning
        a list of tuples for each result: each tuple has the name and URL.
        """
        soup = bs4.BeautifulSoup(html)

        results = soup.find_all(attrs={'class': 'search-result flatbox'})

        pages = []

        for result in results:
            link: bs4.Tag = result.find(name='a')
            url = f'{base_url}{link["href"]}'
            name = link.text
            pages.append((name, url))

        return pages

    @staticmethod
    def get_license_info(url: str, html: str) -> License:
        """
        Parses a license info page to get the info regarding said license as an
        object.
        """
        soup = bs4.BeautifulSoup(html)

        name = soup.find(name='h1', attrs={'class': 'page-title'}).text
        summary = soup.find(name='div', attrs={'class': 'summary-content'})
        summary = summary.text.strip()

        # Get the results license-root div.
        results = soup.find(name='div', attrs={'id': 'license_root'})

        can_tag = results.find(name='ul', attrs={'class': 'bucket-list green'})
        cant_tag = results.find(name='ul', attrs={'class': 'bucket-list red'})
        must_tag = results.find(name='ul', attrs={'class': 'bucket-list blue'})

        def remove_title_li(tag: bs4.Tag):
            # Pop the title
            tag.find(name='li', attrs={'class': 'list-header'}).extract()

        remove_title_li(can_tag)
        remove_title_li(cant_tag)
        remove_title_li(must_tag)

        def get_head_body_pairs(tag: bs4.Tag):
            return (
                tag.find(attrs={'class': 'attr-head'}).text,
                tag.find(attrs={'class': 'attr-body'}).text)

        can = [get_head_body_pairs(li) for li in can_tag.find_all(name='li')]
        cant = [get_head_body_pairs(li) for li in cant_tag.find_all(name='li')]
        must = [get_head_body_pairs(li) for li in must_tag.find_all(name='li')]

        return License(name, summary, can, cant, must, url)

    @commands.group(brief='Search for license info on tldrlegal.',
                    aliases=['license', 'licence'],
                    invoke_without_command=True)
    async def tldrlegal(self, ctx, *, search):
        await self.tldrlegal_logic(ctx, search, False)

    @tldrlegal.command(brief='Search for a license on tldrlegal, and give '
                             'more information in the results.')
    async def more(self, ctx, *, search):
        await self.tldrlegal_logic(ctx, search, True)

    async def tldrlegal_logic(self, ctx, query, verbose):
        """
        Helper to prevent code duplication.
        """
        http = await self.acquire_http()

        # Get search results
        async with http.get(f'{base_url}search', params={'q': query}) as resp:
            if resp.status != 200:
                return await ctx.send(f'tldrlegal said {resp.reason!r}')

            results = self.get_results_from_html(await resp.text())

        count = len(results)

        if count == 0:
            return await ctx.send('Nothing was found.', delete_after=15)
        elif count == 1:
            # Get the URL
            page = results[0]
        else:
            page = await option_picker(
                ctx,
                *results,
                option_formatter=lambda o: o[0].replace('*', '∗')
            )

            if page is None:
                return await ctx.send('Took too long...')

        # Get the info into an object.
        async with http.get(page[1]) as resp:
            if resp.status != 200:
                return await ctx.send(f'tldrlegal said {resp.reason!r}')
            license_info = self.get_license_info(page[1], await resp.text())

        # Generate embed and send.
        embed = discord.Embed(title=license_info.name,
                              description=string.trunc(license_info.brief),
                              colour=alg.rand_colour(),
                              url=license_info.url)
        embed.set_footer(text='Disclaimer: This is only a short summary of the'
                              ' Full Text. No information on TLDRLegal is'
                              ' legal advice.')

        def fmt(prs):
            if verbose:
                s = string.trunc('\n'.join(f'**{n}** {d}' for n, d in prs),
                                 1024)
            else:
                s = string.trunc('\n'.join(f'- {n}' for n, _ in prs),
                                 1024)

            # Prevents errors for empty bodies.
            return s or '—'

        embed.add_field(name='__CAN__', value=fmt(license_info.can),
                        inline=not verbose)
        embed.add_field(name='__CANNOT__', value=fmt(license_info.cant),
                        inline=not verbose)
        embed.add_field(name='__MUST__', value=fmt(license_info.must),
                        inline=not verbose)

        if not verbose:
            embed.add_field(name='\u200b',
                            value='_Run again using `tldrlegal more <query>` '
                                  'to get a longer explanation!_')

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(TldrLegalCog())
