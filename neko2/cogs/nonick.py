#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Prevents nicknames being applied to the bot while this cog is loaded.

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
import asyncio


class NoNickCog:
    def __init__(self, bot):
        self.bot = bot
        self.locks = {}

    async def on_member_update(self, _unused_before, after):
        if after.id != self.bot.user.id:
            return

        # If the nickname is not the bot name, fix it.
        await self.ensure_no_nick(after)

    async def on_ready(self):
        for guild in self.bot.guilds:
            me = guild.me
            await self.ensure_no_nick(me)

    async def ensure_no_nick(self, member):
        # We wait 5 seconds to fire, and use an asyncio lock that is applied
        # per guild. The former prevents a denial-of-service-like attack
        # from being performed via spamming the guild with nickname
        # changes for our bot user. The latter ensures that these requests
        # do not stack up if we are already processing one.
        # This change will trigger itself recursively, so the checks also
        # prevent anything from entering an infinite loop.

        if member.display_name != member.name:
            lock = self.locks.setdefault(member.guild, asyncio.Lock())

            if member is None or lock.locked():
                return
            else:
                with await lock:
                    # Keep lock closed for 5 seconds for a timeout.
                    await asyncio.sleep(5)

                await member.edit(reason='Nickname was changed', nick=None)


def setup(bot):
    bot.add_cog(NoNickCog(bot))
