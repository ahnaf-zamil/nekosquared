#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
I am a slightly weird bot that does a variety of things. Functionality is 
mostly geared towards various development tools, such as interpreters
and compilers for over 45 different programming languages. Various tools
for accessing documentation also exist. Functions to provide an easier way
to manage Discord guilds are also being implemented, and are a work-in-
progress.

Eventually, more random bits and pieces aimed towards general day-to-day
use will also start to appear.

Oh, and I cannot evaluate the price of lime.

If you want to be nosey, you can also [check out the source code on GitHub](
https://github.com/neko404notfound/nekosquared). Bugs and general development
progress will begin to be documented on [Trello](https://goo.gl/NfKvDs).

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
import neko2.cogs
import neko2.engine
import neko2.shared

__author__ = 'Neko404NotFound'
__license__ = 'MIT License'
__url__ = 'https://github.com/neko404notfound/nekosquared'
__version__ = '2.14.4-BLEEDING'
__repository__ = __url__
__trello__ = 'https://trello.com/b/gKTl1rMO'

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
