#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Cog holding owner-only administrative commands, such as those for restarting
the bot, inspecting/loading/unloading commands/cogs/extensions, etc.
"""
import asyncio
import contextlib
import inspect
import io
import random
import traceback
import async_timeout
from discomaton.factories import bookbinding
import discord
from neko2.engine import commands   # command decorator
from neko2.shared import scribe     # scribe


class AdminCog(scribe.Scribe):
    """Holds administrative utilities"""
    def __init__(self, bot):
        self.bot = bot
    
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

    @commands.command(hidden=True)
    async def error(self, ctx):
        """Tests error handling."""
        raise random.choice((
            Exception, RuntimeError, IOError, BlockingIOError,
            UnboundLocalError, UnicodeDecodeError, SyntaxError, SystemError,
            NotImplementedError, FileExistsError, FileNotFoundError,
            InterruptedError, EOFError, NameError, AttributeError, ValueError,
            KeyError, FutureWarning, DeprecationWarning,
            PendingDeprecationWarning, discord.ClientException,
            discord.DiscordException, discord.HTTPException,
            commands.CommandError, commands.DisabledCommand,
            commands.CheckFailure, commands.MissingRequiredArgument,
            commands.BotMissingPermissions('abc'), commands.UserInputError,
            commands.TooManyArguments, commands.NoPrivateMessage,
            commands.MissingPermissions, commands.NotOwner
        ))()
                   
    @commands.command(hidden=True)
    async def exec(self, ctx, *, command):
        self.logger.warning(
            f'{ctx.author} executed {command!r} in {ctx.channel}')
        binder = bookbinding.StringBookBinder(ctx, max_lines=50)
        
        try:
            binder.add_line('Output:')
            if command.count('\n') == 0:
                with async_timeout.timeout(10):
                    if command.startswith('await '):
                        command = command[6:]
                    result = eval(command)
                    if inspect.isawaitable(result):
                        binder.add_line(f'> automatically awaiting result {result}')
                        result = await result
                    binder.add(str(result))
            else:
                with async_timeout.timeout(60):
                    with io.StringIO() as output_stream:
                        with contextlib.redirect_stdout(output_stream):
                            with contextlib.redirect_stderr(output_stream):
                                wrapped_command = (
                                    'async def _aexec(ctx):\n' +
                                    '\n'.join(f'    {line}' 
                                              for line 
                                              in command.split('\n')) +
                                    '\n')
                                exec(wrapped_command)
                                result = await (locals()['_aexec'](ctx))
                        binder.add(output_stream.getvalue())
                        binder.add('Returned ' + str(result))
        except:
            binder.add(traceback.format_exc())
        finally:
            await binder.start()

def setup(bot):
    bot.add_cog(AdminCog(bot))
