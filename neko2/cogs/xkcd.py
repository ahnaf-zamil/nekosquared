#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
xkcd viewer/reference thingy.

Also allows searching for XKCD comic strips by the given
criteria using fuzzy string matching algorithms.

3rd May 2018: Implemented caching of data using threadsafe cached properties.

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
import io
import json
import os
import random
import threading
import time

from cached_property import threaded_cached_property
import discord
import requests

from neko2.shared import commands, configfiles, fuzzy, morefunctools, scribe, \
    traits


def most_recent_xkcd():
    return 'https://xkcd.com/info.0.json'


def get_xkcd(num):
    if num == 404 or num == 0:
        raise FileNotFoundError
    return f'https://xkcd.com/{num}/info.0.json'


def get_alphas(string):
    # noinspection PyPep8Naming
    a, z, A, Z = ord('a'), ord('z'), ord('A'), ord('Z')
    return ''.join(c for c in string if a <= ord(c) <= z or A <= ord(c) <= Z)


# 2 hour
SLEEP_FOR = 60 * 60 * 2
CACHE_FILE = os.path.join(configfiles.CONFIG_DIRECTORY, 'xkcd.json')


# Easier to delegate this to an entirely separate thread and make it run
# every so often. Then it cannot interfere with the bot. Also means I don't
# need to use Asyncio.
class XkcdCache(threading.Thread,
                scribe.Scribe,
                metaclass=morefunctools.SingletonMeta):
    """
    Sequentially crawls xkcd periodically to gather metadata.
    Maintains an in-memory cache of XKCD comics and keeps it updated.
    """

    def __init__(self, bot):
        setattr(bot, '__xkcd_cacher_thread', self)
        super().__init__(daemon=True)

        # Start self.
        self.start()

    @threaded_cached_property
    def cached_metadata(self):
        data = []
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE) as fp:
                data = json.load(fp) or []
        return data

    def run(self):
        """
        Repeatedly runs every 12 hours or so to find the most recent xkcd
        entries, storing metadata about them in xkcd.json. This is done to
        let us use Fuzzy matching to search xkcd  for certain criteria.
        """
        # Wait a while before starting to let anything else set itself up
        # unless we have a specific reason to do this immediately.
        if os.path.exists(CACHE_FILE):
            self.logger.info('xkcd cache already present. Will schedule '
                             'a few hours later.')
            time.sleep(SLEEP_FOR / 2)

        while True:
            self.logger.info('xkcd cacher thread has woken up.')

            # Get old data state. This will block if in an asyncio coro.
            data = self.cached_metadata

            # Use a session, obviously.
            with requests.Session() as sesh:
                # Get most recent strip.
                most_recent = sesh.get(most_recent_xkcd()).json()

                for i in range(1, most_recent['num'] + 1):
                    try:
                        next_comic = sesh.get(get_xkcd(i)).json()
                    except:
                        self.logger.warning(f'Could not get xkcd no. {i}')
                        continue
                    else:
                        self.logger.debug(f'Cached xkcd no. {i}')

                    data.append({
                        'num': next_comic['num'],
                        'title': next_comic['title'],
                        'alt': next_comic['alt'],
                        'transcript': next_comic['transcript']
                    })

            with open(CACHE_FILE, 'w') as fp:
                data = data
                json.dump(data, fp, indent='  ')
            del self.__dict__['cached_metadata']

            self.logger.info('XKCD recache completed. Going to sleep.')
            time.sleep(SLEEP_FOR)


class XkcdCog(traits.CogTraits):
    @commands.command(
        brief='Gets a page from xkcd.',
        examples=['', 'mr', 'new', 'newest', '629', 'exploits of a mom'])
    async def xkcd(self, ctx, *, query=None):
        """
        Returns a page from xkcd.

        If you provide no arguments, a random xkcd comic is output. If you
        input a number, then the comic with that number is returned.

        If you provide either `mr`, `new` or `newest` as the query, then the
        most recent comic entry is output.

        If you provide a string, then that is used as search criteria across
        all xkcd titles. This may take a few seconds to complete, so be patient
        """
        conn = await self.acquire_http()
        try:
            if not query:
                # Get the most recent comic first and inspect the entry number
                # (our cache can be up to 12 hours out of date).
                resp = await conn.get(most_recent_xkcd())
                data = await resp.json()
                num = data['num']

                # Certain pages don't output anything.
                page = random.randint(1, num)
                if page in (404,):
                    url = most_recent_xkcd()
                else:
                    url = get_xkcd(page)
            elif query.isdigit():
                url = get_xkcd(int(query))
            elif query.lower() in ('mr', 'new', 'newest'):
                url = most_recent_xkcd()
            else:

                def executor():
                    # Fuzzy string match
                    library = XkcdCache(ctx.bot).cached_metadata

                    ln = len(library)
                    titles = {library[i]['title']: library[i]['num']
                              for i in range(0, ln)
                              if get_alphas(library[i]['title'])}

                    best_result = fuzzy.extract_best(
                        query,
                        titles,
                        scoring_algorithm=fuzzy.deep_ratio,
                        min_score=50)

                    return (
                        get_xkcd(titles[best_result[0]])
                        if best_result
                        else None)

                with ctx.typing():
                    url = await self.run_in_io_executor(executor)

            if not url:
                return await ctx.send('Nothing to see here.')
        except FileNotFoundError:
            return await ctx.send('But...where is it?', delete_after=10)
        else:
            # Get the entry
            conn = await self.acquire_http()
            resp = await conn.get(url)

            if resp.status != 200:
                return await ctx.send('xkcd says no.')

            page = await resp.json()

            embed = discord.Embed(
                colour=0xFFFFFF,
                url=f'https://xkcd.com/{page["num"]}',
                title=page['title'],
                description=page['alt'])

            embed.set_author(name='xkcd')
            embed.set_footer(
                text=f'#{page["num"]} - '
                     f'{page["day"]}/{page["month"]}/{page["year"]}')
            # 24th May 2018: Discord seems to be ignoring this.
            # embed.set_image(url=page['img'])
                
            
            async with conn.get(page['img']) as resp, ctx.typing():
                resp.raise_for_status()
                bio = io.BytesIO(await resp.read())
            
            bio.seek(0)                
            await ctx.send(embed=embed, file=discord.File(bio, 'xkcd.png'))

                
def setup(bot):
    if not hasattr(bot, '__xkcd_cacher_thread'):
        XkcdCache(bot)
    bot.add_cog(XkcdCog())
