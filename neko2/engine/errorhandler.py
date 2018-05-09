#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import asyncio  # Async sleep
import logging
import sys
import traceback  # Traceback utils.
import discord  # Embeds
import discord.errors as dpy_errors  # Errors for dpy base.
from discord.ext.commands import Paginator
import discord.ext.commands.errors as dpyext_errors  # Errors for ext.
from neko2.shared import excuses, errors
from . import extrabits


async def _dm_me_error(*, bot, cog, ctx, error, event_method):
    embed = discord.Embed(
        title=f'An error occurred: `{type(error).__qualname__}`',
        description=f'Supplied error message: `{error!s}`',
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
        tb = traceback.format_exception(type(error), error, error.__traceback__)

        if cog:
            rel_log = logging.getLogger(type(cog).__name__)
        else:
            rel_log = self.logger

        rel_log.warning('An error was handled.\n' + ''.join(tb).strip())

        # CommandInvokeErrors tend to wrap other errors. If we have a
        # command invoke error wrapping something else, then get that
        # something else.
        check_failed = isinstance(error, dpyext_errors.CheckFailure)
        too_few_args = isinstance(error, dpyext_errors.MissingRequiredArgument)
        bad_args = isinstance(error, dpyext_errors.BadArgument)
        missing_arg = isinstance(error, dpyext_errors.MissingRequiredArgument)
        no_bot_permission = isinstance(error,
                                       dpyext_errors.BotMissingPermissions)
        no_user_permission = isinstance(error, dpyext_errors.MissingPermissions)
        not_owner = isinstance(error, dpyext_errors.NotOwner)
        not_dms = isinstance(error, dpyext_errors.NoPrivateMessage)
        is_not_found = isinstance(error, dpyext_errors.CommandNotFound)
        on_cool_down = isinstance(error, dpyext_errors.CommandOnCooldown)
        too_many_args = isinstance(error, dpyext_errors.TooManyArguments)
        is_disabled = isinstance(error, dpyext_errors.DisabledCommand)

        if isinstance(error,
                      dpyext_errors.CommandInvokeError) and error.__cause__:
            error = error.__cause__

        is_discord = isinstance(error, dpy_errors.HTTPException)
        is_assert = isinstance(error, AssertionError)
        is_deprecation = isinstance(error, (FutureWarning,
                                            DeprecationWarning,
                                            PendingDeprecationWarning))
        is_unfinished = isinstance(error, NotImplementedError)
        is_warning = isinstance(error, Warning)
        is_command_execution_error = isinstance(error,
                                                errors.CommandExecutionError)

        if is_command_execution_error:
            return await ctx.message.send(f'\N{WARNING SIGN} {error!s}')

        # Don't reply to errors with cool downs. Just add a reaction and stop.
        if on_cool_down:
            assert ctx
            try:
                await ctx.message.add_reaction('\N{STOPWATCH}')
                await asyncio.sleep(5)
                await ctx.message.delete()
            finally:
                return

        # If something was not found, just re-raise.
        if isinstance(error, dpy_errors.NotFound):
            raise error

        # Pick an appropriate emote and heading based on the type of error.
        # If we have an event method parameter present, this likely means an
        # event is broken, which means we should notify the owner immediately.
        if event_method:
            reply = f'\N{SQUARED SOS} Error in event {event_method!r}'
        elif is_assert:
            reply = f'\N{CROSS MARK} Assertion failed {error}'
        elif is_deprecation:
            reply = f'\N{WASTEBASKET} Deprecation warning: {error}'
        elif is_unfinished:
            reply = '\N{HAMMER AND WRENCH} This feature is not yet finished!'
        elif missing_arg:
            reply = f'\N{SPEECH BALLOON} {error}'
        elif no_bot_permission:
            reply = f'\N{ROBOT FACE} {error}'
        elif no_user_permission:
            return  # Pass silently
            # reply = f'\N{NO ENTRY SIGN} {error}'
        elif not_owner:
            return  # Pass silently
            # reply = f'\N{NO ENTRY SIGN} You must be the bot owner to do this'
        elif not_dms:
            reply = f'\N{NO ENTRY SIGN} You cannot do this in private messages.'
        elif too_few_args or bad_args or too_many_args:
            # Pick the right adjective.
            if too_many_args:
                adj = 'Too many'
            elif too_few_args:
                adj = 'Too few'
            else:  # elif bad_args:
                adj = 'Bad'
            reply = f'\N{SPEECH BALLOON} {adj} arguments'

            reply += f': {error!s}'

            if ctx is not None:
                reply += f'\nCommand signature: `{ctx.command.signature}`'
        elif is_disabled:
            reply = '\N{NO ENTRY SIGN} This command is disabled globally'
        elif is_not_found:
            return  # Pass silently.
            # reply = f'\N{LEFT-POINTING MAGNIFYING GLASS} {error}'
        elif check_failed:
            reply = '\N{NO ENTRY SIGN} You cannot do that here'
        elif is_discord:
            reply = f'\N{RAISED BACK OF HAND} Discord said: `{error}`'
        elif is_warning:
            reply = ('\N{WARNING SIGN} '
                     + str(error) if str(error) else type(error).__name__)
        else:
            reply = '\N{SQUARED SOS} Something serious went wrong... '
            reply += excuses.get_excuse()

            if bot.debug:
                reply += '\n\nThe following is included while debug mode is ' \
                         'on\n\n '
                reply += ''.join(traceback.format_exception(
                    type(error), error, error.__traceback__))

            if self.should_dm_on_error:
                reply = f'{reply}\n\nEspy has been sent a DM about this issue.'
                # DM me some information about what went wrong.
                await _dm_me_error(bot=bot, ctx=ctx, cog=cog, error=error,
                                   event_method=event_method)

        destination = ctx if ctx else bot.get_owner()

        # Since I take some raw input from errors, this is just a safeguard
        # to ensure messages are never too long. If an error message is
        # anywhere near this size, then it is a stupid error anyway.

        # Clear after 15 seconds and destroy the invoking message also.
        async def fut(reply):
            resp = await destination.send(reply[:2000])

            if not bot.debug:
                # Delete after 5 minutes.
                await asyncio.sleep(300)

                futs = [resp.delete()]
                if ctx:
                    futs.append(ctx.message.delete())

                try:
                    await asyncio.gather(*futs)
                except:
                    pass

        bot.loop.create_task(fut(reply))

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
