#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Listens to messages on all channels, and tests if any substrings can be found
that appear to be units of measurement.

A reaction is then added to the corresponding message for a given period of
time. Interacting with it will trigger the main layer of logic in this
extension.

On a positive hit, we convert those into an SI representation and then back to
every commonly used possibility.
"""
import asyncio
import traceback

import collections
import discord

from neko2.shared import traits, other

from . import parser, lex, conversions, models


# Wait 30 minutes.
TIME_TO_WAIT = 30 * 60
REACTION = '\N{STRAIGHT RULER}'


class UnitCog(traits.CogTraits):
    def __init__(self, bot):
        self.bot = bot

    checks = (
        # Do not respond to bots
        lambda m: not m.author.bot,
        # Do not respond to code blocks
        lambda m: '```' not in m.content,
        # Do not respond to DMs.
        lambda m: bool(m.guild)
    )

    async def on_message(self, message):
        """Delegates the incoming message parsing to a thread-pool worker."""
        if not all(c(message) for c in self.checks):
            return
        else:
            e = await self.run_in_io_executor(self.bot,
                                              self.worker,
                                              self.bot.loop,
                                              message)

            if e:
                await self.await_result_request(message, e)

    def worker(self, loop: asyncio.BaseEventLoop, message):
        """Calculates all conversions on a separate thread."""
        # Parse potential matches by pattern matching.
        tokens = list(lex.tokenize(message.content))

        if not tokens:
            return

        # Parse real unit measurements that we can convert.
        quantities = list(parser.parse(*tokens))

        if not quantities:
            return

        # Get any conversions
        equivalents = collections.OrderedDict()

        for quantity in quantities:
            compatible = conversions.get_compatible_models(
                quantity.unit, ignore_self=True)

            # Convert to SI first.
            si = quantity.unit.to_si(quantity.value)

            this_equivalents = tuple(
                models.ValueModel(c.from_si(si), c)
                for c in compatible)

            equivalents[quantity] = this_equivalents

        embed = discord.Embed(colour=other.rand_colour())

        mass_msg_added = False

        for original, equivalents in list(equivalents.items())[:20]:
            equiv_str = []
            for equivalent in equivalents:
                equivalent = models.pretty_print(
                    equivalent.value,
                    equivalent.name,
                    use_long_suffix=True,
                    use_std_form=not original.unit.never_use_std_form,
                    none_if_rounds_to_zero=True)
                equiv_str.append(equivalent)

            equiv_str = list(filter(bool, equiv_str))

            if not equiv_str:
                continue

            embed.add_field(
                name=models.pretty_print(
                    original.value,
                    original.name,
                    use_long_suffix=True,
                    use_std_form=not original.unit.never_use_std_form,
                    none_if_rounds_to_zero=False),
                value='\n'.join(equiv_str))

            if original.unit.unit_type == models.UnitCategoryModel.FORCE_MASS:
                if not mass_msg_added:
                    mass_msg_added = True
                    embed.set_footer(
                        text='This example assumes that mass measurements are '
                             'accelerating at 1G. Likewise, acceleration '
                             'assumes that it applies to 1kg mass.')

        if not len(embed.fields):
            del embed
            return

        return embed

    async def await_result_request(self, original_message, embed):
        try:
            # Run asynchronously to be more responsive.
            asyncio.ensure_future(
                original_message.add_reaction(REACTION))

            def predicate(reaction, user):
                c1 = reaction.message.id == original_message.id
                c2 = reaction.emoji == REACTION
                c3 = not user.bot

                return all((c1, c2, c3))

            _, user = await self.bot.wait_for('reaction_add',
                                              check=predicate,
                                              timeout=TIME_TO_WAIT)

            m = await original_message.channel.get_message(original_message.id)

            for reaction in m.reactions:
                if reaction.emoji == REACTION:
                    async for r_user in reaction.users():
                        if r_user == self.bot.user or r_user == user:
                            await m.remove_reaction(reaction.emoji, r_user)

            await original_message.channel.send(embed=embed)
        except asyncio.TimeoutError:
            pass
        except BaseException:
            traceback.print_exc()
