#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Repeats whatever you say but in a condescending tone. It should work well with
SQL so that the main code is edited, but comments and strings are not.

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

import random
import re

from neko2.shared import commands


regex = re.compile(r'```[a-zA-Z0-9]+\s([\s\S(^\\`{3})]*?)\s*```')


class MockSqlCog:
    @commands.command(brief='iTS pRonOunCeD sEquEl')
    async def mocksql(self, ctx, *, markup):
        markup_scrub = regex.match(markup)
        if markup_scrub:
            markup = markup_scrub.group(1)

        single_quote = False
        double_quote = False
        single_comment = False
        multiline_comment = False
        
        output = ''
        index = 0

        while index < len(markup):
            if any((single_quote, double_quote,
                    single_comment, multiline_comment)):
                output += markup[index]
                if single_comment and markup[index] == '\n':
                    single_comment = False
                    index += 1
                elif single_quote and markup[index] == "'":
                    single_quote = False
                    index += 1
                elif double_quote and markup[index] == '"':
                    double_quote = False
                    index += 1
                elif multiline_comment and markup[index:].startswith('*/'):
                    multiline_comment = False
                    output += '/'
                    index += 2
                else:
                    index += 1
            else:
                if random.choice((True, False)):
                    output += markup[index].upper()
                else:
                    output += markup[index].lower()

                if markup[index:].startswith('--'):
                    single_comment = True
                    output += '-'
                    index += 2
                elif markup[index:].startswith('/*'):
                    multiline_comment = True
                    output += '*'
                    index += 2
                elif markup[index] == '"':
                    double_quote = True
                    index += 1
                elif markup[index] == "'":
                    single_quote = True
                    index += 1
                else:
                    index += 1

        await ctx.send(f'```sql\n{output}\n```\n')


def setup(bot):
    bot.add_cog(MockSqlCog())
