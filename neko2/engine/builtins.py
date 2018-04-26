#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Builtin extension that is loaded to implement a custom help method.
"""
import asyncio                             # Async subprocess.
import copy                                # Shallow copies.
import inspect                             # Inspection
import subprocess                          # Sync subprocess.
import time                                # Timing stuff.
import traceback
import typing                              # Type checking bits and pieces.

import discord
from discord import embeds                 # Embeds.
import discomaton                          # Finite state machines.
from discomaton.factories import bookbinding

import neko2
from neko2 import modules
from neko2.shared import fuzzy, commands   # Fuzzy string matching.
from neko2.shared import string            # String voodoo.
from . import extrabits


class Builtins(extrabits.InternalCogType):
    def __init__(self, bot):
        """Init the cog."""
        super().__init__(bot)

        try:
            bot.remove_command('help')
        except:
            pass

        try:
            lines_of_code: str = subprocess.check_output(
                [
                    '/bin/bash',
                    '-c',
                    'wc -l $(find neko2 neko2-tests discomaton '
                    'discomaton-examples config -name "*.py" '
                    '-o -name "*.sql" -o -name '
                    '"*.json" -o -name "*.yaml") '
                ],
                universal_newlines=True)
            # Gets the number from the total line of the output for wc
            lines_of_code = (
                lines_of_code.strip()
                .split('\n')[-1]
                .strip()
                .split(' ')[0])

            self.lines_of_code = f'{int(lines_of_code):,} lines of code'
        except:
            self.lines_of_code = 'No idea on how many lines of code'

    @commands.command(brief='Gets usage information for commands.')
    async def help(self, ctx, *, query: str=None):
        """
        If a command name is given, perform a search for that command and
        display info on how to use it. Otherwise, if nothing is provided, then a
        list of available commands is output instead.
        """
        if not query:
            await self._summary_screen(ctx)
        else:
            result = await self.get_best_match(query, ctx)
            if result:
                # Unpack
                real_match, command = result
                await self._command_page(ctx, query, command, real_match)
            else:
                await ctx.send(f'No command found that matches `{query}`',
                               delete_after=15)

    @staticmethod
    async def _command_page(ctx, query, command, real_match):
        """
        Replies with info for the given command object.
        :param ctx: the context to reply to.
        :param query: the original query.
        :param command: the command to document.
        :param real_match: true if we had a perfect match, false if we fell back
            to fuzzy.
        """
        embed = embeds.Embed(
            title=f'Help for {ctx.bot.command_prefix}{command.qualified_name}',
            colour=0x000663)

        brief = command.brief
        full_doc = command.help if command.help else ''
        full_doc = string.remove_single_lines(full_doc)
        examples = getattr(command, 'examples', [])
        signature = command.usage if command.usage else command.signature
        parent = command.full_parent_name
        cooldown = getattr(command, '_buckets')

        if cooldown:
            cooldown = getattr(cooldown, '_cooldown')


        description = [f'```bash\n{ctx.bot.command_prefix}{signature}\n```']

        if not real_match:
            description.insert(0, f'Closest match for `{query}`')

        if brief:
            description.append(brief)
        embed.description = '\n'.join(description)

        if full_doc and len(full_doc) >= 1024:
            full_doc = full_doc[:1020] + '...'

        if full_doc:
            embed.add_field(name='Detailed description', value=full_doc)

        if examples:
            examples = '\n'.join(
                f'- `{ctx.bot.command_prefix}{command.qualified_name} '
                f'{ex}`' for ex in examples)
            embed.add_field(name='Examples', value=examples)

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
            embed.add_field(name='Child commands', value=children)

        if parent:
            embed.add_field(name='Parent', value=f'`{parent}`')

        if cooldown:
            timeout = cooldown.per
            if timeout.is_integer():
                timeout = int(timeout)

            embed.add_field(
                name='Cooldown policy',
                value=(
                    f'{cooldown.type.name.title()}-scoped '
                    f'per {cooldown.rate} '
                    f'request{"s" if cooldown.rate - 1 else ""} '
                    f'with a timeout of {timeout} '
                    f'second{"s" if timeout - 1 else ""}'))

        embed.set_thumbnail(url=ctx.bot.user.avatar_url)

        await ctx.send(embed=embed)

    @staticmethod
    async def _summary_screen(ctx):
        """
        Replies with a list of all commands available.
        :param ctx: the context to reply to.
        """
        pages = []

        # Get commands this user can run, only.
        async def get_runnable_commands(mixin):
            cmds = []
            for command in sorted(mixin.commands, key=lambda c: c.name):
                # If an error is raised by checking permissions for a command,
                # then just ignore that command.
                try:
                    if await command.can_run(ctx):
                        cmds.append(command)
                except:
                    pass
            return cmds

        current_page = ''
        for i, command in enumerate(await get_runnable_commands(ctx.bot)):
            if i % 50 == 0:
                if current_page:
                    pages.append(current_page)
                    current_page = ''

            name = command.name

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

    @property
    def alias2command(self) -> typing.Dict:
        """
        Generates a mapping of all fully qualified command names and aliases
        to their respective command object.
        """
        mapping = {}

        for command in self.all_commands:
            for alias in (command.name, *command.aliases):
                # Generate the name
                partitions = []
                if command.parent:
                    partitions.append(command.full_parent_name)
                partitions.append(alias)
                mapping[' '.join(partitions)] = command

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

    @staticmethod
    async def get_commit():
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
            encoding='utf-8',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
            stdin=asyncio.subprocess.DEVNULL)

        f2 = asyncio.create_subprocess_exec(
            'git', 'log', '--pretty=%s%n%n%b', '-n1',
            encoding='utf-8',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
            stdin=asyncio.subprocess.DEVNULL)

        f3 = asyncio.create_subprocess_shell(
            'git log --oneline | wc -l',
            encoding='utf-8',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
            stdin=asyncio.subprocess.DEVNULL)

        f1_res, f2_res, f3_res = await asyncio.gather(f1, f2, f3)

        return (
            b''.join([await f1_res.stdout.read()]).decode('utf-8').strip(),
            b''.join([await f2_res.stdout.read()]).decode('utf-8').strip(),
            int(b''.join([await f3_res.stdout.read()]).decode('utf-8'))
        )

    @commands.command(aliases=['v'])
    async def version(self, ctx):
        """Shows versioning information and some other useful statistics."""
        author = neko2.__author__
        licence = neko2.__license__
        repo = neko2.__repository__
        version = neko2.__version__
        uptime = ctx.bot.uptime
        docstring = inspect.getdoc(neko2)
        if docstring:
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
        when, update, count = await self.get_commit()

        embed.add_field(name=f'Update #{count} ({when})',
                        value=update, inline=False)

        embed.set_author(name=author)

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

        embed.set_footer(text=f'Uptime: {uptime}')
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)

        embed.add_field(name='Current high score', value=self.lines_of_code)
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        """
        Checks whether the bot is online and responsive or not.
        """
        start = time.monotonic()
        message = await ctx.send(f'Pong!')
        rtt = (time.monotonic() - start) * 1000
        await message.edit(
            content=f'Pong! (Latency: ~{ctx.bot.latency * 1000:,.2f}ms | '
                    f'`ACK` time: ~{rtt:,.2f}ms | '
                    f'System local time: `{time.asctime()}`)')

    async def _load_extension(self, namespace) -> float:
        """
        Loads a given extension into the bot, returning the time taken to
        load it. If the extension is already present, an ImportWarning is
        raised.
        """
        if namespace in self.bot.extensions:
            raise ImportWarning(f'{namespace} extension is already loaded.')

        start_time = time.monotonic()
        self.bot.load_extension(namespace)
        return time.monotonic() - start_time

    async def _unload_extension(self, namespace) -> float:
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
            return time.monotonic() - start_time

    @commands.is_owner()
    @commands.command(hidden=True, brief='Loads a given extension.')
    async def load(self, ctx, *, namespace):
        """Loads a given extension into the bot."""
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
    @commands.command(hidden=True, brief='Unloads a given extension.')
    async def unload(self, ctx, *, namespace):
        """Unloads the given extension from the bot."""
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
                description=f'Successfully unloaded extension `{namespace}` in '
                            f'approximately {secs:,.2f}s.',
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
                unloaded_extensions = []
                for extension in copy.copy(ctx.bot.extensions):
                    if extension.startswith('neko2.engine'):
                        # Ignore internals
                        continue
                    
                    try:
                        secs = await self._unload_extension(extension)
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
                        secs = await self._load_extension(extension)
                    except Exception as ex:
                        log.append(f'Loading `{extension}` failed. '
                                   f'{type(ex).__qualname__}: {ex}')
                        error_count += 1
                    else:
                        log.append(f'Loaded `{extension}` in approximately '
                                   f'{secs*1000:,.2f}ms')
                        loaded_count += 1

            time_taken = time.monotonic() - start_time
            
            book = bookbinding.StringBookBinder(ctx, max_lines=None)

            for line in log:
                book.add_line(line)

            book.add_line('')
            book.add_line('**Completed operation in approximately '
                          f'{time_taken*1000:,.2f}ms**')
            book.add_line(f'**Unloaded {unloaded_count}, loaded {loaded_count}'
                          '**')
            book.add_line(f'**Encountered {error_count} '
                          f'error{"s" if error_count - 1 else ""}**')

            await book.start()
        else:
            await self.unload.callback(self, ctx, namespace=namespace)
            await self.load.callback(self, ctx, namespace=namespace)


def setup(bot):
    bot.add_cog(Builtins(bot))
