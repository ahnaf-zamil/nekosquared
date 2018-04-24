#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Other helper methods that don't belong elsewhere.
"""
import asyncio
import discord


__all__ = ('attempt_delete',)


async def attempt_delete(message: discord.Message,
                         *messages: discord.Message) -> None:
    """Attempts to delete all messages given to the call."""
    messages = (message, *messages)

    async def _consume_error_delete(_message):
        try:
            await _message.delete()
        except:
            return

    await asyncio.gather(*[
        _consume_error_delete(m) for m in [*messages]
    ])
