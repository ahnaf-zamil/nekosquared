#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Reverse-polish-notation parser.

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
from decimal import Decimal

operations = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
    "div": lambda a, b: a / b,
    "idiv": lambda a, b: a // b,
    "//": lambda a, b: a // b,
    "%": lambda a, b: a % b,
    "**": lambda a, b: a ** b,
    "|": lambda a, b: int(a) | int(b),
    "&": lambda a, b: int(a) & int(b),
    "^": lambda a, b: int(a) ^ int(b),
    "<<": lambda a, b: int(a) << int(b),
    ">>": lambda a, b: int(a) >> int(b),
    "<": lambda a, b: 1 if a < b else 0,
    ">": lambda a, b: 1 if a > b else 0,
    "<=": lambda a, b: 1 if a <= b else 0,
    ">=": lambda a, b: 1 if a >= b else 0,
    "==": lambda a, b: 1 if a == b else 0,
    "!=": lambda a, b: 1 if a != b else 0,
    "&&": lambda a, b: 1 if a and b else 0,
    "||": lambda a, b: 1 if a or b else 0,
}


def tokenize(*chunks):
    """
    Returns an iterable of tokens to parse left-to-right from an
    iterable of string chunks. Each chunk is a token.
    """
    for token in chunks:
        try:
            yield Decimal(token)
        except:
            yield token


def parse(tokens):
    """
    Attempts to parse the tokens. If successful, we return the result value.
    """
    if not tokens:
        raise ValueError("Please provide some input.")

    stack = []
    pos = 0

    try:
        for pos, token in enumerate(tokens):
            if isinstance(token, (float, int, Decimal)):
                stack.append(token)
            else:
                op = operations[token]
                right, left = stack.pop(), stack.pop()
                try:
                    stack.append(Decimal(op(left, right)))
                except ZeroDivisionError:
                    stack.append(float("nan"))

    except IndexError:
        return (
            "Pop from empty stack. Perhaps you have too many operators? "
            f"(At token {pos + 1} of {len(tokens)}: {token!r})"
        )
    except KeyError:
        return (
            f"Operator was unrecognised. (At token {pos + 1} of "
            f"{len(tokens)}: {token!r})"
        )
    except Exception as ex:
        return f"{type(ex).__name__}: {ex}"
    else:
        if len(stack) != 1:
            return "Too many values. Perhaps you missed an operator?"
        else:
            return stack.pop()


# Test CLI.
if __name__ == "__main__":
    import sys

    tokens = list(tokenize(*sys.argv[1:]))
    result = parse(tokens)
    print(result)
else:
    from neko2.shared import commands

    class ReversePolishCog:
        @commands.command(brief="Parses the given reverse polish notation.")
        async def rpn(self, ctx, *expression):
            """
            Executes the given reverse polish (postfix) notation expression.

            Note that only binary operators are currently supported. Run
            with the `help` argument for the expression to view what is
            supported.

            For example:
                12 22 /
            will result in the infix expression:
                12 / 22

            5th May 2018: now evaluates expressions in the right order.
                Division and mod operations are no longer inverted.
                Division by zero errors are now handled.
            """
            if len(expression) == 1 and expression[0].lower() == "help":
                await ctx.send(
                    "**Supported Operators:**\n"
                    + ", ".join(sorted(f"`{o}`" for o in operations))
                    + "\n\n"
                    + '**"What the hell is this?"**\n'
                    + "<http://en.wikipedia.org/wiki/"
                    + "Reverse_Polish_notation>"
                )
            else:
                _tokens = list(tokenize(*expression))
                _result = parse(_tokens)
                await ctx.send(_result)

    def setup(bot):
        bot.add_cog(ReversePolishCog())
