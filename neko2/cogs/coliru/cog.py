#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Coliru API for executing code on the fly.
"""
import json
import re
from neko2.engine import commands     # Command decorators
from neko2.shared import configfiles  # Config files
from neko2.shared import fsa          # finite state machines
from neko2.shared import traits       # HTTP pool


# Matches a markdown block
# This looks for ```\w* to start the block, then any set of characters,
# including ^\```, until the first instance of ``` is hit. This denotes the
# end of the block, and the capture group will be the content within that we
# are concerned with.
code_block_re = re.compile(r'```(\w+)\s([\s\S(^\\`{3})]*?)\s```')
coliru_cfg = configfiles.get_from_here('coliru_configs').sync_get()
coliru_endpoint = 'http://coliru.stacked-crooked.com/compile'
four_space_re = re.compile(r'^ {4}')


class ColiruCog(traits.HttpPool):
    @staticmethod
    async def fix_makefile(input_code: str) -> str:
        """
        Fixes makefiles so they actually compile. This converts any leading
        quadruple spaces on a line to a horizontal tab character.
        :param input_code: the input string.
        :return: the makefile-friendly string.
        """
        strings = []
        for line in input_code.splitlines():
            while four_space_re.match(line):
                line = four_space_re.sub('\t', line)
            strings.append(line)
        return '\n'.join(strings)


    @commands.group(
        brief='Compiles and runs code under a given configuration',
        invoke_without_command=True)
    async def coliru(self, ctx, *, input_code: str):
        """
        Compiles the given code using the compiler invocation, and outputs the
        result.

        Format like so:

        ```lang
        source code
        ```

        Where `lang` is an optional markdown-supported language or
        configuration. See the subcommand `coliru configs` to see the supported
        configurations.

        If you use makefiles, indent by four spaces. I will automatically
        translate the leading quadruple spaces to horizontal tabs.

        http://coliru.stacked-crooked.com/
        """

        # noinspection PyTypeChecker
        code = code_block_re.match(input_code)
        if not code or not len(code.groups()) == 2:
            return await ctx.send('Please provide some highlighted code')
        else:
            lang, code = code.groups()

            if lang == 'make':
                code = self.fix_makefile(code)

        try:
            config = coliru_cfg[lang.lower()]

            http = await self.acquire_http()
            with ctx.typing():
                res = await http.post(
                    coliru_endpoint,
                    data=json.dumps({'cmd': config,
                                     'src': code}))

                output = await res.text()

                pag = fsa.LinedPag(prefix='```', suffix='```')

                pag.add_line(f'> {config.replace("main.cpp", "src")}\n')

                for line in output.split('\n'):
                    pag.add_line(line)

                if len(pag.pages) > 1:
                    fsm = fsa.PagMessage.from_paginator(
                        pag=pag, bot=ctx.bot, invoked_by=ctx, timeout=120)

                    # Prevents blocking the typing message.
                    fsm.nowait(fsm.run())
                elif pag.pages:
                    await ctx.send(pag.pages[0])
                else:
                    await ctx.send('No output...')
        except KeyError:
            await ctx.send('Invalid configuration.')

    @coliru.command(
        brief='Lists the supported configurations')
    async def configs(self, ctx):
        paginator = fsa.LinedPag(max_lines=30)

        for config, command in coliru_cfg.items():
            paginator.add_line(f'_{config}_ - `{command}`')

        if len(paginator.pages) > 1:
            fsm = fsa.PagMessage.from_paginator(
                pag=paginator, bot=ctx.bot, invoked_by=ctx, timeout=120)
            await fsm.run()
        else:
            await ctx.send(paginator.pages[0])
