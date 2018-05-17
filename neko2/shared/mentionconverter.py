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

from neko2.shared import alg


class MentionConverter(commands.Converter):
    async def convert(self, ctx, body: str):
        if body.startswith('<') and body.endswith('>'):
            tb = body[1:-1]

            if tb.startswith('@&'):
                return await commands.RoleConverter().convert(ctx, body)
            elif tb.startswith('@') and tb[1:2].isdigit() or tb[1:2] == '!':
                return await commands.MemberConverter().convert(ctx, body)
            elif tb.startswith('#'):
                return await commands.CategoryChannelConverter().convert(
                    ctx, body)
        else:
            try:
                return await commands.EmojiConverter().convert(ctx, body)
            except:
                pass

            try:
                return await commands.PartialEmojiConverter()\
                    .convert(ctx, body)
            except:
                pass

        # Attempt to find in whatever we can look in. Don't bother looking
        # outside this guild though, as I plan to keep data between guilds
        # separate for privacy reasons.

        if ctx.guild:
            all_strings = [
                *ctx.guild.members, *ctx.guild.channels, *ctx.guild.categories,
                *ctx.guild.roles, *ctx.guild.emojis,
            ]

            def search(obj):
                if getattr(obj, 'display_name', '') == body:
                    return True
                if str(obj) == body or obj.name == body:
                    return True
                return False

            # Match case first, as a role and member, say, may share the same
            # name barr the case difference, and this could lead to unwanted
            # or unexpected results. The issue is this will get slower as a
            # server gets larger, generally.
            result = alg.find(search, all_strings)
            if not result:
                # Try again not matching case.

                def search(obj):
                    _body = body.lower()

                    if getattr(obj, 'display_name', '').lower() == _body:
                        return True
                    if str(obj).lower() == _body:
                        return True
                    if obj.name.lower() == _body:
                        return True
                    return False

                result = alg.find(search, all_strings)

            if not result:
                raise commands.BadArgument(f'Could not resolve `{body}`')
            else:
                return result


class MentionOrSnowflakeConverter(MentionConverter):
    async def convert(self, ctx, body: str):
        if body.isdigit():
            return int(body)
        else:
            return await super().convert(ctx, body)
