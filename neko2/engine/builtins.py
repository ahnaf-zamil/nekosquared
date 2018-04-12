#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Builtin extension that is loaded to implement a custom help method.
"""
import asyncio                             # Async subprocess.
import inspect                             # Inspection
import subprocess                          # Sync subprocess.
import time                                # Timing stuff.
import typing                              # Type checking bits and pieces.

from discord import embeds                 # Embeds.
import discomaton                          # Finite state machines.

import neko2
from neko2.engine import commands          # Command decorators.
from neko2.shared import fuzzy             # Fuzzy string matching.
from neko2.shared import string            # String voodoo.
from neko2.shared import traits            # Traits.


class Builtins(traits.CpuBoundPool):
    def __init__(self, bot):
        """Init the cog."""
        bot.remove_command('help')
        self.bot = bot

        try:
            lines_of_code: str = subprocess.check_output(
                [
                    '/bin/bash',
                    '-c',
                    'wc -l $(find neko2 -name "*.py" -o -name "*.sql" -o -name '
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
            if i % 30 == 0:
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


def setup(bot):
    bot.add_cog(Builtins(bot))
