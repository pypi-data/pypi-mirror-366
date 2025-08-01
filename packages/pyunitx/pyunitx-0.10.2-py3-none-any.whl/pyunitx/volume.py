from pyunitx._api import make_compound_dimension, make_compound_unit, si_unit
from pyunitx.length import Length, meters, feet

Volume = make_compound_dimension({Length: 3}, "Volume")

meters_cubed = make_compound_unit(
    scale=1,
    exponents={meters: 3}
)
liters = make_compound_unit(
    name="liters",
    scale="1e-3",
    exponents={meters: 3},
    abbrev="L",
    doc="""\
    A liter is one cubic decimeter, or a cube about as big as the palm of your 
    hand.
    """
)
milliliters = make_compound_unit(
    name="milliliters",
    scale="1e-6",
    exponents={meters: 3},
    abbrev="mL",
    doc="""A milliliter is around 20 drops of water, or the size of a 1-cm cube."""
)

generated = si_unit(base_unit=liters, skip=["milli"])
globals().update(generated)

feet_cubed = make_compound_unit(
    scale=".02831685",
    exponents={feet: 3}
)
fluid_ounces = make_compound_unit(
    name="fluid_ounces",
    exponents={meters: 3},  # As fl oz aren't defined in terms of some particular length cube
    scale="2.957353e-5",
    abbrev="fl oz",
    doc="""\
    Fluid ounces are the closest the |ucs| has to a base unit of volume.
    """
)
fluid_ounce_imperial = make_compound_unit(
    name="imperial fluid ounce",
    exponents={meters: 3},
    scale="2.841306e-5",
)
cups = make_compound_unit(
    name="cups",
    exponents={meters: 3},
    scale="2.365882e-4",
    abbrev="c",
    doc="""\
    Cups are a common unit of measure when cooking. One cup is 8 
    :class:`fluid ounces <fluid_ounces>` or 16 :class:`tablespoons`.
    """
)
teaspoons = make_compound_unit(
    name="teaspoons",
    exponents={meters: 3},
    scale="4.928922e-6",
    abbrev="tsp",
    doc="""\
    Teaspoons are a common unit of measure when cooking. It's about equal to
    5 :class:`milliliters`, if you need to do quick conversion.
    """
)
tablespoons = make_compound_unit(
    name="tablespoons",
    exponents={meters: 3},
    scale="1.478676e-5",
    abbrev="tbsp",
    doc="""\
    Tablespoons are a common unit of measure when cooking.
    One tablespoon is 3 :class:`teaspoons`.
    """
)
gallons = make_compound_unit(
    name="gallons",
    exponents={meters: 3},
    scale="3.785412e-3",
    abbrev="gal",
    doc="""\
    Gallons are the bulk unit of volume in the |ucs|. It is equal to 128
    :class:`fluid ounces <fluid_ounces>`, or 4 quarts, or 8 pints, or 16 
    :class:`cups`. At least this range of measurements is all powers of 2.
    """
)
imperial_gallons = make_compound_unit(
    name="imperial_gallons",
    exponents={meters: 3},
    scale="4.54609e-3"
)

__all__ = [
    "Volume",
    "meters_cubed",
    "liters",
    "milliliters",
    "fluid_ounces",
    "cups",
    "teaspoons",
    "tablespoons",
    "gallons",
    "imperial_gallons",
    "fluid_ounce_imperial",
    *generated.keys()
]
