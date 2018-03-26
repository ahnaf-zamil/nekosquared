#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
C and C++ utilities.
"""
import collections                    # Named tuple
import random                         # RNG
import re                             # Regex
import typing                         # Type checking
from urllib import parse              # URL validation/sanitation

import asyncio
import bs4                            # HTML parser
import discord                        # discord.py

from discomaton import optionpicker   # Option picker
from discomaton.factories import bookbinding

from neko2.engine import commands     # Command decorators
from neko2.shared import errors       # standard errors
from neko2.shared import traits       # HTTP pool


# CppReference stuff
result_path = re.compile(r'^/w/c(pp)?/', re.I)


class SearchResult:
    def __init__(self, text, href):
        self.text = text
        self.href = href

    def __str__(self):
        return f'`{self.text}`'


base_cppr = 'https://en.cppreference.com'
search_cppr = base_cppr + '/mwiki/index.php'


class CppCog(traits.HttpPool):
    @classmethod
    async def results(cls, *terms):
        """Gathers the results for the given search terms from Cppreference."""
        params = {'search': '|'.join(terms)}

        conn = await cls.acquire_http()

        resp = await conn.get(search_cppr, params=params)
        if resp.status != 200:
            raise errors.HttpError(resp)
            
        href = resp.url[len(base_cppr):]
            
        resp = await resp.text()

        # Parse the HTML response.
        tree = bs4.BeautifulSoup(resp)
        
        if href.starts_with('/w/'):
            # Assume we are redirected to the first result page
            # only.
            title = tree.find(name='h1')
            title = title.title if title else resp.url
            return [SearchResult(title, href)]

        search_result_lists: typing.List[bs4.Tag] = tree.find_all(
            name='div',
            attrs={'class': 'mw-search-result-heading'})

        # Discard anything in search results without an inner link
        search_results = []
        for sr_list in search_result_lists:
            results: typing.List[bs4.Tag] = sr_list.find_all(
                name='a', attrs={
                    'href': result_path,
                    'title': lambda t: t
                })

            search_results.extend(results)

        c = []
        cpp = []
        other = []

        for link in search_results:
            href = link['href']
            name = link.text
            if href.startswith('/w/c/'):
                # A C library link
                name = f'[C] {name}'
                c.append(SearchResult(name, href))

            elif href.startswith('/w/cpp/'):
                # This is a C++ library link.
                name = f'[C++] {name}'
                cpp.append(SearchResult(name, href))
            else:
                # This is an "other" link.
                name = f'[Other] {name}'
                other.append(SearchResult(name, href))

        return [*c, *cpp, *other]

    @classmethod
    async def get_information(cls, href):
        """
        Gets information for the given search result.
        """
        url = base_cppr + href
        conn = await cls.acquire_http()
        response = await conn.get(url)
        # Make soup.
        bs = bs4.BeautifulSoup(await response.text())

        taster_tbl: bs4.Tag = bs.find(name='table',
                                      attrs={'class': 't-dcl-begin'})

        if taster_tbl:
            tasters = taster_tbl.find_all(
                name='span',
                attrs={'class': lambda c: c is not None and 'mw-geshi' in c})

            if tasters:
                # Fixes some formatting
                for i, taster in enumerate(tasters):
                    taster = taster.text.split('\n')
                    taster = '\n'.join(t.rstrip() for t in taster)
                    taster = taster.replace('\n\n', '\n')
                    tasters[i] = taster

            # Remove tasters from DOM
            taster_tbl.replace_with(bs4.Tag(name='empty'))
        else:
            tasters = []

        h1 = bs.find(name='h1').text

        # Get the description
        desc = bs.find(
            name='div',
            attrs={'id': 'mw-content-text'})

        if desc:
            desc = '\n'.join(p.text for p in desc.find_all(name='p'))
        else:
            desc = ''

        header = bs.find(name='tr', attrs={'class': 't-dsc-header'})
        if header:
            header = header.text
        else:
            header = ''

        return url, h1, tasters, header, desc

    @commands.command(
        brief='Searches en.cppreference.com for the given criteria',
        aliases=['cref', 'cpp'],
        examples=['std::string', 'stringstream'])
    async def cppref(self, ctx, *terms):
        results = await self.results(*terms)

        if not results:
            return await ctx.send('No results were found.', delete_after=10)

        if len(results) > 1:
            # Show an option picker
            result = await optionpicker.option_picker(
                ctx, *results, max_lines=20)
            await asyncio.sleep(0.25)

            if not result:
                return
        else:
            result = results[0]

        # Fetch the result page.
        url, h1, tasters, header, desc = await self.get_information(result.href)

        binder = bookbinding.StringBookBinder(ctx, max_lines=None)

        binder.add_line(f'**{h1}**\n<{url}>')
        if header:
            binder.add_line(f'`{header}`')

        if tasters:
            for taster in tasters:
                binder.add_line(f'```cpp\n{taster}\n```\n')

        if desc:
            binder.add_line(desc)

        binder.start()


def setup(bot):
    bot.add_cog(CppCog())
