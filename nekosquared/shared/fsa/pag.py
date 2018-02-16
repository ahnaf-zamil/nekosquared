"""
(c) Espeonageon 2018.
Licensed under the Mozilla Public License V2.0

You can use this however you like under the MPLv2.0 license, but you must
make sure to keep this message here.

Adds functionality to the Discord.py paginator to count lines.
"""
import abc
import asyncio
import inspect
import typing

import discord
from discord.ext import commands

from nekosquared.shared.fsa import abstractmachines
from nekosquared.shared.fsa import button


__all__ = (
    'MESSAGE_MAX', 'EMBED_DESCRIPTION_MAX', 'EMBED_FIELD_MAX',
    'Pag', 'LinedPag', 'generate_default_pagination_buttons',
    'AbstractPagFsa', 'PagMessage', 'PagEmbed', 'FocusedPagMessage',
    'FocusedPagEmbed'
)


MESSAGE_MAX = 2000
EMBED_DESCRIPTION_MAX = 2000
EMBED_FIELD_MAX = 1024


class Pag(commands.Paginator):
    """
    I don't usually want stuff in code blocks, so this implementation removes
    that default functionality.
    """
    def __init__(self, prefix='', suffix='', max_size=2000):
        super().__init__(prefix=prefix, suffix=suffix, max_size=max_size)

    def dump_to_embeds(self) -> typing.List[discord.Embed]:
        """Dumps the pages to a series of embed objects which are yielded."""
        if self.max_size > 2000:
            raise ValueError(
                'Embeds cannot have fields greater than 2000 chars.')

        return list(discord.Embed(description=page) for page in self.pages)


class LinedPag(Pag):
    """
    Same as the paginator, but this will allow limits to number of lines
    per page in addition to character count.
    """
    # TODO: perhaps implement code to assert a maximum line length?
    def __init__(self, max_lines=20, **kwargs):
        super().__init__(**kwargs)
        self.max_lines = max_lines

    def add_line(self, line='', *, empty=False):
        lines = line.split('\n')

        def existing():
            return '\n'.join(self._current_page).count('\n')

        while len(lines) > 0:
            ln = lines.pop(0)
            if existing() >= self.max_lines:
                self.close_page()
            super().add_line(ln.rstrip())


def generate_default_pagination_buttons() -> typing.List[button.Button]:
    """Generates a set of default pagination buttons."""
    buttons = []

    def new_btn(*args, **kwargs):
        def decorator(coro):
            b = button.Button.from_coro(*args, **kwargs)(coro)
            buttons.append(b)
            return b

        return decorator

    @new_btn('\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}')
    async def go_to_first_page(_btn, fsa, _user):
        """Jumps to the first page."""
        await fsa.set_index(0)

    @new_btn('\N{BLACK LEFT-POINTING TRIANGLE}')
    async def go_to_previous_page(_btn, fsa, _user):
        """Go back a page."""
        await fsa.offset_index(-1)

    @new_btn('\N{INPUT SYMBOL FOR NUMBERS}')
    async def take_numeric_input_page_number(_btn, _fsa, _user):
        """Take numeric input for a page number."""
        raise NotImplementedError

    @new_btn('\N{BLACK RIGHT-POINTING TRIANGLE}')
    async def go_to_next_page(_btn, fsa, _user):
        """Go forward a page."""
        await fsa.offset_index(+1)

    @new_btn('\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}')
    async def go_to_last_page(_btn, fsa, _user):
        """Jumps to the last page."""
        await fsa.set_index(-1)

    @new_btn('\N{INFORMATION SOURCE}')
    async def show_help_prompt(btn, fsa, _user):
        """Shows this message."""
        if not hasattr(btn, 'has_shown_help'):
            msg = await fsa.get_message()

            strings = ['**Pagination help**']
            for b in fsa.buttons:
                doc = inspect.getdoc(b)
                if doc:
                    doc = inspect.cleandoc(doc)
                else:
                    doc = b.name.replace('_', ' ').title()
                string = f'{b.emoji} - {doc}'
                strings.append(string)
            help_msg = await msg.channel.send('\n'.join(strings))
            setattr(btn, 'has_shown_help', True)
            # noinspection PyProtectedMember
            fsa._buttons.pop(btn.emoji)

            async def callback():
                await asyncio.sleep(30)
                try:
                    await help_msg.delete()
                finally:
                    return

            # Don't block.
            asyncio.ensure_future(callback())

    @new_btn('\N{SQUARED OK}')
    async def remove_buttons(_btn, fsa, _user):
        """Closes the pagination and keeps the current message."""
        fsa.stop()

    @new_btn('\N{PUT LITTER IN ITS PLACE SYMBOL}')
    async def delete_pagination(_btn, fsa, _user):
        """Closes the pagination and deletes the current message."""
        message = await fsa.get_message()

        await asyncio.gather(
            fsa.invoked_by.delete(),
            message.delete()
        )

        fsa.stop()

    return buttons


# Alias for predicate type, as it is rather verbose for my liking.
_self_predicate_t = typing.Callable[
    [typing.Any, discord.Reaction, discord.User], bool
]

_noself_predicate_t = typing.Callable[
    [discord.Reaction, discord.User], bool
]

predicate_t = typing.Union[_self_predicate_t, _noself_predicate_t]


def is_not_bot_and_valid_button(self, reaction, user):
    """
    Predicate to ensure the user is not our bot, and the reaction is an
    existing button.
    """
    return user != self.bot.user and reaction.emoji in self._buttons


def allow_author_only(self, reaction, user):
    """
    Predicate to ensure the user was the original author only.
    """
    if is_not_bot_and_valid_button(self, reaction, user):
        return self.user == self.invoked_by.author
    else:
        return False


def allow_author_and_owner(self, reaction, user):
    """
    Same as ``allow_author_only`` but this also makes an exception in the rule
    for the bot owner.
    """
    if is_not_bot_and_valid_button(self, reaction, user):
        return user.id in (self.bot.owner_id, self.bot.user.id)
    else:
        return False


# If you hate the default predicate, then go replace these in your code or
# something, idk. These MUST point to methods that have the specific signature
# of (self, reaction, user) -> bool. If you use anything else, all my stuff will
# break and you will be made to wear a dunce hat for three days. I will
# mockingly laugh at you in your face for your blatant disregard to my kind and
# wordy comments. And remember. I know who you are. I know where you live, and
# you cannot ride your bike there.
default_predicate = is_not_bot_and_valid_button
default_focused_predicate = allow_author_and_owner


class AbstractPagFsa(abstractmachines.FiniteStateAutomaton, abc.ABC):
    """
    Implementation of a paginated system. This is an abstract implementation,
    and leaves several members open to be defined in concrete implementations
    as appropriate.

    :param bot: the bot instance to associate with.
    :param invoked_by: the original message that invoked this state machine.
    :param buttons: collection of button reactions to add.
    :param timeout: the timeout to wait for, before closing the state machine.
    """
    def __init__(self,
                 bot: discord.Client,
                 invoked_by: discord.Message,
                 buttons: typing.Iterable[button.Button],
                 timeout: float):
        """Init the paginated state machine."""
        super().__init__(bot, invoked_by)
        self._index = 0
        self._reply_message: discord.Message = None
        self._buttons = {b.emoji: b for b in buttons}
        self.timeout = timeout

    @property
    def buttons(self):
        """Gets the buttons."""
        return tuple(self._buttons.values())

    @abc.abstractmethod
    def __len__(self) -> int:
        """Should return the number of pages available."""
        pass

    @property
    def index(self):
        """Gets the page index. This is a read-only property."""
        return self._index

    async def get_message(self):
        """
        Gets the message we are using to display content. If this does not
        yet exist, then we will send one first.
        """
        if self._reply_message is None:
            msg = await self.invoked_by.channel.send('\N{HOURGLASS}')
            self._reply_message = msg

        return self._reply_message

    async def offset_index(self, offset: int):
        """Offsets the index by the given offset."""
        index = self.index + offset
        await self.set_index(index)

    async def set_index(self, index: int):
        """Handles setting the page number using a zero based index."""
        if len(self) == 0:
            index = 0
        else:
            while index < 0:
                index += len(self)
            while index >= len(self):
                index -= len(self)
        self._index = index

        # Change the page.
        await self.update_page()

    async def set_page_number(self, page_number: int):
        """Works using a 1-based index."""
        await self.set_index(page_number - 1)

    @abc.abstractmethod
    async def get_page(self):
        """Gets the current page."""
        pass

    @abc.abstractmethod
    async def update_page(self):
        """Should be called to update the content on Discord."""
        pass

    async def _refresh_reply(self):
        """This recaches the message object holding our reply."""
        mid = self._reply_message.id
        chan = self._reply_message.channel

        # If our message has been deleted, give up.
        try:
            self._reply_message = await chan.get_message(mid)
        except discord.NotFound:
            raise StopAsyncIteration

    async def display_buttons(self):
        """
        This displays the buttons on the message if they do not exist. If they
        do exist, then this will remove any non-applicable reacts. Furthermore,
        this will reorder the reacts if needed. This is a mostly-brute force
        approach to this problem.
        """
        try:
            # Get existing reactions
            await self._refresh_reply()
            current_reacts = self._reply_message.reactions
            expected_reacts = tuple(self._buttons.keys())
            er_tot = len(expected_reacts)

            er_idx = 0
            for react in current_reacts:
                # Flags any reacts that are not meant to be here.
                if er_idx >= er_tot or react.emoji != expected_reacts[er_idx]:
                    async for member in react.users():
                        self.nowait(
                            self._reply_message.remove_reaction(react.emoji,
                                                                member))
                elif react.emoji == expected_reacts[er_idx]:
                    async for member in react.users():
                        # Do not clear our reaction.
                        if member == self.bot.user:
                            continue
                        else:

                            self.nowait(
                                self._reply_message.remove_reaction(react.emoji,
                                                                    member))

                    er_idx += 1

            while er_idx < len(expected_reacts):
                await self._reply_message.add_reaction(expected_reacts[er_idx])
                er_idx += 1
        except discord.NotFound:
            # Message was deleted.
            return
        except discord.Forbidden:
            # No permission anymore. Just die.
            return

    async def on_timeout(self):
        """Optional hook to implement when a timeout is hit."""
        pass

    async def clear_buttons(self):
        """Attempt to clear the buttons."""
        self.nowait(self._reply_message.clear_reactions())

    def react_predicate(self,
                        reaction: discord.Reaction,
                        user: discord.User) -> bool:
        """
        If you want to filter out reactions before you pass any data to
        the button callbacks, you can implement the predicate in this
        co-routine. By default it just returns True if the reaction is a
        valid button. This also ignores the bot user.
        """
        return default_predicate(self, reaction, user)

    def set_predicate(self, predicate: predicate_t):
        """
        Quick overwrite of the existing predicate. This can have a self
        parameter, or not supply it.
        """
        params = tuple(inspect.signature(predicate).parameters.values())
        if len(params) < 2:
            raise AttributeError('Expected at least two parameters.')
        elif len(params) > 3:
            raise AttributeError('Expected no more than three parameters.')

        # Determine whether to allow the ``self`` parameter to be injected or
        # not.
        if str(params[0]) == 'self':
            inner_predicate = predicate

            def predicate(react, user):
                return inner_predicate(self, react, user)

            setattr(self, 'react_predicate', predicate)

        else:
            # This automatically encapsulates and deals with self, so will not
            # expect the predicate to supply it to the predicate body.
            setattr(self, 'react_predicate', predicate)

    async def main(self):
        try:
            await self.update_page()
            self.nowait(self.display_buttons())

            reaction, user = await self.wait_for(
                'reaction_add',
                predicate=self.react_predicate,
                timeout=self.timeout)

            if reaction.emoji not in self._buttons:
                return None
            else:
                # Remove the reaction
                await self._reply_message.remove_reaction(reaction.emoji, user)

                # Await the button logic.
                return await self._buttons[reaction.emoji](self, user)

        except abstractmachines.AsyncioTimeoutError:
            await self.on_timeout()
            await self.clear_buttons()
            raise StopAsyncIteration

    async def run(self):
        # noinspection PyBroadException
        try:
            await super().run()
        except BaseException:
            import traceback
            traceback.print_exc()
            await self._reply_message.add_reaction('\N{BROKEN HEART}')
        finally:
            await self.clear_buttons()


class PagMessage(AbstractPagFsa):
    """
    Initialises the state machine for displaying text.

    This allows all users to control it.

    :param bot: the bot we are using.
    :param invoked_by: the message that triggered this pagination to be
        output.
    :param timeout: how long to live for without any input before giving up.
    :param buttons: buttons to add. If not specified, we use the default
        pagination buttons.
    """
    def __init__(self,
                 bot: discord.Client,
                 invoked_by: discord.Message,
                 timeout: float,
                 buttons: typing.Iterable[button.Button] = None):
        self.pages = []
        if buttons is None:
            buttons = generate_default_pagination_buttons()
        super().__init__(bot, invoked_by, buttons, timeout)

    def __len__(self) -> int:
        """Gets the number of pages we have."""
        return len(self.pages)

    async def get_page(self):
        """Accesses the current page we are on."""
        return self.pages[self.index]

    async def update_page(self):
        """Updates the current page on discord."""

        message = await self.get_message()
        try:
            text = await self.get_page()

            page_numbering = f'**Page {self.index + 1} of {len(self)}**'

            if len(text) + len(page_numbering) < 2000:
                text = page_numbering + text
            else:
                text = text[:2000]

            await message.edit(content=text)
        except IndexError:
            await message.edit(content='No content.')

    def add_pages(self, *pages: str):
        """Adds more pages to the state machine."""
        self.pages.extend(pages)

    @classmethod
    def from_paginator(cls,
                       *,
                       pag: Pag,
                       **kwargs):
        """
        Takes an existing paginator, and generates a skeleton paginated message
        object. Each page from the paginator is added to the object's pages,
        and then it is returned.
        :param pag: the paginator to use.
        :param kwargs: parameters to pass to the constructor of this class.
        :return: the generated object.
        """
        return cls.from_strings(*pag.pages, **kwargs)

    @classmethod
    def from_strings(cls,
                     *strings: str,
                     **kwargs):
        """
        Takes an existing list of strings, and generates a skeleton message
        object. Each page from the list is added to the object's pages,
        and then it is returned.
        :param strings: zero or more strings to add.
        :param kwargs: parameters to pass to the constructor of this class.
        :return: the generated object.
        """
        obj = cls(**kwargs)
        obj.add_pages(*strings)
        return obj


class PagEmbed(AbstractPagFsa):
    """
    Initialises the state machine for displaying text using embed objects.

    This allows all users to control it.

    :param bot: the bot we are using.
    :param invoked_by: the message that triggered this pagination to be
        output.
    :param timeout: how long to live for without any input before giving up.
    :param buttons: buttons to add. If not specified, we use the default
        pagination buttons.
    """
    def __init__(self,
                 bot: discord.Client,
                 invoked_by: discord.Message,
                 timeout: float,
                 buttons: typing.Iterable[button.Button]=None):
        self.pages = []
        if buttons is None:
            buttons = generate_default_pagination_buttons()
        super().__init__(bot, invoked_by, buttons, timeout)

    def __len__(self) -> int:
        """Gets the number of pages we have."""
        return len(self.pages)

    async def get_page(self) -> discord.Embed:
        """Accesses the current page we are on."""
        return self.pages[self.index]

    async def update_page(self):
        """Updates the current page on discord."""

        message = await self.get_message()
        try:
            embed = await self.get_page()

            page_numbering = f'**Page {self.index + 1} of {len(self)}**\n\n'

            await message.edit(content=page_numbering, embed=embed)
        except IndexError:
            await message.edit(content='No content.')

    def add_pages(self, *pages: discord.Embed):
        """Adds more pages to the state machine."""
        self.pages.extend(pages)

    @classmethod
    def from_embeds(cls, embeds: typing.List[discord.Embed], **kwargs):
        """
        Takes an existing list of embeds, and generates a skeleton paginated
        object. Each embed is added to the object's pages, and then the object
        is returned.
        :param embeds: zero or more embeds to add.
        :param kwargs: parameters to pass to the constructor of this class.
        :return: the generated object.
        """
        obj = cls(**kwargs)
        obj.add_pages(*embeds)
        return obj


class _FocusedPagMixin(abc.ABC):
    """
    Mixin class for paginator FSAs to provide customisable focus. This is a
    customisable predicate to allow only specific users the ability to change
    the machine's state (i.e. actually get a response from reacting to buttons).

    :param predicate: the predicate to use. This should have the signature
        ``(discord.Reaction, discord.User) -> bool``. If this is not
        specified, then a predicate that only allows the author to respond is
        used instead.
    """
    _buttons: typing.Iterable[button.Button]
    invoked_by: discord.Message

    def __init__(self, predicate: predicate_t=None, **__):
        if predicate is None:
            predicate = default_focused_predicate

        spm = getattr(self, 'set_predicate', None)
        if spm is None:
            raise TypeError('Class must implement `set_predicate\'.')
        else:
            spm(predicate)

    @classmethod
    def from_predicate(cls, **kwargs):
        """
        Returns a decorator for a non-coroutine predicate. This is used to
        generate a focused paginated message of some sort, using the constructor
        arguments given to this call as keyword arguments.
        :param kwargs: the arguments to pass to the constructor.
        :return: the decorator for the function. This decorator returns a
            generated _FocusedPagMixin object with the functionality of the
            class you called this ``from_predicate`` class-method from.
        """
        def decorator(predicate: predicate_t):
            return cls(predicate=predicate, **kwargs)
        return decorator


class FocusedPagMessage(PagMessage, _FocusedPagMixin):
    """Focused Paginator for textual messages."""
    def __init__(self,
                 bot: discord.Client,
                 invoked_by: discord.Message,
                 timeout: float,
                 buttons: typing.Iterable[button.Button] = None,
                 predicate: predicate_t = None):
        PagMessage.__init__(self, bot, invoked_by, timeout, buttons)
        _FocusedPagMixin.__init__(self, predicate)


class FocusedPagEmbed(PagEmbed, _FocusedPagMixin):
    """Focused Paginator for textual messages within embeds."""
    def __init__(self,
                 bot: discord.Client,
                 invoked_by: discord.Message,
                 timeout: float,
                 buttons: typing.Iterable[button.Button] = None,
                 predicate: predicate_t = None):
        PagEmbed.__init__(self, bot, invoked_by, timeout, buttons)
        _FocusedPagMixin.__init__(self, predicate)
