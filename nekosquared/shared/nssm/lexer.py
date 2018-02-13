"""
(c) Espeonageon 2018.
Licensed under the Mozilla Public License V2.0

You can use this however you like under the MPLv2.0 license, but you must
make sure to keep this message here.

---

Lexical analyser/tokenizer/lexer

Takes string input and outputs tokens.
"""
import typing

from .tokens import *

__all__ = ()


# Used for reference later. Some may not be used.
BINARY_DIGITS = '01'
OCTAL_DIGITS = BINARY_DIGITS + '234567'
DECIMAL_DIGITS = OCTAL_DIGITS + '89'
HEXADECIMAL_DIGITS = DECIMAL_DIGITS + 'ABCDEFabcdef'


class NssmBadSyntax(RuntimeError):
    __slots__ = ('row', 'col', 'index', 'line', 'reason')

    def __init__(self, row: int, col: int, index: int, line: str, reason: str):
        self.row = row
        self.col = col
        self.line = line
        self.index = index
        self.reason = reason

    def __repr__(self):
        return (
            f'<{type(self).__name__} row={self.row!r}, col={self.col!r}, '
            f'index={self.index!r}, line={self.line!r}, '
            f'reason={self.reason!r}>'
        )

    def __str__(self):
        return '\n'.join((
            f'Syntax error at {self.row}:{self.col} -- {self.reason}',
            self.line,
            (' ' * (self.col - 1)) + '^'
        ))


class Lexer:
    """Iterable lexer. This will yield token objects."""
    __slots__ = ('input', 'row', 'col', 'index', '_has_yielded_eof')

    def __init__(self, src: str):
        """Initialise the lexer."""
        self.input = src
        self.row = 1
        self.col = 1
        self.index = 0
        self._has_yielded_eof = False

    def __iter__(self):
        """We are an iterator of our self."""
        return self

    def __next__(self):
        """Returns the next token."""
        # Check if we are at EOF. If we are, first yield an EOF, then raise
        # the StopIteration.
        if self.index >= len(self.input):
            if self._has_yielded_eof:
                raise StopIteration
            else:
                self._has_yielded_eof = True
                return Token(TokenType.END_OF_FILE, 'EOF')
        else:
            rest = self._rest

            if rest[0] in '\'"':
                return self._parse_str()
            elif self._is_next_a_num():
                return self._parse_num()

    @property
    def _rest(self):
        """Gets the slice rest of the string."""
        return self.input[self.index:]

    def _parse_bin(self):
        """Parses an unsigned binary integer."""
        self._ensure_then_step('0b', '0B')
        bin_str = self._get_while(lambda c: c in BINARY_DIGITS, 1)
        num = int(bin_str, 2)
        return Token(TokenType.NUMBER, num)

    def _parse_oct(self):
        """Parses an unsigned octal integer."""
        self._ensure_then_step('0o', '0O')
        oct_str = self._get_while(lambda c: c in OCTAL_DIGITS, 1)
        num = int(oct_str, 8)
        return Token(TokenType.NUMBER, num)

    def _parse_int(self):
        """Parses an unsigned decimal integer."""
        int_str = self._get_while(str.isdigit, 1)
        return Token(TokenType.NUMBER, int(int_str))

    def _parse_dec(self):
        """Parses some form of decimal number. This may be a real or an int."""
        number_str = ''
        curr = self._rest
        if curr.isdigit():
            number_str += self._parse_int()
            curr = self._rest

        if curr == '.':
            number_str += '.'
            self._step()
            curr = self._rest

        if curr.isdigit():
            number_str += self._parse_int()
            curr = self._rest

        if curr in 'eE':
            number_str += 'e'
            self._step()
            curr = self._rest

            if curr in '+-':
                number_str += curr
                self._step()
            number_str += self._parse_int()

        if not len(number_str):
            self._raise_syntax_error('Expected at least one digit')
        elif any(c in 'eE+-.' for c in number_str):
            return Token(TokenType.NUMBER, float(number_str))
        else:
            return Token(TokenType.NUMBER, int(number_str))

    def _parse_hex(self):
        """Parses an unsigned hexadecimal integer."""
        self._ensure_then_step('0o', '0O')
        hex_str = self._get_while(lambda c: c in HEXADECIMAL_DIGITS, 1)
        num = int(hex_str, 16)
        return Token(TokenType.NUMBER, num)

    def _parse_num(self):
        """Parses an unsigned floating point literal, or an integer."""
        curr = self._rest
        if any(curr.startswith(x) for x in ('0b', '0B')):
            return self._parse_bin()
        elif any(curr.startswith(x) for x in ('0o', '0O')):
            return self._parse_oct()
        elif any(curr.startswith(x) for x in ('0x', '0X')):
            return self._parse_hex()
        else:
            return self._parse_dec()

    def _parse_str(self):
        raise NotImplementedError

    def _parse_id_or_rw(self):
        """
        Handles parsing identifiers or reserve words. This includes operators
        and misc symbols.
        """
        raise NotImplementedError

    def _is_next_a_num(self):
        """
        We should parse a number if the given string starts with any of:
        0b, 0B, 0o, 0O, 0x, OX, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, or a period ``.``
        :return: true if we should parse the next token as a number.
        """
        return any(self._rest.startswith(x) for x in (
            '0b', '0B', '0o', '0O', '0x', '0X', *DECIMAL_DIGITS, '.'))

    def _step(self, offset=1):
        """Steps to the next character, or an offset if provided."""
        assert not self._has_yielded_eof

        while offset > 0:
            if self._rest.startswith('\n'):
                self.row += 1
                self.col = 1
            else:
                self.col += 1

            self.index += 1

    def _ensure_then_step(self, first: str, *rest: str):
        """
        Ensures that the rest of the input starts with one of the given
        strings. If it does, we proceed forwards by that amount of characters
        in steps. If it does not, we raise a syntax error. Otherwise, we
        return the string that was detected.

        Note that to aid performance, strings are not checked in descending
        order of length implicitly. It is up to you to pass the strings in, in
        the correct order.
        """
        strings = first, *rest

        for string in strings:
            if self._rest.startswith(string):
                self._step(len(string))
                return string

        rest = self._rest if self._rest else '<EOF>'
        if len(strings) > 1:
            self._raise_syntax_error(f'Expected one of {strings}, got {rest!r}')
        else:
            self._raise_syntax_error(f'Expected {string}, got {rest!r}')

    # noinspection PyUnresolvedReferences
    def _get_while(self, pred: typing.Callable[[str], bool], at_least=0):
        """
        Keeps extracting characters while the predicate is true, or until we
        reach EOF. The extracted substring is returned. This iterates over each
        character individually, remember.
        :param pred: predicate accepting the current character.
        :param at_least: minimum number of matching chars to get. This defaults
            to 0. If the extracted string is shorter than this value, then a
            syntax error will be raised.
        :return: the string (zero or more characters).
        """
        bucket = ''

        # EOF
        while self.index < len(self.input) and pred(self.input[self.index]):
            # Append current char and increment.
            bucket += self.input[self.index]
            self._step()

        if len(bucket) < at_least:
            self._raise_syntax_error('Unexpected character or end of file')

        return bucket

    def _raise_syntax_error(self, reason) -> typing.NoReturn:
        """Extracts current state information and raises a SyntaxException."""
        # Extract the current line using string voodoo.
        line, _, _ = self.input[self.index - self.col + 1:].partition('\n')
        raise NssmBadSyntax(self.row, self.col, self.index, line, reason)
