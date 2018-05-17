#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Updates the bot status if Discord goes down at all.

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

import discord

from neko2.shared import morefunctools, traits


class IsDiscordDownStatus(traits.CogTraits):
    def __init__(self, bot):
        self.bot = bot
        self.last_status = None
        # Invoke first time
        self.discord_down = True
        self.status_task = None

    async def on_ready(self):
        """
        Starts a coroutine background worker to periodically change the
        bot status if Discord is playing up.
        """
        self.maybe_spawn_status_worker()

    def maybe_spawn_status_worker(self):
        if self.status_task:
            # noinspection PyUnresolvedReferences
            if not (self.status_task.done() or self.status_task.cancelled()):
                return

        # Invokes the message to spawn the first time.
        self.discord_down = True

        task = self.check_status(self)
        self.status_task = task

    @morefunctools.always_background()
    async def check_status(self):
        """
        Checks Discord's status each minute. If an issue occurs with their
        systems, we change the bot's status to reflect this, otherwise, the
        bot will just say "watching for n.help".
        """
        await asyncio.sleep(5)
        if bot.user.activity:
            self.last_status = bot.user.activity.name
        while self.bot.is_ready():
            try:
                conn = await self.acquire_http()
                # We use unresolved as status does not seem to provide
                # information about outages. Source: tried it when discord
                # went down and it said "all systems operational" despite the
                # main page saying "major service outage."
                resp = await conn.get(
                    'https://status.discordapp.com/api/v2'
                    '/incidents/unresolved.json')
                assert resp.status == 200, resp.reason
                data = await resp.json()

                # https://status.discordapp.com/api#incidents-unresolved
                problems = data.get('incidents')
                if problems:
                    problem = problems.pop(0)
                    name = problem['name']
                    await self.bot.change_presence(
                        activity=discord.Activity(
                            type=discord.ActivityType.watching,
                            name=name),
                        status=discord.Status.dnd)
                    self.discord_down = True
                else:
                    # Only change presence if discord has just gone
                    # back up again. This way, we can allow other cogs
                    # to change the message if they fancy.
                    if self.discord_down:
                        await self.bot.change_presence(
                            activity=discord.Activity(
                                type=discord.ActivityType.watching,
                                name=self.last_status),
                            status=discord.Status.online)
                        self.discord_down = False
            except BaseException as ex:
                self.logger.warning('Background checker for Discord status: ' +
                                    type(ex).__qualname__ + ': ' + str(ex))
            finally:
                await asyncio.sleep(60)


def setup(bot):
    bot.add_cog(IsDiscordDownStatus(bot))
