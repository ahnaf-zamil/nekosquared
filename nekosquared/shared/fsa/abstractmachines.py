"""
(c) Espeonageon 2018.
Licensed under the Mozilla Public License V2.0

You can use this however you like under the MPLv2.0 license, but you must
make sure to keep this message here.

Base finite state automaton. This is an asynchronous iterator abstract
class type.
"""
import abc
import asyncio
import typing

import discord
from discord.ext import commands


__all__ = ('AsyncioTimeoutError', 'FiniteStateAutomaton')


# Gives the timeout error we are interested in, a non-confusing alias.
AsyncioTimeoutError = asyncio.TimeoutError


class FiniteStateAutomaton(abc.ABC):
    """
    Underlying implementation of a finite-state automaton.

    These are glorified async iterators. As such, they will repeatedly
    call this class's ``main`` method until a StopAsyncIteration is raised.

    The classes' ``__aenter__`` and ``__aexit__`` co-routines are called
    internally before and after each iteration.

    You can either use these directly as async iterators; if so, the return
    result of ``main`` will be the element that is returned by the iterator;
    for example::

        async for result in fsa:
            print(result)

    ...given that ``result`` is returned by ``main``.
    """
    def __init__(self, bot: discord.Client, invoked_by: discord.Message):
        if isinstance(invoked_by, commands.Context):
            invoked_by = invoked_by.message

        self.invoked_by: discord.Message = invoked_by
        self.bot: discord.Client = bot
        self._counter = 0

    def __aiter__(self):
        """Must return this object. It is the async iterator of itself."""
        return self

    async def __anext__(self):
        """Polls the next result from the main method."""
        async with self:
            self._counter += 1
            return await self.main()

    async def __aenter__(self):
        """Optional entry hook."""
        pass

    async def __aexit__(self, *__):
        """Optional exit hook."""
        pass

    async def main(self):
        """Override this with your chosen implementation of runtime logic."""
        self.stop()

    async def wait_for(self,
                       event: str,
                       *,
                       predicate: typing.Callable=None,
                       timeout=None):
        """
        Shortcut for calling bot.wait_for. Returns the arguments that are
        part of the event that successfully triggered stopping the pause.
        Raises ``AsyncioTimeoutError`` if the timeout is reached.
        """
        return await self.bot.wait_for(event, check=predicate, timeout=timeout)

    @staticmethod
    def stop() -> typing.NoReturn:
        """Just raises a StopAsyncIteration."""
        raise StopAsyncIteration

    @staticmethod
    def nowait(future):
        """Allows overriding how non-awaiting bits and bobs work."""
        return asyncio.ensure_future(future)

    async def run(self) -> None:
        """
        Runs the finite state machine, awaiting it to terminate before
        returning.

        This is basically the same as just doing::
            async for _ in your_fsa: pass

        ...except errors should be handled in derived implementations for you
        here automatically.
        """
        async for _ in self:
            pass
