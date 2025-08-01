# pyunitx

[![Coverage Status](https://coveralls.io/repos/github/the-nick-of-time/units/badge.svg?branch=main)](https://coveralls.io/github/the-nick-of-time/units?branch=main)
[![Documentation Status](https://readthedocs.org/projects/pyunitx/badge/?version=latest)](https://pyunitx.readthedocs.io/en/latest/?badge=latest)

When doing calculations using physical measurements, it's all too easy to forget to account for
units. This can result in problems when you find you've been adding kilograms to newtons and
your calculation is off by a factor of ten.

This library uses the standard
library [decimal.Decimal](https://docs.python.org/3/library/decimal.html) for all calculations
to avoid most floating-point calculation pitfalls. Values given for units are automatically
converted so you can enter any value that constructor can take. Functionally, this means that
float notation should be given as strings rather than float literals.

## Illustrative Examples

Q. How many meters does light travel in a millisecond?

```pycon
>>> from pyunitx.time import seconds
>>> from pyunitx.constants import c
>>> (c * seconds("1e-3")).sig_figs(5)
2.9979E+5 m

```

Q. What is that in feet?

```pycon
>>> from pyunitx.time import seconds
>>> from pyunitx.constants import c
>>> (c * seconds("1e-3")).to_feet().sig_figs(5)
9.8357E+5 ft

```

Q. How fast is someone on the equator moving around the center of the earth?

```pycon
>>> from pyunitx.time import days
>>> from pyunitx.constants import earth_radius
>>> from math import pi
>>> circumference = 2 * pi * earth_radius
>>> (circumference / days(1)).to_meters_per_second().sig_figs(3)
464 m s^-1

```

Q. How fast is the earth orbiting the sun?

```pycon
>>> from pyunitx.time import julian_years
>>> from pyunitx.length import au
>>> from math import pi
>>> circumference = 2 * pi * au(1)
>>> (circumference / julian_years(1)).to_kilometers_per_hour().sig_figs(3)
1.07E+5 km hr^-1

```

Q. What's the mass of air in one of your car tires, if the inner radius is 6 inches, the outer
radius is 12.5 inches, the width is 8 inches, and it's filled to 42 psi?[^1]

[^1]: No, I don't write homework problems. Why do you ask?

```pycon
>>> from pyunitx.length import inches
>>> from pyunitx.pressure import psi
>>> from pyunitx.constants import R, air_molar_mass
>>> from pyunitx.temperature import celsius, celsius_to_kelvin_absolute
>>> from math import pi
>>> volume = (pi * inches(8) * (inches("12.5") ** 2 - inches(6) ** 2)).to_meters_cubed()
>>> pressure = psi(42).to_pascals()
>>> temperature = celsius_to_kelvin_absolute(celsius(25))
>>> mols = pressure * volume / (R * temperature)
>>> mass = mols * air_molar_mass
>>> mass.to_pounds_mass().sig_figs(3)
0.369 lbm

```

All constants like `R` are defined in SI base units so you will need to convert your units, but
as you can see, that task is easy. It's just a matter of calling `.to_<other unit>()`. You can
convert from any unit to another that measures the same dimension this way. If you're going to a
composite unit that hasn't been explicitly declared with a name, this is still possible, and the
library will create a converter for you - you just need to get the name right. The name format
is as intuitive as possible, as you can see with the above examples.

A name is made of the names of the base units, suffixed with `_squared`, `_cubed`, etc. to
relate the size of the exponent and prefixed by `per_` if the exponent is negative. Units with
negative exponents are made singular[^2] to follow how you would say it.

[^2]: Naively; it's done by just stripping off a trailing 's' if there is one.

Some examples of the most complicated possible situations will be illustrative.

```pycon
>>> from pyunitx.constants import gas_constant, stefan_boltzmann
>>> print(gas_constant.to_feet_pounds_per_mole_per_rankine().sig_figs(4))
3.407 ft^2 slug mol^-1 °R^-1 s^-2

>>> print(stefan_boltzmann.to_horsepower_per_feet_squared_per_rankine_to_the_fourth().sig_figs(5))
3.7013E-10 slug s^-3 °R^-4

```

You will notice that the output will have all units broken down to their bases. It is guaranteed
to be equivalent.

Now what happens if a calculation results in a predefined unit, like how newtons times meters
equals joules?

```pycon
>>> from pyunitx.voltage import volts
>>> from pyunitx.resistance import ohms
>>> print(volts(2) / ohms(100))
0.02 A

```

Calculations check their result against all the units that have been specially defined to find a
match. However, if you end up with a result that could be broken into some product of complex
units (like newton-seconds) this library will *not* do that for you and instead display it in
its basest components. This is because the number of possible options is large and it's not
possible to figure out what you want.

This library predefines all the SI units and dimensions, as well as a bunch of US Customary
units, but what if that's not enough? You might want to model some other quantity, like cash
flow in your budget.

```pycon
>>> from pyunitx import make_dimension, make_unit
>>> from pyunitx.time import days
>>> Money = make_dimension('Money')
>>> dollars = make_unit(name="dollars", abbrev="$", dimension=Money, scale=1)
>>> euros = make_unit(name="euros", abbrev="€", dimension=Money, scale="0.98019")
>>> (dollars(150) / days(7)).to_euros_per_year().sig_figs(6)
7984.80 € yr^-1

```

For more examples, including derived units, see the definitions in the package, like
[energy](https://github.com/the-nick-of-time/units/blob/main/pyunitx/energy.py) or
[time](https://github.com/the-nick-of-time/units/blob/main/pyunitx/time.py).

## `uconvert`

This package also comes with a command-line tool to perform unit conversions between any
predefined units.

Q. What's the conversion factor between kilowatts and foot-pounds per second?

```shell
$ uconvert 1 kW ft.lb/s
737.562 ft^2 slug s^-3
```

Q. What's my cat's weight in pounds, rounded to 3 significant figures?

```shell
$ uconvert -f 3 4.9 kg lbm
10.8 lbm
```

## Resistor color code converter

In the `resistance` module there is a function to construct a resistance from a color code.

Q. What's the value of a resistor reading "orange, violet, red, silver"?

```pycon
>>> from pyunitx.resistance import from_color
>>> from_color("OVRS")
3700 Ω

```

Q. I want to know the tolerance on that same resistor.

```pycon
>>> from pyunitx.resistance import from_color
>>> from_color("OVRS", include_tol=True)
(3700 Ω, 370.0 Ω)

```

Q. What's the full specification of a six-band resistor reading "green, blue, blue, orange,
brown, red"?

```pycon
>>> from pyunitx.resistance import from_color
>>> from_color("EUUOBR", include_coeff=True)
(566000 Ω, 5660.00 Ω, 28.30000 m^2 kg K^-1 A^-2 s^-3)

```

Note: that last quantity is ohms per kelvin. As above, it gets decomposed into its base units
due to not being a named derived unit.

For the mapping between letter and color,
see [the documentation](https://pyunitx.readthedocs.io/en/latest/complex.html#resistance).
Because the
starting letter of the colors are not unique (black, brown, and blue, as well as green, gray,
and gold) the letter chosen to represent it isn't perfectly intuitive. If you want your code to
be more readable, all the colors are defined in an enum that you can use directly.

```pycon
>>> from pyunitx.resistance import from_color, Color
>>> from_color([Color.ORANGE, Color.VIOLET, Color.RED, Color.SILVER], include_tol=True)
(3700 Ω, 370.0 Ω)

```

There is also a companion command-line tool that outputs its values in a human-readable format.
It is installed as `resistor` alongside `uconvert`.

```shell
$ resistor -c euuobr
566 kΩ + 28.3 Ω/K ± 5.66 kΩ
```

The full documentation can be found at [ReadTheDocs](https://pyunitx.readthedocs.io/en/latest/).
