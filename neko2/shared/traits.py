"""
Various thread and process pool templates.
"""
import asyncio   # Asyncio coroutines, ensuring futures
import concurrent.futures as futures   # Thread and Process pool executors.
import logging   # Logging utils.
import os   # File system access.
import typing   # Type hints.

import aiohttp   # Asynchronous HTTP/HTTPs.
import aiofiles   # Asynchronous file I/O.
import asyncpg   # Asynchronous PostgreSQL integration.

from neko2.engine import shutdown   # Shutdown hooks.
from neko2.shared import configfiles   # Config file support.
from neko2.shared import faketypes   # Fake type hints.


__all__ = ('Scribe', 'CpuBoundPool', 'IoBoundPool', 'FsPool',
           'HttpPool', 'PostgresPool')


T = typing.TypeVar('T')


class Scribe:
    """Adds functionality to a class to allow it to log information."""
    logging.basicConfig(level='INFO')
    logger: logging.Logger

    def __init_subclass__(cls, **_):
        cls.logger: logging.Logger = logging.getLogger(cls.__name__)


def _magic_number(*, cpu_bound=False):
    """
    Returns the magic number for this machine. This is the number of
    concurrent execution media to spawn in a pool.
    :param cpu_bound: defaults to false. Determines if we are considering
        IO bound work (the default) or CPU bound.
    :return: 5 * the number of USABLE logical cores if we are IO bound. If we
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
        return 5 * (len(os.sched_getaffinity(0)) or 1)


_processes, _threads = _magic_number(cpu_bound=True), _magic_number()
logging.getLogger('CpuBoundPool').info(
    f'Made pool for up to {_processes} cpu workers.')
logging.getLogger('IoBoundPool').info(
    f'Made pool for up to {_threads} thread workers.')

_cpu_pool = futures.ProcessPoolExecutor(_processes)
_io_pool = futures.ThreadPoolExecutor(_threads)


@shutdown.on_shutdown
async def _terminate_children():
    # This will likely block, and if the processes or threads are blocking on
    # an asyncio coroutine, this should allow us to prevent deadlock.
    def kill_io():
        logging.getLogger('IoBoundPool').info('Killing workers.')
        _io_pool.shutdown(wait=True)
        logging.getLogger('IoBoundPool').info('Successfully killed workers.')

    def kill_cpu():
        logging.getLogger('CpuBoundPool').info('Killing workers.')
        _cpu_pool.shutdown(wait=True)
        logging.getLogger('CpuBoundPool').info('Successfully killed workers.')

    try:
        await asyncio.wait_for(
            asyncio.gather(
                # Uses default executor. We don't really care as asyncio
                # will clear that up for us. This will run in a thread, so it
                # is not really asynchronous, however, it will mean that the
                # timeout is shared between both kill functions.
                asyncio.get_event_loop().run_in_executor(None, kill_io),
                asyncio.get_event_loop().run_in_executor(None, kill_cpu),
            ),
            timeout=10
        )
    except asyncio.TimeoutError:
        logging.getLogger(__name__).error(
            'Terminating pools took too long, cowardly refusing '
            'to wait any longer.'
        )
    else:
        logging.getLogger(__name__).info('Killed all pools successfully.')
    finally:
        logging.getLogger(__name__).info('Pool resources are now freed.')

del _processes, _threads, _magic_number


class CpuBoundPool:
    """
    Trait that implements a process pool execution service for CPU-bound work.

    This is more costly to run than a thread, as it is essentially spawning a
    new process on the operating system each time we start one, however, these
    are cancellable. Generally this should only be used if work is very slow and
    consists mainly of CPU-based work.
    """
    @property
    def cpu_pool(self) -> futures.Executor:
        return _cpu_pool


class IoBoundPool:
    """
    Trait that implements a thread pool execution service for IO-bound work.

    This is less costly than a process pool, however, these are non-cancellable
    and are locked into the same affinity as the thread they are spawned by.
    There is also an issue of taking into account thread safety.
    """
    @property
    def io_pool(self) -> futures.Executor:
        return _io_pool


class FsPool(IoBoundPool, Scribe):
    """
    Trait that allows the acquisition of an asynchronous file handle from
    the local file system. This runs in the same pool of workers as the
    IoBoundPool uses.
    """
    @classmethod
    async def acquire_fp(cls, file, mode='r', buffering=-1, encoding=None,
                         errors=None, newline=None, closefd=True, opener=None):
        """Acquires an asynchronous file pointer to a file stream."""
        cls.logger.info(f'Opening {file!r} with mode {mode!r}')
        return await aiofiles.open(
            file, mode, buffering, encoding, errors, newline, closefd, opener,
            executor=_io_pool)


class ConnectionContextManager:
    """Fake context manager for an aiohttp client session global instance."""
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self) -> faketypes.ClientSessionT:
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class HttpPool(Scribe):
    """
    Allows you to acquire an HTTP pool to use. This returns a context manager
    that can only be used in non-async blocks.

    with (await self.acquire_http()) as conn:
        resp = await conn.get('https://google.com')

    Todo: try to fix this to work with asynchronous blocks instead.
    """

    @classmethod
    async def acquire_http(cls) -> ConnectionContextManager:
        """
        :return: the client session.
        """
        if not hasattr(cls, '_http_pool'):
            cls.logger.info('Initialising HTTP pool.')
            cls._http_pool = aiohttp.ClientSession()

            @shutdown.on_shutdown
            async def shutdown_callback():
                cls.logger.info('Closing HTTP pool.')
                await cls._http_pool.close()
        else:
            cls.logger.info(f'Acquiring existing HTTP pool.')

        # noinspection PyTypeChecker
        return ConnectionContextManager(cls._http_pool)


class PostgresPool(Scribe):
    """
    Allows you to acquire a connection to the database from the connection pool.
    """
    @classmethod
    async def acquire_db(cls, timeout=None) -> asyncpg.Connection:
        """
        :param timeout: optional timeout.
        :return: connection.
        """

        if not hasattr(cls, f'__{cls.__name__}_postgres_pool'):
            cls.logger.info('Initialising PostgreSQL pool from config.')
            cfg = configfiles.get_config_holder('database.yaml')
            cls.__postgres_pool = await asyncpg.create_pool(
                **await cfg.async_get())

            @shutdown.on_shutdown
            async def shutdown_callback():
                cls.logger.info('Closing PostgreSQL pool.')
                await cls.__postgres_pool.close()
        else:
            cls.logger.info(f'Acquiring existing PostgreSQL pool.')

        return await cls.__postgres_pool.acquire(timeout=timeout)