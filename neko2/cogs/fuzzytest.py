#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import discord

from neko2.engine import commands
from neko2.shared import traits
from neko2.shared.other import excuses
from neko2.shared.other import fuzzy


@traits.disable
class FuzzyTestCog:
    @commands.command()
    async def dev_fuzzy(self, ctx, *, query):
        """Demonstrates various fuzzy string matching algorithms."""
        with ctx.typing():
            partial = fuzzy.extract(
                query,
                excuses.excuses,
                scoring_algorithm=fuzzy.best_partial)

            normal = fuzzy.extract(
                query,
                excuses.excuses,
                scoring_algorithm=fuzzy.ratio)

            quick = fuzzy.extract(
                query,
                excuses.excuses,
                scoring_algorithm=fuzzy.quick_ratio)

            real_quick = fuzzy.extract(
                query,
                excuses.excuses,
                scoring_algorithm=fuzzy.real_quick_ratio)

            deep = fuzzy.extract(
                query,
                excuses.excuses,
                scoring_algorithm=fuzzy.deep_ratio)

        embed = discord.Embed(title=f'Search results for `{query}`')

        def to_s(results):
            results = [f'`{a}` @ {b}' for a, b in results]
            return f'{len(results)} result(s)\n' + '\n'.join(results)

        embed.add_field(name='Best Partial Match', value=to_s(partial))
        embed.add_field(name='Bog-standard ratio', value=to_s(normal))
        embed.add_field(name='Quick ratio', value=to_s(quick))
        embed.add_field(name='Real quick ratio', value=to_s(real_quick))
        embed.add_field(name='Deep ratio', value=to_s(deep))

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(FuzzyTestCog())