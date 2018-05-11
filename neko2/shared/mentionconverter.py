#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
A discord converter that can convert any form of mention into a corresponding
object (excluding emojis, as they don't count).

There is an additional implementation that will also accept raw snowflake
integers.

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
from discord.ext import commands


class MentionConverter(commands.Converter):
    async def convert(self, ctx, argument: str):
        print(argument)

        if len(argument) < 4:
            raise commands.BadArgument('Expected a mention here')

        if not argument.startswith('<') and not argument.endswith('>'):
            raise commands.BadArgument('Expected a mention here')

        body = argument[1:-1]

        if body.startswith('@&'):
            return await commands.RoleConverter().convert(ctx, argument)
        elif body.startswith('@') and body[1:2].isdigit() or body[1:2] == '!':
            return await commands.MemberConverter().convert(ctx, argument)
        elif body.startswith('#'):
            return await commands.CategoryChannelConverter().convert(
                ctx, argument)
        else:
            raise commands.BadArgument('Unrecognised mention.')

            
class MentionOrSnowflakeConverter(MentionConverter):
    async def convert(self, ctx, argument: str):
        if argument.isdigit():
            return int(argument)
        else:
            return super().convert(ctx, argument)
