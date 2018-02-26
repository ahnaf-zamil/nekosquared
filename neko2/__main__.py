#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Application entry point.
"""
from neko2.engine import autoloader
from neko2.engine import client
from neko2.shared import configfiles


cfg_file = configfiles.get_config_holder('discord.yaml')

bot = client.Bot(cfg_file.sync_get())
autoloader.auto_load_modules(bot)

bot.run()

exit(0)
