from pyunitx._api import make_compound_dimension, make_compound_unit, si_unit
from pyunitx.length import Length, meters
from pyunitx.time import Time, seconds
from pyunitx.voltage import Potential, volts

MagneticFluxDensity = make_compound_dimension({Potential: 1, Time: 1, Length: -2})

tesla = make_compound_unit(
    name="tesla",
    abbrev="T",
    exponents={volts: 1, seconds: 1, meters: -2},
    scale=1,
    doc="""\
    The strength of a magnetic field in a particular location is best 
    represented as an area density.
    """
)

generated = si_unit(base_unit=tesla)
globals().update(generated)

__all__ = [
    "MagneticFluxDensity",
    "tesla",
    *generated.keys()
]
