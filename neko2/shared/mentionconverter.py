#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
A discord converter that can convert any form of mention into a corresponding
object (excluding emojis, as they don't count)
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
