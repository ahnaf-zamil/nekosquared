#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Handles running the bot. This should be the thing you call to start the bot, as
it ensures the trait resources are acquired and released correctly and safely.

===

MIT License

Copyright (c) 2018 Neko404NotFound

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import asyncio
import logging
import sys
import traceback

from neko2.engine import BotInterrupt, autoloader, client
from neko2.shared import configfiles, scribe, traits


class NekoSquaredBotProcess(scribe.Scribe):
    """
    Holds the bot, and the resource handlers.
    """

    def __init__(self, args=sys.argv):
        """
        Inits the bot process handler.
        :param args: command line args to process.
        """
        self.args = args

        # Initialise file-based logging to prevent spamming the
        # journal.
        """
        logging.captureWarnings(True)
        neko2logs = logging.getLogger('neko2')
        timestamp = str(datetime.utcnow())
        fh = logging.FileHandler(f'/tmp/neko2_{timestamp}.log')
        fh.setLevel('DEBUG')
        sh = logging.StreamHandler()
        sh.setLevel('WARNING')
        logging.basicConfig(level='INFO', handlers=[fh, sh])
        
        
        # Intercept calls to traceback
        _unused_old_exc = traceback.print_exc

        def new_exc(limit=None, file=None, chain=True):
            '''Intercepts the printing of tracebacks and logs them.'''
            traceback.print_exception(*sys.exc_info(),
                                      limit=limit,
                                      file=file,
                                      chain=chain)
            neko2logs.error('Traceback dumped on request',
                            exc_info=sys.exc_info())

        traceback.print_exc = new_exc
        
        # Add an on-error hook
        def my_excepthook(exc_type, exc_value, traceback, logger=neko2logs):
            logger.error("Logging an uncaught exception",
                         exc_info=(exc_type, exc_value, traceback))

        
        """
        logging.basicConfig(level='INFO')
        # Stops rate limiting spam from books.
        logging.getLogger('discord.http').setLevel('WARNING')

        if len(self.args) > 1:
            config_path = self.args[1]
            configfiles.CONFIG_DIRECTORY = config_path

        try:
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        except:
            self.logger.warning('UVloop could not be loaded. Using default '
                                'asyncio event policy implementation...')
        else:
            self.logger.info('UVloop was detected. Switched to that asyncio '
                             'event policy implementation!')
        finally:
            loop = asyncio.get_event_loop()

        self.loop = loop

        cfg_file = configfiles.get_from_config_dir('discord')
        self.bot = client.Bot(self.loop, cfg_file.sync_get())

        setattr(self.bot, 'neko2botprocess', self)

        # Acquire resources
        # noinspection PyProtectedMember
        self.loop.run_until_complete(traits.CogTraits._alloc(self.loop))

        _ = autoloader.auto_load_modules(self.bot)

    # noinspection PyProtectedMember, PyBroadException
    def run(self):
        """Runs the bot until it logs out or an interrupt is hit."""
        try:
            try:
                self.loop.run_until_complete(self.bot.start(self.bot.token))
            except BotInterrupt as ex:
                self.logger.warning(f'Received interrupt {ex}')
            except BaseException:
                traceback.print_exc()
                self.logger.fatal('An unrecoverable error occurred.')
            else:
                self.logger.info('The bot stopped executing as expected')

            try:
                if self.bot._logged_in:
                    self.loop.run_until_complete(self.bot.logout())
            except BotInterrupt:
                self.bot.logger.fatal('Giving up all hope of a safe exit')
            except BaseException:
                traceback.print_exc()
                self.bot.logger.fatal('Giving up all hope of a safe exit')
            else:
                self.bot.logger.info('Process is terminating NOW.')
            finally:
                return
        except KeyboardInterrupt:
            return
        finally:
            self.loop.run_until_complete(traits.CogTraits._dealloc())
            delattr(self.bot, 'neko2botprocess')
