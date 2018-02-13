"""
(c) Espeonageon 2018.
Licensed under the Mozilla Public License V2.0

You can use this however you like under the MPLv2.0 license, but you must
make sure to keep this message here.

---

Tokens that can be produced by the lexer. This includes literal values,
identifiers, reserve words, and operators. These are hard coded into the
interpreter module from here.
"""
import enum

from . import util

__all__ = ('TokenType', 'Token', 'RWS', 'OPS')


class TokenType(enum.IntFlag):
    """Holds various types of token type as flags."""
    # Null operation.
    NOP = 0

    # Value types
    NUMBER = enum.auto()
    STRING = enum.auto()
    IDENTIFIER = enum.auto()

    # Reserve words
    FOR = enum.auto()               # for
    IF = enum.auto()                # if
    ELSE_IF = enum.auto()           # elif
    ELSE = enum.auto()              # else
    WHILE = enum.auto()             # while
    UNTIL = enum.auto()             # until
    RETURN = enum.auto()            # return
    BREAK = enum.auto()             # break
    CONTINUE = enum.auto()          # continue
    LOOP = enum.auto()              # loop
    TRUE = enum.auto()              # true
    FALSE = enum.auto()             # false
    NULL = enum.auto()              # null
    DO = enum.auto()                # do
    TO = enum.auto()                # to
    IN = enum.auto()                # in

    # Operators
    PLUS = enum.auto()              # +
    DBL_PLUS = enum.auto()          # ++
    MINUS = enum.auto()             # -
    DBL_MINUS = enum.auto()         # --
    ASTERISK = enum.auto()          # *
    DBL_ASTERISK = enum.auto()      # **
    SOLIDUS = enum.auto()           # /
    DBL_SOLIDUS = enum.auto()       # //
    PERCENT = enum.auto()           # %
    AMPERSAND = enum.auto()         # &
    DBL_AMPERSAND = enum.auto()     # &&
    PIPE = enum.auto()              # |
    DBL_PIPE = enum.auto()          # ||
    CARET = enum.auto()             # ^
    TILDE = enum.auto()             # ~
    BANG = enum.auto()              # !
    ASSIGN = enum.auto()            # =
    EQUALS = enum.auto()            # ==
    LESS_THAN = enum.auto()         # <
    LESS_OR_EQUAL = enum.auto()     # <=
    GREATER_THAN = enum.auto()      # >
    GREATER_OR_EQUAL = enum.auto()  # >=
    UNEQUAL = enum.auto()           # !=
    BSL = enum.auto()               # <<
    SIGNED_BSR = enum.auto()        # >>
    UNSIGNED_BSR = enum.auto()      # >>>
    LAMBDA = enum.auto()            # =>
    DOT = enum.auto()               # .
    DOTDOT = enum.auto()            # ..
    DOTDOTDOT = enum.auto()         # ...
    COMMA = enum.auto()             # ,
    SEMI = enum.auto()              # ;
    COLON = enum.auto()             # :
    LEFT_PAREN = enum.auto()        # (
    RIGHT_PAREN = enum.auto()       # )
    LEFT_BRACE = enum.auto()        # {
    RIGHT_BRACE = enum.auto()       # }
    LEFT_SQ = enum.auto()           # [
    RIGHT_SQ = enum.auto()          # ]
    PLUS_ASS = enum.auto()          # +=
    MINUS_ASS = enum.auto()         # -=
    ASTERISK_ASS = enum.auto()      # *=
    DBL_ASTERISK_ASS = enum.auto()  # **=
    SOLIDUS_ASS = enum.auto()       # /=
    DBL_SOLIDUS_ASS = enum.auto()   # //=
    PERCENT_ASS = enum.auto()       # %=
    AMPERSAND_ASS = enum.auto()     # &=
    PIPE_ASS = enum.auto()          # |=
    CARET_ASS = enum.auto()         # ^=
    BSL_ASS = enum.auto()           # <<=
    SIGNED_BSR_ASS = enum.auto()    # >>=
    UNSIGNED_BSR_ASS = enum.auto()  # >>>=

    # Misc
    END_OF_FILE = enum.auto()       # Literal end of input.

    # Flag combinations for easier generic classification.
    VALUE_TYPE = NUMBER | STRING | IDENTIFIER

    RESERVE_WORD = (
        FOR | IF | ELSE_IF | ELSE | WHILE | UNTIL | RETURN | BREAK |
        CONTINUE | LOOP | TRUE | FALSE | NULL |
        IN | TO | DO)

    OPERATOR = (
        PLUS | DBL_PLUS | MINUS | DBL_MINUS | ASTERISK | DBL_ASTERISK |
        SOLIDUS | DBL_SOLIDUS | PERCENT | AMPERSAND | DBL_AMPERSAND |
        PIPE | DBL_PIPE | CARET | TILDE | BANG | ASSIGN | EQUALS |
        LESS_THAN | LESS_OR_EQUAL | GREATER_THAN | GREATER_OR_EQUAL |
        UNEQUAL | BSL | SIGNED_BSR | UNSIGNED_BSR | LAMBDA | DOT | COMMA |
        SEMI | COLON | LEFT_PAREN | RIGHT_PAREN | LEFT_BRACE | RIGHT_BRACE |
        LEFT_SQ | RIGHT_SQ | PLUS_ASS | MINUS_ASS | ASTERISK_ASS |
        DBL_ASTERISK_ASS | SOLIDUS_ASS | PERCENT_ASS | AMPERSAND_ASS |
        PIPE_ASS | CARET_ASS | BSL_ASS | SIGNED_BSR_ASS | UNSIGNED_BSR_ASS |
        DOTDOT | DOTDOTDOT)

    MISC = NOP | END_OF_FILE


class Token:
    """Token placeholder."""
    __slots__ = ('type', 'value')

    def __init__(self, token_type: TokenType, **kwargs):
        self.type = token_type
        self.value = kwargs.pop('value', token_type.name)

    def __eq__(self, other):
        """
        Determines equality.

        :param other: a TokenType, value type of some description, or another
            Token object to compare with.
        :return: true if this and ``other`` are deemed equivalent.
        """
        if isinstance(other, TokenType):
            return self.type == other
        if not isinstance(other, Token):
            return self.value == other
        else:
            return self.value == other.value and self.type == other.type

    def __repr__(self):
        return f'<Token type={self.type.name!r}, value={self.value!r}>'

    def __str__(self):
        return f'{self.type.name} token with value {self.value!r}'


# This pair of two-way ordered mappings aid in defining which string sequences
# are associated with which token types. RWS maps reserve words, while OPS
# maps operators. The difference between the two is that reserve-words must
# be followed by some sort of white space; operators do not have this
# requirement. The reason being that reserve words, if they have extra
# characters at the end, are probably not actually reserve words, but just
# similarly named identifiers. If this is the case, then they should be
# ignored and parsed as an identifier.
# Longer strings must come first before shorter strings that are a substring
# of the start of the longer string, otherwise they will be misinterpreted.
RWS = util.ReversingOrderedDict({
    # 8 chars
    TokenType.CONTINUE: 'continue',

    # 6 chars
    TokenType.RETURN: 'return',

    # 5 chars
    TokenType.BREAK: 'break',
    TokenType.FALSE: 'false',
    TokenType.UNTIL: 'until',
    TokenType.WHILE: 'while',

    # 4 chars
    TokenType.ELSE_IF: 'elif',
    TokenType.ELSE: 'else',
    TokenType.LOOP: 'loop',
    TokenType.NULL: 'null',
    TokenType.TRUE: 'true',

    # 3 chars
    TokenType.FOR: 'for',

    # 2 chars
    TokenType.DO: 'do',
    TokenType.IF: 'if',
    TokenType.IN: 'in',
    TokenType.TO: 'to',
})

OPS = util.ReversingOrderedDict({
    # 4 chars
    TokenType.UNSIGNED_BSR_ASS: '>>>=',

    # 3 chars
    TokenType.DOTDOTDOT: '...',
    TokenType.UNSIGNED_BSR: '>>>',
    TokenType.BSL_ASS: '<<=',
    TokenType.SIGNED_BSR_ASS: '>>=',
    TokenType.DBL_ASTERISK_ASS: '**=',
    TokenType.DBL_SOLIDUS_ASS: '//=',

    # 2 chars
    TokenType.DOTDOT: '..',
    TokenType.DBL_PLUS: '++',
    TokenType.DBL_MINUS: '--',
    TokenType.DBL_ASTERISK: '**',
    TokenType.DBL_SOLIDUS: '//',
    TokenType.DBL_AMPERSAND: '&&',
    TokenType.DBL_PIPE: '||',
    TokenType.EQUALS: '==',
    TokenType.LESS_OR_EQUAL: '<=',
    TokenType.GREATER_OR_EQUAL: '>=',
    TokenType.UNEQUAL: '!=',
    TokenType.BSL: '<<',
    TokenType.SIGNED_BSR: '>>',
    TokenType.LAMBDA: '=>',
    TokenType.PLUS_ASS: '+=',
    TokenType.MINUS_ASS: '-=',
    TokenType.ASTERISK_ASS: '*=',
    TokenType.SOLIDUS_ASS: '/=',
    TokenType.PERCENT_ASS: '%=',
    TokenType.AMPERSAND_ASS: '&=',
    TokenType.PIPE_ASS: '|=',
    TokenType.CARET_ASS: '^=',

    # 1 char
    TokenType.PLUS: '+',
    TokenType.MINUS: '-',
    TokenType.ASTERISK: '*',
    TokenType.SOLIDUS: '/',
    TokenType.PERCENT: '%',
    TokenType.AMPERSAND: '&',
    TokenType.PIPE: '|',
    TokenType.CARET: '^',
    TokenType.TILDE: '~',
    TokenType.BANG: '!',
    TokenType.ASSIGN: '=',
    TokenType.LESS_THAN: '<',
    TokenType.GREATER_THAN: '>',
    TokenType.DOT: '.',
    TokenType.SEMI: ';',
    TokenType.COLON: ':',
    TokenType.LEFT_PAREN: '(',
    TokenType.RIGHT_PAREN: ')',
    TokenType.LEFT_BRACE: '{',
    TokenType.RIGHT_BRACE: '}',
    TokenType.LEFT_SQ: '[',
    TokenType.RIGHT_SQ: ']',
})
