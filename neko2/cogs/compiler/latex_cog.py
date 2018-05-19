#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Cog providing the LaTeX commands.

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
from neko2.shared import commands, traits
from .toolchains import latex


class LatexCog(traits.CogTraits):
    @commands.command(
        name='tex', aliases=['latex', 'texd', 'latexd'],
        brief='Attempts to parse a given LaTeX string and display a preview.')
    async def latex_cmd(self, ctx, *, content: str):
        """
        Add the `d` prefix to the command to delete your message before the
        response is shown.
        """
        delete = ctx.invoked_with.endswith('d')

        if delete:
            await commands.try_delete(ctx)

        async with ctx.typing():
            msg = await latex.LatexCogHelper.get_send_image(ctx, content)

        if not delete:
            await commands.wait_for_edit(ctx=ctx, msg=msg, timeout=1800)

