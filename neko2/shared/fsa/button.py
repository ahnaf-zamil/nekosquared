#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
(c) Espeonageon 2018.
Licensed under the Mozilla Public License V2.0

You can use this however you like under the MPLv2.0 license, but you must
make sure to keep this message here.

Button implementation.
"""

import typing

import discord

from neko2.shared.fsa import abstractmachines


__all__ = ('Button', 'as_button')


class Button:
    """
    Clickable button implemented as a reaction.

    This wraps a co-routine with signature:
        (self, automaton, user)

    :param callback: the callback to perform on button click. Whether this is
        triggered for any user, or just the user that is applicable, is down
        to the implementation of the finite state machine.
    :param name: the optional button identifier.
    :param emoji: either a string, or a custom emoji object.
    """

    def __init__(self,
                 callback,
                 *,
                 emoji: typing.Union[str, discord.PartialEmoji, discord.Emoji],
                 name: str=None):
        if name is None:
            name = callback.__name__

        self.__doc__ = callback.__doc__
        self.callback = callback
        self.emoji = emoji
        self.name = name

    def __hash__(self):
        return hash(self.emoji)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __set_name__(self, owner, name):
        self.name = name

    def __str__(self):
        return self.name if self.name else 'Button'

    def __repr__(self):
        if self.name:
            head = f'<Button name={self.name!r} '
        else:
            head = '<Button '

        return f'{head} emote={self.emoji!r} callback={self.callback}>'

    async def __call__(self,
                       automaton: abstractmachines.FiniteStateAutomaton,
                       user: discord.User):
        return await self.callback(self, automaton, user)

    @classmethod
    def from_coro(cls, emoji: str, name: str=None):
        """
        Decorates a co-routine and returns the Button object it is represented
        by.
        :param emoji: the emote to use for the button.
        :param name: the name of the button (optional).
        """
        def decorator(coro):
            return Button(coro, emoji=emoji, name=name)
        return decorator


as_button = Button.from_coro
