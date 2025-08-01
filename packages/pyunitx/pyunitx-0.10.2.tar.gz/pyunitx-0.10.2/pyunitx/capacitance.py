from pyunitx._api import make_compound_dimension, make_compound_unit, si_unit
from pyunitx.charge import coulombs, Charge
from pyunitx.voltage import volts, Potential

Capacitance = make_compound_dimension(
    name="Capacitance",
    exponents={Charge: 1, Potential: -1}
)

farads = make_compound_unit(
    name="farads",
    abbrev="F",
    scale=1,
    exponents={coulombs: 1, volts: -1},
    doc="""\
    Capacitance is related to how much energy can be stored inside a capacitor.
    It is extremely large for practical use, so most capacitors you can find are
    in the nano to pico range.
    """
)

generated = si_unit(base_unit=farads)
globals().update(generated)

__all__ = [
    "Capacitance",
    "farads",
    *generated.keys()
]
