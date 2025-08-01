"""A module for the first-class manipulation of physical quantities.

It is named ``pyunitx`` as a reference to the ``siunitx`` LaTeX package.

Most conversion factors come from
`this document from NIST <https://physics.nist.gov/cuu/pdf/sp811.pdf>`_.
Most values of constants come from
`this list also from NIST <https://physics.nist.gov/cuu/Constants/Table/allascii.txt>`_.
"""

# After the update for automatic conversion functions, this is somewhat less
# important, at least in terms of "not knowing about the conversion functions".
# However, it is still nice to have all the pre-constructed units and dimensions
# with special names available.
# noinspection PyUnresolvedReferences
from . import (
    angle,
    area,
    capacitance,
    charge,
    constants,
    current,
    data,
    derived,
    energy,
    force,
    frequency,
    inductance,
    length,
    luminosity,
    magneticflux,
    magneticfluxdensity,
    mass,
    mole,
    power,
    pressure,
    resistance,
    temperature,
    time,
    volume,
    voltage,
)

from ._api import (
    make_dimension,
    make_unit,
    make_compound_dimension,
    make_compound_unit,
    SIUNITX_OLD,
    SIUNITX_NEW,
)
