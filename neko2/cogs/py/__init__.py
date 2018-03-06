#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Since the Sphinx documentation facilities use a client-side JavaScript-based
search, we cannot abuse the search system like in the ``coliru`` extension.

(Well, I could possibly, but it would mean either rewriting thousands of lines
of undocumented and minified JavaScript, or implementing a JavaScript parser
and DOM into this bot, which are dumb ideas considering this bot should be
relatively lightweight and simple).

Thus, the solution to the issue is to design a fuzzy string search system that
will be implemented in `neko2.shared.other.fuzzy` in case I need it elsewhere,
and some tools to brute-force inspect all elements exposed by a Python module
by inspection. This will be done by spawning processes that run in the
background and traverse the module trees. They will then cache results in
files on disk, where possible.
"""
from . import cog   # cog


def setup(bot):
    bot.add_cog(cog.PyCog())
