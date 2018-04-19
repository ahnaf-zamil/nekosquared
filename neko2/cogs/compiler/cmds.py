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
from .toolchains import latex, r
from . import tools
from neko2.cogs.compiler.toolchains import coliru_compilers


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

    @staticmethod
    async def _execute_r(ctx, source):
        with ctx.typing():
            result = await r.eval_r(source)

        # Last line is some error about rm not working.
        binder = bookbinding.StringBookBinder(ctx,
                                              prefix='```',
                                              suffix='```',
                                              max_lines=40)

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

    @commands.group(
        invoke_without_subcommand=True,
        name='cc', aliases=['coliru', 'code', 'run'],
        brief='Attempts to execute the given code.')
    async def code_execution_group(self, ctx, *, arguments):
        """
        Attempts to execute some code by detecting the language in the
        syntax highlighting.
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
            return await self._execute_r(ctx, source)

        try:
            with ctx.typing():
                output = await coliru_compilers.targets[language](source)
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


