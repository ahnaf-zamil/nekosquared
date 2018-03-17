#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Cog holding owner-only administrative commands, such as those for restarting
the bot, inspecting/loading/unloading commands/cogs/extensions, etc.
"""
import asyncio

from neko2.engine import commands   # command decorator


class AdminCog:
    """Holds administrative utilities"""
    @staticmethod
    async def __local_check(ctx):
        return await ctx.bot.is_owner(ctx.author)

    @commands.command(aliases=['stop', 'die'])
    async def restart(self, ctx):
        """
        Kills the bot. If it is running as a systemd service, this should
        cause the bot to restart.
        """
        commands.acknowledge(ctx)
        await asyncio.sleep(2)
        await ctx.bot.logout()

    @commands.command()
    async def ping(self, ctx):
        """
        Checks whether the bot is online and responsive or not.
        """
        await ctx.send(f'Pong! ({ctx.bot.latency * 1000:.2f}ms)')


def setup(bot):
    bot.add_cog(AdminCog())
