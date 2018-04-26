#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Handles running the bot. This should be the thing you call to start the bot, as
it ensures the trait resources are acquired and released correctly and safely.
"""
import asyncio
import sys
import traceback

from neko2.engine import client, autoloader, BotInterrupt
from neko2.shared import configfiles, traits


# noinspection PyProtectedMember
def run():
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
        configfiles.CONFIG_DIRECTORY = config_path

    loop = asyncio.get_event_loop()

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
