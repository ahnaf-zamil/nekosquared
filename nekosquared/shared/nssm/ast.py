"""
(c) Espeonageon 2018.
Licensed under the Mozilla Public License V2.0

You can use this however you like under the MPLv2.0 license, but you must
make sure to keep this message here.

---

Abstract Syntax Tree implementation.

This consists of inner trees.
"""
import abc
import inspect
import typing

from . import tokens


################################################################################
# Ast type.                                                                    #
################################################################################
class Ast(abc.ABC):
    """Base type."""
    @abc.abstractmethod
    def __str__(self):
        pass

    @abc.abstractmethod
    def __repr__(self):
        pass


class NullOp(Ast):
    def __str__(self):
        return 'Null operation'

    def __repr__(self):
        return f'<Ast class={type(self).__name__!r}>'


################################################################################
# Atoms.                                                                       #
################################################################################
class Atom(Ast, abc.ABC):
    """Atomic value, such as an operator, identifier, or literal value."""
    token_type = tokens.TokenType.NOP

    def __init__(self, token: tokens.Token):
        # First assert the value is indeed valid.
        if not self.token_type & token.type:
            raise TypeError(f'Require {self.token_type!s}, got {token.type!s}')
        else:
            self.token = token

    def __init_subclass__(cls, **kwargs):
        # Get and assign the token type.
        cls.token_type = kwargs.pop('token_type')

    @property
    def type(self) -> tokens.TokenType:
        return self.token.type

    @property
    def row(self) -> int:
        return self.token.row

    @property
    def col(self) -> int:
        return self.token.col

    @property
    def index(self) -> int:
        return self.token.index

    @property
    def value(self) -> typing.Any:
        return self.token.value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f'<Atom class={type(self).__name__!r}, token={self.token!r}>'


class Operator(Atom, token_type=tokens.TokenType.OPERATOR):
    pass


class Value(abc.ABC):
    pass


class Identifier(Atom, Value, token_type=tokens.TokenType.IDENTIFIER):
    pass


class Number(Atom, Value, token_type=tokens.TokenType.NUMBER):
    pass


class String(Atom, Value, token_type=tokens.TokenType.STRING):
    pass


class Boolean(Atom, Value,
              token_type=tokens.TokenType.TRUE | tokens.TokenType.FALSE):
    pass


################################################################################
# Composites.                                                                  #
################################################################################
class Composite(Ast, abc.ABC):
    """Composite type."""
    def __str__(self):
        return type(self).__name__

    def __repr__(self):
        return (f'<Composite class={str(self)!r}, '
                f'contents={set(self._contents())!s}>')

    # Was going to cache this, but the use of a property causes infinite
    # recursion when we inspect the property itself.
    def _contents(self) -> {(str, typing.Any)}:
        """
        Reflects on any members that are Composites or Atoms, caching
        them.
        """
        members = inspect.getmembers(self)
        return frozenset((k, v) for k, v in members if isinstance(v, Ast))


class PrefixUnaryOperation(Composite):
    """Prefixed unary operator."""
    def __init__(self, operator: Operator, value: Value):
        assert isinstance(operator, Operator)
        assert isinstance(value, Value)

        self.operator = operator
        self.value = value


class PostfixUnaryOperation(Composite):
    """Post-fixed unary operator."""
    def __init__(self, value: Value, operator: Operator):
        assert isinstance(operator, Operator)
        assert isinstance(value, Value)

        self.operator = operator
        self.value = value


class BinaryOperation(Composite):
    """Binary operator."""
    def __init__(self, lvalue: Value, operator: Operator, rvalue: Value):
        assert isinstance(lvalue, Value)
        assert isinstance(operator, Operator)
        assert isinstance(rvalue, Value)

        self.lvalue = lvalue
        self.operator = operator
        self.rvalue = rvalue


class AssignmentOperation(Composite):
    """Binary assignment operator."""
    def __init__(self,
                 identifier: Identifier,
                 operator: Operator,
                 value: Value):
        assert isinstance(identifier, Identifier)
        assert isinstance(operator, Operator)
        assert isinstance(value, Value)

        self.identifier = identifier
        self.operator = operator
        self.value = value
