#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Gets information on various Python modules.
"""
import contextlib
import io
import re
from discomaton.factories import bookbinding
from neko2.engine import commands


str2flags = {
  'a': re.ASCII,
  'i': re.IGNORECASE,
  'l': re.LOCALE,
  'm': re.MULTILINE,
  's': re.DOTALL,
  'x': re.VERBOSE,
  'u': re.UNICODE
}


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
                                          max_lines=None,
                                          prefix='```markdown',
                                          suffix='```')

        for line in data:
            line = line.replace('`', '′')
            bb.add_line(line)

        await bb.start()

    @commands.command(
        brief='Tests a Python regular expression, or analyses it.',
        examples=['".*" -f iu "hello world" "foobar" " "'],
        usage='"pyregex <regex>" [-f [ailmsxu]+] ["test case"]*')
    async def pyregex(self, ctx, *query):
        if len(query) == 0:
            return

        regex_str = query[0]
        flags_strings = set()
        flags = set()
        tests = set()
        query = query[1:]

        for i in range(0, len(query)):
            if query[i] == '-f' and not flags and len(query) > i + 1:
                i += 1
                for flag in query[i]:
                    if flag not in str2flags:
                        return await ctx.send(f'Unrecognised flag `{flag}`',
                                              delete_after=5)
                    else:
                        flags_strings.add(flag)
                        flags.add(str2flags[flag])
            else:
                tests.add(query[i])

        try:
            flags_int = 0
            for flag in flags:
                flags_int |= flag

            regex = re.compile(regex_str, flags=flags_int)
        except BaseException as ex:
            return await ctx.send('An error occurred: {ex!s}', delete_after=10)

        result = bookbinding.StringBookBinder(ctx)

        if tests:
            pass



def setup(bot):
    bot.add_cog(PyCog())
