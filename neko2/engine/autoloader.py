#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Automatically loads modules listed in the config file.

Discord.py refers to these as extensions. Extensions contain zero or more
cogs which are holders of logic.

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
import logging  # Loggers.
import traceback  # Traceback utils.
import typing  # Type checking

from neko2.modules import modules  # Modules to load with.
from neko2.shared import alg  # Timing.

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
        logger.warning(f'Loaded {len(modules) - len(errors)}/{len(modules)} '
                       'modules successfully. Will now start bot.')
    return errors
