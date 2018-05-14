#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Handles incoming errors safely.

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
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.*giggl
"""
import asyncio  # Async sleep
import logging
import sys
import traceback  # Traceback utils.

import discord  # Embeds
from discord.ext.commands import Paginator
import discord.ext.commands.errors as dpyext_errors  # Errors for ext.

from neko2.shared import excuses, morefunctools, string
from . import extrabits

# Respond with a reaction.
ignored_errors = {
    dpyext_errors.CommandNotFound: '\N{BLACK QUESTION MARK ORNAMENT}',
    dpyext_errors.DisabledCommand: '\N{NO ENTRY SIGN}',
    dpyext_errors.CommandOnCooldown: '\N{SNOWFLAKE}',
    NotImplementedError: '\N{CONSTRUCTION SIGN}'
}

handled_errors = {
    dpyext_errors.CheckFailure,
    dpyext_errors.NotOwner,
    dpyext_errors.MissingRequiredArgument,
    dpyext_errors.BadArgument,
    dpyext_errors.BotMissingPermissions,
    dpyext_errors.MissingPermissions,
    dpyext_errors.NoPrivateMessage,
    dpyext_errors.TooManyArguments,
}


@morefunctools.always_background()
async def _react_for_a_little_while(me, message, reaction, time=5):
    try:
        await message.add_reaction(reaction)
        await asyncio.sleep(time)
        await message.remove_reaction(reaction, me)
    except:
        pass


async def _dm_me_error(*, bot, cog, ctx, error, event_method):
    embed = discord.Embed(
        title=f'An error occurred: `{type(error).__qualname__}`',
        description=f'Supplied error message: `{error or "—"}`',
        colour=0xFF0000)

    trace = traceback.format_tb(error.__traceback__)
    trace = ''.join(trace)
    should_pag = len(trace) > 1010

    if not should_pag:
        trace = f'```\n{trace}\n```'
        embed.add_field(name='Traceback', value=trace, inline=False)

    if ctx:
        whom_info = (
            f'{ctx.command.qualified_name} invoked as {ctx.invoked_with}\n'
            f'Invoked by: {ctx.author} (`{ctx.author.id}`)\n'
            f'{"Guild: " + str(ctx.guild) if ctx.guild else "in DMs"}\n'
            f'Channel: #{ctx.channel}\n'
            f'When: {ctx.message.created_at}')
        body = ctx.message.content
        body = body.replace('`', '’')
        if len(body) > 1000:
            body = f'{body[:997]}...'
        body = f'```\n{body}\n```'
        embed.add_field(name='Command info', value=whom_info)
        embed.add_field(name='Command body', value=body)
    if cog:
        embed.add_field(name='Cog', value=str(cog))
    if event_method:
        embed.add_field(name='Event method', value=str(event_method))

    owner = bot.get_user(bot.owner_id)
    await owner.send(embed=embed)

    if should_pag:
        p = Paginator()
        for line in trace.split('\n'):
            p.add_line(line)
        for page in p.pages:
            # Send the last 15 only. Prevents a hell of a lot
            # of spam if the bot hits a stack overflow.
            await owner.send(page[-15:])


class ErrorHandler(extrabits.InternalCogType):
    def __init__(self, should_dm_on_error, bot):
        super().__init__(bot)
        self.should_dm_on_error = should_dm_on_error

    async def handle_error(self, *, bot, cog=None, ctx=None, error,
                           event_method=None):
        """Send your errors here to be handled properly."""
        # Discard any errors as a result of handling this error.
        try:
            await self.__handle_error(
                bot=bot,
                cog=cog,
                ctx=ctx,
                error=error,
                event_method=event_method)

        except BaseException as ex:
            ex.__cause__ = error
            traceback.print_exception(type(ex), ex, ex.__traceback__)

    async def __handle_error(self, *, bot, cog=None, ctx=None, error,
                             event_method=None):
        # Print the traceback first. This means I still see the TB even if
        # something else breaks when outputting results to discord.
        tb = traceback.format_exception(
            type(error), error, error.__traceback__)

        if cog:
            rel_log = logging.getLogger(type(cog).__name__)
        else:
            rel_log = self.logger

        rel_log.warning('An error was handled.\n' + ''.join(tb).strip())

        cause = error.__cause__ or error

        # Don't reply to errors with cool downs. Just add a reaction and stop.
        if type(cause) in handled_errors:
            reply = string.cap(str(cause))
        elif type(cause) in ignored_errors:
            return _react_for_a_little_while(ctx.bot.user,
                                             ctx.message,
                                             ignored_errors[type(cause)])
        else:
            reply = '\N{SQUARED SOS} Something serious went wrong... '
            reply += excuses.get_excuse()

            if bot.debug:
                reply += (
                    '\n\nThe following is included while debug mode is '
                    'on. As a result, I won\'t bother DMing '
                    f'<@{ctx.bot.owner_id}> about it.\n\n ')
                reply += ''.join(traceback.format_exception(
                    type(cause), cause, cause.__traceback__))

            if self.should_dm_on_error and not bot.debug:
                reply += '\n\nEspy has been sent a DM about this issue.'
                # DM me some information about what went wrong.
                await _dm_me_error(bot=bot, ctx=ctx, cog=cog, error=cause,
                                   event_method=event_method)

        destination = ctx if ctx else bot.get_owner()

        # Since I take some raw input from errors, this is just a safeguard
        # to ensure messages are never too long. If an error message is
        # anywhere near this size, then it is a stupid error anyway.

        # Clear after 15 seconds and destroy the invoking message also.
        @morefunctools.always_background()
        async def fut(reply):
            resp = await destination.send(string.trunc(reply))

            if not bot.debug:
                # Delete after 30s.
                await asyncio.sleep(30)

                futs = [resp.delete()]
                if ctx:
                    futs.append(ctx.message.delete())

                try:
                    await asyncio.gather(*futs)
                except:
                    pass

        fut(reply)

    async def on_command_error(self, context, exception):
        """
        Handles invoking command error handlers.
        """
        # noinspection PyBroadException
        try:
            await self.handle_error(
                bot=self.bot, ctx=context, error=exception)
        except BaseException:
            traceback.print_exc()

    async def on_error(self, event_method, *_unused_args, **_unused_kwargs):
        """
        General error handling mechanism.
        """
        # noinspection PyBroadException
        try:
            _, err, _ = sys.exc_info()
            await self.handle_error(
                bot=self.bot, event_method=event_method, error=err)
        except BaseException:
            traceback.print_exc()
