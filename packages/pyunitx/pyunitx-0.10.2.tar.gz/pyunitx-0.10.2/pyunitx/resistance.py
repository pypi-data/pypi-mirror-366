import enum
from decimal import Decimal
from typing import Union, Tuple, Iterable

from pyunitx._api import make_compound_unit, make_compound_dimension, si_unit
from pyunitx.current import Current, amperes
from pyunitx.temperature import kelvin
from pyunitx.voltage import Potential, volts

Resistance = make_compound_dimension(name="Resistance", exponents={Potential: 1, Current: -1})

ohms = make_compound_unit(
    name="ohms",
    abbrev="Ω",
    exponents={volts: 1, amperes: -1},
    scale=1,
    doc="""\
    A current of one ampere traveling through one ohm of resistance drops its
    potential by one volt.
    """
)

generated = si_unit(base_unit=ohms)
globals().update(generated)


class Color(enum.Enum):
    """Resistor color codes.

    This associates the colors with their value as digits, or multipliers, or
    tolerance percentages.
    """
    BLACK = "K"
    BROWN = "B"
    RED = "R"
    ORANGE = "O"
    YELLOW = "Y"
    GREEN = "E"
    BLUE = "U"
    VIOLET = "V"
    GRAY = "G"
    WHITE = "W"
    GOLD = "L"
    SILVER = "S"
    BLANK = None

    def digit(self):
        """Gets the value of a color when used as a digit."""
        values = {
            Color.BLACK: 0,
            Color.BROWN: 1,
            Color.RED: 2,
            Color.ORANGE: 3,
            Color.YELLOW: 4,
            Color.GREEN: 5,
            Color.BLUE: 6,
            Color.VIOLET: 7,
            Color.GRAY: 8,
            Color.WHITE: 9,
        }
        return values[self]

    def multiplier(self):
        """Gets the value of a color when used as a multiplier."""
        multipliers = {
            Color.BLACK: 10 ** 0,
            Color.BROWN: 10 ** 1,
            Color.RED: 10 ** 2,
            Color.ORANGE: 10 ** 3,
            Color.YELLOW: 10 ** 4,
            Color.GREEN: 10 ** 5,
            Color.BLUE: 10 ** 6,
            Color.VIOLET: 10 ** 7,
            Color.GRAY: 10 ** 8,
            Color.WHITE: 10 ** 9,
            Color.GOLD: 10 ** -1,
            Color.SILVER: 10 ** -2,
        }
        return multipliers[self]

    def tolerance(self):
        """Gets the value of a color when used as a tolerance percentage."""
        tolerances = {
            Color.BROWN: Decimal(1),
            Color.RED: Decimal(2),
            Color.GREEN: Decimal(".5"),
            Color.BLUE: Decimal(".25"),
            Color.VIOLET: Decimal(".1"),
            Color.GRAY: Decimal(".05"),
            Color.GOLD: Decimal("5"),
            Color.SILVER: Decimal("10"),
            Color.BLANK: Decimal("20"),
        }
        return tolerances[self] / 100

    def temp_coefficient(self):
        """Gets the value of a color used as a temperature coefficient, in
        fractions per kelvin."""
        coefficients = {
            Color.BLACK: 250,
            Color.BROWN: 100,
            Color.RED: 50,
            Color.ORANGE: 15,
            Color.YELLOW: 25,
            Color.GREEN: 20,
            Color.BLUE: 10,
            Color.VIOLET: 5,
            Color.GRAY: 1,
        }
        return (Decimal(coefficients[self]) / 1000000) / kelvin(1)


coeff = type(ohms(1) / kelvin(1))


def from_color(spec: Union[str, Iterable[Color]], include_tol=False, include_coeff=False) \
        -> Union[ohms, Tuple[ohms, ohms], Tuple[ohms, ohms, coeff]]:
    """Read the definition of a resistor from its color code.

    By default, just returns the resistor value in ohms. The return type is
    changed by ``include_tol`` and ``include_coeff``, as described below.

    :param spec: Either a string where each character is a color code, or an
        iterable of :class:`Color`\\ s to be somewhat more readable.
    :param include_tol: If True, output a tuple of (resistor value in ohms,
        absolute resistor tolerance in ohms).
    :param include_coeff: If True, output a tuple of (resistor value in ohms,
        absolute resistor tolerance in ohms, absolute resistor temperature
        sensitivity in ohms per kelvin). Overrides ``include_tol``.
    """
    if isinstance(spec, str):
        spec = spec.upper()
    if len(spec) == 4:
        digits = spec[:2]
        multiplier = spec[2]
        tolerance = spec[3]
        sensitivity = None
    elif len(spec) == 5:
        digits = spec[:3]
        multiplier = spec[3]
        tolerance = spec[4]
        sensitivity = None
    elif len(spec) == 6:
        digits = spec[:3]
        multiplier = spec[3]
        tolerance = spec[4]
        sensitivity = spec[5]
    elif len(spec) == 3:
        digits = spec[:2]
        multiplier = spec[2]
        tolerance = None
        sensitivity = None
    else:
        raise ValueError("Resistor codes can be 3-6 bands long.")
    value = 0
    for i, char in enumerate(reversed(digits)):
        e = Color(char)
        value += e.digit() * 10 ** i
    value *= Color(multiplier).multiplier()
    if include_coeff:
        return (ohms(value),
                ohms(value) * Color(tolerance).tolerance(),
                ohms(value) * Color(sensitivity).temp_coefficient())
    if include_tol:
        return ohms(value), ohms(value) * Color(tolerance).tolerance()
    return ohms(value)


__all__ = [
    "Resistance",
    "ohms",
    "from_color",
    "Color",
    *generated.keys()
]
