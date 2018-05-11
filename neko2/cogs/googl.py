#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
goo.gl URL shortener.

Also has a command to generate a "let me google that for you" link

Make an API key here:
https://console.developers.google.com/apis/credentials

See:
https://developers.google.com/url-shortener/v1/getting_started#APIKey

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
import re
import traceback
import urllib.parse

from neko2.shared import configfiles, alg
from neko2.shared import commands
from neko2.shared import errors
from neko2.shared import traits

config_file = 'urlshorten'


# noinspection PyBroadException
class UrlShortenerCog(traits.CogTraits):
    """Shortens URLS"""
    try:
        _key: str = configfiles.get_config_data(config_file)
    except:
        traceback.print_exc()
        _key = None

    def __init__(self, bot):
        self.bot = bot

    @classmethod
    async def googl(cls, url):
        if cls._key is None:
            return None

        conn = await cls.acquire_http()

        res = await conn.post('https://www.googleapis.com/urlshortener/v1/url',
                              params={'key': cls._key},
                              json={'longUrl': url},
                              headers={'content_type': 'application/json'})

        if res.status != 200:
            raise errors.HttpError(res)

        return (await res.json())['id']

    @commands.command(brief='Shortens the given URL', aliases=['goo.gl'])
    async def shorten(self, ctx, url: str, *, optional_description: str=None):
        """
        You can pass a description to put with the link if you like.
        """
        try:
            url = await self.googl(url)
            if url is None:
                await ctx.send('I can\'t connect to goo.gl at the moment.')
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

    async def smoke_a_pipe(self, content, guild_members=None):
        """
        Takes some input string. If the string ends in `| [discord mention]`,
        we return the left hand side of the pipe, and the user, as a
        tuple. Otherwise, we return the input and None as the result.
        """
        guild_members = guild_members or []

        if '|' in content:
            query, _, mention = content.rpartition('|')

            query = query.rstrip()
            mention = mention.strip()

            mention_match = re.match(r'^<@!?(\d+)>$', mention)
            if mention_match:
                mention = int(mention_match.group(1))

            if isinstance(mention, int) or mention.isdigit() :
                user = alg.find(lambda u: u.id == int(mention),
                                guild_members)
            elif mention:
                user = alg.find(
                    lambda u: u.display_name.lower() == mention.lower(),
                    guild_members)
            else:
                user = None
        else:
            query, user = content, None

        return query, user

    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.channel)
    @commands.cooldown(1, 30, commands.BucketType.user)
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
        query, user = await self.smoke_a_pipe(query, ctx.guild.members)

        frag = urllib.parse.urlencode({'q': query})

        if ctx.invoked_with == 'lmgtfyd':
            await ctx.message.delete()

        url = f'http://lmgtfy.com?{frag}'

        try:
            short_url = await self.googl(url)
            url = short_url or url
        except:
            pass

        # noinspection PyUnresolvedReferences
        mention = user.mention + ': ' if user else ''

        await ctx.send(''.join((mention, f'<{url}>')))

    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.channel)
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(
        brief='Outputs a link to a Google search.',
        usage="query [| @mention]",
        examples=['how to buy lime', 'what is a discord.py? | @mention#1234'],
        aliases=['googled'])
    async def google(self, ctx, *, query):
        """
        You can pipe the output to a given member.

        If it is a truly deserving case, use lmgtfy instead for some banter.

        (Call googled to delete your message).
        """
        query, user = await self.smoke_a_pipe(query, ctx.guild.members)

        frag = urllib.parse.urlencode({'q': query})

        if ctx.invoked_with == 'googled':
            await ctx.message.delete()

        url = f'https://google.com/search?{frag}'
        try:
            short_url = await self.googl(url)
            url = short_url or url
        except:
            pass

        # noinspection PyUnresolvedReferences
        mention = user.mention + ': ' if user else ''

        await ctx.send(''.join((mention, f'<{url}>')))


if not getattr(UrlShortenerCog, '_key', None):
    UrlShortenerCog.logger.info('I will attempt to continue without goo.gl '
                                'support.')


def setup(bot):
    bot.add_cog(UrlShortenerCog(bot))
