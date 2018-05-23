#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Converts to-and-from ASCII to unsigned big-endian binary.
"""
import math
from neko2.shared import commands


aliases = {
    'bin': 2, 'binary': 2, '2s': 2, 'twos': 2,
    'tri': 3,
    'oct': 8, 'octal': 8, 'eight': 8,
    'denary': 10, 'dec': 10, 'decimal': 10, 'ten': 10,
    'hex': 16, 'hexadecimal': 16, 'sixteen': 16
}


def to_base(n, base):
   convert_string = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
   if n < base:
       return convert_string[n]
   else:
       return to_base(n // base, base) + convert_string[n % base]
        


class Bin2AsciiCog:
    @commands.command(name='base', 
                      brief='Converts between bases and also to/from ASCII.')
    async def base_group(self, ctx, query): 
        values = query.replace(',', '').replace(' to', '').split(' ')
        
        if len(values) < 3 or len(values) > 3:
            return await ctx.send('Expected exactly three arguments.',
                                  delete_after=10)
        
        from_base, to_base, value = values[0], values[1], values[2]
        
        try:
            if not from_base.isdigit():
                from_base = aliases[from_base.lower()]
            else:
                from_base = int(from_base)
                
            if not to_base.isdigit():
                to_base = aliases[to_base.lower()]
            else:
                to_base = int(to_base)            
                
            if not all(0 < x <= 36 for x in (from_base, to_base)):
                return await ctx.send(
                    'Bases must be greater than zero and less or equal to 36.')
        except KeyError as ex:
            return await ctx.send(f'I didn\'t recognise the base {str(ex)!r}...')
        
        try:
            value = abs(int(value, from_base))
        except ValueError as ex:
            return await ctx.send(f'Error: {ex}.')
        
        await ctx.send(to_base(value, to_base) or '0')

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
        string = ''.join(c for c in string if 0 <= ord(c) < 0xFFFF)
        
        if not string:
            return await ctx.send('No valid ASCII characters given.',
                                  delete_after=10)

        binaries = [bin(ord(c))[2:11].rjust(8, '0') for c in string]
        
        await ctx.send(' '.join(binaries))


def setup(bot):
    bot.add_cog(Bin2AsciiCog())
