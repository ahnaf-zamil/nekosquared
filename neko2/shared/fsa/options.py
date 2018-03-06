#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
An extension of a paginated state machine that handles option picking.
"""
import typing                   # Type checking
import discord                  # Discord.py
from neko2.shared import fsa    # Other FSA stuff


__all__ = ('OptionPicker', 'FocusedOptionPicker')


class OptionPicker(fsa.AbstractPagFsa):
    """
    Paginator that works as an option picker.

    Takes a dict of options. These are string emoji keys, and tuples of
    string representation and objects values.

    When an option is selected by the invoking user, then that option
    is returned.


    Example options layout.:

    {
        '\\N{OK HAND SIGN}: ('Accept', 1),
        '\\N{THUMB DOWN SIGN}: ('Decline', 0),
    }

    If Accept is picked, then 1 is returned, otherwise 0 is returned.

    """
    def __init__(self, options: typing.Dict[str, typing.Tuple[str, typing.Any]],
                 bot: discord.Client, invoked_by: discord.Message,
                 timeout: float):
        """
        Init the option picker.
        :param options: dict of emojis mapping to tuples of string descriptions
                and object values.
        :param bot: the bot.
        :param invoked_by: who invoked the picker.
        :param timeout: the timeout.
        """

        # Generate buttons from the options
        assert options
        buttons = []

        def make_button_scoped(emoji, option_str, option_obj):
            @fsa.as_button(emoji, option_str)
            async def option_btn(*_):
                await self.clear_buttons()
                return option_obj
            return option_btn

        for emoji, (option_str, option_obj) in options.items():
            buttons.append(make_button_scoped(emoji, option_str, option_obj))

        buttons.append(make_button_scoped(
            '\N{PUT LITTER IN ITS PLACE SYMBOL}', 'Cancel', None
        ))

        self.options = options

        super().__init__(bot, invoked_by, buttons, timeout)

    async def get_page(self):
        """
        Returns a list of options.
        """
        lines = ['Please pick an option:']

        for emoji, (option_str, option_obj) in self.options.items():
            lines.append(f'{emoji} - `{option_str}`')
        return '\n'.join(lines)

    def __len__(self) -> int:
        return 1

    async def run(self) -> typing.Union[typing.Any, None]:
        """Returns the option that was picked, or None if we timed out."""
        return_result = None
        async for result in self:
            return_result = result
            break
        await (await self.get_message()).delete()
        return return_result


class FocusedOptionPicker(OptionPicker, fsa.FocusedPagMixin):
    """Paginated mixin with focus."""
    def __init__(self, options: typing.Dict[str, typing.Tuple[str, typing.Any]],
                 bot: discord.Client, invoked_by: discord.Message,
                 timeout: float, predicate: fsa.predicate_t = None):
        OptionPicker.__init__(self, options, bot, invoked_by, timeout)
        fsa.FocusedPagMixin.__init__(self, predicate=predicate)
