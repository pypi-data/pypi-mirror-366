from pyunitx._api import make_compound_dimension, make_compound_unit
from pyunitx.length import Length, meters

__all__ = [
    "Area",
    "acres",
    "hectares",
]

Area = make_compound_dimension(name="Area", exponents={Length: 2})

acres = make_compound_unit(
    name="acres",
    abbrev="acre",
    scale="4.046873e3",
    exponents={meters: 2},
    doc="""\
    An acre is a common measure of land area.
    """
)
hectares = make_compound_unit(
    name="hectares",
    abbrev="ha",
    scale="1e4",
    exponents={meters: 2},
    doc="""\
    A hectare is a unit of land area compatible with SI units, being defined as
    10,000 square meters or the area of a square 100 meters on a side.
    """
)
