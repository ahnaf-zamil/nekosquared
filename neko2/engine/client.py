#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Holds the bot implementation.
"""
import copy                             # Deep and shallow copies of objects.
import inspect                          # Inspection
import os                               # Access to file system tools.
import signal                           # Access to kernel signals.
import time                             # Measuring uptime.
import traceback                        # Exception traceback utilities.

import cached_property                  # Cached properties.
import discord                          # Basic discord.py bits and pieces.
from discord.ext import commands        # Discord.py extensions.
from discord.utils import oauth_url     # OAuth URL generator

from neko2.engine import errorhandler, extrabits  # Error handling.
from neko2.shared import scribe, perms  # Logging

__all__ = ('BotInterrupt', 'Bot')


# Sue me.
BotInterrupt = KeyboardInterrupt


################################################################################
# Register the termination signals to just raise a keyboard interrupt, as      #
# I can catch this in the event loop and ensure a graceful shutdown.           #
################################################################################
def terminate(signal_no, frame):
    raise BotInterrupt(f'Caught interrupt {signal_no} in frame {frame}')


windows_signals = {signal.SIGABRT, signal.SIGTERM, signal.SIGSEGV}
unix_signals = {*windows_signals, signal.SIGQUIT}

signals = unix_signals if not os.name == 'nt' else windows_signals

for s in signals:
    # Register listener
    signal.signal(s, terminate)

del signals, unix_signals, windows_signals, terminate


################################################################################
# Bot class definition.                                                        #
################################################################################
class Bot(commands.Bot, scribe.Scribe):
    """
    My implementation of the Discord.py bot. This implements a few extra things
    on top of the existing Discord.py and discord.ext.commands implementations.

    Attributes
    ----------
    - ``permbits`` - optional (not yet implemented). An integer bitfield
        representing the default permissions to invite the bot with when
        generating OAuth2 URLs.

    Properties
    ----------
    - ``invite`` - generates an invite URL.

    Events
    ------
    These are called before the task they represent is executed.
    - on_start()
    - on_logout()

    These are executed after the task they represent has been executed.
    - on_add_command(command)
    - on_remove_command(command)
    - on_add_cog(cog)
    - on_remove_cog(cog)
    - on_load_extension(extension)
    - on_unload_extension(name)

    :param bot_config:
        This accepts a dict with two sub-dictionaries:
        - ``auth`` - this must contain a ``token`` and a ``client_id`` member.
        - ``bot`` - this contains a group of kwargs to pass to the Discord.py
            Bot constructor.
    """

    def __init__(self,
                 bot_config: dict):
        """
        Initialise the bot using the given configuration.
        """
        commands.Bot.__init__(self, **bot_config.pop('bot', {}))

        try:
            auth = bot_config['auth']
            self.__token = auth['token']
            self.client_id = auth.get('client_id', None)
            self.debug = bot_config.pop('debug', False)
        except KeyError:
            raise SyntaxError('Ensure config has `auth\' section containing '
                              'a `token\' and `client_id\' field.')

        # Used to prevent recursively calling logout.
        self._logged_in = False

        # Load version and help commands
        self.logger.info(f'Using command prefix: {self.command_prefix}')

        self._on_exit_funcs = []
        self._on_exit_coros = []

        self.load_extension('neko2.engine.builtins')
        self.add_cog(errorhandler.ErrorHandler(True, self))
        self.add_listener(self._on_connect)
        self.add_listener(self._on_ready)

    def on_exit(self, func):
        """
        Registers a function or coroutine to be called when we exit, before
        the event loop is shut down.
        :param func: the function or coroutine to call.
        """
        if inspect.iscoroutinefunction(func):
            self._on_exit_coros.append(func)
        else:
            self._on_exit_funcs.append(func)
        return func

    @cached_property.cached_property
    def invite(self):
        perm_bits = getattr(self, 'permbits', 0)

        permissions = perms.Permissions.to_discord_type(perm_bits)

        return oauth_url(self.client_id, permissions=permissions)

    @property
    def uptime(self) -> float:
        """Returns how many seconds the bot has been up for."""
        curr = time.time()
        return curr - getattr(self, 'start_time', curr)

    async def get_owner(self) -> discord.User:
        """
        Attempts to read the bot owner object from the cache.
        If that cannot be found, then we have to query Discord for the
        information. If that fails, the owner_id is probably invalid. A
        discord.NotFound error is raised in this case.
        """
        user = self.get_user(self.owner_id)
        if not user:
            # noinspection PyUnresolvedReferences
            user = await self.get_user_info(self.owner_id)

        return user

    async def start(self, token):
        """Starts the bot with the given token."""
        self.logger.info(f'Invite me to your server at {self.invite}')
        self._logged_in = True
        self.dispatch('start')
        setattr(self, 'start_time', time.time())
        await super().start(token)

    # noinspection PyBroadException
    async def logout(self):
        """
        Overrides the default behaviour by attempting to unload modules
        safely first.
        """
        if not self._logged_in:
            return
        else:
            self.dispatch('logout')

        self.logger.info('Unloading modules, then logging out')

        # We cannot iterate across the current dict object holding extensions
        # while removing items from it as Python will not allow continued
        # iteration over a non-constant state iterator... so we make a shallow
        # copy of it first and iterate across that.
        cached_extensions = copy.copy(self.extensions)
        for extension in cached_extensions:
            # Sometimes have an issue with None extensions existing for some
            # strange reason.
            if not extension:
                continue

            try:
                self.unload_extension(extension)
            except BaseException:
                traceback.print_exc()

        # Cannot resize dict as we iterate across it.
        cached_cogs = copy.copy(self.cogs)
        for cog in cached_cogs:
            try:
                self.remove_cog(cog)
            except BaseException:
                traceback.print_exc()

        await super().logout()

        self._logged_in = False

        # Call on_exit handlers
        for handler in self._on_exit_funcs:
            handler()
        for handler in self._on_exit_coros:
            await handler()

    # OCD.
    stop = logout

    # noinspection PyBroadException
    def add_cog(self, cog):
        """
        The default implementation does not attempt to tidy up if a cog does
        not load properly. This attempts to fix this.
        """
        try:
            self.logger.info(f'Loading cog {type(cog).__name__!r}')

            super().add_cog(cog)
            self.dispatch('add_cog', cog)
        except BaseException as ex:
            try:
                self.remove_cog(cog)
            finally:
                raise ImportError(ex)

    def remove_cog(self, name):
        """Logs and removes a cog."""
        if isinstance(self.cogs[name],
                      extrabits.InternalCogType):
            raise PermissionError(f'{name} is a builtin cog and will not be '
                                  'unloaded.')

        self.logger.info(f'Removing cog {name!r}')
        # Find the cog.
        cog = self.get_cog(name)
        super().remove_cog(name)
        self.dispatch('remove_cog', cog)

    def add_command(self, command):
        """Logs and adds a command."""
        self.logger.info(f'Adding command {str(command)!r}')
        super().add_command(command)
        self.dispatch('add_command', command)

    def remove_command(self, name):
        """Logs and removes an existing command."""
        self.logger.info(f'Removing command {name!r}')
        # Find the command
        command = self.get_command(name)
        super().remove_command(name)
        self.dispatch('remove_command', command)

    def load_extension(self, name):
        """
        Overrides the default behaviour by logging info about the extension
        that is being loaded. This also returns the extension object we
        have loaded.
        :param name: the extension to load.
        :return: the extension that has been loaded.
        """
        self.logger.info(f'Loading extension {name!r}')
        super().load_extension(name)
        extension = self.extensions[name]
        self.dispatch('load_extension', extension)
        return extension

    def unload_extension(self, name):
        """Logs and unloads the given extension."""
        self.logger.info(f'Unloading extension {name!r}')
        super().unload_extension(name)

    # noinspection PyBroadException
    def run(self):
        """
        Alters the event loop code ever-so-slightly to ensure all modules
        are safely unloaded.
        """
        try:
            self.loop.run_until_complete(self.start(self.__token))
        except BotInterrupt as ex:
            self.logger.warning(f'Received interrupt {ex}')
        except BaseException:
            traceback.print_exc()
        else:
            self.logger.info('The event loop was shut down gracefully')
        try:
            if self._logged_in:
                self.loop.run_until_complete(self.logout())
        except BotInterrupt:
            self.logger.fatal('Giving up all hope of a safe exit')
        except BaseException:
            traceback.print_exc()
            self.logger.fatal('Giving up all hope of a safe exit')
        else:
            self.logger.info('Process is terminating NOW.')
        finally:
            # For some reason, keyboard interrupt still propagates out of
            # this try catch unless I do this.
            return

    async def _on_connect(self):
        await self.change_presence(status=discord.Status.dnd)

    async def _on_ready(self):
        await self.change_presence(status=discord.Status.online)
