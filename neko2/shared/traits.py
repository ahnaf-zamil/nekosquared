# -*- coding: utf-8 -*-
"""
Various thread and process pool templates.
"""
import asyncio
import concurrent.futures             # Executors.
import functools
import os                             # File system access.
import typing

import aiofiles
import aiohttp
import async_timeout

from neko2.shared import scribe       # Scribe
from neko2.shared.classtools import ClassProperty

__all__ = ('CogTraits',)


def _magic_number(*, cpu_bound=False):
    """
    Returns the magic number for this machine. This is the number of
    concurrent execution media to spawn in a pool.
    :param cpu_bound: defaults to false. Determines if we are considering
        IO bound work (the default) or CPU bound.
    :return: 3 * the number of USABLE logical cores if we are IO bound. If we
        are CPU bound, we return 2 * the number of processor cores, as CPU
        bound work utilises the majority of it's allocated time to doing
        meaningful work, whereas IO is usually slow and consists of thread
        yielding. There is no point spamming the CPU with many more jobs than
        it can concurrently handle with CPU bound work, whereas it will provide
        a significant performance boost for IO bound work. We don't consider
        scheduler affinity for CPU bound as we expect that to use a process
        pool, which is modifiable by the kernel.
    """
    # OR with 1 to ensure at least 1 "node" is detected.
    if cpu_bound:
        return 2 * (os.cpu_count() or 1)
    else:
        return 3 * (len(os.sched_getaffinity(0)) or 1)


class CogTraits(scribe.Scribe):
    """Contains any shared resource traits we may want to acquire."""
    __io_pool: concurrent.futures.Executor = None
    __http_pool: aiohttp.ClientSession = None
    __loop: asyncio.AbstractEventLoop = None

    @classmethod
    async def _alloc(cls, loop):
        cls.__loop = loop
        cls.logger.info('Initialising IO pool.')
        cls.__io_pool = concurrent.futures.ThreadPoolExecutor(
            _magic_number(cpu_bound=False))
        cls.logger.info('Initialising HTTP session.')
        cls.__http_pool = aiohttp.ClientSession(loop=loop)

    @classmethod
    async def _dealloc(cls):
        if cls.__http_pool:
            await cls.__http_pool.close()
            cls.__http_pool = None
        if cls.__io_pool:
            with async_timeout.timeout(30):
                cls.__io_pool.shutdown(wait=True)

    @classmethod
    async def acquire_http(cls):
        """
        Acquires the shared global session.
        Should not be closed after use.
        """
        return cls.__http_pool

    @classmethod
    async def acquire_http_session(cls, loop=None):
        """
        Acquires a new HTTP client session. This must be closed after use to
        avoid leaving connections open.
        """
        loop = cls.__loop if not loop else loop
        return aiohttp.ClientSession(loop=loop)

    @classmethod
    def file(cls, file_name, *args, **kwargs):
        kwargs.setdefault('executor', cls.__io_pool)
        kwargs.setdefault('loop', cls.__loop)

        return functools.partial(
            aiofiles.open,
            file_name,
            *args,
            **kwargs)()

    @classmethod
    async def run_in_io_executor(cls,
                                 call: typing.Callable,
                                 args: typing.List=None,
                                 kwargs: typing.Dict=None,
                                 loop=None):
        if not loop:
            loop = cls.__loop

        if not args:
            args = []
        if not kwargs:
            kwargs = {}

        return await loop.run_in_executor(
            cls.__io_pool,
            functools.partial(call, *args, **kwargs))
