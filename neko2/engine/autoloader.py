"""
Automatically loads modules listed in the config file.

Discord.py refers to these as extensions. Extensions contain zero or more
cogs which are holders of logic.
"""
import logging   # Loggers.
import traceback   # Traceback utils.

from neko2.shared import alg    # Timing.
from neko2.shared import configfiles   # Config file utils.


__all__ = ('FILE', 'auto_load_modules')

FILE = 'modules.yaml'


def auto_load_modules(bot, *, config_file=FILE):
    """
    Autoloads any modules into the given bot.
    :param bot: the bot to load modules into.
    :param config_file: optional. Config file to read. Defaults to the
            'modules.yaml' file if unspecified.

    If any extensions fail to load, then we do not halt. A traceback is printed
    and we continue.
    """
    config = configfiles.get_config_data(config_file)
    logger = logging.getLogger(__name__)

    if config is None:
        logger.warning('No modules were listed.')
        return
    elif not isinstance(config, list):
        raise TypeError('Expected list of module names.')
    else:
        for module in config:
            # noinspection PyBroadException
            try:
                _, time = alg.time_it(lambda: bot.load_extension(module))
            except BaseException:
                logger.fatal(f'FAILED TO LOAD {module}. SEE TRACEBACK BELOW.')
                traceback.print_exc()
            else:
                logger.info(f'Loaded {module} in {time * 1000:,.2f}ms')
