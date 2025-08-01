from pyunitx._api import make_dimension, make_unit, si_unit

Length = make_dimension("Length")

meters = make_unit(
    name="meters",
    dimension=Length,
    scale=1,
    abbrev="m",
    doc="""\
    Meters are the base SI unit of length. It is currently defined in terms of
    the speed of light.
    """
)

generated = si_unit(base_unit=meters)
globals().update(generated)

feet = make_unit(
    name="feet",
    dimension=Length,
    scale="0.3048",
    abbrev="ft",
    doc="""Feet are the base unit of length in the |ucs|."""
)
miles = make_unit(
    name="miles",
    dimension=Length,
    scale="1609.344",
    abbrev="mi",
    doc="""Miles are the long distance measure in the |ucs|."""
)
yards = make_unit(
    name="yards",
    dimension=Length,
    scale="0.9144",
    abbrev="yd",
    doc="""One yard is equal to three feet."""
)
inches = make_unit(
    name="inches",
    dimension=Length,
    scale="0.0254",
    abbrev="in",
    doc="""Twelve inches make up one foot."""
)
astronomical_unit = au = make_unit(
    name="au",
    dimension=Length,
    scale=149_597_870_700,
    abbrev="au",
    doc="""\
    One astronomical unit, or AU, is the average distance between Earth and the
    Sun. It's used in astronomical measurements, and is part of the definition
    of the :class:`parsecs <pyunitx.derived.parsecs>`.
    """
)
angstroms = make_unit(
    name="angstroms",
    dimension=Length,
    scale="1e-10",
    abbrev="Å",
    doc="""\
    Angstroms are a very small unit of length, useful in discussing the space
    between atoms in molecules.
    """
)

__all__ = [
    "Length",
    "meters",
    "feet",
    "miles",
    "yards",
    "inches",
    "astronomical_unit",
    "au",
    *generated.keys()
]
