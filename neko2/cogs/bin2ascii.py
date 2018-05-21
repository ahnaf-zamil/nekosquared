#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Converts to-and-from ASCII to unsigned big-endian binary.
"""
import math
from neko2.shared import commands


class Bin2AsciiCog:
    @commands.command(brief='Converts the binary string to ASCII.')
    async def bin2ascii(self, ctx, *, string):
        string = ''.join(c for c in string if c not in ' \t\r\n')
        if not all(c in '01' for c in string):
            return await ctx.send('Not binary input...', delete_after=10)

        zeros = math.ceil(len(string)/8)
        string = string.rjust(zeros, '0')

        chars = []
        for i in range(0, len(string), 8):
            chars.append(chr(int(string[i:i+8], 2)))

        text = ''.join(chars)
        await ctx.send(text)
    
    @commands.command(brief='Converts the ASCII string to binary.')
    async def ascii2bin(self, ctx, *, string):
        """
        Any UTF-8 characters are removed.
        """
        string = ''.join(c for c in string if 0 <= ord(c) < 128)
        
        if not string:
            return await ctx.send('No valid ASCII characters given.',
                                  delete_after=10)

        binaries = [bin(ord(c))[2:11].rjust(0) for c in string]
        
        await ctx.send(' '.join(binaries))


def setup(bot):
    bot.add_cog(Bin2AsciiCog())
