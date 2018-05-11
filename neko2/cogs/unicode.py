#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Unicode character inspection.

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
# Unicode data does not define character information for all of the characters
# usable in python, namely, no names are provided for ASCII control characters,
# only aliases. http://fileformat.info provides more information, and the HTML
# is generally fairly simple for each page, so we can just mine the info from
# those results instead to be more accurate, even if it is a bit slower.
# Note that this website provides an `index.json` for each char also, but this
# appears to be incomplete. We only fall back to this therefore if we cannot
# resolve a character normally.
import re
from typing import Union, Optional
import unicodedata

import bs4
from dataclasses import dataclass

from discomaton.factories import bookbinding

from neko2.shared import alg, commands
from neko2.shared import collections
from neko2.shared import errors
from neko2.shared import traits


def _make_fileformat_url(codepoint: int) -> str:
    return (
        'http://www.fileformat.info/info/unicode/char'
        f'/{hex(codepoint)[2:]}/index.htm')


_char2category = {
    # https://en.wikipedia.org/wiki/Template:General_Category_(Unicode%29
    'Lu': 'Uppercase letter',
    'Ll': 'Lowercase letter',
    'Lm': 'Modifier letter',
    'Lt': 'Titlecase letter',
    'Lo': 'Other letter',
    'Mn': 'Non-spacing mark',
    'Mc': 'Spacing-combining mark',
    'Me': 'Enclosing mark',
    'Nd': 'Decimal number',
    'Nl': 'Letter number',
    'No': 'Other number',
    'Pc': 'Punctuation connector',
    'Pd': 'Punctuation dash',
    'Ps': 'Open punctuation',
    'Pe': 'Closed punctuation',
    'Pi': 'Opening quote punctuation',
    'Pf': 'Closing quote punctuation',
    'Po': 'Other punctuation',
    'Sm': 'Mathematical symbol',
    'Sc': 'Currency symbol',
    'Sk': 'Modifier symbol',
    'So': 'Other symbol',
    'Zs': 'Space separator',
    'Zl': 'Line separator',
    'Zp': 'Paragraph separator',
    'Cc': 'Other control',
    'Cf': 'Other format',
    'Cs': 'Other surrogate',
    'Co': 'Other private-use',
    'Cn': 'Other unassigned'
}


class UnicodeCog(traits.CogTraits):
    # noinspection PyUnresolvedReferences
    @dataclass
    class Unicode:
        name: str
        category: str
        raw: int

        def __hash__(self):
            return self.raw

        @property
        def char(self) -> str:
            return chr(self.raw)

        @classmethod
        async def from_name(cls, name: str) -> Optional['Unicode']:
            """Looks up a given character by a name or alias."""

        @classmethod
        async def from_raw(cls, raw: str) -> Optional['Unicode']:
            """Looks up a given character by the raw literal."""
            pass

        @classmethod
        async def from_number(cls,
                              number: Union[str, int]) -> Optional['Unicode']:
            """Looks up a given character by hex/octal/binary/integer value."""
            pass

    async def __lookup_online(self, bot, code_point: int):
        """
        Looks up the code point online to get the Unicode object.
        If nothing is returned, then we assume it is not found.
        """
        conn = await self.acquire_http()
        url = _make_fileformat_url(code_point)
        resp = await conn.get(url)
        if resp.status == 404:
            return None
        elif resp.status != 200:
            raise errors.HttpError(resp)

        content = await resp.text()
        soup = bs4.BeautifulSoup(content)

        '''
        <!-- Expects to find this somewhere -->
        
        <tr class="row0">
            <td>Name</td>
            <td>&lt;control&gt;</td>
        </tr>
        <tr class="row1">
            <td>Block</td>
            <td><a href="/info/unicode/block/basic_latin/index.htm">Basic Latin
                </a></td>
        </tr>
        <tr class="row0">
            <td>Category</td>
            <td><a href="/info/unicode/category/Cc/index.htm">Other, Control 
                [Cc]</a></td>
        </tr>
        <tr class="row1">
            <td>Combine</td>
            <td>0</td>
        </tr>
        <tr class="row0">
            <td>BIDI</td>
            <td>Paragraph Separator [B]</td>
        </tr>
        
        <tr class="row1">
            <td>Mirror</td>
            <td>N</td>
        </tr>
        
        <tr class="row0">
            <td>Old name</td>
            <td>LINE FEED (LF)</td>
        </tr>
        
        <tr class="row1">
            <td valign="top">Index entries</td>
            <td>eol<br />LINE FEED<br />line, new<br />new line<br />end of 
            line<br />lf<br />line, end of<br />nl<br /></td>
        </tr>        
        '''
        name: bs4.Tag = soup.find(name='td', text='Name')
        old_name: bs4.Tag = soup.find(name='td', text='Old name')
        bidi: bs4.Tag = soup.find(name='td', text='BIDI')
        idxs: bs4.Tag = soup.find(name='td', text='Index entries')
        category: bs4.Tag = soup.find(name='td', text='Category')

        # Name resolution order.
        def resolve(tag) -> str:
            if not tag:
                return ''
            else:
                sib = tag.find_next_sibling()
                return sib.text if sib else ''

        name = resolve(name)

        if name == '<control>':
            # Force resolving another name first.
            nro = (resolve(old_name), resolve(bidi),
                   resolve(idxs).splitlines(), name)
        else:
            nro = (name, resolve(old_name), resolve(bidi),
                   resolve(idxs).splitlines())

        name: str = alg.find(bool, nro, 'UNKNOWN')
        category: str = resolve(category)
        category = re.findall('\[(.*)\]', category)
        category: str = category[0] if category else '??'

        return self.Unicode(name, category, code_point)

    async def _lookup_literal(self, bot, character: str) -> Unicode:
        """
        Looks up the given literal to get data. If it cannot be resolved
        by unicodedata, then it will resort to searching online.
        """
        assert len(character) == 1

        try:
            name = unicodedata.name(character)
            category = unicodedata.category(character)
            return self.Unicode(name, category, ord(character))
        except Exception:
            return await self.__lookup_online(bot, ord(character))

    @staticmethod
    async def _send_table(ctx, *unicodes):
        """Creates a markdown formatted table of results for characters."""

        book = bookbinding.StringBookBinder(ctx, max_lines=None)

        preamble = (
            f'**Character info (Unicode v{unicodedata.unidata_version})**',
            '__**`##  Ct UTF-CODE DECIMAL DESCRIPTION`**__')

        # Categories for current page
        categories = set()
        current_page = []

        def dump_page():
            nonlocal current_page
            # Define the categories used.
            category_amble = ''
            for category in sorted(categories):
                desc = _char2category.get(category, 'Unknown')
                category_amble += f'\n`{category}` - {desc}'

            page = '\n'.join((*preamble, *current_page, category_amble))
            book.add_break()
            book.add_raw(page)
            categories.clear()
            current_page = []

        for i, char in enumerate(unicodes):
            decimal = char.raw
            hexd = f'U+{hex(decimal)[2:]}'
            category = char.category
            name = char.name
            lit = chr(char.raw)

            current_page.append(
                f'`{i+1:02}  {category} {hexd:>8} {decimal:>7} '
                f'{name}  {lit}`  {lit}')

            categories.add(category)

            if i % 16 == 15:
                dump_page()

        if current_page:
            dump_page()

        booklet = book.build()
        if len(booklet) > 1:
            await book.start()
        else:
            await ctx.send(booklet.current_page)

    @commands.group(name='char', brief='Character inspection for Unicode.',
                    invoke_without_command=True,
                    aliases=['unicode', 'utf', 'utf-8', 'utf8'],
                    examples=['¯\_(ツ)_/¯  0x1Q44c :musical_note: '])
    async def char_group(self, ctx, *, characters):
        """
        Outputs unicode information about the given characters.
        """
        # Make an ordered set of all characters. Maintains insertion order of
        # each first occurrence.
        charlist = []
        i = 0
        while i < len(characters):
            character = await self._lookup_literal(ctx.bot, characters[i])
            if character:
                charlist.append(character)
            i += 1

        await self._send_table(ctx, *charlist)

    @char_group.command(brief='Looks up a given character description.',
                        examples=['OK HAND SIGN'])
    async def lookup(self, ctx, *, description):
        """
        Looks up a given unicode character by an alias, name or description.
        """
        try:
            await self._send_table(ctx, await self._lookup_literal(
                ctx.bot,
                unicodedata.lookup(description)
            ))
        except:
            await ctx.send('No match...', delete_after=5)

    @char_group.command(brief='Looks up characters by ordinal value.',
                        examples=[''])
    async def ord(self, ctx, ordinal: str, *ordinals: str):
        """
        Takes decimal, binary (`0b1101`), octal (`0o173`), and hexadecimal
        (`0x10FF3` or `#10FF3`) values and looks them up in the unicode
        table.
        """
        i = 0

        try:
            ordinals = (ordinal, *ordinals)

            charlist = []
            while i < len(ordinals) and len(charlist) < 20:
                ordinal = int(ordinals[i].replace('#', '0x'), 0)

                character = await self._lookup_literal(ctx.bot, chr(ordinal))
                if character:
                    charlist.append(character)
                i += 1

            charset = collections.OrderedSet(charlist)
            await self._send_table(ctx, *charset)
        except:
            await ctx.send(f'Invalid input on ordinal #{i+1}.', delete_after=5)


def setup(bot):
    bot.add_cog(UnicodeCog())
