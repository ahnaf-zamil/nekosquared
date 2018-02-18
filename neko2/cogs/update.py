"""
Utility to enable the bot to update its' source code.

This assumes you are working in a virtual environment and thus have permission
to alter your own packages. It also makes the assumption that this package
was installed via ``pip`` initially.
"""
import io
import pip

from neko2.engine import commands
from neko2.shared import traits


class BotUpdateCog(traits.CpuBoundPool):
    @staticmethod
    def update():
        """
        Updates the bot, and captures any output. This is designed to
        be invoked on a CPU pool.
        """
