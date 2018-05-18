#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Lets the user run `!!` to reinvoke the previous command.

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
from neko2.shared import commands


class BangBangCog:
    def __init__(self):
        self.user2context = {}

    async def on_command(self, ctx):
        """Cache the last-executed commands."""
        if ctx.command != self.bangbang:
            self.user2context[ctx.author] = ctx

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.not_bot()
    @commands.command(aliases=['!!'], brief='Reinvoke the last command.')
    async def bangbang(self, ctx: commands.Context):
        if ctx.author not in self.user2context:
            await ctx.send('No command history. Perhaps the bot restarted?',
                           delete_after=10)
        else:
            await self.user2context[ctx.author].reinvoke(call_hooks=True)


def setup(bot):
    bot.add_cog(BangBangCog())
