from pyunitx._api import make_dimension, make_unit, si_unit

Mass = make_dimension("Mass")

kilograms = make_unit(
    name="kilograms",
    dimension=Mass,
    scale=1,
    abbrev="kg",
    doc="""\
    Kilograms are the SI base unit of mass, despite having a magnitude prefix.
    """
)
grams = make_unit(
    name="grams",
    dimension=Mass,
    scale="0.001",
    abbrev="g",
    doc="""A gram is roughly defined as the mass of a milliliter of water."""
)

generated = si_unit(base_unit=grams, skip=["kilo"])
globals().update(generated)

tonnes = make_unit(
    name="tonnes",
    abbrev="t",
    scale=1000,
    dimension=Mass,
    doc="""\
    A metric tonne is equal to 1000 kilograms. This is equivalent to a megagram
    (Mg) and is easily confusable with the :class:`short ton <ton>`, so the
    megagram should be preferred.
    """
)

atomic_mass_unit = make_unit(
    name="atomic_mass_unit",
    abbrev="u",
    dimension=Mass,
    scale="1.660538782e-27",
    doc="""
    The unified atomic mass unit is defined as 1/12 of the mass of one atom of
    carbon-12, approximately the mass of one proton or neutron. As such, it is 
    equal to :math:`\\frac{1 g}{N_A}`.
    """
)

pounds_mass = make_unit(
    name="pounds_mass",
    dimension=Mass,
    scale="0.45359237",
    abbrev="lbm",
    doc="""Avoirdupois pounds are one of the definitions of mass in the |ucs|."""
)
troy_pound = make_unit(
    name="troy_pounds_mass",
    dimension=Mass,
    scale="0.3732417",
    abbrev="lbm_T",
    doc="""Troy pounds are a little smaller."""
)
slugs = make_unit(
    name="slugs",
    dimension=Mass,
    scale="14.59390",
    abbrev="slug",
    doc="""\
    A slug is the amount of mass that would be accelerated at 1 
    foot/second/second by a force of one pound. Using slugs you can form a 
    consistent set of measurements whereas the pound-mass cannot.
    """
)
tons = make_unit(
    name="tons",
    abbrev="tn",
    scale="907.18474",
    dimension=Mass,
    doc="""\
    One short ton is 2000 pounds. It should not be confused with the metric 
    tonne, which is 1000 kilograms.
    """
)

__all__ = [
    "Mass",
    "kilograms",
    "pounds_mass",
    "troy_pound",
    "slugs",
    "grams",
    "tonnes",
    "tons",
    "atomic_mass_unit",
    *generated.keys()
]
