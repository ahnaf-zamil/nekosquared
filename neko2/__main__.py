#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Application entry point.
"""
import traceback

from neko2.engine import autoloader
from neko2.engine import client
from neko2.shared import configfiles


cfg_file = configfiles.get_config_holder('discord.yaml')

bot = client.Bot(cfg_file.sync_get())
errors = autoloader.auto_load_modules(bot)


# If any errors occur on startup... DM me each error.
@bot.listen()
async def on_ready():
    global errors
    if errors:
        for error in errors:
            string = ''.join(traceback.format_exception(
                type(error),
                error,
                error.__traceback__))
            owner = bot.get_user(bot.owner_id)
            await owner.send(f'```\n{string[:1990]}\n```')
        errors = None

bot.run()
exit(0)
