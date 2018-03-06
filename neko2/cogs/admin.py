#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Cog holding owner-only administrative commands, such as those for restarting
the bot, inspecting/loading/unloading commands/cogs/extensions, etc.
"""
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
        try:
            await ctx.add_reaction('\N{OK HAND SIGN}')
        except:
            await ctx.send('\N{OK HAND SIGN}')
        finally:
            await ctx.bot.logout()



def setup(bot):
    bot.add_cog(AdminCog())
