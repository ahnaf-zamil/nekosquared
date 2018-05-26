#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Builtin extension that is loaded to implement a custom help method, ping

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
import asyncio  # Async subprocess.
import contextlib
import copy  # Shallow copies.
import inspect  # Introspection
import io
import os
import random
import shutil
import subprocess  # Sync subprocess.
import sys  # System streams and bits
import time  # Timing stuff.
import traceback  # Error stuff
import typing  # Type checking bits and pieces.

import async_timeout
from cached_property import cached_property
import discord
from discord.ext import commands as dpycmds
from discord import embeds  # Embeds.

import discomaton  # Finite state machines.
import discomaton.util.pag
from discomaton.factories import bookbinding
import neko2  # n2 versioning
from neko2 import modules  # Loadable modules
from neko2.shared import commands, fuzzy, string, collections, alg, traits
import neko2.shared.morefunctools
from neko2.engine import extrabits  # Internal cog type

lines_of_code = None


def count_loc():
    """
    Counts the lines of code.
    """
    global lines_of_code
    try:
        extrabits.InternalCogType.logger.info('Counting and caching LOC.')
        lines_of_code = subprocess.check_output(
            [
                '/bin/bash',
                '-c',
                'wc -l $(find neko2 neko2tests discomaton '
                'discomaton-examples config -name "*.py" '
                '-o -name "*.sql" -o -name '
                '"*.json" -o -name "*.yaml") '
            ],
            universal_newlines=True)
        # Gets the number from the total line of the output for wc
        lines_of_code = (
            lines_of_code.strip().split('\n')[-1]
                                 .strip()
                                 .split(' ')[0]
        )
    finally:
        return


# Count initial LOC.
count_loc()


class Builtins(traits.CogTraits):
    def __init__(self, bot):
        """Init the cog."""
        try:
            bot.remove_command('help')
        except:
            pass
        
        self.bot = bot

    # Prevents webhook exploits spamming the hell out of this.
    async def __global_check(self, ctx):
        """
        Prevents us, while not in debug mode, from responding to other
        bots what-so-ever.

        This is a useful thing to have in debugging mode for testing.
        """
        return self.bot.debug or not ctx.author.bot

    @property
    def uptime(self) -> str:
        """Get the uptime of the bot as a string."""
        uptime = self.bot.uptime
        if uptime >= 60 * 60 * 24:
            uptime /= (60.0 * 60 * 24)
            uptime = round(uptime, 1)
            uptime = f'{uptime} day{"s" if uptime != 1 else ""}'
        elif uptime >= 60 * 60:
            uptime /= (60.0 * 60)
            uptime = round(uptime, 1)
            uptime = f'{uptime} hour{"s" if uptime != 1 else ""}'
        elif uptime >= 60:
            uptime /= 60.0
            uptime = round(uptime, 1)
            uptime = f'{uptime} minute{"s" if uptime != 1 else ""}'
        else:
            uptime = int(uptime)
            uptime = f'{uptime} second{"s" if uptime != 1 else ""}'

        return uptime

    @property
    def lines_of_code(self):
        """Gets the #lines of code as a string description."""
        if lines_of_code is not None:
            return f'{int(lines_of_code):,} lines of code'
        else:
            return 'No idea on how many lines of code'

    @commands.command(brief='Gets the developer\'s high score (lines of code)')
    async def loc(self, ctx):
        await ctx.send(self.lines_of_code)

    @commands.command(brief='Shows the license for this bot.')
    async def mylicense(self, ctx):
        """Displays the current license agreement for source code usage."""
        binder = bookbinding.StringBookBinder(ctx, suffix='```', prefix='```',
                                              max_lines=25)
        async with self.file('LICENSE') as fp:
            for line in await fp.readlines():
                binder.add(line)
        binder.start()

    @commands.command(brief='Links to the GitHub repository.',
                      aliases=['github', 'repo', 'bitbucket', 'svn'])
    async def git(self, ctx, who: discord.Member = None):
        """Gets the repository that the bot's source code is hosted in."""
        who = who or ctx.author
        await ctx.send(f'{who.mention}: <{neko2.__repository__}>')

    @commands.command(brief='Links to the Trello page.')
    async def trello(self, ctx, who: discord.Member = None):
        """Gets the Trello page for the bot development."""
        who = who or ctx.author
        await ctx.send(f'{who.mention}: <{neko2.__trello__}>')

    @commands.command(brief='Gets usage information for commands.')
    async def help(self, ctx, *, query: str = None):
        """
        If a command name is given, perform a search for that command and
        display info on how to use it. Otherwise, if nothing is provided, then
        a list of available commands is output instead.

        Provide the `--compact` or `-c` flag to view a compact list of commands
        and aliases to run. This is the original help dialog.
        """
        if not query:
            await self._new_dialog(ctx)
        elif query.lower() in ('-c', '--compact'):
            await self._summary_screen(ctx, bool(query))
        else:
            result = await self.get_best_match(query, ctx)
            if result:
                # Unpack
                real_match, command = result
                await self._command_page(ctx, query, command, real_match)
            else:
                await ctx.send(f'No command found that matches `{query}`',
                               delete_after=15)

    # noinspection PyUnresolvedReferences
    @staticmethod
    async def _new_dialog(ctx):
        embeds = []
        # Includes those that cannot be run.
        all_cmds = list(sorted(ctx.bot.commands, key=str))

        commands = []

        for potential_command in all_cmds:
            # noinspection PyUnresolvedReferences
            try:
                if await potential_command.can_run(ctx):
                    commands.append(potential_command)
            except:
                # E.g. NotOwner is raised.
                continue

        # We only show 10 commands per page.
        for i in range(0, len(commands), 12):
            embed_page = discord.Embed(
                title='Neko² commands',
                colour=alg.rand_colour())
            # embed_page.set_thumbnail(url=ctx.bot.user.avatar_url)

            next_commands = commands[i:i + 12]

            for command in next_commands:
                # Special space char
                name = command.name

                embed_page.add_field(
                    name=name,
                    # If we put a zero space char first, and follow with an
                    # EM QUAD, it won't strip the space.
                    value='\u200e\u2001' + (command.brief or '—'),
                    inline=False)

            embeds.append(embed_page)

        discomaton.EmbedBooklet(pages=embeds, ctx=ctx).start()

    @staticmethod
    async def _command_page(ctx, query, command, real_match):
        """
        Replies with info for the given command object.
        :param ctx: the context to reply to.
        :param query: the original query.
        :param command: the command to document.
        :param real_match: true if we had a perfect match, false if we fell
            back to fuzzy.
        """
        colour = 0x9EE4D9

        pages = []

        def new_page():
            next_page = embeds.Embed(
                title=f'Help for {ctx.bot.command_prefix}'
                      f'{command.qualified_name}',
                colour=colour)
            pages.append(next_page)
            return next_page

        # Generate the first page.
        new_page()

        brief = command.brief
        full_doc = command.help if command.help else ''
        full_doc = string.remove_single_lines(full_doc)
        examples = getattr(command, 'examples', [])
        signature = command.signature
        cog = command.cog_name

        parent = command.full_parent_name
        cooldown = getattr(command, '_buckets')

        if cooldown:
            cooldown = getattr(cooldown, '_cooldown')

        description = [
            f'```markdown\n{ctx.bot.command_prefix}{signature}\n```'
        ]

        if cog:
            pages[-1].add_field(
                name='Module defined in',
                value=string.pascal2title(cog))

        if not real_match:
            description.insert(0, f'Closest match for `{query}`')

        if brief:
            description.append(brief)
        pages[-1].description = '\n'.join(description)

        # We detect this later to see if we should start paginating if the
        # description is too long.
        should_paginate_full_doc = False

        if full_doc and len(full_doc) >= 500:
            pages[-1].add_field(
                name='Detailed description',
                value=f'{string.trunc(full_doc, 500)}\n\nContinued on the '
                      'next page...')

            should_paginate_full_doc = True
        elif full_doc:
            pages[-1].add_field(name='Detailed description', value=full_doc)

        if examples:
            examples = '\n'.join(
                f'- `{ctx.bot.command_prefix}{command.qualified_name} '
                f'{ex}`' for ex in examples)
            pages[-1].add_field(name='Examples', value=examples)

        if isinstance(command, commands.BaseGroupMixin):
            _children = sorted(command.commands, key=lambda c: c.name)
            children = []

            for child in _children:
                try:
                    if await child.can_run(ctx):
                        children.append(child)
                except:
                    # This prevents crashing if the child has an is_owner
                    # check on it, as dpy raises a NotOwner exception rather
                    # than returning False in this case.
                    pass
        else:
            children = []

        if children:
            children = ', '.join(f'`{child.name}`' for child in children)
            pages[-1].add_field(name='Child commands', value=children)

        if parent:
            pages[-1].add_field(name='Parent', value=f'`{parent}`')

        if cooldown:
            timeout = cooldown.per
            if timeout.is_integer():
                timeout = int(timeout)

            pages[-1].add_field(
                name='Cooldown policy',
                value=(
                    f'{cooldown.type.name.title()}-scoped '
                    f'per {cooldown.rate} '
                    f'request{"s" if cooldown.rate - 1 else ""} '
                    f'with a timeout of {timeout} '
                    f'second{"s" if timeout - 1 else ""}'))

        # pages[-1].set_thumbnail(url=ctx.bot.user.avatar_url)

        if hasattr(command.callback, '_probably_broken'):
            pages[0].add_field(name='In active development',
                               value='Expect voodoo-type shit behaviour!')

        if should_paginate_full_doc:
            # Generate pages using the Discord.py paginator.
            pag = discomaton.RapptzPaginator(
                prefix='', suffix='', max_size=1024)

            for line in full_doc.splitlines():
                pag.add_line(line)

            for page in pag.pages:
                next_page = new_page()
                next_page.description = pages[0].description
                next_page.add_field(name='Detailed description',
                                    value=page)

        if len(pages) == 0:
            raise RuntimeError('Empty help')
        elif len(pages) == 1:
            await ctx.send(embed=pages[-1])
        else:
            # Paginate using embed paginator
            await discomaton.EmbedBooklet(
                pages=pages,
                ctx=ctx).start()

    @staticmethod
    async def _summary_screen(ctx, show_aliases=False):
        """
        Replies with a list of all commands available.
        :param ctx: the context to reply to.
        """
        pages = []

        # Get commands this user can run, only.
        async def get_runnable_commands(mixin):
            cmds = []

            for command in mixin.commands:
                # If an error is raised by checking permissions for a command,
                # then just ignore that command.
                try:
                    if await command.can_run(ctx):
                        cmds.append(command)
                except:
                    pass
            return cmds

        current_page = ''

        runnable_commands = await get_runnable_commands(ctx.bot)

        unordered_strings = {}
        for c in runnable_commands:
            if show_aliases:
                for alias in c.aliases:
                    unordered_strings[alias] = c
            unordered_strings[c.name] = c

        # Order here now we have the aliases, otherwise the aliases are
        # ignored from the order and it looks kinda dumb.
        keys = list(unordered_strings.keys())
        keys.sort()
        strings = collections.OrderedDict()
        for k in keys:
            strings[k] = unordered_strings[k]

        for i, (name, command) in enumerate(strings.items()):
            if i % 50 == 0 and i < len(strings):
                if current_page:
                    current_page += ' _continued..._'
                    pages.append(current_page)
                    current_page = ''

            if isinstance(command, commands.BaseGroupMixin):
                # This is a command group. Only show if we have at least one
                # available sub-command, though.
                if len(await get_runnable_commands(command)) > 0:
                    name = f'{name}...'

            if current_page:
                current_page += ', '
            current_page += f'`{name}`'

        if current_page:
            pages.append(current_page)

        def mk_page(body):
            """
            Makes a new page with the current body. This is a template
            for embeds to ensure a consistent layout if we can't fit the
            commands list on one page.
            """
            page = embeds.Embed(
                title='Available Neko² Commands',
                colour=0x000663,
                description='The following can be run in this channel:\n\n'
                            f'{body}')
            page.set_footer(text='Commands proceeded by ellipses signify '
                                 'command groups with sub-commands available.')
            page.add_field(
                name='Want more information?',
                value=f'Run `{ctx.bot.command_prefix}help <command>` '
                      f'for more details on a specific command!',
                inline=False)
            page.set_thumbnail(url=ctx.bot.user.avatar_url)
            return page

        if len(pages) == 0:
            await ctx.send('You cannot run any commands here.')
        elif len(pages) == 1:
            await ctx.send(embed=mk_page(pages.pop()))
        else:
            page_embeds = []
            for page in pages:
                page_embeds.append(mk_page(page))

            fsm = discomaton.EmbedBooklet(pages=page_embeds,
                                          ctx=ctx)

            await fsm.start()

    @property
    def all_commands(self) -> typing.FrozenSet[commands.BaseCommand]:
        """
        Generates a set of all unique commands recursively.
        """
        return frozenset([command for command in self.bot.walk_commands()])

    @classmethod
    def gen_qual_names(cls, command: commands.Command):
        aliases = [command.name, *command.aliases]

        if command.parent:
            parent_names = [*cls.gen_qual_names(command.parent)]

            for parent_name in parent_names:
                for alias in aliases:
                    yield f'{parent_name} {alias}'
        else:
            yield from aliases

    @cached_property
    def alias2command(self) -> typing.Dict:
        """
        Generates a mapping of all fully qualified command names and aliases
        to their respective command object.
        """
        mapping = {}

        for command in self.bot.walk_commands():
            for alias in self.gen_qual_names(command):
                mapping[alias] = command
        return mapping

    async def get_best_match(self, string: str, context) \
            -> typing.Optional[typing.Tuple[bool, commands.BaseCommand]]:
        """
        Attempts to get the best match for the given string. This will
        first attempt to resolve the string directly. If that fails, we will
        instead use fuzzy string matching. If no match above a threshold can
        be made, we give up.

        We take the context in order to only match commands we can actually
        run (permissions).

        The result is a 2-tuple of a boolean and a command. If the output
        is instead None, then nothing was found. The boolean of the tuple is
        true if we have an exact match, or false if it was a fuzzy match.
        """
        alias2command = self.alias2command

        if string in alias2command:
            command = alias2command[string]
            try:
                if context.author.id == context.bot.owner_id:
                    return True, command
                elif await command.can_run(context):
                    return True, command
            except:
                pass

        try:
            # Require a minimum of 60% match to qualify. The bot owner
            # gets to see all commands regardless of whether they are
            # accessible or not.
            if context.author.id == context.bot.owner_id:
                result = fuzzy.extract_best(
                    string,
                    alias2command.keys(),
                    scoring_algorithm=fuzzy.deep_ratio,
                    min_score=60)

                if not result:
                    return None
                else:
                    guessed_name, score = result

                return score == 100, alias2command[guessed_name]
            else:
                score_it = fuzzy.extract(
                    string,
                    alias2command.keys(),
                    scoring_algorithm=fuzzy.deep_ratio,
                    min_score=60,
                    max_results=None)

                for guessed_name, score in score_it:
                    can_run = False
                    next_command = alias2command[guessed_name]

                    try:
                        can_run = await next_command.can_run(context)
                        can_run = can_run and next_command.enabled
                    except:
                        # Also means we cannot run
                        pass

                    if can_run:
                        return score == 100, next_command
        except KeyError:
            pass

        return None

    @cached_property
    async def get_commit(self):
        """
        Gets the most recent commit.
        :return:
        """
        # Returns a tuple of how long ago, the body, and the number of commits.
        # %ar = how long ago
        # %b  = body
        # %h  = shortened hash
        # $(git log --oneline | wc -l) - commit count.

        f1 = asyncio.create_subprocess_exec(
            'git',
            'log',
            '--pretty=%ar',
            '--relative-date',
            '-n1',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
            stdin=asyncio.subprocess.DEVNULL)

        f2 = asyncio.create_subprocess_exec(
            'git', 'log', '--pretty=%s%n%n%b', '-n1',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
            stdin=asyncio.subprocess.DEVNULL)

        f3 = asyncio.create_subprocess_shell(
            'git log --oneline | wc -l',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
            stdin=asyncio.subprocess.DEVNULL)

        f1_res, f2_res, f3_res = await asyncio.gather(f1, f2, f3)

        return (
            b''.join([await f1_res.stdout.read()]).decode('utf-8').strip(),
            b''.join([await f2_res.stdout.read()]).decode('utf-8').strip(),
            int(b''.join([await f3_res.stdout.read()]).decode('utf-8'))
        )

    @commands.command(name='uptime', brief='Shows how long I have been alive '
                                           'for.')
    async def uptime_cmd(self, ctx):
        """Determines the monotonic runtime of the bot."""
        await ctx.send(self.uptime)

    @commands.command(aliases=['v', 'ver', 'about'],
                      brief='Shows versioning info, and some other things.')
    async def version(self, ctx):
        """Shows versioning information and some other useful statistics."""
        author = neko2.__author__
        licence = neko2.__license__
        repo = neko2.__repository__
        version = neko2.__version__
        uptime = self.uptime
        docstring = inspect.getdoc(neko2)
        if docstring:
            # Ensures the license is not included in the description, as that
            # is rather long.
            docstring = ''.join(docstring.split('===', maxsplit=1)[0:1])

            docstring = [
                string.remove_single_lines(inspect.cleandoc(docstring))]
        else:
            docstring = []

        docstring.append(f'_Licensed under the **{licence}**_')

        embed = embeds.Embed(
            title=f'Neko² v{version}',
            colour=0xc70025,
            description='\n\n'.join(docstring),
            url=repo)

        # Most recent changes
        # Must do in multiple stages to allow the cached property to do
        # magic first.
        commit = self.get_commit
        when, update, count = await commit

        embed.add_field(name=f'Update #{count} ({when})',
                        value=string.trunc(update, 1024), inline=False)

        embed.set_author(name=author)

        embed.set_footer(text=f'Uptime: {uptime}')
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)

        embed.add_field(name='Developer EXP', value=self.lines_of_code)
        await ctx.send(embed=embed)

    @commands.command(brief='Shows the current latencies for the me.')
    async def ping(self, ctx):
        """
        Checks whether I am online and responsive or not.
        """
        start = time.monotonic()
        message = await ctx.send(f'Pong!')
        rtt = (time.monotonic() - start) * 1000
        await message.edit(
            content=f'Pong! (Latency: ~{ctx.bot.latency * 1000:,.2f}ms | '
                    f'`ACK` time: ~{rtt:,.2f}ms | '
                    f'System local time: `{time.asctime()}`)')

    async def _load_extension(self, namespace, recache=True) -> float:
        """
        Loads a given extension into the bot, returning the time taken to
        load it. If the extension is already present, an ImportWarning is
        raised.
        """
        if namespace in self.bot.extensions:
            raise ImportWarning(f'{namespace} extension is already loaded.')

        start_time = time.monotonic()
        self.bot.load_extension(namespace)
        ttr = time.monotonic() - start_time
        # Recache LOC.
        if recache:
            self.bot.loop.create_task(self.run_in_io_executor(count_loc))
        self.flush_command_cache()
        return ttr

    async def _unload_extension(self, namespace, recache=True) -> float:
        """
        Unloads a given extension from the bot, returning execution time.
        If no extension matching the namespace is found, a ModuleNotFoundError
        is raised.
        """
        if namespace.startswith('neko2.engine'):
            raise PermissionError('Seems that this is an internal extension. '
                                  'These cannot be dynamically unloaded from '
                                  'the bot engine. Please restart instead.')

        elif namespace not in self.bot.extensions:
            raise ModuleNotFoundError(
                f'{namespace} was not loaded into this bot instance, and so '
                'was not able to be unloaded.')

        else:
            start_time = time.monotonic()
            self.bot.unload_extension(namespace)
            ttr = time.monotonic() - start_time
            # Recache LOC.
            if recache:
                self.bot.loop.create_task(self.run_in_io_executor(count_loc))

            self.flush_command_cache()
            return ttr

    @commands.is_owner()
    @commands.command(hidden=True, brief='Loads an extension into me.')
    async def load(self, ctx, *, namespace):
        """Makes me load a given extension from disk."""
        try:
            secs = await self._load_extension(namespace)
        except ImportWarning as ex:
            await ctx.send(embed=discord.Embed(
                title=type(ex).__qualname__,
                description=str(ex),
                colour=0xffff00))
        except ModuleNotFoundError as ex:
            await ctx.send(embed=discord.Embed(
                title=type(ex).__qualname__,
                description=str(ex),
                colour=0xffff00))
        except Exception as ex:
            await ctx.send(embed=discord.Embed(
                title=type(ex).__qualname__,
                description=str(ex),
                colour=0xff0000))
            tb = ''.join(traceback.format_exc())
            pag = discomaton.Paginator(prefix='```', suffix='```')
            pag.add(tb)
            for page in pag.pages:
                await ctx.send(page)
        else:
            await ctx.send(embed=discord.Embed(
                title=f'Loaded `{namespace}`',
                description=f'Successfully loaded extension `{namespace}` in '
                            f'approximately {secs:,.2f}s.',
                colour=0x00ff00
            ))

    @commands.is_owner()
    @commands.command(hidden=True, brief='Unloads a given extension from me.')
    async def unload(self, ctx, *, namespace):
        """Unloads the given extension from my code."""
        try:
            secs = await self._unload_extension(namespace)
        except ModuleNotFoundError as ex:
            await ctx.send(embed=discord.Embed(
                title=type(ex).__qualname__,
                description=str(ex),
                colour=0xffff00))
        except Exception as ex:
            await ctx.send(embed=discord.Embed(
                title=type(ex).__qualname__,
                description=str(ex),
                colour=0xff0000))
            tb = ''.join(traceback.format_exc())
            pag = discomaton.Paginator(prefix='```', suffix='```')
            pag.add(tb)
            for page in pag.pages:
                await ctx.send(page)
        else:
            await ctx.send(embed=discord.Embed(
                title=f'Unloaded `{namespace}`',
                description=f'Successfully unloaded extension `{namespace}` in'
                            f' approximately {secs:,.2f}s.',
                colour=0x00ff00
            ))

    @commands.is_owner()
    @commands.command(hidden='True', brief='Reloads an extension.')
    async def reload(self, ctx, *, namespace=None):
        """
        Reloads a given extension. If the extension is not specified, then all
        loaded extensions (excluding builtins) are reloaded.
        """
        if namespace is None:
            log = []
            error_count = 0
            unloaded_count = 0
            loaded_count = 0

            start_time = time.monotonic()
            with ctx.typing():
                log.append(f'Unloading `discomaton` cached module data.')

                try:
                    del sys.modules['discomaton']
                except:
                    pass

                log.append(f'Unloading `neko2` cached module data.')

                try:
                    del sys.modules['neko2']
                except:
                    pass

                log.append('\n' + '-' * 50 + '\n')

                unloaded_extensions = []
                for extension in copy.copy(ctx.bot.extensions):
                    if extension.startswith('neko2.engine'):
                        # Ignore internals
                        continue

                    try:
                        secs = await self._unload_extension(extension, False)
                    except Exception as ex:
                        log.append(f'Unloading `{extension}` failed. '
                                   f'{type(ex).__qualname__}: {ex}')
                        error_count += 1
                    else:
                        log.append(f'Unloaded `{extension}` in approximately '
                                   f'{secs*1000:,.2f}ms')
                        unloaded_count += 1
                        unloaded_extensions.append(extension)

                # Reload.
                for extension in frozenset((*modules.modules,
                                            *unloaded_extensions)):
                    try:
                        secs = await self._load_extension(extension, False)
                    except Exception as ex:
                        log.append(f'Loading `{extension}` failed. '
                                   f'{type(ex).__qualname__}: {ex}')
                        error_count += 1
                    else:
                        log.append(f'Loaded `{extension}` in approximately '
                                   f'{secs*1000:,.2f}ms')
                        loaded_count += 1

            time_taken = time.monotonic() - start_time

            book = bookbinding.StringBookBinder(ctx, max_lines=None,
                                                timeout=30)

            book.add_line('Completed operation in approximately '
                          f'**{time_taken*1000:,.2f}ms**')
            book.add_line(f'Unloaded **{unloaded_count}**, '
                          f'loaded **{loaded_count}**')
            book.add_line(f'Encountered **{error_count} '
                          f'error{"s" if error_count - 1 else ""}**')
            book.add_line('')
            book.add_line('_See following pages for logs._')

            book.add_break()

            for line in log:
                book.add_line(line)

            # Recache LOC.
            self.bot.loop.create_task(self.run_in_io_executor(count_loc))

            book.start()
        else:
            await self.unload.callback(self, ctx, namespace=namespace)
            await self.load.callback(self, ctx, namespace=namespace)

    @commands.command(brief='Determines if you can run the command here.')
    async def canirun(self, ctx, command):
        command = ctx.bot.get_command(command)
        if command is None:
            return await ctx.send('That command does not exist...',
                                  delete_after=5)

        try:
            can_run = await command.can_run(ctx)
        except Exception as ex:
            await ctx.send('You cannot run the command here, because: '
                           f'`{type(ex).__name__}: {ex!s}`')
        else:
            await ctx.send(f'You {can_run and "can" or "cannot"} run this '
                           'command here.')

    def flush_command_cache(self):
        try:
            del self.__dict__['alias2command']
        except KeyError:
            pass

    async def on_connect(self):
        """
        Due to how this works, the cache will potentially get created
        before the other cogs get loaded. We thus should remove the
        command cache when we connect to prevent the help utility from
        functioning incorrectly.
        """
        self.flush_command_cache()

    # @staticmethod
    # async def __local_check(ctx):
    #     return await ctx.bot.is_owner(ctx.author)

    @commands.is_owner()
    @commands.command(aliases=['stop', 'die'])
    async def restart(self, ctx):
        """
        Kills the bot. If it is running as a systemd service, this should
        cause the bot to restart.
        """
        commands.acknowledge(ctx)
        await asyncio.sleep(2)
        await ctx.bot.logout()

    @commands.is_owner()
    @commands.command(hidden=True)
    async def error(self, ctx, discord: bool = False):
        """Tests error handling."""
        if discord:
            from discord.ext.commands import errors

            error_type = random.choice((
                errors.TooManyArguments,
                errors.CommandOnCooldown,
                errors.DisabledCommand,
                errors.CommandNotFound,
                errors.NoPrivateMessage,
                errors.MissingPermissions,
                errors.NotOwner,
                errors.BadArgument,
                errors.MissingRequiredArgument,
                errors.CheckFailure,
                errors.CommandError,
                errors.DiscordException,
                errors.CommandInvokeError))
        else:
            error_type = random.choice((
                Exception, RuntimeError, IOError, BlockingIOError,
                UnboundLocalError, UnicodeDecodeError, SyntaxError,
                SystemError, NotImplementedError, FileExistsError,
                FileNotFoundError, InterruptedError, EOFError, NameError,
                AttributeError, ValueError, KeyError, FutureWarning,
                DeprecationWarning, PendingDeprecationWarning))

        await ctx.send(f'Raising {error_type.__qualname__}')
        raise error_type

    @commands.is_owner()
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
            binder.start()

    @commands.is_owner()
    @commands.command(hidden=True, rest_is_raw=True)
    async def shell(self, ctx, *, command):
        self.logger.warning(
            f'{ctx.author} executed shell {command!r} in {ctx.channel}')

        binder = bookbinding.StringBookBinder(ctx, max_lines=30,
                                              prefix='```bash',
                                              suffix='```')

        try:
            with async_timeout.timeout(600):
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
                    binder.add(out_stream.getvalue().replace('`', 'ˋ'))
        except:
            binder.add(traceback.format_exc())
        finally:
            binder.start()

    @commands.is_owner()
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

    @commands.is_owner()
    @commands.command(brief='Changes the avatar to the given URL.')
    async def setavatar(self, ctx, *, url):
        conn = await self.acquire_http()
        async with conn.request('get', url) as r, ctx.typing():
            await ctx.bot.user.edit(avatar=await r.read())
        commands.acknowledge(ctx)

    @commands.is_owner()
    @commands.command(brief='Shows host health, resource utilisation, etc.')
    async def syshealth(self, ctx):
        command = ('set -x',
                   'ps -eo euser,args,rss,thcount,%cpu,%mem | '
                   'grep -P "^($(whoami)|EUSER)"',
                   'uptime',
                   'free -hl',
                   'who -Ha',
                   'set +x')
        command = '(' + ' && '.join(command) + ') 2>&1'

        await self.shell.callback(self, ctx, command=command)

    @commands.is_owner()
    @commands.command(brief='Shows event loop information.')
    async def loophealth(self, ctx):
        all_tasks = asyncio.Task.all_tasks(loop=ctx.bot.loop)

        booklet = bookbinding.StringBookBinder(ctx,
                                               prefix='```',
                                               suffix='```',
                                               max_lines=None)
        summary = []

        for task in all_tasks:
            with io.StringIO() as fp:
                task.print_stack(file=fp)
                booklet.add_line(fp.getvalue())
                # noinspection PyProtectedMember
                # Repr, shorten it as it is obscenely long
                tup = task._repr_info()[1]
                summary.append(tup)
            booklet.add_break()

        booklet.add_break(to_start=True)
        summary = '\n'.join(summary)
        booklet.add(summary, to_start=True)
        booklet.add_line(f'{len(all_tasks)} coroutines in the loop.',
                         to_start=True)
        booklet.start()

    @commands.is_owner()
    @commands.command()
    async def redeploy(self, ctx: commands.Context, should_restart=None):
        """
        Redeploys Neko code. Provide '--rs' as an argument to restart the bot,
        otherwise the modules just get reloaded instead.
        """
        if should_restart:
            return await self.update.callback(self, ctx, '--mute', '--restart')
        else:
            await self.update.callback(self, ctx, '--mute')

            # Find the reload command and call it if it exists
            cmd = alg.find(lambda c: c.name == 'reload', ctx.bot.commands)

            if cmd:
                await self.reload.callback(self, ctx)
            else:
                await ctx.send('No reload command found.')

    @commands.is_owner()
    @commands.command(
        brief='Clears the stash, and ensures we are up to date with master, '
              'even if it means destroying the current code base. Use this to '
              'invoke a bot update remotely.')
    async def update(self, ctx, *args):
        """
        This will DM you the results.

        The following assumptions are made:
          - The current system user has permission to modify the `.git`
            directory, and modify the contents of this directory.
          - That git is installed.
          - That the current working directory contains the `.git` directory.

        As of v1.3, the bot will not automatically restart. To force the bot
        to restart, provide the `--restart` or `-r` flag with the command
        invocation.

        As of 2.13, run `--mute` or `-m` to not receive inbox spam.
        """

        should_restart = '--restart' in args or '-r' in args

        should_mute = '--mute' in args or '-m' in args

        # Ensure git is installed first
        git_path = shutil.which('git')

        commands.acknowledge(ctx)

        did_fail = False

        async with ctx.channel.typing():
            if not git_path:
                return await ctx.author.send('I can\'t seem to find git!')

            # Ensure that we have a `.git` folder in the current directory
            if os.path.exists('.git'):
                if os.path.isdir('.git'):
                    pass
                else:
                    return await ctx.author.send('.git is not a directory')
            else:
                return ctx.author.send('.git does not exist. Is this a repo?')

            with io.StringIO() as out_s:
                shell = os.getenv('SHELL')
                if shell is None:
                    shell = shutil.which('sh')
                    if shell is None:
                        shell = '?? '

                async def call(cmd):
                    nonlocal did_fail
                    out_s.write(f'{shell} -c {cmd}')
                    process = await asyncio.create_subprocess_shell(
                        cmd,
                        # encoding='utf-8',
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE)
                    out_s.write(f'> Invoked PID {process.pid}\n')
                    # Might deadlock?
                    out_s.write((await process.stdout.read()).decode())
                    out_s.write((await process.stderr.read()).decode())
                    code = process.returncode if process.returncode else 0

                    if code:
                        did_fail = True
                    out_s.write(f'> Terminated with code {code}\n\n')

                try:
                    await call(f'{git_path} fetch --all')
                    print('The following changes will be lost:')
                    await call(f'{git_path} diff --stat HEAD origin/master')
                    print('And replaced with')
                    await call(f'{git_path} show --stat | '
                               'sed "s/<.*@.*[.].*>/<email>/g"')
                    print()
                    print('Status:')
                    await call(f'{git_path} status --porcelain')
                    print()
                    print('Overwriting local history with remote history.')
                    await call(f'{git_path} reset --hard origin/$(git '
                               'rev-parse --symbolic-full-name --abbrev-ref '
                               'HEAD)')
                    await call(f'{git_path} stash list && {git_path} stash '
                               'drop; true')
                except BaseException as ex:
                    err = traceback.format_exception(
                        type(ex), ex, ex.__traceback__)
                    # Seems that lines might have newlines. This is annoying.

                    err = ''.join(err).split('\n')
                    err = [f'# {e_ln}\n' for e_ln in err]

                    # Remove last comment.
                    err = ''.join(err)[:-1]
                    out_s.write(err)
                    traceback.print_exception(type(ex), ex, ex.__traceback__)
                    did_fail = True
                finally:
                    log = out_s.getvalue()

                    self.logger.warning(
                        f'{ctx.author} Invoked destructive update from '
                        f'{ctx.guild}@#{ctx.channel}\n{log}')

                    p = dpycmds.Paginator()

                    for line in log.split('\n'):
                        p.add_line(line)

                    if not should_mute:
                        await ctx.author.send(
                            f'Will send {len(p.pages)} messages of output!')

                        for page in p.pages:
                            if page:
                                await ctx.author.send(page)

        if did_fail:
            await ctx.author.send('The fix process failed at some point '
                                  'I won\'t restart. Please update '
                                  'manually.')
            self.logger.fatal('Fix failure.')
        else:
            if should_restart:
                await ctx.send(
                    'The fix process succeeded. I will now '
                    'shut down!')
                self.logger.warning(
                    'Successful fix! Going offline in 2 seconds')
                await asyncio.sleep(2)
                await ctx.bot.logout()
            else:
                await ctx.send('Completed.', delete_after=10)

    @commands.cooldown(1, 30, commands.BucketType.guild)
    @commands.command(brief='Shows a summary of what this bot can see, the '
                            'bot\'s overall health and status, and software '
                            'versioning information')
    async def stats(self, ctx):
        import threading
        from datetime import timedelta
        from time import monotonic
        import platform
        import os

        # Calculates the ping, and will store our message response a little
        # later
        ack_time = 0

        def callback(*_, **__):
            nonlocal ack_time
            ack_time = monotonic()

        start_ack = monotonic()
        future = ctx.bot.loop.create_task(ctx.send('Getting ping!'))
        future.add_done_callback(callback)

        message = await future

        event_loop_latency = monotonic() - start_ack
        ack_time -= start_ack
        event_loop_latency -= ack_time
        # priority = os.getpriority(os.PRIO_PROCESS, os.getpid())

        # users = max(len(ctx.bot.users), len(list(ctx.bot.get_all_members())))
        tasks = len(asyncio.Task.all_tasks(loop=asyncio.get_event_loop()))

        stats = collections.OrderedDict({
            # 'Users': f'{users:,}',
            'Guilds': f'{len(ctx.bot.guilds):,}',
            # 'Channels': f'{len(list(ctx.bot.get_all_channels())):,}',
            # 'Private channels': f'{len(ctx.bot.private_channels):,}',
            'Shards': f'{ctx.bot.shard_count or 1:,}',
            'Commands': f'{len(frozenset(ctx.bot.walk_commands())):,}',
            'Aliases': f'{len(ctx.bot.all_commands):,}',
            'Cogs': f'{len(ctx.bot.cogs):,}',
            'Extensions': f'{len(ctx.bot.extensions):,}',
            'Futures': f'{tasks:,}',
            'Threads': f'{threading.active_count():,}',
            'Uptime': str(timedelta(seconds=ctx.bot.uptime)),
            'System uptime': str(timedelta(seconds=monotonic())),
            'L.O.C.': f'{int(lines_of_code or 0):,}',
            'Latency': f'{ctx.bot.latency * 1000:,.2f}ms; '
                       f'`ACK`: {ack_time * 1000:,.2f}ms',
            # 'Days since last accident': random.randrange(0, 100),
            'Loop latency': f'{event_loop_latency * 1e6:,.2f}µs',
            'Affinity': f'{", ".join(map(str, os.sched_getaffinity(0)))}',
            # 'Scheduling nice': f'{priority}',
            'Architecture': f'{platform.machine()} '
                            f'{" ".join(platform.architecture())}',
            # 'discord.py': f'v{discord.__version__}',
            # 'aiohttp': f'v{aiohttp.__version__}',
            # 'websockets': f'v{websockets.__version__}',
            'Python':
                f'{platform.python_implementation()} '
                f'{platform.python_version()}\n'
                f'{" ".join(platform.python_build()).title()}\n'
                f'{platform.python_compiler()}'
        })

        embed = discord.Embed(title='Statistics and specs for nerds',
                              colour=alg.rand_colour())

        # embed.set_thumbnail(url=ctx.bot.user.avatar_url)

        embed.set_footer(text=platform.platform())

        for name, value in stats.items():
            embed.add_field(name=name, value=value)

        await message.edit(content='', embed=embed)

        em = '\N{REGIONAL INDICATOR SYMBOL LETTER X}'

        @neko2.shared.morefunctools.always_background()
        async def later():
            try:
                await message.add_reaction(em)
                await ctx.bot.wait_for('reaction_add',
                                       timeout=300,
                                       check=lambda r, u:
                                       r.emoji == em and not u.bot
                                       and r.message.id == message.id
                                       and u.id == ctx.message.author.id)
            except asyncio.TimeoutError:
                try:
                    await message.clear_reactions()
                finally:
                    return
            else:
                try:
                    await commands.try_delete(message)
                    await commands.try_delete(ctx)
                finally:
                    return

        later()

    @commands.command(brief='Shows you what OS I am running.')
    async def os(self, ctx):
        modenv = os.environ
        modenv = dict(modenv)
        modenv['USER'] = modenv['USERNAME'] = 'Neko²'

        process = await asyncio.create_subprocess_shell(
            'screenfetch -N -p -d "-shell"',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            # Fool screenfetch into outputting false values for these options.
            env=modenv)

        stdout = (await process.stdout.read()).decode().replace('`', 'ˋ')
        stdout = f'```brainfuck\n{stdout}\n```'
        await ctx.send(stdout)

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

            start_time, execution_time = 0, 0

            loop = ctx.bot.loop

            def on_done(*_):
                nonlocal execution_time
                execution_time = time.monotonic() - start_time

            start_time = time.monotonic()
            future = loop.create_task(ctx.bot.invoke(new_ctx))
            future.add_done_callback(on_done)
            await future
            await ctx.send(f'`{ctx.message.content.replace("`", "ˋ")}`'
                           f' took **{execution_time*1000:,.2f}ms** to'
                           f' complete.')

        except Exception as ex:
            await ctx.send(f'{type(ex).__qualname__}: {ex}')

    @commands.command(brief='Sends an invite to let you add the bot to your '
                            'server.')
    async def invite(self, ctx):
        await ctx.send(f'{ctx.author.mention}: {ctx.bot.invite}')


def setup(bot):
    bot.add_cog(Builtins(bot))
