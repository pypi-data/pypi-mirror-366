from pyunitx._api import make_compound_dimension, make_compound_unit, si_unit
from pyunitx.length import Length, meters, feet
from pyunitx.mass import Mass, kilograms, slugs
from pyunitx.time import Time, seconds

Force = make_compound_dimension(((Mass, 1), (Length, 1), (Time, -2)))

newtons = make_compound_unit(
    name="newtons",
    scale=1,
    exponents={kilograms: 1, meters: 1, seconds: -2},
    abbrev="N",
    doc="""The newton is the base SI unit of force."""
)

generated = si_unit(base_unit=newtons)
globals().update(generated)

kgf = kilograms_force = make_compound_unit(
    name="kilograms_force",
    scale="9.80665",
    exponents={kilograms: 1, meters: 1, seconds: -2},
    abbrev="kgf",
    doc="""One kgf is the weight of a kilogram in standard earth gravity."""
)
pounds = make_compound_unit(
    name="pounds",
    scale="4.4482216152605",
    exponents={slugs: 1, feet: 1, seconds: -2},
    abbrev="lb",
    doc="""\
    Pounds are a more elementary unit in |ucs| than an actual mass.
    """
)

__all__ = [
    "Force",
    "newtons",
    "pounds",
    "kgf",
    "kilograms_force",
    *generated.keys()
]
