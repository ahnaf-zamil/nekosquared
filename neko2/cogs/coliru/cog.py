#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Coliru API for executing code on the fly.
"""
import json
import re

import asyncio
from discomaton.factories import bookbinding

from neko2.engine import commands     # Command decorators
from neko2.shared import configfiles  # Config files
from neko2.shared import traits       # HTTP pool


# Matches a markdown block
# This looks for ```\w* to start the block, then any set of characters,
# including ^\```, until the first instance of ``` is hit. This denotes the
# end of the block, and the capture group will be the content within that we
# are concerned with.
code_block_re = re.compile(r'```(\w+)\s([\s\S(^\\`{3})]*?)\s*```')
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
        invoke_without_command=True,
        aliases=['colirud', 'cc', 'ccd'])
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

            with ctx.typing():

                http = await self.acquire_http()

                res = await http.post(
                    coliru_endpoint,
                    data=json.dumps({'cmd': config,
                                     'src': code}))

            output = await res.text()

            binder = bookbinding.StringBookBinder(ctx,
                                                  prefix='```',
                                                  suffix='```',
                                                  max_lines=40)

            binder.add_line(f'> {config.replace("main.cpp", "src")}\n---')

            for line in output.split('\n'):
                binder.add_line(line, dont_alter=True)

            if ctx.invoked_with in ('ccd', 'colirud'):
                await commands.try_delete(ctx)

            if len(output.strip()) == 0:
                msg = await ctx.send('No output...')
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

        except KeyError:
            await ctx.send('Invalid configuration.')

    @coliru.command(
        brief='Lists the supported configurations')
    async def configs(self, ctx):
        binder = bookbinding.StringBookBinder(ctx, max_lines=20)

        for config, command in coliru_cfg.items():
            binder.add_line(f'_{config}_ - `{command}`', dont_alter=True)

        await binder.start()

