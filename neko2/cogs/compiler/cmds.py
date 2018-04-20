#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Main cog for command implementations for this module.
"""
import asyncio
import io


from discomaton.factories import bookbinding
import discord

from neko2.shared import traits, commands
from .toolchains import latex
from . import tools
from neko2.cogs.compiler.toolchains import compilers


class CompilerCog(traits.CogTraits):
    @commands.command(
        name='tex', aliases=['latex', 'texd', 'latexd'],
        brief='Attempts to parse the given LaTeX string and display a preview.')
    async def latex_cmd(self, ctx, *, content: str):
        """
        Add the `d` prefix to the command to delete your message before the
        response is shown.
        """
        delete = ctx.invoked_with.endswith('d')

        if delete:
            await commands.try_delete(ctx)

        async with ctx.typing():
            msg = await latex.LatexCogHelper.get_send_image(ctx, content)

        if not delete:
            await commands.wait_for_edit(ctx=ctx, msg=msg, timeout=1800)

    @commands.group(
        invoke_without_command=True,
        name='cc', aliases=['coliru', 'code', 'run'],
        brief='Attempts to execute the given code.')
    async def code_execution_group(self, ctx, *, arguments):
        """
        Attempts to execute some code by detecting the language in the
        syntax highlighting.

        Run `cc help` to view a list of the supported languages, or
        `cc help <lang>` to view the help for a specific language.
        """

        code_block = tools.code_block_re.match(arguments)

        if not code_block or len(code_block.groups()) < 2:
            return await ctx.send(
                'Please provide a valid syntax highlighted '
                'language. Check the help page out for this command '
                'for more details and instructions.')

        # Extract the code
        language, source = code_block.groups()
        language = language.lower()

        # Look up the language in the tables of supported languages.
        if language in ('r', 'cranr'):
            result = await compilers.targets[language](ctx, source)

            binder = bookbinding.StringBookBinder(ctx,
                                                  prefix='```',
                                                  suffix='```',
                                                  max_lines=40)

            # Last line is some error about rm not working.
            for line in result.output.split('\n'):
                if line == 'sh: 1: rm: Permission denied':
                    continue
                binder.add_line(line, dont_alter=True)

            binder.add_line(f'RESULT: {result.result.title()}')
            binder.add_line(f'STATE: {result.state.title()}')
            if result.fail_reason:
                binder.add_line(f'FAILURE REASON: {result.fail_reason}')

            booklet = binder.build()

            booklet.start()

            for i in range(0, min(6, len(result.images))):
                with io.BytesIO(result.images[i][0]) as bio:
                    f = discord.File(bio, f'output_{i+1}.png')
                    await ctx.send(file=f)
        else:
            try:
                with ctx.typing():
                    output = await compilers.targets[language](source)
            except KeyError:
                return await ctx.send(
                    f'That language ({language}) is not currently supported by '
                    'this toolchain. Sorry!')
            else:
                binder = bookbinding.StringBookBinder(ctx,
                                                      prefix='```',
                                                      suffix='```',
                                                      max_lines=40)

                for line in output.split('\n'):
                    binder.add_line(line, dont_alter=True)

                if ctx.invoked_with in ('ccd', 'colirud'):
                    await commands.try_delete(ctx)

                if len(output.strip()) == 0:
                    await ctx.send('No output...')
                    return

                booklet = binder.build()

                booklet.start()

                # Lets the book start up first, otherwise we get an error. If we
                # cant send, then just give up.
                for _ in range(0, 60):
                    if not len(booklet.response_stk):
                        await asyncio.sleep(1)
                    else:
                        await commands.wait_for_edit(ctx=ctx,
                                                     msg=booklet.root_resp,
                                                     timeout=1800)
                        break

    @code_execution_group.command(brief='Shows help for supported languages.')
    async def help(self, ctx, *, language=None):
        if not language:
            output = '**Supported languages**\n'
            for lang in sorted(compilers.languages):
                output += (f'- {lang.title()} -- `{ctx.prefix}cc '
                           f'ˋˋˋ{compilers.languages[lang.lower()][0]} ...`\n')
            await ctx.send(output)
        else:
            try:
                language = language.lower()

                help_text = compilers.docs[language]
                help_text += '\n\n'
                help_text += (
                    'Invoke using syntax highlighted code blocks with '
                    'one of the following names:\n')
                help_text += ', '.join(f'`{x}`'
                                       for x in compilers.languages[language])

                await ctx.send(help_text)
            except KeyError:
                await ctx.send(f'Could not find anything for `{language}`')
