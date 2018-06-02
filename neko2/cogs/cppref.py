#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
C and C++ utilities.

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
import asyncio
import re  # Regex
import typing  # Type checking

import bs4  # HTML parser

from discomaton import userinput  # Option picker
from discomaton.factories import bookbinding
from neko2.shared import commands, errors, traits  # standard errors; HTTP pool

# CppReference stuff
result_path = re.compile(r'^/w/c(pp)?/', re.I)


class SearchResult:
    def __init__(self, text, href):
        self.text = text
        self.href = href

    def __str__(self):
        return f'`{self.text}`'


# 25th Apr 2018: Certificate issues on HTTPS, so using
# HTTP instead.
base_cppr = 'http://en.cppreference.com'
base_cppr_https = 'https://en.cppreference.com'
search_cppr = base_cppr + '/mwiki/index.php'


class CppCog(traits.CogTraits):
    @classmethod
    async def results(cls, *terms):
        """Gathers the results for the given search terms from Cppreference."""
        params = {'search': '|'.join(terms)}

        conn = await cls.acquire_http()

        resp = await conn.get(search_cppr, params=params)
        if resp.status != 200:
            raise errors.HttpError(resp)

        url = str(resp.url)
        if url.starts_with(base_cppr_https):
            href = url[len(base_cppr_https):]
        else:
            href = url[len(base_cppr):]
            
        resp = await resp.text()

        # Parse the HTML response.
        tree = bs4.BeautifulSoup(resp)
        
        cls.logger.info(href)

        if href.startswith('/w/'):
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

        header = bs.find(name='tr', attrs={'class': 't-dsc-header'})
        if header:
            header = header.text
        else:
            header = ''

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
            # first_par_node = desc.find(name='p')
            # description = first_par_node.text + '\n'
            # sibs = first_par_node.find_next_siblings()
            # for sib in sibs:
            #    description += sib.text + '\n'
            description = '\n'.join(p.text for p in desc.find_all(name='p')
                                    if not p.text.strip().endswith(':') and
                                    not p.text.strip().startswith('(') and
                                    not p.text.strip().endswith(')'))
        else:
            description = ''

        return url, h1, tasters, header, description

    @commands.command(
        brief='Searches en.cppreference.com for the given criteria.',
        aliases=['cref', 'cpp'],
        examples=['std::string', 'stringstream'])
    async def cppref(self, ctx, *terms):

        try:
            async with ctx.typing():
                results = await self.results(*terms)
        except BaseException as ex:
            return await ctx.send(
                'CppReference did something unexpected. If this keeps '
                'happening, contact Esp with the following info: \n\n'
                f'{type(ex).__qualname__}: {ex!s}')

        if not results:
            return await ctx.send('No results were found.', delete_after=10)

        if len(results) > 1:
            # Show an option picker
            result = await userinput.option_picker(
                ctx, *results, max_lines=20)
            await asyncio.sleep(0.25)

            if not result:
                return
        else:
            result = results[0]

        # Fetch the result page.
        try:
            url, h1, tasters, header, desc = await self.get_information(
                result.href)
        except:
            return await ctx.send('Rude! Cppreference just hung up on me..!')

        binder = bookbinding.StringBookBinder(ctx, max_lines=50)

        binder.add_line(f'**{h1}**\n<{url}>', dont_alter=True)
        if header:
            binder.add_line(f'\n`{header}`', dont_alter=True)

        if tasters:
            for taster in tasters:
                binder.add_line(f'```cpp\n{taster}\n```', dont_alter=True)

        if desc:
            binder.add_line(desc.replace('*', '∗'))

        binder.start()


def setup(bot):
    bot.add_cog(CppCog())
