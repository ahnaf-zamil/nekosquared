#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Reverse-polish-notation parser.
"""
operations = {
    '+': lambda a, b: a + b,            
    '-': lambda a, b: a - b, 
    '*': lambda a, b: a * b,
    '/': lambda a, b: a / b,
    'div': lambda a, b: a / b,
    'idiv': lambda a, b: a // b,
    '//': lambda a, b: a // b,    
    '%': lambda a, b: a % b,
    '**': lambda a, b: a ** b,
    '|': lambda a, b: int(a) | int(b),            
    '&': lambda a, b: int(a) & int(b),
    '^': lambda a, b: int(a) ^ int(b),           
    '<<': lambda a, b: int(a) << int(b),
    '>>': lambda a, b: int(a) >> int(b),  
    '<': lambda a, b: 1 if a < b else 0,
    '>': lambda a, b: 1 if a > b else 0,           
    '<=': lambda a, b: 1 if a <= b else 0,
    '>=': lambda a, b: 1 if a >= b else 0,           
    '==': lambda a, b: 1 if a == b else 0,
    '!=': lambda a, b: 1 if a != b else 0
}


def tokenise(*chunks):
    """
    Returns an iterable of tokens to parse left-to-right from an
    iterable of string chunks. Each chunk is a token.
    """
    for token in chunks:
        try:
            yield float(token)
        except ValueError:
            yield token

def parse(tokens):
    """
    Attempts to parse the tokens. If successful, we return the result value.
    """
    if not tokens:
        raise ValueError('Please provide some input.')

    stack = []
    pos = 0

    try:
        for pos, token in enumerate(tokens):
            if isinstance(token, (float, int)):
                stack.append(token)
            else:
                op = operations[token]

                left, right = stack.pop(), stack.pop()
                stack.append(op(left, right))

    except IndexError:
        return (
            'Pop from empty stack. Perhaps you have too many operators? '
            f'(At token {pos + 1} of {len(tokens)}: {token!r})')
    except KeyError:
        return (
            f'Operator was unrecognised. (At token {pos + 1} of '
            f'{len(tokens)}: {token!r})')
    else:
        if len(stack) != 1:
            return 'Too many values. Perhaps you missed an operator?'
        else:
            return stack.pop()

# Test CLI.
if __name__ == '__main__':
    import sys
    tokens = list(tokenise(*sys.argv[1:]))
    result = parse(tokens)
    print(result)
else:
    from neko2.shared import commands

    class ReversePolishCog:
        @commands.command(brief='Parses the given reverse polish notation.')
        async def rpn(self, ctx, *expression):
            """
            Executes the given reverse polish (postfix) notation expression.

            Note that only binary operators are currently supported. Run
            with the `help` argument for the expression to view what is 
            supported.
            """
            if len(expression) == 1 and expression[0].lower() == 'help':
                await ctx.send(
                    '**Supported Operators:**\n' +
                    ', '.join(sorted(str(o) for o in operators)) + '\n\n' +
                    '**"What the hell is this?"**\n' + 
                    '<http://en.wikipedia.org/wiki/' +
                    'Reverse_Polish_notation>')
            else:
                tokens = list(tokenise(*expression))
                result = parse(tokens)
                await ctx.send(result)

    def setup(bot):
        bot.add_cog(ReversePolishCog())
        
