"""
Application entry point.
"""
from nekosquared.engine import autoloader
from nekosquared.engine import client
from nekosquared.shared import configfiles


cfg_file = configfiles.get_config_holder('discord.yaml')

bot = client.Bot(cfg_file.sync_get())
autoloader.auto_load_modules(bot)

bot.run()

exit(0)
