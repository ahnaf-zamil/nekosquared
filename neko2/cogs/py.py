#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Gets information on various Python modules.
"""
import contextlib
import io
from discomaton.factories import bookbinding
from neko2.shared import commands


class PyCog:
    @commands.command(brief='Looks up documentation for the given member.')
    async def py(self, ctx, member):
        """Gets some help regarding the given member."""
        with io.StringIO() as buff:
            with contextlib.redirect_stdout(buff):
                with contextlib.redirect_stderr(buff):
                    help(member)
            data = buff.getvalue().splitlines()

        bb = bookbinding.StringBookBinder(ctx,
                                          max_lines=20,
                                          prefix='```markdown',
                                          suffix='```')

        for line in data:
            line = line.replace('`', '′')
            bb.add_line(line)

        await bb.start()


def setup(bot):
    bot.add_cog(PyCog())
