"""
(c) Espeonageon 2018.
Licensed under the Mozilla Public License V2.0

You can use this however you like under the MPLv2.0 license, but you must
make sure to keep this message here.

---

Parser

This consumes a collection of tokens and attempts to generate a representative
abstract syntax tree for the entire input sequence.
"""
from . import ast
from . import tokens

__all__ = ('Parser',)


class Parser:
    """Parser implementation."""
    def __init__(self, tokens):
        self.tokens = tuple(tokens)
        # Token number we are visiting.
        self.pos = 0

    def __call__(self):
        """
        Generates the abstract syntax tree for the given token collection,
        and returns it.
        """
        yield ast.BinaryOperator(
            ast.Identifier(
                tokens.Token(
                    token_type=tokens.TokenType.IDENTIFIER,
                    value="foobar",
                    row=0, col=0, index=0)
            ),

            ast.Operator(
                tokens.Token(
                    token_type=tokens.TokenType.UNSIGNED_BSR,
                    row=1, col=1, index=1
                )
            ),

            ast.Identifier(
                tokens.Token(
                    token_type=tokens.TokenType.IDENTIFIER,
                    value="bazbork",
                    row=2, col=2, index=2)
            )
        )

    def _statement(self):
        """Parses a single statement, returning it as an AST node."""