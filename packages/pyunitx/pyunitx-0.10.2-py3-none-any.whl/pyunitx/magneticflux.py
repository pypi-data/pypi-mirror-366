from pyunitx._api import make_compound_dimension, make_compound_unit, si_unit
from pyunitx.time import Time, seconds
from pyunitx.voltage import Potential, volts

MagneticFlux = make_compound_dimension({Potential: 1, Time: 1})

weber = make_compound_unit(
    name="weber",
    abbrev="Wb",
    scale=1,
    exponents={volts: 1, seconds: 1},
    doc="""\
    The amount of magnetic field passing through a certain area is called the
    magnetic flux. By Gauss's law, the value of this property measured over a 
    closed surface is zero; that is, as much is leaving as is entering.
    """
)

generated = si_unit(base_unit=weber)
globals().update(generated)

__all__ = [
    "MagneticFlux",
    "weber",
    *generated.keys()
]
