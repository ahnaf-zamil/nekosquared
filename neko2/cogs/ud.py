#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Urban Dictionary support.
"""
import discord

from neko2.engine import commands
from neko2.shared import fsa
from neko2.shared import traits


urban_random = 'http://api.urbandictionary.com/v0/random'
urban_search = 'http://api.urbandictionary.com/v0/define'


class UrbanDictionaryCog(traits.HttpPool):
    """Urban dictionary cog."""
    @staticmethod
    def _format_urban_defn(definition: dict) -> discord.Embed:
        """
        Takes an UrbanDictionary word response and formats an embed
        to represent the output, before returning it.
        """

        # Adds ellipses to the end and truncates if a string is too long.
        def dots(string, limit=1024):
            return string if len(string) < limit else string[:limit-3] + '...'

        title = definition['word'].title()
        defn = dots(definition['definition'], 2000)

        # Remove embedded URLS to stop Discord following them.
        defn = defn.replace('https://', '').replace('http://', '')
        # [] signify bold phrases
        defn = defn.replace('[', '**').replace(']', '**')

        # Sanitise backticks and place in a code block if applicable.
        example = dots(definition['example'].replace('`', '’'))
        if example:
            example = f'`{example}`'

        author = definition['author']
        yes = definition['thumbs_up']
        no = definition['thumbs_down']
        permalink = definition['permalink']

        embed = discord.Embed(
            title=title,
            description=defn,
            colour=0xFFFF00,
            url=permalink)

        embed.set_author(
            name=f'{author} (\N{HEAVY BLACK HEART} {yes} \N{PILE OF POO} {no})')

        if example:
            embed.add_field(name='Example', value=example)

        if 'tags' in definition and definition['tags']:
            tags = ', '.join(sorted({*definition['tags']}))
            embed.set_footer(text=tags)
        return embed

    @commands.command(
        brief='Looks up a definition on Urban Dictionary',
        examples=['java', ''], aliases=['ud'])
    async def urban(self, ctx, *, phrase: str=None):
        """If no phrase is given, we pick some random ones to show."""
        conn = await self.acquire_http()

        with ctx.typing():
            # Get the response
            if phrase:
                resp = await conn.get(urban_search, params={'term': phrase})
            else:
                resp = await conn.get(urban_random)

            # Decode the JSON.
            resp = (await resp.json())['list']

        if len(resp) == 0:
            return await ctx.send('No results. You sure that is a thing?',
                                  delete_after=15)

        embeds = [self._format_urban_defn(word) for word in resp]

        # If we have more than one result, make a FSM from the pages.
        if len(embeds) == 1:
            await ctx.send(embed=embeds[0])
        else:
            await fsa.FocusedPagEmbed.from_embeds(
                embeds, bot=ctx.bot, invoked_by=ctx, timeout=120).run()

def setup(bot):
    bot.add_cog(UrbanDictionaryCog())
