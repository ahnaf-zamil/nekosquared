#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Cog holding owner-only administrative commands, such as those for restarting
the bot, inspecting/loading/unloading commands/cogs/extensions, etc.
"""
import asyncio
import collections
import contextlib
import inspect
import io
import os
import random
import time
import traceback

import async_timeout
from discomaton.factories import bookbinding
import discord
from neko2.shared import traits, commands, other


class AdminCog(traits.CogTraits):
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
        binder = bookbinding.StringBookBinder(ctx, max_lines=50,
                                              prefix='```python',
                                              suffix='```')

        try:
            binder.add_line('# Output:')
            if command.count('\n') == 0:
                with async_timeout.timeout(10):
                    if command.startswith('await '):
                        command = command[6:]
                    result = eval(command)
                    if inspect.isawaitable(result):
                        binder.add_line(
                            f'# automatically awaiting result {result}')
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
                        binder.add('# Returned ' + str(result))
        except:
            binder.add(traceback.format_exc())
        finally:
            await binder.start()

    @commands.command(hidden=True, rest_is_raw=True)
    async def shell(self, ctx, *, command):
        self.logger.warning(
            f'{ctx.author} executed shell {command!r} in {ctx.channel}')

        binder = bookbinding.StringBookBinder(ctx, max_lines=30,
                                              prefix='```bash',
                                              suffix='```')

        try:
            with async_timeout.timeout(600):
                fp = None
                # Random string name.
                temp_script = f'/tmp/{time.monotonic()}{time.time()}.sh'
                binder.add(f'# This will time out after 600 seconds...')
                binder.add(f'# Creating script {temp_script} (chmod 744)\n')
                with open(temp_script, 'w') as fp:
                    for line in command.split('\n'):
                        fp.write(f'{line}\n')
                os.chmod(temp_script, 0o744)

                # Execute script in shell.
                with io.StringIO() as out_stream:
                    process = await asyncio.create_subprocess_shell(
                        temp_script,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE)
                    stdout = (await process.stdout.read()).decode()
                    stderr = (await process.stderr.read()).decode()

                    if stdout:
                        out_stream.write('# ==/dev/stdout==\n')
                        if not stdout.endswith('\n'):
                            stdout += '\n'
                        out_stream.write(stdout)
                    if stderr:
                        out_stream.write('# ==/dev/stderr==\n')
                        if not stderr.endswith('\n'):
                            stderr += '\n'
                        out_stream.write(stderr)
                    if stdout or stderr:
                        out_stream.write('# ======EOF======\n')

                    out_stream.write(
                        '# Returned '
                        f'{process.returncode if process.returncode else 0}')
                    binder.add(out_stream.getvalue())
        except:
            binder.add(traceback.format_exc())
        finally:
            await binder.start()

    @commands.command(brief='Disables repl until restart.', hidden=True)
    async def lockdown(self, ctx):
        """In case I notice someone managed to get to the repl somehow."""
        try:
            ctx.bot.remove_command('exec')
        except BaseException as e:
            await ctx.send(f'Can\'t disable exec.\n{type(e).__name__}: {e}')
        else:
            await ctx.send('Disabled exec.')
        try:
            ctx.bot.remove_command('shell')
        except BaseException as e:
            await ctx.send(f'Can\'t disable shell.\n{type(e).__name__}: {e}')
        else:
            await ctx.send('Disabled shell.')
            
    @commands.command(brief='Changes the avatar to the given URL.')
    async def avatar(self, ctx, *, url):
        conn = await self.acquire_http()
        async with conn.request('get', url) as r, ctx.typing():
            await ctx.bot.user.edit(avatar=await r.read())
        commands.acknowledge(ctx)

    @commands.command(brief='Shows host health, resource utilisation, etc.')
    async def health(self, ctx):
        command = ('set -x',
                   'ps -eo euser,comm,rss,thcount,%cpu,%mem | '
                   'grep -P "^($(whoami)|EUSER)"',
                   'uptime',
                   'free -hl',
                   'who -Ha',
                   'set +x')
        command = '(' + ' && '.join(command) + ') 2>&1'

        await self.shell.callback(self, ctx, command=command)


class NonAdminCog:
    """Cogs for "admin" commands that can be run by anyone."""
    @commands.command(brief='Shows a summary of what this bot can see...')
    async def stats(self, ctx):
        import threading
        from datetime import timedelta
        from time import monotonic
        from neko2.engine import builtins
        
        # Calculates the ping, and will store our message response a little
        # later
        event_loop_latency = 0
        ack_time = 0
        
        def callback(*_, **__):
            nonlocal ack_time
            ack_time = monotonic()
        
        start_ack = monotonic()        
        future = asyncio.ensure_future(ctx.send('Loading!'))
        future.add_done_callback(callback)
        message = await future
        event_loop_latency = monotonic() - start_ack
        ack_time -= start_ack
        event_loop_latency -= ack_time
        
        stats = collections.OrderedDict({
            'Users': max(len(ctx.bot.users), len(list(ctx.bot.get_all_members()))),
            'Guilds': len(ctx.bot.guilds),
            'Channels': len(list(ctx.bot.get_all_channels())),
            'Private channels': len(ctx.bot.private_channels),
            'Shards': ctx.bot.shard_count or 1,
            'Commands': len(frozenset(ctx.bot.walk_commands())),
            'Commands (inc. aliases)': len(ctx.bot.all_commands),
            'Loaded cogs': len(ctx.bot.cogs),
            'Loaded extensions': len(ctx.bot.extensions),
            'Active tasks': len(asyncio.Task.all_tasks(
                                    loop=asyncio.get_event_loop())),
            'Active threads': threading.active_count(),
            'Uptime': str(timedelta(seconds=ctx.bot.uptime)),
            'System uptime': str(timedelta(seconds=monotonic())),
            'Lines of code at startup': builtins.lines_of_code,
            'Latency': f'{ctx.bot.latency * 1000:,.2f}ms',
            '`ACK` time': f'{ack_time * 1000:,.2f}ms',
            'Event loop latency': f'{event_loop_latency * 1000:,.2f}ms'
        })
        
        embed = discord.Embed(title='Statistics for nerds', 
                              colour=other.rand_colour())
        
        for name, value in stats.items():
            embed.add_field(name=name, value=value)
        
        await message.edit(content='', embed=embed)

def setup(bot):
    bot.add_cog(AdminCog(bot))
    bot.add_cog(NonAdminCog())
