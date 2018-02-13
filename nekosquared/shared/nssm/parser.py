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

__all__ = ('Parser',)


class Parser:
    """Parser implementation."""
    def __init__(self, tokens):
        self.tokens = tokens
        # Token number we are visiting.
        self.pos = 0

    def __call__(self):
        """
        Generates the abstract syntax tree for the given token collection,
        and returns it.
        """



    def _statement(self):
        """Parses a single statement, returning it as an AST node."""