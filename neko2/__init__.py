#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
I am a slightly weird bot that does a variety of cool things.

For one, I try to be a bot developer's best friend. I provide commands to
execute arbitrary code in a multitude of different programming languages, and
can display information from various library docs. Additionally, several
extra development utilities exist. These include: shortening of URLs;
generation of bot invites from snowflake client IDs; the ability to view
manpages and tldr pages; and unicode character inspection.

I will also attempt to provide useful conversions for units of measurement
automatically. Someone using fahrenheit? No problem!

A bunch of other commands exist, and will hopefully be steadily increased as
time progresses. Just run `n.help` to see what is available!
"""
import neko2.shared
import neko2.cogs
import neko2.engine


__author__ = 'Neko404NotFound'
__license__ = 'Mozilla Public License Version 2.0'
__url__ = 'https://github.com/neko404notfound/nekosquared'
__version__ = '1.6-BLEEDING'
__repository__ = __url__


# Get commit number, if possible, and append to the version.
import subprocess
try:
    output = subprocess.check_output('git log --oneline',
                                     universal_newlines=True,
                                     shell=True).strip().split('\n')
    __version__ += f' build {len(output)}'
    del output
except:
    pass
finally:
    del subprocess

# Print out version to console.
import sys
print('Neko^2', __version__, __author__, __url__, file=sys.stderr)
del sys
