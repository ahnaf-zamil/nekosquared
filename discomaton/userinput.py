#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
A very primitive option picker that shows an unlimited number of results, and
uses the booklet implementation behind the scenes to format the options to the
user in a format that is understandable and moderately concise.

This is still new and not tested thoroughly, so if you are going to use it,
be aware that it may still misbehave.
"""
import asyncio
import typing

import async_timeout
import discord
from discord.ext import commands

from .util import helpers
from .book import AbstractBooklet, default_formatter
from .factories import bookbinding


__all__ = ('option_picker_formatter', 'ResultPickedInterrupt',
           'ClosedInterrupt', 'option_picker', 'get_user_input')


def option_picker_formatter(booklet: AbstractBooklet) -> str:
    string = default_formatter(booklet)
    return f'{string}\n**Please reply with an option:**'


class ResultPickedInterrupt(RuntimeError):
    """Exceptions can interrupt asyncio.gather immediately!"""
    def __init__(self, result):
        self.result = result


class ClosedInterrupt(RuntimeError):
    """Raised if the option picker is closed."""
    pass


async def option_picker(ctx,
                        *options,
                        timeout: float=300,
                        formatter=option_picker_formatter,
                        max_lines: int=6) -> typing.Any:
    """
    Displays a list of options, enabling the user to pick one by
    providing input. If the user closes the pagination of options, we assume
    this to be closing the option picker, and we return None.

    If timeout is reached, we return None.

    :param ctx: the command context, or a tuple of bot, message, and channel
    :param options: the options to show.
    :param timeout: timeout to wait for before killing the prompt.
    :param formatter: the formatter for each page of options.
    :param max_lines: the max lines to show per page.
    """
    if isinstance(ctx, commands.Context):
        bot, message, channel = ctx.bot, ctx.message, ctx.channel
    else:
        bot, message, channel = ctx

    if message.guild is None:
        raise commands.NoPrivateMessage('Option pickers will not work in DMs.')

    binder = bookbinding.StringBookBinder(ctx,
                                          max_lines=max_lines,
                                          timeout=None)

    binder.with_page_number_formatter(formatter)

    for i, option in enumerate(options):
        binder.add_line(f'{i + 1} - {option!s}', dont_alter=True)

    book = binder.build()

    async def run_options_view():
        await book.start()
        raise ClosedInterrupt

    def predicate(response):
        return response.author == message.author and \
               response.channel == message.channel

    async def get_option():
        # Raises a ResultPickedInterrupt when finished.
        user_input = None

        while user_input is None:
            m = await bot.wait_for(
                'message',
                check=predicate,
                timeout=timeout)

            content = m.content

            try:
                option_num = int(content)

                if option_num < 1 or option_num > len(options):
                    raise IndexError
            except IndexError:
                await channel.send('Out of range', delete_after=5)
                continue
            except ValueError:
                await channel.send('Cancelling...', delete_after=5)
                await helpers.attempt_delete(m)
                raise ClosedInterrupt
            else:
                await helpers.attempt_delete(m)

            raise ResultPickedInterrupt(options[option_num - 1])
    try:
        option, _ = await asyncio.gather(
            get_option(),
            run_options_view())
    except ResultPickedInterrupt as result:
        return result.result
    except ClosedInterrupt:
        return None
    except asyncio.TimeoutError:
        return None
    except discord.Forbidden as ex:
        raise ex from None
    finally:
        try:
            if book.is_running():
                await book.delete()
                await book.__aexit__(None, None, None)
        except:
            pass


def from_user(user):
    """
    Generates a predicate for a message validator that only returns
    true if the given user sent the message.
    """
    def predicate(msg):
        return msg.author == user
    return predicate


async def get_user_input(ctx: typing.Union[
                            commands.Context,
                            typing.Tuple[discord.TextChannel, discord.Client]
                         ],
                         only_if: typing.Callable[
                             [discord.Message], bool
                         ]=lambda _: True,
                         timeout=300) -> discord.Message:
    """
    Awaits user input.
    :param ctx: the context to associate with. This is either a commands.Context
        object, or a tuple of the channel and the discord client object.
    :param only_if: a predicate to use to determine whether to accept the
        given message event or not. Defaults to a predicate that returns True
        regardless.
    :param timeout: timeout to wait for. This is not reset each time a new
        event comes through.
    :return: the accepted message.
    """
    if isinstance(ctx, commands.Context):
        channel, client = ctx.channel, ctx.bot
    else:
        channel, client = ctx[0], ctx[1]

    with async_timeout.timeout(timeout=timeout):
        return await client.wait_for('message',
                                     check=only_if)
