#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
goo.gl URL shortener.

Make an API key here:
https://console.developers.google.com/apis/credentials

See:
https://developers.google.com/url-shortener/v1/getting_started#APIKey
"""
import aiohttp

from neko2.engine import commands
from neko2.shared import configfiles
from neko2.shared import errors
from neko2.shared import traits

config_file = 'neko2.cogs.urlshorten.key'


class UrlShortenerCog(traits.HttpPool):
    """Shortens URLS"""
    def __init__(self):
        self._key: str = configfiles.get_config_data(config_file)

    @commands.command(brief='Shortens the given URL')
    async def shorten(self, ctx, url: str, *, optional_description: str=None):
        """
        You can pass a description to put with the link if you like.
        """
        conn = await self.acquire_http()

        res = await conn.post('https://www.googleapis.com/urlshortener/v1/url',
                              params={'key': self._key},
                              json={'longUrl': url},
                              headers={'content_type': 'application/json'})

        if not optional_description:
            optional_description = 'shortened a URL'

        if res.status != 200:
            raise errors.HttpError(res)
        try:
            data = await res.json()
        except aiohttp.ClientResponseError:
            return await ctx.send('Bad request.', delete_after=10)
        try:

            if 'error' in data:
                first_error = data['error']['errors'][0]
                message = first_error['message']
                location_type = message['locationType']
                location = message['location'].replace('.', ' ')

                err_msg = f'{message} {location_type} for {location}.'
                await ctx.send(err_msg, delete_after=10)
            else:
                # Try to delete the initial message
                await commands.try_delete(ctx)
                return await ctx.send(
                    f'{ctx.author.mention} {optional_description}: '
                    f'{data["id"]}')

        except Exception as ex:
            raise RuntimeError(str(ex) + ': ' + res.reason)


def setup(bot):
    bot.add_cog(UrlShortenerCog())
