# !/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Cog providing the `r` command.

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

import discord
from discomaton.factories import bookbinding
from neko2.shared import traits, commands
from . import tools
from .toolchains import r


class RCog(traits.CogTraits):
    @commands.command(name='r', aliases=['cranr'],
                      brief='Executes a given R-code block, showing the output'
                            ' and any graphs that were plotted.')
    async def _r(self, ctx, *, source):
        """
        Use the following to highlight your syntax:

        ```
        n.r
        ˋˋˋr
        
        t = (1:625) / 100\n
        x <- cos(t)\n
        y <- sin(t)\n
        plot(x, y)\n
        ˋˋˋ
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
            binder.add_line(line)

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

        await tools.listen_to_edit(ctx, booklet, *additionals)
