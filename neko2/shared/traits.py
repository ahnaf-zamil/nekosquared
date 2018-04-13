# -*- coding: utf-8 -*-
"""
Various thread and process pool templates.
"""
import concurrent.futures             # Executors.
import functools
import os                             # File system access.

import aiohttp

from neko2.shared import scribe       # Scribe


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
    __cpu_pool: concurrent.futures.Executor = None
    __http_pool: aiohttp.ClientSession = None

    @classmethod
    async def acquire_http(cls, bot):
        if not cls.__http_pool:
            cls.logger.info('Opening HTTP pool.')
            cls.__http_pool = aiohttp.ClientSession()

            @bot.on_exit
            async def on_exit():
                cls.logger.info('Closing HTTP pool.')
                await cls.__http_pool.close()
                cls.__http_pool = None

        return cls.__http_pool

    @classmethod
    async def run_in_io_executor(cls, bot, call, *args, **kwargs):
        if not cls.__io_pool:
            cls.logger.info('Creating thread pool executor.')
            cls.__io_pool = concurrent.futures.ThreadPoolExecutor(
                thread_name_prefix=__name__,
                max_workers=_magic_number(cpu_bound=False)
            )

            @bot.on_exit
            def on_exit():
                cls.logger.info('Shutting down thread pool executor.')
                cls.__io_pool.shutdown(True)
                cls.__io_pool = None

        loop = bot.loop

        partial = functools.partial(call, *args, **kwargs)

        return await loop.run_in_executor(cls.__io_pool, partial)

    @classmethod
    async def run_in_cpu_executor(cls, bot, call, *args, **kwargs):
        if not cls.__cpu_pool:
            cls.logger.info('Creating process pool executor.')
            cls.__cpu_pool = concurrent.futures.ProcessPoolExecutor(
                max_workers=_magic_number(cpu_bound=True)
            )

            @bot.on_exit
            def on_exit():
                cls.logger.info('Shutting down process pool executor.')
                cls.__cpu_pool.shutdown(True)
                cls.__cpu_pool = None

        loop = bot.loop

        partial = functools.partial(call, *args, **kwargs)

        return await loop.run_in_executor(cls.__cpu_pool, partial)
