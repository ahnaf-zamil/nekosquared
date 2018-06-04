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


class GuildChannelConverter(commands.Converter):
    """
    Gets a guild channel
    """

    async def convert(self, ctx, body: str):
        for t in (commands.TextChannelConverter, commands.VoiceChannelConverter):
            try:
                return await t().convert(ctx, body)
            except:
                pass

        raise commands.BadArgument(f"No channel matching `{body}` was found.")


class LowercaseCategoryConverter(commands.Converter):
    """
    Gets a category case insensitive. Discord doesn't show the name in the
    case the name is stored in; instead, it is transformed to uppercase. This
    makes this whole thing kind of useless to the user unless they can guess
    the correct permutation of character cases that was used.
    """

    async def convert(self, ctx, argument):
        argument = argument.lower()

        for category in ctx.guild.categories:
            if category.name.lower() == argument:
                return category

        raise commands.BadArgument(f"Category matching `{argument}` was not " "found.")


class GuildChannelCategoryConverter(commands.Converter):
    """
    Gets a guild channel or category.
    """

    async def convert(self, ctx, body: str):
        # If the input is in the format <#123> then it is a text channel.
        if body.startswith("<#") and body.endswith(">"):
            sf_str = body[2:-1]
            if sf_str.isdigit():
                sf = int(sf_str)
                channel = alg.find(lambda c: c.id == sf, ctx.guild.channels)

                if channel:
                    return channel

            raise commands.BadArgument(
                "Unable to access that channel. Make "
                "sure that it exists, and that I have "
                "access to it, and try again."
            )

        # Otherwise, it could be a text channel, a category or a voice channel.
        # We need to hunt for it manually.
        else:
            to_search = {*ctx.guild.channels, *ctx.guild.categories}
            channel = alg.find(lambda c: c.name == body, to_search)
            if channel:
                return channel

            # Attempt case insensitive searching
            body = body.lower()
            channel = alg.find(lambda c: c.name.lower() == body, to_search)
            if channel:
                return channel
            raise commands.BadArgument("No channel matching input was found.")


class MentionConverter(commands.Converter):
    """
    A converter that takes generic types of mentions.
    """

    async def convert(self, ctx, body: str):
        if body.startswith("<") and body.endswith(">"):
            tb = body[1:-1]

            if tb.startswith("@&"):
                return await commands.RoleConverter().convert(ctx, body)
            elif tb.startswith("@") and tb[1:2].isdigit() or tb[1:2] == "!":
                return await commands.MemberConverter().convert(ctx, body)
            elif tb.startswith("#"):
                return await commands.TextChannelConverter().convert(ctx, body)
        else:
            try:
                return await commands.EmojiConverter().convert(ctx, body)
            except:
                pass

            try:
                return await GuildChannelCategoryConverter().convert(ctx, body)
            except:
                pass

            try:
                return await commands.PartialEmojiConverter().convert(ctx, body)
            except:
                pass

        # Attempt to find in whatever we can look in. Don't bother looking
        # outside this guild though, as I plan to keep data between guilds
        # separate for privacy reasons.

        if ctx.guild:
            all_strings = [
                *ctx.guild.members,
                *ctx.guild.channels,
                *ctx.guild.categories,
                *ctx.guild.roles,
                *ctx.guild.emojis,
            ]

            def search(obj):
                if getattr(obj, "display_name", "") == body:
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

                    if getattr(obj, "display_name", "").lower() == _body:
                        return True
                    if str(obj).lower() == _body:
                        return True
                    if obj.name.lower() == _body:
                        return True
                    return False

                result = alg.find(search, all_strings)

            if not result:
                raise commands.BadArgument(f"Could not resolve `{body}`")
            else:
                return result


class MentionOrSnowflakeConverter(MentionConverter):
    """
    A specialisation of MentionConverter that ensures that raw snowflakes can
    also be input.
    """

    async def convert(self, ctx, body: str):
        if body.isdigit():
            return int(body)
        else:
            return await super().convert(ctx, body)
