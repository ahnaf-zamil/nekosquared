#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Man page support. This supports any man pages that are supported locally.

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
import asyncio
import re

from discomaton import button
from discomaton.factories import bookbinding
from neko2.shared import commands


class ManCog:
    @commands.command(brief='Shows manpages.')
    async def man(self, ctx, page, section: str = None, *, grep=None):
        """
        Searches man pages for the given input.

        Usage:

        - `man page` - gets the given page, from any section.
        - `man page * ` - gets the given page, from any section.
        - `man page 2` - gets the given page from section 2.
        - `man page * 'pattern'` - searches all pages for the
            given pattern (Python regex).

        Sections:
           1   Executable programs or shell commands
           2   System calls (functions provided by the kernel)
           3   Library calls (functions within program libraries)
           4   Special files (usually found in /dev)
           5   File formats and conventions eg /etc/passwd
           6   Games
           7   Miscellaneous (including macro packages and conventions),
                e.g. man(7), groff(7)
           8   System administration commands (usually only for root)
           9   Kernel routines [Non standard]
        """
        if section and section != '*' and not section.isdigit():
            raise commands.BadArgument('Expected a * or integer for section.')
        else:
            if section == '*':
                section = None
            if section is not None:
                section = int(section)

        if section is not None and not (1 <= section <= 9):
            return await ctx.send('Section must be between 1 and 9.',
                                  delete_after=10)
        elif page.strip().startswith('-'):
            return await ctx.send('Flag-like arguments are not allowed.',
                                  delete_after=10)
        else:
            section = str(section) if section else None

        common_args = [page] if not section else [section, page]

        # Gets the full manpage content which will be huge.
        main_proc = await asyncio.create_subprocess_exec(
            'man', *common_args,
            # encoding='utf-8',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
            stdin=asyncio.subprocess.DEVNULL,
            env={'COLUMNS': '75'})

        main_stream = b''.join([await main_proc.stdout.read()]).decode('utf-8')

        if main_proc.returncode or not len(main_stream.strip()):
            await ctx.send('Error: the man page might not exist on my system.',
                           delete_after=10)
        else:
            book = (bookbinding.StringBookBinder(ctx)
                    .with_prefix('```')
                    .with_suffix('```')
                    .with_max_lines(30))

            for line in main_stream.splitlines():
                book.add_line(line, dont_alter=True)

            book = book.build()

            # Find the results
            if grep:
                try:
                    regex = re.compile(grep)
                    matching_pages = []

                    for i, page in enumerate(book.pages):
                        if regex.search(page):
                            matching_pages.append(i + 1)
                            continue

                    if len(matching_pages) >= 1:
                        book.set_starting_page_number(matching_pages[0])

                    if len(matching_pages) > 1:
                        # Metadata to be used later by the regex button.
                        setattr(book, '_regex_matches', matching_pages)
                        # Index in the match list
                        setattr(book, '_current_match', 0)

                        # noinspection PyProtectedMember
                        @button.as_button(name='Next match', reaction='⏯')
                        async def next_match(_unused_btn,
                                             machine,
                                             _unused_react,
                                             _unused_user_):
                            cm = machine._current_match + 1
                            cm %= len(machine._regex_matches)

                            machine._current_match = cm

                            page = machine._regex_matches[cm]
                            await machine.set_page_number(page)

                        book.buttons[next_match.reaction] = next_match

                except Exception as ex:
                    await ctx.send(ex, delete_after=10)

            book.start()


def setup(bot):
    import shutil
    assert shutil.which('man'), 'Install `man` first.'
    bot.add_cog(ManCog())
