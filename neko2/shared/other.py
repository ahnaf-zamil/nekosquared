#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Other bits and pieces that do not belong elsewhere.
"""
import asyncio

from neko2.shared import classtools

__all__ = ('rand_colour', 'always_background')


def rand_colour() -> int:
    """Gets a random colour."""
    from random import randint
    return randint(0, 0xFFFFFF)


def always_background(loop: asyncio.AbstractEventLoop=None):
    """
    Decorates a coroutine and ensures that whenever we invoke it, we
    actually end up creating a task in the background. This is a neat
    little drop-in that will essentially allow both await and normal
    calling, to ensure compatibility.

    :param loop: the event loop to delegate on. Uses the default if
        unspecified.
    """
    def decorator(coro):
        @classtools.patches(coro)
        class AlwaysInvokeAsTaskInBackground:
            __slots__ = ()

            def __call__(self, *args, **kwargs):
                """Invokes as a task."""
                nonlocal loop

                if loop is None:
                    loop = asyncio.get_event_loop()

                task = loop.create_task(coro(*args, **kwargs))

                # Enables awaiting, optionally.
                return task

        return AlwaysInvokeAsTaskInBackground()
    return decorator
