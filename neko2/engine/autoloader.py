#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Automatically loads modules listed in the config file.

Discord.py refers to these as extensions. Extensions contain zero or more
cogs which are holders of logic.
"""
import logging                         # Loggers.
import traceback                       # Traceback utils.
import typing                          # Type checking
from neko2.shared import alg           # Timing.
from neko2.modules import modules      # Modules to load with.


__all__ = ('auto_load_modules',)


def auto_load_modules(bot) \
        -> typing.List[typing.Tuple[BaseException, str]]:
    """
    Auto-loads any modules into the given bot.
    :param bot: the bot to load modules into.
    :param config_file: optional. Config file to read. Defaults to the
            'modules.yaml' file if unspecified.

    If any extensions fail to load, then we do not halt. A traceback is printed
    and we continue. Any errors are returned in a collection of 2-tuples paired
    with the name of the corresponding extension that caused the error.
    """
    logger = logging.getLogger(__name__)

    errors = []

    if modules is None:
        logger.warning('No modules were listed.')
    else:
        for module in modules:
            # noinspection PyBroadException
            try:
                _, time = alg.time_it(lambda: bot.load_extension(module))
            except BaseException as ex:
                logger.fatal(f'FAILED TO LOAD {module}. SEE TRACEBACK BELOW.')
                traceback.print_exc()
                errors.append((ex, module))
            else:
                logger.info(f'Loaded module {module} in {time * 1000:,.2f}ms')
    return errors
