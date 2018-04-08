#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Gets information on various Python modules.
"""
import contextlib
import io
import re
import sre_parse
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


class SubPatternDebug(sre_parse.SubPattern):
    """
    Overrides dump method implementation by sre_parse.py
    """
    def dump(self, level=0):
            nl = True
            seqtypes = (tuple, list)
            for op, av in self.data:
                if op.name.startswith('LITERAL'):
                    print('  ' * level + '"' + chr(av) + '"')
                    continue
                else:
                    print(level * "  " + op.name, end='')

                if op.name == 'IN':
                    # member sublanguage
                    print()
                    for op, a in av:
                        if isinstance(op, sre_parse.SubPattern):
                            SubPatternDebug.dump(a, level + 1)
                        elif op.name.startswith('LITERAL'):
                            print('  ' * (level + 1) + '"' + chr(a) + '"')
                        else:
                            print((level + 1) * "  " + str(op), a)
                elif op.name == 'BRANCH':
                    print()
                    for i, a in enumerate(av[1]):
                        if i:
                            print(level * "  " + "OR")
                        if isinstance(op, sre_parse.SubPattern):
                            SubPatternDebug.dump(a, level + 1)
                        elif op.name.startswith('LITERAL'):
                            print('  ' * (level + 1) + '"' + chr(a) + '"')
                        else:
                            a.dump(level + 1)
                elif op.name == 'GROUPREF_EXISTS':
                    condgroup, item_yes, item_no = av
                    print('', condgroup)
                    item_yes.dump(level + 1)
                    if item_no:
                        print(level * "  " + "ELSE")
                        item_no.dump(level + 1)
                elif isinstance(av, seqtypes):
                    nl = False
                    for a in av:
                        if isinstance(a, sre_parse.SubPattern):
                            if not nl:
                                print()
                            SubPatternDebug.dump(a, level + 1)
                            nl = True
                        elif op.name.startswith('LITERAL'):
                            print('  ' * (level + 1) + '"' + chr(a) + '"')
                        else:
                            if not nl:
                                print(' ', end='')
                            print(a, end='')
                            nl = False
                    if not nl:
                        print()
                else:
                    print('', av)

    @classmethod
    def coerce(cls, other):
        other.__class__ = cls
        return other


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
            return await ctx.send(f'An error occurred: {ex!s}', delete_after=10)

        result = bookbinding.StringBookBinder(ctx, prefix='```', suffix='``` ',
                                              max_lines=None)

        result.add_line(f'Regex: {regex_str}', empty_after=True)

        if tests:
            # Print whether each test matches
            result.add_line('Tests')
            result.add_line('=====', empty_after=True)

            for test in tests:
                result.add_line(f'  {test!r}:')
                matches = regex.match(test)
                if matches:
                    for match in matches.groups():
                        result.add_line(f'    {match}')

        result.add_page_break()

        result.add_line('Parsed SRE tree')
        result.add_line('===============', empty_after=True)

        result.add_line(self.parse_regex_tree(regex_str, flags_int))

        await result.start()

    def parse_regex_tree(self, pattern, flags):
        import sre_parse
        tree = sre_parse.parse(pattern, flags)
        tree = SubPatternDebug.coerce(tree)

        with io.StringIO() as string:
            with contextlib.redirect_stdout(string):
                tree.dump()
                return string.getvalue()



def setup(bot):
    bot.add_cog(PyCog())
