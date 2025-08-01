from pyunitx._api import make_compound_dimension, make_compound_unit, si_unit
from pyunitx.current import Current, amperes
from pyunitx.time import Time, seconds
from pyunitx.voltage import Potential, volts

Inductance = make_compound_dimension(
    name="Inductance",
    exponents={Potential: 1, Time: 1, Current: -1}
)

henry = make_compound_unit(
    name="henry",
    abbrev="H",
    exponents={volts: 1, seconds: 1, amperes: -1},
    scale=1,
    doc="""\
    The henry is used to quantify the response of an inductor loop to 
    """
)
generated = si_unit(base_unit=henry)
globals().update(generated)

__all__ = [
    "Inductance",
    "henry",
    *generated.keys()
]
