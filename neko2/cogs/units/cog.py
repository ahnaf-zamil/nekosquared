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
            await self.run_in_io_executor(self.bot,
                                          self.worker,
                                          self.bot.loop,
                                          message)

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

        # Create a task to show and wait on the original message for a reaction
        # to be interacted with to display the measurement in chat. This way
        # we won't spam chat like the old version did. This passes control
        # back to the asyncio thread.
        loop.create_task(self.await_result_request(message, equivalents))

    async def await_result_request(self, original_message, conversions: dict):
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

            embed = discord.Embed(colour=other.rand_colour())

            for original, equivalents in list(conversions.items())[:20]:
                embed.add_field(name=str(original),
                                value='\n'.join(str(e) for e in equivalents))

            await original_message.channel.send(embed=embed)
        except asyncio.TimeoutError:
            pass
        except BaseException as ex:
            self.logger.warning(traceback.format_exception_only(type(ex), ex))
