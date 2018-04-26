#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Application entry point. This loads any modules, DMing the owner if there is
any error, and then starts the bot.

If a path is provided as the first argument, we look in this path directory
for any configuration files, otherwise, we assume ../neko2config.

"""
from neko2.engine import runner

runner.run()
