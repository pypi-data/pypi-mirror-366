from pyunitx._api import si_unit, make_unit, make_dimension

Current = make_dimension("Current")

amperes = make_unit(
    name="amperes",
    abbrev="A",
    scale=1,
    dimension=Current,
    doc="""\
    An ampere is a rate of charge movement equal to one coulomb per second. It
    is one of the fundamental units in the SI system.
    """
)

generated = si_unit(base_unit=amperes)
globals().update(generated)

__all__ = [
    "Current",
    "amperes",
    *generated.keys()
]
