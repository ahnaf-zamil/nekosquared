#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Wraps around TLDR Pages to provide an interface simpler than
Man.
"""
import random

from discomaton import book
from discomaton.util import pag

import discord

from neko2.engine import commands
from neko2.shared import traits


class TldrCog(traits.HttpPool):
    @commands.command(brief='Shows TLDR pages (like man, but simpler).')
    async def tldr(self, ctx, page: str, platform: str='common'):
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
        and defaults to `common` if unspecified.
        """
        platform = platform.lower()
        if platform not in ('common', 'linux', 'osx', 'sunos', 'windows'):
            return await ctx.send('Invalid platform.', delete_after=10)
        elif any(x in page for x in '#?/'):
            return await ctx.send('Invalid page name.', delete_after=10)

        url = 'https://raw.githubusercontent.com/tldr-pages/tldr/master/pages/'
        url += f'{platform}/{page}.md'

        conn = await self.acquire_http()
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
            title = f'{page} ({platform})'

        paginator = pag.Paginator()
        last_line_was_bullet = False
        for line in content:

            # Removes the blank line between bullets and code examples.
            if last_line_was_bullet and not line.lstrip().startswith('- '):
                if not line.strip():
                    last_line_was_bullet = False
                    continue
            elif line.lstrip().startswith('- '):
                last_line_was_bullet = True

            paginator.add_line(line)

        pages = []
        for page in paginator.pages:
            pages.append(discord.Embed(
                title=title,
                description=page,
                colour=random.randint(0, 0xFFFFFF)
            ))

        booklet = book.EmbedBooklet(ctx=ctx, pages=pages)
        await booklet.start()


def setup(bot):
    bot.add_cog(TldrCog())
