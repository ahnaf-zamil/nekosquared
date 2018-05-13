#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Holds a list of modules to always load on startup.

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


def _(module: str):
    return f'neko2.cogs.{module}'


modules = frozenset({
    _('compiler'),
    _('mew'),
    _('admin'),
    _('cat'),
    _('cppref'),
    _('botupdate'),
    _('man'),
    _('py'),
    _('tldr'),
    _('ud'),
    _('googl'),
    _('wordnik'),
    _('tableflip'),
    _('unicode'),
    _('rpn'),
    _('xkcd'),
    _('units'),
    _('f'),
    _('chatty'),
    _('steam'),
    _('iss'),
    _('mocksql'),
    # _('nonick'),      # Uncomment to enforce nickname sanitation.
    _('tldrlegal'),
    _('isdiscorddownstatus'),
    _('botutils'),
    _('guildstuff'),
})
