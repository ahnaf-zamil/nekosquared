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


from neko2.engine import client, autoloader, BotInterrupt
from neko2.shared import configfiles, traits


# noinspection PyProtectedMember
def run():
    # UVloop is more efficient than asyncio.

    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except:
        logging.warning('UVloop could not be loaded. Using default asyncio '
                        'event policy implementation...')
    else:
        logging.info('UVloop was detected. Switched to that asyncio '
                     'event policy implementation!')
    finally:
        loop = asyncio.get_event_loop()

    if len(sys.argv) > 1:
        config_path = sys.argv[1]
        configfiles.CONFIG_DIRECTORY = config_path

    try:
        cfg_file = configfiles.get_from_config_dir('discord')

        bot = client.Bot(loop, cfg_file.sync_get())

        # Acquire resources.
        loop.run_until_complete(traits.CogTraits._alloc(bot.loop))

        _ = autoloader.auto_load_modules(bot)

        try:
            # noinspection PyUnresolvedReferences
            loop.run_until_complete(bot.start(bot.token))
        except BotInterrupt as ex:
            bot.logger.warning(f'Received interrupt {ex}')
        except BaseException:
            traceback.print_exc()
            bot.logger.fatal('An unrecoverable error occurred.')
        else:
            bot.logger.info('The bot stopped executing gracefully as expected')

        try:
            if bot._logged_in:
                loop.run_until_complete(bot.logout())
        except BotInterrupt:
            bot.logger.fatal('Giving up all hope of a safe exit')
        except BaseException:
            traceback.print_exc()
            bot.logger.fatal('Giving up all hope of a safe exit')
        else:
            bot.logger.info('Process is terminating NOW.')
        finally:
            return
    except KeyboardInterrupt:
        return
    finally:
        loop.run_until_complete(traits.CogTraits._dealloc())
