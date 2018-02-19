"""
C and C++ utilities.
"""
import collections
import random
import re
import typing
from urllib import parse

import bs4
import discord

from neko2.engine import commands
from neko2.shared import errors
from neko2.shared import fsa
from neko2.shared import traits


result_path = re.compile(r'^/w/c(pp)?/', re.I)
SearchResult = collections.namedtuple('SearchResult', 'text href')
SearchResults = collections.namedtuple(
    'SearchResults',
    [
        'cpp_general',
        'cpp_concepts',
        'cpp_keywords',
        'cpp_experimental',
        'c_general',
        'c_keywords',
        'c_experimental',
        'other'
    ]
)
base_cppr = 'https://en.cppreference.com'
search_cppr = base_cppr + '/mwiki/index.php'


class CppCog(traits.HttpPool):
    @classmethod
    async def results(cls, *terms):
        """Gathers the results for the given search terms from Cppreference."""
        params = {'search': '|'.join(terms)}

        with (await cls.acquire_http()) as conn:
            resp = await conn.get(search_cppr, params=params)
            if resp.status != 200:
                raise errors.HttpError(resp)
            else:
                resp = await resp.text()

        # Parse the HTML response.
        tree = bs4.BeautifulSoup(resp)

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

        # Sort in lexicographical order.
        search_results = sorted(search_results, key=lambda t: t.text)

        cpp_general = []
        cpp_concepts = []
        cpp_keywords = []
        cpp_experimental = []

        c_general = []
        c_keywords = []
        c_experimental = []

        other = []

        for link in search_results:
            href = link['href']
            name = link.text
            if href.startswith('/w/c/'):
                # This is a C-library link.
                if href.startswith('/w/c/experimental'):
                    c_experimental.append(SearchResult(name, href))
                else:
                    c_general.append(SearchResult(name, href))

            elif href.startswith('/w/cpp/'):
                # This is a C++ library link.
                if href.startswith('/w/cpp/concept'):
                    cpp_concepts.append(SearchResult(name, href))
                elif href.startswith('/w/cpp/keyword'):
                    cpp_keywords.append(SearchResult(name, href))
                elif href.startswith('/w/cpp/experimental'):
                    cpp_experimental.append(SearchResult(name, href))
                else:
                    cpp_general.append(SearchResult(name, href))
            else:
                # This is an "other" link.
                other.append(SearchResult(name, href))

        return SearchResults(
            cpp_general, cpp_concepts, cpp_keywords, cpp_experimental,
            c_general, c_keywords, c_experimental, other)

    @commands.command(
        name='cppref',
        brief='Searches en.cppreference.com for the given criteria',
        aliases=['cref'])
    async def cpp_reference_cmd(self, ctx, *terms):
        results = await self.results(*terms)

        embeds = []

        result_url = (
                search_cppr + '?' + parse.urlencode({'search': '|'.join(terms)})
        )

        def process_results(lang, category, category_results):
            # Skip if no results.
            if not category_results:
                return

            pag = fsa.LinedPag(10, max_size=fsa.EMBED_FIELD_MAX)
            for result in category_results:
                pag.add_line(f'- **{result.text}**:\r\t'
                             f'{base_cppr}{result.href}')

            for i, page in enumerate(pag.pages):
                embed = discord.Embed(
                    title=f'Search results for `{" ".join(terms)}`',
                    colour=random.randint(0, 0xFFFFFF),
                    url=result_url)

                if lang:
                    embed.description = f'Results that apply to **{lang}**'
                else:
                    embed.description = 'Other results'

                embed.add_field(name=category, value=page)
                if i + 1 < len(pag.pages):
                    embed.set_footer(
                        text='Current list continued on next page '
                             f'({i + 1}/{len(pag.pages)})')
                embeds.append(embed)

        process_results('C++', 'General', results.cpp_general)
        process_results('C++', 'Concepts', results.cpp_concepts)
        process_results('C++', 'Keywords', results.cpp_keywords)
        process_results('C++', 'Experimental', results.cpp_experimental)
        process_results('C', 'General', results.c_general)
        process_results('C', 'Keywords', results.c_keywords)
        process_results('C', 'Experimental', results.c_experimental)
        process_results(None, 'Other Results', results.other)

        if len(embeds):
            fsm = fsa.FocusedPagEmbed.from_embeds(
                embeds, bot=ctx.bot, invoked_by=ctx, timeout=120)
            await fsm.run()
        else:
            await ctx.send('No results were found.', delete_after=10)


def setup(bot):
    bot.add_cog(CppCog())
