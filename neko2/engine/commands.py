#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Provides some bits and pieces that are overridden from the default command
definitions provided by Discord.py.

This has been altered so that command errors are not dispatched from here
anymore. Instead, they are to be dispatched by the client.
"""
import typing  # Type checking

import asyncio
import cached_property  # Caching properties
import discord  # Message type.

from discord.ext import commands as discord_commands
# noinspection PyUnresolvedReferences
from discord.ext.commands.context import Context
# noinspection PyUnresolvedReferences
from discord.ext.commands.core import *
# noinspection PyUnresolvedReferences
from discord.ext.commands.converter import *
# noinspection PyUnresolvedReferences
from discord.ext.commands.cooldowns import *
# noinspection PyUnresolvedReferences
from discord.ext.commands.errors import *

BaseCommand = discord_commands.Command
BaseGroup = discord_commands.Group
BaseGroupMixin = discord_commands.GroupMixin


class CommandMixin:
    """
    Basic command implementation override.
    """
    name: property
    aliases: property
    full_parent_name: property
    qualified_name: property
    usage: property
    clean_params: property
    examples: list

    def __init__(self, *args, **kwargs):
        self.examples = kwargs.pop('examples', [])

    @cached_property.cached_property
    def names(self) -> typing.FrozenSet[str]:
        """Gets all command names."""
        return frozenset({self.name, *self.aliases})

    @cached_property.cached_property
    def qualified_aliases(self) -> typing.FrozenSet[str]:
        """Gets all qualified aliases."""
        parent_fqcn = self.full_parent_name
        if parent_fqcn:
            parent_fqcn += ' '
        return frozenset({parent_fqcn + alias for alias in self.aliases})

    @cached_property.cached_property
    def qualified_names(self) -> typing.FrozenSet[str]:
        """Gets all qualified names."""
        return frozenset({self.qualified_name, *self.qualified_aliases})


class Command(discord_commands.Command, CommandMixin):
    """Neko command: tweaks some stuff Discord.py provides."""

    def __init__(self, *args, **kwargs):
        discord_commands.Command.__init__(self, *args, **kwargs)
        CommandMixin.__init__(self, *args, **kwargs)


class Group(discord_commands.Group, CommandMixin):
    """Neko command group: tweaks some stuff Discord.py provides."""

    def __init__(self, *args, **kwargs):
        discord_commands.Group.__init__(self, *args, **kwargs)
        CommandMixin.__init__(self, *args, **kwargs)


def command(**kwargs):
    """Decorator for a command."""
    # Ensure the class is set correctly.
    cls = kwargs.pop('cls', Command)
    kwargs['cls'] = cls
    return discord_commands.command(**kwargs)


def group(**kwargs):
    """Decorator for a command group."""
    # Ensure the class is set correctly.
    cls = kwargs.pop('cls', Group)
    kwargs['cls'] = cls
    return discord_commands.command(**kwargs)


def acknowledge(ctx: Context,
                *,
                emoji: str = '\N{OK HAND SIGN}',
                timeout: float = 15) -> None:
    """
    Acknowledges the message in the given context. This tries to add a reaction
    and if this is not possible, it replies with a message holding the emoji
    instead.

    If anything doesn't work, this is dealt with silently. No errors should
    propagate out of this method.

    :param ctx: the context to acknowledge.
    :param emoji: emoji to use. This defaults to OK HAND SIGN
    :param timeout: how long to wait before destroying messages, or None if they
            should not be destroyed. Defaults to 15 seconds.
    """

    async def fut():
        messages = [ctx.message]

        try:
            await ctx.message.add_reaction(emoji)
        except:
            try:
                messages.append(await ctx.send(emoji))
            except:
                pass
        finally:
            if timeout is not None:
                await asyncio.sleep(timeout)
                for message in messages:
                    try:
                        await message.delete()
                    except:
                        pass

    asyncio.ensure_future(fut())


class StatusMessage:
    """
    Wraps around a message to enable using it as a status message by using
    a unified function call
    """
    __slots__ = ('invoked_by', 'message_to_edit')

    def __init__(self, invoked_by: typing.Union[discord.Message, Context]):
        if isinstance(invoked_by, Context):
            invoked_by = invoked_by.message

        self.invoked_by = invoked_by
        self.message_to_edit = None

    async def set_message(self, message):
        if self.message_to_edit is None:
            self.message_to_edit = await self.invoked_by.channel.send(message)
        else:
            try:
                await self.message_to_edit.edit(content=message)
            except discord.NotFound:
                # Resend
                self.message_to_edit = None
                await self.set_message(message)

    @property
    def current_content(self) -> str:
        return self.message_to_edit.content if self.message_to_edit else ''

    @property
    def current_embed(self) -> typing.Optional[discord.Embed]:
        return self.message_to_edit.embed if self.message_to_edit else None

    async def delete(self):
        if self.message_to_edit:
            await self.message_to_edit.delete()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        await self.delete()


async def try_delete(message: typing.Union[Context, discord.Message]):
    """
    Attempts to delete a given message. If we cannot, then we just
    return False, rather than raising an error. If we can delete it, we
    return True.
    """
    try:
        if isinstance(message, Context):
            message = message.message

        await message.delete()
        return True
    except:
        return False


async def wait_for_edit(*,
                        ctx: Context,
                        msg: typing.Optional[discord.Message]=None,
                        timeout: float):
    """
    Listens for the on_message_edit event for a given period of time, before
    returning. If nothing happens and the timeout is hit, we return quietly.
    If we detect a message edit from the author with the same invoking
    command prefix, and a valid alias of the invoking command, we attempt to
    delete the original response, and then reinvoke the command. This allows
    reactive editing to alter a command's output.

    :param ctx: the calling context.
    :param msg: the response message to delete. Set to None if you do not wish
            to delete the response.
    :param timeout: the timeout to wait for before giving up.
    """

    def predicate(_before: discord.Message,
                  _after: discord.Message) -> bool:
        if _after.id != ctx.message.id:
            return False
        elif not _after.content.startswith(ctx.prefix):
            return False
        else:
            _content = _after.content[len(ctx.prefix):].lstrip()

            return any(_content.startswith(a)
                       for a in ctx.command.qualified_names)

    try:
        _, after = await ctx.bot.wait_for('message_edit',
                                          check=predicate,
                                          timeout=timeout)
        new_ctx = await ctx.bot.get_context(after)

        if msg is not None:
            await try_delete(msg)

        # If we reach here, we are reinvoking. If we have a message to
        # delete, try to do that.
        await ctx.command.reinvoke(new_ctx)
        # Force a 5 second timeout.
        await asyncio.sleep(5)

        # Invoke asynchronously to allow the original caller to return.
    except asyncio.TimeoutError:
        # We timed out, so stop listening.
        return
