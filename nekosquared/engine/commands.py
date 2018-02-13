"""
Provides some bits and pieces that are overridden from the default command
definitions provided by Discord.py.

This has been altered so that command errors are not dispatched from here
anymore. Instead, they are to be dispatched by the client.
"""
import typing

import cached_property
# Used internally.
from discord.ext import commands
# Ensures these modules are in the same namespace.
# noinspection PyUnresolvedReferences
from discord.ext.commands.context import Context
# noinspection PyUnresolvedReferences
from discord.ext.commands.core import *
# noinspection PyUnresolvedReferences
from discord.ext.commands.converter import *
# noinspection PyUnresolvedReferences
from discord.ext.commands.cooldowns import *


class CommandMixin:
    """
    Basic command implementation override.
    """
    name: property
    aliases: property
    full_parent_name: property
    qualified_name: property

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


class Command(commands.Command, CommandMixin):
    pass


class Group(commands.Group, CommandMixin):
    pass


def command(**kwargs):
    """Decorator for a command."""
    # Ensure the class is set correctly.
    cls = kwargs.pop('cls', Command)
    kwargs['cls'] = cls
    return commands.command(**kwargs)


def group(**kwargs):
    """Decorator for a command group."""
    # Ensure the class is set correctly.
    cls = kwargs.pop('cls', Group)
    kwargs['cls'] = cls
    return commands.command(**kwargs)
