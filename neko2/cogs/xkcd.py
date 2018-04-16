#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
xkcd viewer/reference thingy.

Also allows searching for XKCD comic strips by the given
criteria using fuzzy string matching algorithms.
"""
import json
import os
import random
import threading
import time

import discord
import requests

from neko2.shared import classtools
from neko2.shared import commands
from neko2.shared import configfiles
from neko2.shared import fuzzy
from neko2.shared import scribe
from neko2.shared import traits


def most_recent_xkcd():
    return 'https://xkcd.com/info.0.json'


def get_xkcd(num):
    if num == 404 or num == 0:
        raise FileNotFoundError
    return f'https://xkcd.com/{num}/info.0.json'


def get_alphas(string):
    a, z, A, Z = ord('a'), ord('z'), ord('A'), ord('Z')
    return ''.join(c for c in string if a <= ord(c) <= z or A <= ord(c) <= Z)


# 12 hours
SLEEP_FOR = 60 * 60 * 12
CACHE_FILE = os.path.join(configfiles.CONFIG_DIRECTORY, 'xkcd.json')


# Easier to delegate this to an entirely separate thread and make it run
# every so often. Then it cannot interfere with the bot. Also means I don't
# need to use Asyncio.
class XkcdCacher(threading.Thread,
                 scribe.Scribe,
                 metaclass=classtools.SingletonMeta):
    """Sequentially crawls xkcd periodically to gather metadata."""

    def __init__(self, bot):
        setattr(bot, '__xkcd_cacher_thread', self)

        super().__init__(daemon=True)

        # Start self.
        self.start()

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

            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE) as fp:
                    data = json.load(fp)
            else:
                data = []

            # Use a session, obviously.
            with requests.Session() as sesh:
                # Get most recent strip.
                most_recent = sesh.get(most_recent_xkcd()).json()

                for i in range(0, most_recent['num'] + 1):
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
                json.dump(data, fp, indent='  ')

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
        all xkcd titles. This may take a few seconds to complete, so be patient.
        """
        try:
            if not query:
                # Get the most recent comic first and inspect the entry number
                # (our cache can be up to 12 hours out of date).
                conn = await self.acquire_http(ctx.bot)

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
                # Fuzzy string match
                if os.path.exists(CACHE_FILE):

                    try:
                        fp = await self.file(CACHE_FILE)
                        library = json.loads(await fp.read())

                    finally:
                        # noinspection PyUnboundLocalVariable
                        fp.close()
                else:
                    return await ctx.send('Still getting ready. Try later.')

                def executor():
                    # Todo: optimise the shit out of this crap.
                    ln = len(library)
                    titles = {library[i]['title']: library[i]['num']
                              for i in range(0, ln)
                              if get_alphas(library[i]['title'])}

                    best_result = fuzzy.extract_best(
                        query,
                        titles,
                        # TODO: test out best_partial and ratio algorithms...
                        # ... they will be twice as fast as this.
                        scoring_algorithm=fuzzy.deep_ratio,
                        min_score=50)

                    return (
                        get_xkcd(titles[best_result[0]])
                        if best_result
                        else None)

                with ctx.typing():
                    url = await self.run_in_io_executor(ctx.bot, executor)

            if not url:
                return await ctx.send('Nothing to see here.')
        except FileNotFoundError:
            return await ctx.send('But...where is it?', delete_after=10)
        else:
            # Get the entry
            conn = await self.acquire_http(ctx.bot)
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
            embed.set_image(url=page['img'])

            await ctx.send(embed=embed)


def setup(bot):
    if not hasattr(bot, '__xkcd_cacher_thread'):
        XkcdCacher(bot)
    bot.add_cog(XkcdCog())
