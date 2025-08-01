from pyunitx._api import make_dimension, make_unit, si_unit

Quantity = make_dimension("Quantity")

moles = make_unit(
    name="moles",
    dimension=Quantity,
    scale=1,
    abbrev="mol",
    doc="""\
    A mole is the number of atoms in 12 grams of carbon-12.
    
    It basically is a dimensionless quantity, but is included in the SI system
    for its pragmatic usefulness in chemistry and fluid physics.
    """
)
pound_moles = make_unit(
    name="pound_moles",
    abbrev="lbmol",
    dimension=Quantity,
    scale="453.59237",
    doc="""\
    One lbmol is equal to the number of atoms in 12 lbm of carbon-12. As such
    it is as much larger than the mol as a lbm is larger than a gram.
    """
)
generated = si_unit(base_unit=moles)
globals().update(generated)

__all__ = [
    "Quantity",
    "moles",
    "pound_moles",
    *generated.keys()
]
