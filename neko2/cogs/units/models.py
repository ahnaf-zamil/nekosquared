#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Implementation of the conversion data types.
"""
from decimal import Decimal
import enum
import typing


from neko2.shared import alg


@enum.unique
class UnitCategory(enum.Enum):
    """Holds a category of units."""
    DISTANCE = enum.auto()
    SPEED = enum.auto()
    ACCELERATION = enum.auto()
    AREA = enum.auto()
    VOLUME = enum.auto()
    # Also includes weight. For the benefit of the doubt,
    # we include grams in this category, since it is most
    # often used as a measurement of weight, rather than
    # mass.
    FORCE = enum.auto()


class Unit:
    """
    Representation of some unit measurement definition, such as meters.

    This will not store an arbitrary quantity. It exists as a way of simplifying
    the definition of what a unit is.

    :param to_si: formulae to take a decimal and convert it to SI from this.
    :param from_si: formulae to take a decimal and convert it from SI to this.
    :param name: main name.
    :param other_names: other names and abbreviations.
    :param is_si: True if this is an SI measurement, False otherwise and by
            default.
    """

    # What 1 si of whatever this unit measures is in this specific unit.
    def __init__(self,
                 to_si: typing.Callable[[Decimal], Decimal],
                 from_si: typing.Callable[[Decimal], Decimal],
                 name: str,
                 *other_names: str,
                 is_si: bool=False):
        self.names = (name, *other_names)
        self._to_si = to_si
        self._from_si = from_si
        self.is_si = is_si

    @property
    def name(self) -> str:
        return self.names[0]

    def to_si(self, this: Decimal) -> Decimal:
        """Converts this measurement to the SI equivalent."""
        if self.is_si:
            return this

        return self._to_si(this)

    def from_si(self, si: Decimal) -> Decimal:
        """Converts this measurement from the SI equivalent to this."""
        if self.is_si:
            return si

        return self._from_si(si)

    def __eq__(self, other: typing.Union[str, 'Unit']):
        """Equality is defines as a string match for any name"""
        if isinstance(other, Unit):
            return super().__eq__(other)
        else:
            return other.lower() in (n.lower() for n in self.names)

    def __hash__(self):
        """Enables hashing by the unit's primary name."""
        return hash(self.name.lower())

    def __str__(self):
        """"""
        return self.name

    def __repr__(self):
        return (
            f'<Unit name={self.name} '
            f'aliases={f", ".join("{a}" for a in self.names[1:])}')

    @classmethod
    def new_mult(cls,
                 si_per_this: Decimal,
                 name: str,
                 *other_names: str) -> "Unit":
        """
        Initialises a unit that is purely a multiple of the SI quantity.

        This is useful if there is a constant linear relationship, as is for
        most measurements, except for Temperature.
        """
        def to_si(c: Decimal):
            return c * si_per_this

        def from_si(c: Decimal):
            return c / si_per_this

        return cls(to_si, from_si, name, *other_names)

    @classmethod
    def new_si(cls, name: str, *other_names: str) -> "Unit":
        """Initialises a new SI measurement."""
        # noinspection PyTypeChecker
        return cls(None, None, name, *other_names, is_si=True)


class UnitCollection:
    def __init__(self,
                 unit_type: UnitCategory,
                 si: Unit,
                 *other_conversions: Unit):
        self.si = si
        # Obviously.
        self.si.is_si = True
        self.conversions = (si, *other_conversions)
        self.type = unit_type

    def find_unit(self, name: str) -> typing.Optional[Unit]:
        """
        Looks for a unit with a matching name, and returns it.

        If one does not exist, we return None.
        """
        return alg.find(lambda c: c == name, self.conversions)

    def __contains__(self, unit: str):
        """
        Determine if we can match the given string to some unit definition.
        :param unit: string to look up.
        :return: true if we can, false otherwise.
        """
        return bool(self.find_unit(unit))

    @staticmethod
    def convert(qty: Decimal, unit: Unit, to: Unit):
        """
        Converts one quantity to another assuming they are the same
        type of unit.
        """
        if unit == to:
            return qty
        else:
            return Decimal('1')

    def find_conversions(self, qty: Decimal, unit: Unit):
        """
        Returns a list of all conversion equivalents for this unit.

        The unit passed in is not included in this.
        """
        results = []
        for other_unit in self.conversions:
            if other_unit == unit:
                continue

            results.append(self.convert(qty, unit, other_unit))

        return tuple(results)

    def __iter__(self) -> typing.Iterator[Unit]:
        return iter(self.conversions)
