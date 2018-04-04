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
from neko2.engine import errorhandler
from neko2.shared import configfiles

if len(sys.argv) > 1:
    config_path = sys.argv[1]
    configfiles.CONFIG_DIRECTORY = config_path

cfg_file = configfiles.get_from_config_dir('discord')

bot = client.Bot(cfg_file.sync_get())
errors = autoloader.auto_load_modules(bot)

bot.run()
