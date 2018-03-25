#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Builtin extension that is loaded to implement a custom help method.
"""
'''
import typing                              # Type checking bits and pieces

from discord import embeds                 # Embeds
from neko2.engine import commands          # Command decorators
from neko2.shared import fsa, fuzzy        # Finite state machines
from neko2.shared import string            # String voodoo


class HelpCog:
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
        embed = embeds.Embed(title=command.qualified_name, colour=0xc70025)

        brief = command.brief
        full_doc = command.help if command.help else ''
        full_doc = string.remove_single_lines(full_doc)
        examples = getattr(command, 'examples', [])
        signature = command.signature
        parent = command.full_parent_name

        description = [f'```css\n{signature}\n```']

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
                f'- `{command.qualified_name} {ex}`' for ex in examples)
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
            page_embeds = []
            for page in pages:
                page_embeds.append(mk_page(page))

            fsm = fsa.PagEmbed.from_embeds(
                page_embeds,
                bot=ctx.bot,
                invoked_by=ctx,
                timeout=300)

            await fsm.run()

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


def setup(bot):
    # Remove any existing help command first.
    bot.remove_command('help')
    bot.add_cog(HelpCog(bot))
'''

def setup(bot):
    import warnings
    warnings.warn('Please re-enable help once FSA is rewritten.')