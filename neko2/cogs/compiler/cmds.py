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
from neko2.cogs.compiler.toolchains import coliru_configs, coliru
from neko2.cogs.compiler.toolchains import r


class CompilerCog(traits.CogTraits):
    @commands.command(
        name='tex', aliases=['latex', 'texd', 'latexd'],
        brief='Attempts to parse a given LaTeX string and display a preview.')
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
        brief='Attempts to execute the given code using Coliru.')
    async def coliru(self, ctx, *, arguments):
        """
        Attempts to execute some code by detecting the language in the
        syntax highlighting. You MUST format the code using markdown-formatted
        code blocks. Please, please, PLEASE read this before saying "it is
        broken!"

        Run `cc help` to view a list of the supported languages, or
        `cc help <lang>` to view the help for a specific language.

        If you want to upload more than one file, or you wish to specify a
        custom build routine or flags, see `cc a`.
        """

        code_block = tools.code_block_re.search(arguments)

        if not code_block or len(code_block.groups()) < 2:
            return await ctx.send(
                'Please provide a valid syntax highlighted '
                'language. Check the help page out for this command '
                'for more details and instructions.')

        # Extract the code
        language, source = code_block.groups()
        language = language.lower()

        try:
            with ctx.typing():
                output = await coliru_configs.targets[language](source)
        except KeyError:
            return await ctx.send(
                f'That language ({language}) is not currently supported by'
                ' this toolchain. Sorry!')
        else:
            binder = bookbinding.StringBookBinder(ctx,
                                                  prefix='```markdown',
                                                  suffix='```',
                                                  max_lines=25)

            for line in output.split('\n'):
                binder.add_line(line, dont_alter=True)

            if ctx.invoked_with in ('ccd', 'colirud'):
                await commands.try_delete(ctx)

            if len(output.strip()) == 0:
                await ctx.send('No output...')
                return

            booklet = binder.build()
            booklet.start()

            await self._listen_to_edit(ctx, booklet)

    @coliru.command(brief='Shows help for supported languages.')
    async def help(self, ctx, *, language=None):
        if not language:
            output = '**Supported languages**\n'
            for lang in sorted(coliru_configs.languages):
                output += (f'- {lang.title()} -- `{ctx.prefix}cc '
                           f'ˋˋˋ{coliru_configs.languages[lang.lower()][0]} '
                           f'...`\n')
            await ctx.send(output)
        else:
            try:
                lang = language.lower()

                help_text = coliru_configs.docs[language]
                help_text += '\n\n'
                help_text += (
                    'Invoke using syntax highlighted code blocks with '
                    'one of the following names:\n')
                help_text += ', '.join(f'`{x}`'
                                       for x in coliru_configs.languages[lang])

                await ctx.send(help_text)
            except KeyError:
                await ctx.send(f'Could not find anything for `{language}`')

    @coliru.command(brief='Allows fine-tuned customisation of how a job is '
                          'run, at the loss of some of the simplicity.',
                    usage='ˋbash commandˋ [ˋfile_nameˋ ˋˋˋcodeˋˋˋ]*',
                    name='a')
    async def advanced(self, ctx, *, arguments):
        """
        This tool enables you to specify more than one file, in any supported
        language on Coliru. It also lets you upload source code files.

        Advanced code execution will first pool all source files into the
        current working directory in the sandbox. It will then proceed to
        execute the build/run command: this is the first argument, and should
        be enclosed in single back-ticks. The execute command can be something
        as simple as `make`, or as complicated as you like. You must invoke
        all of your logic you wish to perform from this argument, however.

        It is worth noting that this build script WILL be executed as Bash
        commands.

        For small programs, it may be as simple as invoking the interpreter
        or compiler, and then running the output. However, if you have much
        more complicated input, it is advisable to invoke something like a
        Makefile and call your logic from that.

        You can upload source code files as attachments, or specify them
        inline. If you wish to specify them inline, you should use the
        following syntax:

        ˋfile_nameˋ

        ˋˋˋpython

        print('some code goes here')

        ˋˋˋ

        This can be repeated as many times as required (within the limits
        provided by Discord, of course).

        ---

        _A working example_: this should give you a feel for exactly how to
        run this tool.

        n.cc a `make`


        `Makefile`

        ```makefile

        all: a.o b.o c.o
            gcc -Wall -Wextra -Werror $^ -lstdc++

        %.o: %.cpp
            g++ -Wall -Wextra -std=c++14 -c $< -o $@

        %.o: %.c
            gcc -Wall -Wextra -Werror -std=c99 -c $< -o $@
        ```
        `a.c`

        ```c

        extern void printer(const char* const);

        extern const char* const message;

        int main(void) { printer(message); }
        ```
        `b.cpp`

        ```cpp
        #include <iostream>
        #include <string>

        extern "C" {
            void printer(const char* const string) {
                std::cout << std::string(string);
            }
        }
        ```
        `c.c`

        ```c

        const char* const message = "HELLO WORLD!!!!!!!!";
        ```
        """

        try:
            # Get the first block as the command.
            command = tools.inline_block_re.search(arguments)

            if not command:
                raise ValueError('No command was given.')

            command = command.groups()[0]

            rest = arguments[len(command):].lstrip()

            # Get files:
            files = []
            for m in tools.file_name_and_block_re.findall(rest):
                files.append(m)

            for attachment in ctx.message.attachments:
                with io.StringIO() as buff:
                    attachment.save(buff)
                    buff = buff.getvalue()

                files.append((attachment.filename, buff))

            if len(files) == 0:
                raise ValueError('Expected one or more source files.')

            # Map to sourcefile objects
            files = [coliru.SourceFile(*file) for file in files]

            # Main file
            main = coliru.SourceFile('.run.sh', command)

            # Generate the coliru API client instance.
            c = coliru.Coliru('bash .run.sh', main, *files, verbose=True)

            output = await c.execute(await self.acquire_http())

            binder = bookbinding.StringBookBinder(ctx,
                                                  prefix='```markdown',
                                                  suffix='```',
                                                  max_lines=25)

            for line in output.split('\n'):
                binder.add_line(line, dont_alter=True)

            if ctx.invoked_with in ('ccd', 'colirud'):
                await commands.try_delete(ctx)

            if len(output.strip()) == 0:
                await ctx.send('No output...')
                return

            booklet = binder.build()
            booklet.start()

            await self._listen_to_edit(ctx, booklet)

        except IndexError:
            return await ctx.send('Invalid input format.')
        except ValueError as ex:
            return await ctx.send(str(ex))

    @commands.command(name='r', aliases=['cranr'],
                      brief='Executes a given R-code block, showing the output'
                            ' and any graphs that were plotted.')
    async def _r(self, ctx, *, source):
        """
        Use the following to highlight your syntax:

        n.r
        ```r
        t = (1:625) / 100
        x <- cos(t)
        y <- sin(t)
        plot(x, y)
        ```
        """
        code_block = tools.code_block_re.search(source)
        if code_block:
            source = code_block.group(2)

        with ctx.typing():
            result = await r.eval_r(await self.acquire_http(),
                                    source)

        binder = bookbinding.StringBookBinder(ctx,
                                              prefix='```markdown',
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

        additionals = []

        for i in range(0, min(6, len(result.images))):
            with io.BytesIO(result.images[i][0]) as bio:
                f = discord.File(bio, f'output_{i+1}.png')
                additionals.append(await ctx.send(file=f))

        await self._listen_to_edit(ctx, booklet, *additionals)

    @staticmethod
    async def _listen_to_edit(ctx, booklet, *additional_messages):
        # Lets the book start up first, otherwise we get an error. If
        # we cant send, then just give up.
        for _ in range(0, 60):
            if not len(booklet.response_stk):
                await asyncio.sleep(1)
            else:
                await commands.wait_for_edit(ctx=ctx,
                                             msg=booklet.root_resp,
                                             timeout=1800)
                for message in additional_messages:
                    asyncio.ensure_future(message.delete())
                break
