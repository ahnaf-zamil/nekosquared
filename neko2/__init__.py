#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
I am a slightly weird bot that does a variety of cool things. I cannot evaluate
the price of lime.

If you want to be nosey, you can also [check out the source code on GitHub.](
https://github.com/neko404notfound/nekosquared)
"""
import neko2.shared
import neko2.cogs
import neko2.engine


__author__ = 'Neko404NotFound'
__license__ = 'Mozilla Public License Version 2.0'
__url__ = 'https://github.com/neko404notfound/nekosquared'
__version__ = '1.10.0-BLEEDING'
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
