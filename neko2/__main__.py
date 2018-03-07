#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Application entry point. This loads any modules, DMing the owner if there is
any error, and then starts the bot.

If a path is provided as the first argument, we look in this path directory
for any configuration files, otherwise, we assume ../neko2config.

This is done to support the following design.

- neko2bot
  |
  |--nekosquared
  |  |
  |  |--neko2
  |  |--venv
  |  |--LICENSE
  |  |--README.md
  |  `--etc
  |
  `--neko2config
     |
     `--config files
"""
import sys
import traceback

from neko2.engine import autoloader
from neko2.engine import client
from neko2.shared import configfiles


if len(sys.argv) > 1:
    config_path = sys.argv[1]
    configfiles.CONFIG_DIRECTORY = config_path

cfg_file = configfiles.get_from_config_dir('discord.yaml')

bot = client.Bot(cfg_file.sync_get())
errors = autoloader.auto_load_modules(bot)


# If any errors occur on startup... DM me each error.
@bot.listen()
async def on_ready():
    global errors
    if errors:
        err_cnt = len(errors)
        owner = bot.get_user(bot.owner_id)
        await owner.send(f'{err_cnt} error{"s" if err_cnt - 1 else ""} occurred'
                         ' whilst starting the bot.')
        while errors:
            error, extension = errors.pop(0)

            string = f'Error caused by extension: {extension}\n\n'
            string += ''.join(traceback.format_exception(
                type(error),
                error,
                error.__traceback__))
            for i in range(0, min(20000, len(string)), 1990):
                await owner.send(f'```\n{string[i:i+1990]}\n```')

bot.run()
exit(0)
