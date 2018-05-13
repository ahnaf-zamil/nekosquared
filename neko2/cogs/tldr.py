#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Wraps around TLDR Pages to provide an interface simpler than manpages.

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
from discomaton.util import pag
from neko2.shared import alg, commands, traits


def scrub_tags(text):
    return text


class TldrCog(traits.CogTraits):
    @commands.command(brief='Shows TLDR pages (like man, but simpler).')
    async def tldr(self, ctx, page: str, platform=None):
        """
        Similar to man pages, this shows information on how to use a command,
        the difference being that this is designed to be human readable.

        Usage:

        - tldr gcc
        - tldr gcc <platform>

        `platform` can be any of the following:
        - common
        - linux
        - osx
        - sunos
        - windows

        If unspecified, we check all platforms. This will take a little longer
        to respond.
        """
        platform = None if platform is None else platform.lower()
        supported_platforms = ('common', 'linux', 'osx', 'sunos', 'windows')

        if platform and platform not in supported_platforms:
            return await ctx.send('Invalid platform.', delete_after=10)
        elif any(x in page for x in '#?/'):
            return await ctx.send('Invalid page name.', delete_after=10)

        url = 'https://raw.githubusercontent.com/tldr-pages/tldr/master/pages/'

        conn = await self.acquire_http()

        if platform is None:
            resp = None
            for platform in supported_platforms:
                resp = await conn.get(f'{url}{platform}/{page}.md')
                if 200 <= resp.status < 300:
                    break
                else:
                    ctx.bot.loop.create_task(resp.release())
        else:
            url += f'{platform}/{page}.md'
            resp = await conn.get(url)

        if resp.status != 200:
            return await ctx.send(f'Error: {resp.reason}.', delete_after=10)

        content = ''.join(await resp.text()).splitlines()

        if not content:
            raise RuntimeError('No response from GitHub. Is the page empty?')
        elif len(content) == 1:
            raise RuntimeError('No body, only a title. Is the page empty?')

        # First line is title if it starts with '#'
        if content[0].startswith('#'):
            title = content.pop(0)[1:].lstrip() + f' ({platform})'
        else:
            title = f'{page} ({platform.title()})'

        paginator = pag.Paginator()
        last_line_was_bullet = False
        for line in content:

            # Removes the blank line between bullets and code examples.
            if last_line_was_bullet and not line.lstrip().startswith('- '):
                if not line.strip():
                    last_line_was_bullet = False
                    continue
            elif line.lstrip().startswith(' '):
                last_line_was_bullet = True

            paginator.add_line(line)

        pages = []
        for page in paginator.pages:
            page = scrub_tags(page)
            pages.append(discord.Embed(
                title=title,
                description=page,
                colour=alg.rand_colour()
            ))

        booklet = book.EmbedBooklet(ctx=ctx, pages=pages)
        await booklet.start()


def setup(bot):
    bot.add_cog(TldrCog())
