#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Man page support. This supports any man pages that are supported locally.
"""
import asyncio

from discomaton.factories import bookbinding

from neko2.shared import commands


class ManCog:
    @commands.command(brief='Shows manpages.')
    async def man(self, ctx, page, section: int = None):
        """
        Searches man pages for the given input.

        Usage:

        - `man page` - gets the given page
        - `man page 2` - gets the given page from section 2.

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

            await book.start()


def setup(bot):
    import shutil
    assert shutil.which('man'), 'Install `man` first.'
    bot.add_cog(ManCog())
