from pyunitx._api import make_compound_unit, make_compound_dimension, si_unit
from pyunitx.charge import Charge, coulombs
from pyunitx.energy import Energy, joules

Potential = make_compound_dimension(name="Potential", exponents={Energy: 1, Charge: -1})

volts = make_compound_unit(
    name="volts",
    abbrev="V",
    scale=1,
    exponents={joules: 1, coulombs: -1},
    doc="""\
    Volts are the only real unit of electrical potential energy.
    """
)

generated = si_unit(base_unit=volts)
globals().update(generated)

__all__ = [
    "Potential",
    "volts",
    *generated.keys()
]
