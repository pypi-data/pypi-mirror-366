from decimal import Decimal

from pyunitx._api import make_compound_dimension, make_compound_unit, si_unit
from pyunitx.force import Force, pounds, newtons
from pyunitx.length import Length, meters, inches

Pressure = make_compound_dimension(name="Pressure", exponents={Force: 1, Length: -2})

pascals = make_compound_unit(
    name="pascals",
    abbrev="Pa",
    scale=1,
    exponents={newtons: 1, meters: -2},
    doc="""The pascal is the base unit of pressure, but it is very small."""
)

generated = si_unit(base_unit=pascals)
globals().update(generated)

bars = make_compound_unit(
    scale="1e5",
    exponents={newtons: 1, meters: -2},
    name="bars",
    abbrev="bar",
    doc=r"""\
    A bar is 10\ :sup:`5` pascals, around sea level atmospheric pressure.
    """
)
psi = make_compound_unit(
    scale="6.894757e3",
    exponents={pounds: 1, inches: -2},
    name="psi",
    abbrev="psi",
    doc="""\
    Pounds per square inch are the typical units of pressure in |ucs|, despite 
    not using the base unit of length.
    """
)
torr = make_compound_unit(
    scale=Decimal(101325) / 760,
    exponents={newtons: 1, meters: -2},
    name="torr",
    abbrev="Torr",
    doc="""\
    One torr is equivalent to 1/760 of a :data:`standard atmosphere <pyunitx.constants.atm>`.
    It is used sometimes for fine gradations of pressure.
    """
)

__all__ = [
    "Pressure",
    "pascals",
    "bars",
    "psi",
    "torr",
    *generated.keys()
]
