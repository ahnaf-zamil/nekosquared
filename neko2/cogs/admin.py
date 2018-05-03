#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Cog holding owner-only administrative commands, such as those for restarting
the bot, inspecting/loading/unloading commands/cogs/extensions, etc.
"""
import asyncio
import collections
import contextlib
import copy
import inspect
import io
import os
import random
import time
import traceback
import websockets

import uvloop

import aiohttp
import async_timeout

from discomaton.factories import bookbinding
import discord
from neko2.shared import traits, commands, alg


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

    @commands.cooldown(1, 30, commands.BucketType.guild)
    @commands.command(brief='Shows a summary of what this bot can see, the '
                            'bot\'s overall health and status, and software '
                            'versioning information')
    async def stats(self, ctx):
        import threading
        from datetime import timedelta
        from time import monotonic
        from neko2.engine import builtins
        import platform
        import os

        # Calculates the ping, and will store our message response a little
        # later
        ack_time = 0

        def callback(*_, **__):
            nonlocal ack_time
            ack_time = monotonic()

        start_ack = monotonic()
        future = asyncio.ensure_future(ctx.send('Getting ping!'))
        future.add_done_callback(callback)
        message = await future
        event_loop_latency = monotonic() - start_ack
        ack_time -= start_ack
        event_loop_latency -= ack_time
        priority = os.getpriority(os.PRIO_PROCESS, os.getpid())

        users = max(len(ctx.bot.users), len(list(ctx.bot.get_all_members())))
        tasks = len(asyncio.Task.all_tasks(loop=asyncio.get_event_loop()))

        stats = collections.OrderedDict({
            'Users': f'{users:,}',
            'Guilds': f'{len(ctx.bot.guilds):,}',
            'Channels': f'{len(list(ctx.bot.get_all_channels())):,}',
            'Private channels': f'{len(ctx.bot.private_channels):,}',
            'Shards': f'{ctx.bot.shard_count or 1:,}',
            'Commands': f'{len(frozenset(ctx.bot.walk_commands())):,}',
            'Commands (inc. aliases)': f'{len(ctx.bot.all_commands):,}',
            'Loaded cogs': f'{len(ctx.bot.cogs):,}',
            'Loaded extensions': f'{len(ctx.bot.extensions):,}',
            'Active/sleeping tasks': f'{tasks:,}',
            'Active/sleeping threads': f'{threading.active_count():,}',
            'Uptime': str(timedelta(seconds=ctx.bot.uptime)),
            'System uptime': str(timedelta(seconds=monotonic())),
            'L.O.C. at startup': f'{int(builtins.lines_of_code or 0):,}',
            'Latency': f'{ctx.bot.latency * 1000:,.2f}ms; '
                       f'`ACK`: {ack_time * 1000:,.2f}ms',
            'Days since last accident': random.randrange(0, 100),
            'Event loop latency': f'{event_loop_latency * 1e6:,.2f}µs',
            'Affinity': f'{", ".join(map(str, os.sched_getaffinity(0)))}',
            'Scheduling nice': f'{priority}',
            'Architecture': f'{platform.machine()} '
                            f'{" ".join(platform.architecture())}',
            'discord.py': f'v{discord.__version__}',
            'aiohttp': f'v{aiohttp.__version__}',
            'websockets': f'v{websockets.__version__}',
            'Python implementation': f'{platform.python_implementation()} '
                                     f'{platform.python_version()}',
            'Python build': f'{" ".join(platform.python_build()).title()}\n'
                            f'{platform.python_compiler()}'
        })

        embed = discord.Embed(title='Statistics and specs for nerds',
                              colour=alg.rand_colour())

        embed.set_thumbnail(url=ctx.bot.user.avatar_url)

        embed.set_footer(text=platform.platform())

        for name, value in stats.items():
            embed.add_field(name=name, value=value)

        await message.edit(content='', embed=embed)

        em = '\N{REGIONAL INDICATOR SYMBOL LETTER X}'

        try:
            await ctx.bot.wait_for('reaction_add',
                                   timeout=300,
                                   check=lambda r, u:
                                   r.emoji == em and not u.bot
                                   and r.message.id == message.id)
        except asyncio.TimeoutError:
            try:
                await message.clear_reactions()
            finally:
                return
        else:
            try:
                await message.delete()
            finally:
                return

    @commands.command(brief='Times the execution of another command.')
    async def timeit(self, ctx, *, content):
        # Make a fake copy of the message to produce a new context with
        msg = copy.copy(ctx.message)
        msg.content = f'{ctx.prefix}{content}'

        try:
            new_ctx = await ctx.bot.get_context(msg)

            if not new_ctx.command:
                raise commands.CommandNotFound('That command doesn\'t exist.')

            if new_ctx.command == self.timeit:
                return await ctx.send('Don\'t be a smartass.')

            start_time = 0

            loop = ctx.bot.loop

            def on_done(*_):
                execution_time = time.monotonic() - start_time

                async def say_result():
                    await ctx.send(f'`{ctx.message.content.replace("`", "ˋ")}`'
                                   f' took **{execution_time*1000:,.2f}ms** to'
                                   f' complete.')

                loop.create_task(say_result())

            start_time = time.monotonic()
            future = loop.create_task(ctx.bot.invoke(new_ctx))
            future.add_done_callback(on_done)
            await future
        except Exception as ex:
            await ctx.send(f'{type(ex).__qualname__}: {ex}')


def setup(bot):
    bot.add_cog(AdminCog(bot))
    bot.add_cog(NonAdminCog())
