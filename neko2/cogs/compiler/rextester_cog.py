#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Rextester cog interface.

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
from discomaton.factories import bookbinding
from neko2.shared import traits, commands

from . import tools
from .toolchains import rextester


class RextesterCog(traits.CogTraits):

    @commands.probably_broken
    @commands.group(
        invoke_without_command=True,
        name='rextester',
        aliases=['rxt'],
        brief='Attempts to execute the code using '
              '[rextester.](http://rextester.com)')
    async def rextester_group(self, ctx, *, source):
        """
        Attempts to execute some code by detecting the language in the
        syntax highlighting. You MUST format the code using markdown-formatted
        code blocks. Please, please, PLEASE read this before saying "it is
        broken!"

        This provides many more languages than coliru does, however, it is
        mainly untested and will probably break in a lot of places. It also
        has much less functionality. Many languages have to be formatted
        in a specific way or have specific variable names or namespaces.

        Run `rxt help` to view a list of the supported languages, or
        `rxt help <lang>` to view the help for a specific language.
        """
        code_block = tools.code_block_re.search(source)

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

        if language not in rextester.Language.__members__:
            booklet = bookbinding.StringBookBinder(ctx)
            booklet.add_line('Doesn\'t look like I support that language. '
                             'Run `rtx help` for a list.')

            booklet = booklet.build()
            booklet.start()
            return await tools.listen_to_edit(ctx, booklet)

        booklet = bookbinding.StringBookBinder(ctx,
                                               prefix='```markdown',
                                               suffix='```')

        lang_no = rextester.Language.__members__[language]

        http = await self.acquire_http()
        response = await rextester.execute(http, lang_no, source)

        if response.errors:
            booklet.add_line('> ERRORS:')
            booklet.add_line(response.errors)

        if response.warnings:
            booklet.add_line('> WARNINGS:')
            booklet.add_line(response.warnings)

        if response.result:
            booklet.add_line('> OUTPUT:')
            booklet.add_line(response.result)

        booklet.add_line(response.stats)

        if response.files:
            booklet.add_line(f'- {len(response.files)} file(s) included. Bug '
                             'Esp to implement this properly!')

        booklet = booklet.build()
        booklet.start()
        await tools.listen_to_edit(ctx, booklet)

    @rextester_group.command(brief='Shows help for supported languages.')
    async def help(self, ctx, *, language=None):
        """
        Shows all supported languages and their markdown highlighting
        syntax expected to invoke them correctly.
        """
        if not language:
            booklet = bookbinding.StringBookBinder(ctx)
            booklet.add_line('**Supported languages**')

            for lang in sorted(rextester.Language.__members__.keys()):
                lang = lang.lower()
                booklet.add_line(f'- {lang.title()} -- `{ctx.prefix}rxt '
                                 f'ˋˋˋ{lang} ...`')
            booklet.start()
        else:
            await ctx.send('There is nothing here yet. The developer has '
                           'been shot as a result.')
