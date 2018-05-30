#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Cog providing Coliru commands.

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
import io

from discomaton.factories import bookbinding

from neko2.shared import commands
from neko2.shared import traits


from . import tools
from .toolchains import coliru


class ColiruCog(traits.CogTraits):
    @commands.group(
        invoke_without_command=True,
        name='coliru', aliases=['cc'],
        brief='Attempts to execute the given code using '
              '[coliru](http://coliru.stacked-crooked.com).')
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
            booklet = bookbinding.StringBookBinder(ctx)
            booklet.add_line('I couldn\'t detect a valid language in your '
                             'syntax highlighting... try again by editing '
                             'your initial message.')
            booklet = booklet.build()
            booklet.start()

            return await tools.listen_to_edit(ctx, booklet)

        # Extract the code
        language, source = code_block.groups()
        language = language.lower()

        try:
            with ctx.typing():
                output = await coliru.targets[language](source)
        except KeyError:
            booklet = bookbinding.StringBookBinder(ctx)
            booklet.add_line(f'That language ({language}) is not yet supported'
                             ' by this toolchain. Feel free to edit your'
                             ' message if you wish to do something else.')
            booklet = booklet.build()
            booklet.start()

            await tools.listen_to_edit(ctx, booklet)
        else:
            binder = bookbinding.StringBookBinder(ctx,
                                                  prefix='```markdown',
                                                  suffix='```',
                                                  max_lines=25)

            binder.add_line(f'Interpreting as {language!r} source.')

            for line in output.split('\n'):
                binder.add_line(line)

            if ctx.invoked_with in ('ccd', 'colirud'):
                await commands.try_delete(ctx)

            if len(output.strip()) == 0:
                await ctx.send('No output...')
                return

            booklet = binder.build()
            booklet.start()

            await tools.listen_to_edit(ctx, booklet)

    @coliru.command(brief='Shows help for supported languages.')
    async def help(self, ctx, *, language=None):
        """
        Shows all supported languages and their markdown highlighting
        syntax expected to invoke them correctly.
        """
        if not language:
            output = '**Supported languages**\n'
            for lang in sorted(coliru.languages):
                output += (f'- {lang.title()} -- `{ctx.prefix}cc '
                           f'ˋˋˋ{coliru.languages[lang.lower()][0]} '
                           f'...`\n')
            await ctx.send(output)
        else:
            try:
                lang = language.lower()

                help_text = coliru.docs[language]
                help_text += '\n\n'
                help_text += (
                    'Invoke using syntax highlighted code blocks with '
                    'one of the following names:\n')
                help_text += ', '.join(f'`{x}`'
                                       for x in coliru.languages[lang])

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
                binder.add_line(line)

            if ctx.invoked_with in ('ccd', 'colirud'):
                await commands.try_delete(ctx)

            if len(output.strip()) == 0:
                await ctx.send('No output...')
                return

            booklet = binder.build()
            booklet.start()

            await tools.listen_to_edit(ctx, booklet)

        except IndexError:
            return await ctx.send('Invalid input format.')
        except ValueError as ex:
            return await ctx.send(str(ex))
