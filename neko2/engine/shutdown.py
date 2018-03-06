#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Holds callbacks for when we are about to shut the bot down. These can be
either futures or

Couldn't find another way of handling this sadly. Hooray for global variables.
"""
import asyncio   # Asyncio queues.


__all__ = ('on_shutdown', 'terminate')


_calls = asyncio.Queue()


def on_shutdown(coro):
    _calls.put_nowait(coro)
    return coro


async def terminate():
    while not _calls.empty():
        next_callable = await _calls.get()
        await next_callable()

