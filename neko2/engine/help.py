#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Builtin extension that is loaded to implement a custom help method.
"""
import typing

import cached_property
import discord

from neko2.engine import commands          # Command decorators
from neko2.shared import traits            # Traits
from neko2.shared import fsa               # Finite state machines
from neko2.shared.other import fuzzy       # Traits


class HelpCog(traits.Scribe):
    def __init__(self, bot):
        self.bot = bot

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
            raise NotImplementedError

    async def _summary_screen(self, ctx):
        """
        Replies with a list of all commands available.
        :param ctx: the context to reply to.
        """
        pages = []

        # Get commands this user can run, only.
        def get_runnable_commands(mixin):
            cmds = []
            for command in sorted(mixin.commands, key=lambda c: c.name):
                # If an error is raised by checking permissions for a command,
                # then just ignore that command.
                try:
                    if command.can_run(ctx):
                        cmds.append(command)
                except:
                    pass
            return cmds

        current_page = ''
        for i, command in enumerate(get_runnable_commands(ctx.bot)):
            if i % 30 == 0:
                if current_page:
                    pages.append(current_page)
                    current_page = ''

            name = command.name

            if isinstance(command, commands.BaseGroupMixin):
                # This is a command group. Only show if we have at least one
                # available sub-command, though.
                if len(get_runnable_commands(command)) > 0:
                    name = f'{name}...'

            if current_page:
                current_page += ', '
            current_page += f'`{name}`'

        if current_page:
            pages.append(current_page)

        def mk_page(body):
            page = discord.Embed(
                title='Available Neko² Commands',
                colour=0xc70025,
                description='The following can be run in this channel:\n\n'
                            f'{body}')
            page.set_footer(text='Commands proceeded by ellipses signify '
                                 'command groups with sub-commands available.')
            page.set_thumbnail(url=ctx.bot.user.avatar_url)
            return page

        if len(pages) == 0:
            await ctx.send('You cannot run any commands here.')
        elif len(pages) == 1:
            await ctx.send(embed=mk_page(pages.pop()))
        else:
            embeds = []
            for page in pages:
                embeds.append(mk_page(page))

            fsm = fsa.PagEmbed.from_embeds(
                embeds,
                bot=ctx.bot,
                invoked_by=ctx,
                timeout=300)

            await fsm.run()

    @cached_property.cached_property
    def all_commands(self) -> typing.FrozenSet[commands.BaseCommand]:
        """
        Generates a set of all unique commands recursively.
        """
        return frozenset([command for command in self.bot.walk_commands()])

    @cached_property.cached_property
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

    def get_best_match(self, string: str) \
            -> typing.Optional[commands.BaseCommand]:
        """
        Attempts to get the best match for the given string. This will
        first attempt to resolve the string directly. If that fails, we will
        instead use fuzzy string matching. If no match above a threshold can
        be made, we give up.
        """
        if string in self.alias2command:
            return self.alias2command[string]
        else:
            try:
                # Require a minimum of 60% match to qualify.
                guessed_name = fuzzy.extract_best(
                    string,
                    self.alias2command.keys(),
                    scoring_algorithm=fuzzy.deep_ratio,
                    min_score=60)

                return self.alias2command[guessed_name]
            except KeyError:
                return None

    def __invalidate(self):
        for attr in 'all_commands', 'alias2command':
            try:
                del self.__dict__[attr]
            except:
                pass

    async def on_connect(self):
        self.__invalidate()

    async def on_add_command(self, _):
        self.__invalidate()

    async def on_remove_command(self, _):
        self.__invalidate()

def setup(bot):
    # Remove any existing help command first.
    bot.remove_command('help')
    bot.add_cog(HelpCog(bot))
