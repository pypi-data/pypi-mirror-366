from pyunitx._api import make_compound_dimension, make_compound_unit, si_unit
from pyunitx.energy import Energy, joules
from pyunitx.force import pounds
from pyunitx.length import feet
from pyunitx.time import Time, seconds

Power = make_compound_dimension(exponents={Energy: 1, Time: -1}, name="Power")

watts = make_compound_unit(
    name="watts",
    scale=1,
    exponents={joules: 1, seconds: -1},
    abbrev="W",
    doc="""\
    A watt is a joule per second. In most cases, like calculating the energy
    expenditure of a heating system, collecting rates of energy use is the most
    useful then multiplying by time to get overall energy usage.
    """
)

generated = si_unit(base_unit=watts)
globals().update(generated)

kilowatts = make_compound_unit(
    name="kilowatts",
    scale=1000,
    exponents={joules: 1, seconds: -1},
    abbrev="kW",
    doc="""\
    A kilowatt is 1000 joules per second. Most household appliances draw power
    on the order of kilowatts.
    """
)

horsepower = make_compound_unit(
    name="horsepower",
    scale="7.456999e2",
    exponents={feet: 1, pounds: 1, seconds: -1},
    abbrev="hp",
    doc="""
    One horsepower is 550 foot-pounds per second, and is produced by a very 
    standards-compliant equine.
    """
)

__all__ = [
    "Power",
    "watts",
    "kilowatts",
    "horsepower",
    *generated.keys()
]
