from pyunitx._api import make_unit, si_unit
from pyunitx.angle import arcseconds
from pyunitx.constants import c
from pyunitx.length import Length, au
from pyunitx.time import julian_years

parsec_calc = au(1) / arcseconds(1).to_radians()
parsecs = make_unit(
    name="parsecs",
    dimension=Length,
    scale=parsec_calc.to_meters().value,
    abbrev="pc",
    doc="""\
    One parsec is an astronomical distance defined by observation of the stars.
    As we orbit the sun, nearer stars move with respect to the extremely distant
    ones, an effect called parallax. Since we know the distance from the earth
    to the sun, we can calculate the distance the distance to those stars
    with a little trigonometry.
    
    If a star moves across an angle of one 
    :class:`arcsecond <pyunitx.angle.arcsecond>` as we observe it at either end of
    a distance of 1 AU, that means it is one parsec away. 
    """
)

si_parsec = si_unit(base_unit=parsecs)
globals().update(si_parsec)

lightyears = make_unit(
    name="lightyears",
    dimension=Length,
    scale=c.value * julian_years.scale,
    abbrev="ly",
    doc="""\
    A lightyear is the distance light travels in one year.
    As the real duration of a year changes over time (we're not going to say a
    lightyear is a different distance in a leap year) it uses a constant value
    of a Julian year, or 365.25 days.
    """
)

si_lightyear = si_unit(base_unit=lightyears)
globals().update(si_lightyear)

__all__ = [
    "parsecs",
    "lightyears",
    *si_parsec.keys(),
    *si_lightyear.keys(),
]
