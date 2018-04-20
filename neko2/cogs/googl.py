#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
goo.gl URL shortener.

Also has a command to generate a "let me google that for you" link

Make an API key here:
https://console.developers.google.com/apis/credentials

See:
https://developers.google.com/url-shortener/v1/getting_started#APIKey
"""
import re
import traceback
import urllib.parse

from neko2.shared import configfiles, commands
from neko2.shared import errors
from neko2.shared import traits

config_file = 'urlshorten'



class UrlShortenerCog(traits.CogTraits):
    """Shortens URLS"""
    def __init__(self):
        self._key: str = configfiles.get_config_data(config_file)

    async def _shorten(self, url, bot):
        conn = await self.acquire_http(bot)

        res = await conn.post('https://www.googleapis.com/urlshortener/v1/url',
                              params={'key': self._key},
                              json={'longUrl': url},
                              headers={'content_type': 'application/json'})

        if res.status != 200:
            raise errors.HttpError(res)

        return (await res.json())['id']

    @commands.command(brief='Shortens the given URL')
    async def shorten(self, ctx, url: str, *, optional_description: str=None):
        """
        You can pass a description to put with the link if you like.
        """
        try:
            url = await self._shorten(url, ctx.bot)
        except BaseException:
            traceback.print_exc()
            await ctx.send('There was an error handling this request.')
        else:
            if not optional_description:
                optional_description = 'shortened a URL'

            # Try to delete the initial message
            await commands.try_delete(ctx)
            return await ctx.send(
                f'{ctx.author.mention} {optional_description}: '
                f'{url}')

    @commands.command(
        brief="Directs stupid questions to their rightful place.",
        usage="query [| @mention]",
        examples=['how to buy lime', 'what is a discord.py? | @mention#1234'],
        aliases=['lmgtfyd'])
    async def lmgtfy(self, ctx, *, query):
        """
        Garbage question = garbage answer.
        Call `lmgtfyd` to destroy your initial message.

        You can "pipe" the output to a given member. This will mention them
        in the response.
        """
        if '|' in query:
            query, _, mention = query.rpartition('|')

            mention = mention.strip()

            if not re.match(r'^<!?@\d+>$', mention):
                mention = ''
            else:
                query, mention = query.rstrip(), mention + ': '
        else:
            mention = ''

        frag = urllib.parse.urlencode({'q': query})

        if ctx.invoked_with == 'lmgtfyd':
            await ctx.message.delete()

        url = f'http://lmgtfy.com?{frag}'
        url = await self._shorten(url, ctx.bot)

        await ctx.send(''.join((mention, f'<{url}>')))


def setup(bot):
    bot.add_cog(UrlShortenerCog())
