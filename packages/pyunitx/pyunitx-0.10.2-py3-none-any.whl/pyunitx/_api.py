import itertools
import math
import re
import textwrap
import warnings
from decimal import Decimal
from fractions import Fraction
from typing import Union, Tuple, Type, Dict, Iterator, Optional

import sigfig

from pyunitx._exceptions import OperationError, ImplicitConversionError

__all__ = [
    "make_dimension",
    "make_unit",
    "make_compound_dimension",
    "make_compound_unit",
    "si_unit",
    "SIUNITX_NEW",
    "SIUNITX_OLD",
]

UnitOperand = Union['UnitBase', int, float, Decimal]
Scale = Union[Decimal, float, str]
UnitLike = Union[Type['UnitBase'], 'DimensionBase']
Pair = Tuple[UnitLike, Union[int, float, Decimal]]
Pairs = Tuple[Pair, ...]
Exponents = Union[Pairs, Dict[UnitLike, Union[int, float, Decimal]], 'Multiset']

SIUNITX_NEW = 3
SIUNITX_OLD = 2
_SI_PREFIXES = [
    ["yotta", "Y", "1e24"],
    ["zetta", "Z", "1e21"],
    ["exa", "E", "1e18"],
    ["peta", "P", "1e15"],
    ["tera", "T", "1e12"],
    ["giga", "G", "1e9"],
    ["mega", "M", "1e6"],
    ["kilo", "k", "1e3"],
    ["hecto", "h", "1e2"],
    ["deka", "da", "1e1"],
    ["deci", "d", "1e-1"],
    ["centi", "c", "1e-2"],
    ["milli", "m", "1e-3"],
    ["micro", "μ", "1e-6"],
    ["nano", "n", "1e-9"],
    ["pico", "p", "1e-12"],
    ["femto", "f", "1e-15"],
    ["atto", "a", "1e-18"],
    ["zepto", "z", "1e-21"],
    ["yocto", "y", "1e-24"],
]

_EXTANT_UNITS = {}


def make_dimension(name: str) -> 'DimensionBase':
    """Dimensions are the basic measurable quantities about the world, like length and time.

    For complex dimensions, see :func:`make_compound_dimension`.

    :param name: The name of this dimension.
    :return: An object that captures information about the dimension and the
        units that implement it.
    """
    dimension = make_compound_dimension((), name)
    return dimension


def make_unit(*, name: str, dimension: 'DimensionBase', scale: Scale, abbrev: str, doc="") \
        -> Type['UnitBase']:
    """A unit is a particular convention for measuring a dimension.

    The resulting class represents the abstract concept of the unit, say meters.
    Instances of the class associate that unit with a number, defining in this
    example a particular length like 8 meters. Instances of a unit class are
    called "measurements" within this documentation. Instances are immutable;
    any interactions with the public API will not change the object, anything
    that appears like it (for instance rounding with
    :meth:`sig_figs <pyunitx.length.meters.sig_figs>`) instead constructs and
    returns a copy.

    :param name: The name of the new unit, like "meters". Should be in its
        plural form.
    :param dimension: The dimension this unit measures.
    :param scale: How many of the base unit it would take to get one of the
        current unit. For instance, one kilometer has a scale of 1000 when the
        base unit is meters.
    :param abbrev: The canonical abbreviation for this unit, like "lb" for
        pounds or "g" for grams. Officially called the unit's symbol. Used for
        output.
    :param doc: Documentation for this unit, optional.
    :return: A class representing the unit. Instances of this class are
        measurements using the unit.
    """
    # @formatter:off
    # noinspection PyTypeChecker
    unit: Type[UnitBase] = type(name, (UnitBase,), {
        # Special class variables
        "__name__": name,
        "__doc__": textwrap.dedent(doc),
        # Class variables
        "abbreviation": abbrev,
        "scale": Decimal(scale),
        "instances": {},
        "dimension": dimension,
    })
    # @formatter:on
    unit.composition = Compound(((unit, 1),))

    setattr(dimension, "to_" + name.replace(" ", "_"), _make_converter(unit))
    _EXTANT_UNITS[unit.__name__] = unit
    return unit


def make_compound_dimension(exponents: Exponents, name: str = None) -> 'DimensionBase':
    """Create a dimension that's composed of basic dimensions.

    :param exponents: A sequence of tuples or dict that pair existing
        dimensions with the exponent they should be raised to.
    :param name: A name to give this dimension, like velocity for length/time.
        If there isn't a physically useful name for it, leave it unfilled and
        a name will automatically be created by using the names of its
        constituents.
    :return: An object that captures information about the dimension and the
        units that implement it.
    """
    if isinstance(exponents, dict):
        exponents = tuple(exponents.items())
    if name is None:
        name = str(Multiset(exponents))
    dimension = DimensionBase(name, exponents)

    return dimension


def make_compound_unit(*, scale: Scale, exponents: Exponents, name: str = None, abbrev=None,
                       doc="") -> Type['UnitBase']:
    """Create or retrieve a unit composed of other units.

    If an identical unit has already been created (defined by same exponents
    and scale) then return that pre-constructed unit. This makes sure that 
    calculations that result in a named unit (such as ohms) will be correctly
    reported as such rather than breaking down into their base components.

    :param scale: How many of the base unit one of this unit is equivalent to.
        Note that the scale factors of the constituent units are not taken into
        account. For instance, even though the conversion factor from meters per
        second to miles per hour could be determined strictly from the scale
        factors already defined for miles -> meters and hours -> seconds, doing
        that calculation is up to the constructor of the unit. I think this
        obeys the principle of least surprise, but I might be wrong. When new
        units are constructed by multiplication and division, the results *do*
        have the scale automatically computed as there is no other way that
        makes sense.
    :param exponents: A sequence of tuples or dict that pair existing units
        with the exponent they should be raised to.
    :param name: A name to give this unit, like joules. If no particular
        physical name exists, leave it unfilled and a name will be automatically
        constructed using the names of its component units and their exponents.
    :param abbrev: A canonical abbreviation for this unit, like J for joules.
        Officially called the unit's symbol. If no particular one exists, leave
        it unfilled and it will be automatically be constructed using the
        symbols of its base units.
    :param doc: Documentation for this unit, to show in tools like Sphinx.
    :return: A class representing this unit. Instances of the class are
        measurements with a magnitude.
    """
    if isinstance(exponents, dict):
        exponents = tuple(exponents.items())
    composition = Compound(exponents)
    existing = _access_unit_cache(composition, Decimal(scale))
    if existing:
        return existing
    if name is None:
        name = str(Multiset(exponents))
    dims_extracted = tuple((unit.dimension, exp) for unit, exp in composition.to_pairs())
    dims = _sort(_dedupe(dims_extracted))
    dimension = make_compound_dimension(dims)
    unit = make_unit(
        name=name,
        dimension=dimension,
        scale=scale,
        abbrev=abbrev if abbrev is not None else composition.make_abbreviation(),
        doc=doc
    )
    unit.composition = composition
    return unit


def si_unit(*, base_unit: Type['UnitBase'], skip=()) \
        -> Dict[str, Type['UnitBase']]:
    """Create the full range of SI prefixes on a unit.

    :param base_unit: The unit to which prefixes can be applied.
    :param skip: If you've already created one of the units (I did this with
        kilograms since prefixes apply to grams), list the prefix here so it
        doesn't get overwritten.
    :return: A dictionary between the name of the unit and the unit class.
    """
    generated = {}
    for prefix, short, scale in _SI_PREFIXES:
        if prefix in skip:
            continue
        new_scale = Decimal(scale) * base_unit.scale
        new_name = prefix + base_unit.__name__
        new_abbrev = short + base_unit.abbreviation
        if _is_base(base_unit.composition):
            new_unit = make_unit(
                name=new_name,
                abbrev=new_abbrev,
                scale=new_scale,
                dimension=base_unit.dimension,
            )
        else:
            new_unit = make_compound_unit(
                name=new_name,
                abbrev=new_abbrev,
                scale=new_scale,
                exponents=base_unit.composition.to_pairs(),
            )
        generated[new_name] = new_unit
    return generated


def _make_converter(unit):
    def converter(self):
        f"""Convert {self.__name__} to {unit.__name__}"""
        return unit(self.value * self.scale / unit.scale)

    return converter

def _exponent_name(unit: type, exponent: int) -> str:
    value_names = {
        1: "",
        2: "_squared",
        3: "_cubed",
        4: "_to_the_fourth",
        5: "_to_the_fifth",
        # that's the highest I've ever seen
    }
    prefix = 'per_' if exponent < 0 else ''
    body = unit.__name__.rstrip("s") if exponent < 0 else unit.__name__
    suffix = value_names.get(abs(exponent), f"_to_the_{abs(exponent)}")
    return f"{prefix}{body}{suffix}"


def _decompose_all(exponents: Pairs) -> Pairs:
    accumulator = []
    for unitish, exponent in exponents:
        accumulator.extend(_decompose(unitish, exponent))
    return _sort(accumulator)


def _decompose(unit: UnitLike, factor: int) -> Pairs:
    if not hasattr(unit, "composition"):
        # must be a unit currently under construction and doesn't have composition yet
        return (unit, factor),
    if len(unit.composition) == 1:
        return tuple((k, e * factor) for k, e in unit.composition.to_pairs())
    accumulator = []
    for k, e in unit.composition.to_pairs():
        accumulator.extend(_decompose(k, e * factor))
    return tuple(accumulator)


def _dedupe(pairs: Iterator[Pair]) -> Dict[UnitLike, int]:
    accumulator = {}
    for unitish, num in pairs:
        if unitish in accumulator:
            accumulator[unitish] += num
        else:
            accumulator[unitish] = num
    return accumulator


def _sort(d: Union[Exponents, Iterator[Pair]]) -> Pairs:
    if isinstance(d, dict):
        pairs = tuple(d.items())
    else:
        pairs = d
    return tuple(sorted(pairs, key=lambda p: (-p[1], p[0].__name__)))


def _access_unit_cache(c: 'Compound', scale) -> Optional[Type['UnitBase']]:
    remap = {(_sort(_dedupe(unit.composition.to_pairs())), unit.scale): unit
             for name, unit in _EXTANT_UNITS.items()}
    key = (_sort(_dedupe(c.to_pairs())), scale)
    if key in remap:
        return remap[key]
    if len(c) == 1 and _is_base(c):
        # Particular case: SI derivatives of base units are also base units,
        # divorced from their root
        magnitude = scale.log10()
        if magnitude == int(magnitude):
            si_prefix = [prefix for prefix, _, sc in _SI_PREFIXES if Decimal(sc) == scale]
            if len(si_prefix) != 1:
                return None
            si_name = si_prefix[0] + c.to_pairs()[0][0].__name__
            if si_name in _EXTANT_UNITS:
                return _EXTANT_UNITS[si_name]
    return None


def _is_base(composition: 'Compound') -> bool:
    return (len(composition) == 1
            and composition.to_pairs()[0][1] == 1
            and composition.to_pairs()[0][0].composition == composition)


def _base_scale(composition: Union['Compound', Pairs]) -> Decimal:
    base_scale = Decimal(1)
    for u, e in composition:
        base_scale *= u.scale ** e
    return base_scale


def _frac_to_decimal(frac: Union[Fraction, Decimal, int, float]) -> Decimal:
    if hasattr(frac, "numerator"):
        return frac.numerator / Decimal(frac.denominator)
    return Decimal(frac)


class DimensionBase:
    __INSTANCES = {}

    def __new__(cls, name: str, exponents: Pairs):
        exponents = tuple((k, v) for k, v in exponents if v != 0)
        if len(exponents) == 0:
            # Base dimensions are identified by name
            key = name
        elif len(exponents) == 1 and exponents[0][1] == 1:
            # If you end up with a base unit after a calculation
            decomposed = _decompose_all(exponents)
            if len(decomposed) == 1 and decomposed[0][1] == 1:
                key = name
            else:
                key = decomposed
        else:
            # Compound dimensions with the same base dimensions must refer to the same thing
            key = _decompose_all(exponents)
        if key not in cls.__INSTANCES:
            cls.__INSTANCES[key] = super(DimensionBase, cls).__new__(cls)
            this = cls.__INSTANCES[key]
            this.__name__ = name
            this.composition = Compound(exponents or ((this, 1),))
        return cls.__INSTANCES[key]

    def __hash__(self):
        return hash(self.__name__)

    def __repr__(self):
        return self.__name__


class Multiset:
    # just different enough from collections.Counter to be worth writing
    def __init__(self, pairs: Union[Pairs, 'Multiset', dict]):
        if isinstance(pairs, Multiset):
            self.store = pairs.store.copy()
        # Split these cases from each other just because it makes pycharm's
        # type inference work properly
        elif isinstance(pairs, dict):
            self.store = pairs.copy()
        else:
            self.store = _dedupe(pairs)
        self.store = {k: v for k, v in self.store.items() if v != 0}

    def __iter__(self) -> Iterator[UnitLike]:
        return iter(self.store.keys())

    def __getitem__(self, item):
        return self.store[item]

    def __eq__(self, other):
        if isinstance(other, Multiset):
            return self.store == other.store
        return False

    def __len__(self):
        return len(self.store)

    def __str__(self):
        names = [_exponent_name(k, v) for k, v in _sort(self.store)]
        return "_".join(names)

    def add(self, elem: Union[type, 'Multiset']):
        if isinstance(elem, type):
            elem = Multiset({elem: 1})
        return self.__merge(elem)

    def remove(self, elem: Union[type, 'Multiset']):
        if isinstance(elem, type):
            elem = Multiset({elem: -1})
        else:
            elem = Multiset({key: -value for key, value in elem.store.items()})
        return self.__merge(elem)

    def to_pairs(self) -> Pairs:
        return _sort((key, self[key]) for key in self)

    def __merge(self, other: 'Multiset') -> 'Multiset':
        copy = self.store.copy()
        for key in other:
            if key in copy:
                copy[key] += other[key]
            else:
                copy[key] = other[key]
            if copy[key] == 0:
                del copy[key]
        return Multiset(copy)


class Compound:
    def __init__(self, units: Union[Pairs, Multiset]):
        if isinstance(units, Multiset):
            self.units = Multiset(units)
        else:
            decomposed = _decompose_all(units)
            self.units = Multiset(decomposed)

    def __eq__(self, other):
        try:
            return self.units == other.units
        except AttributeError:
            return False

    def __len__(self):
        return len(self.units)

    def __iter__(self):
        yield from self.to_pairs()

    def __mul__(self, other: Union[type, Multiset, 'Compound']) -> 'Compound':
        if isinstance(other, type):
            other = Multiset({other: 1})
        elif isinstance(other, Compound):
            other = other.units
        self.__verify_no_dimension_mismatch(other)
        return Compound(self.units.add(other))

    def __truediv__(self, other: Union[type, Multiset, 'Compound']) -> 'Compound':
        if isinstance(other, type):
            other = Multiset({other: 1})
        elif isinstance(other, Compound):
            other = other.units
        self.__verify_no_dimension_mismatch(other)
        return Compound(self.units.remove(other))

    def __pow__(self, power: Union[int, float, Decimal, Fraction]):
        pairs = []
        for t, e in self.to_pairs():
            new_exponent = e * power
            pairs.append((t, _frac_to_decimal(new_exponent)))
        return Compound(tuple(pairs))

    def __verify_no_dimension_mismatch(self, extra: Multiset):
        existing_dimensions = {unit.dimension: unit for unit in self.units}
        for unit in extra:
            if (unit.dimension in existing_dimensions
                    and existing_dimensions[unit.dimension] is not unit):
                # the dimension is already represented in the current unit, but it isn't the
                # same unit
                raise ImplicitConversionError(unit, existing_dimensions[unit.dimension])

    def to_pairs(self) -> Pairs:
        return self.units.to_pairs()

    def make_abbreviation(self) -> str:
        ordered = _sort(self.to_pairs())
        chunks = []
        for unit, exponent in ordered:
            if exponent == 1:
                chunks.append(unit.abbreviation)
            else:
                chunks.append(f"{unit.abbreviation}^{exponent}")
        return " ".join(chunks)

    @classmethod
    def from_string(cls, spec: str) -> 'Compound':
        name_values = {
            None: 1,
            "": 1,
            "_squared": 2,
            "_cubed": 3,
            "_to_the_fourth": 4,
            "_to_the_fifth": 5,
            # that's the highest I've ever seen
        }
        names = "|".join(
            itertools.chain(
                _EXTANT_UNITS,
                [n.rstrip("s") for n in _EXTANT_UNITS]
            )
        )
        pattern = re.compile(
            r"(per_)?(" + names + "|[a-z]+)(_squared|_cubed|_to_the_fourth|_to_the_fifth)?"
        )
        pairs = []
        for match in re.finditer(pattern, spec):
            name = match.group(2)
            if name not in _EXTANT_UNITS:
                name = name + "s"
                if name not in _EXTANT_UNITS:
                    raise KeyError(f"The requested unit {name} does not exist")
            unit = _EXTANT_UNITS[name]
            power = name_values[match.group(3)]
            if match.group(1):
                power *= -1
            pairs.append((unit, power))
        return cls(tuple(pairs))


class UnitBase:
    """The base class for unit classes, defining their interface."""
    composition: 'Compound'
    scale: 'Decimal'
    abbreviation: str
    dimension: DimensionBase
    __slots__ = ["value"]

    def __new__(cls, value: Scale):
        """Create a new measurement using this unit.

        Instances are flyweights; two invocations of ``meters(1)`` will return
        the same object.

        :param value: The numerical value of the measurement, in any form that
            :external:py:class:`decimal.Decimal` can accept.
        :return: The newly created measurement, or the cached version.
        """
        v = Decimal(value)
        if v not in cls.instances:
            # noinspection PySuperArguments
            cls.instances[v] = super(type, cls).__new__(cls)
        instance = cls.instances[v]
        instance.value = v
        return instance

    def __add__(self, other: UnitOperand) -> 'UnitBase':
        """Add two measurements of the same unit together.

        :param other: Another measurement, with the same units.
        :raises TypeError: If measurements are not the same unit.
        :return: A measurement with the values of the two added.
        """
        if type(other) != type(self):
            raise OperationError("add", type(self), type(other))
        return type(self)(self.value + other.value)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other: UnitOperand) -> 'UnitBase':
        """Subtract a measurement of the same unit from this.

        :param other: Another measurement, with the same units.
        :raises TypeError: If measurements are not the same unit.
        :return: A measurement with the values of the two subtracted.
        """
        if type(other) != type(self):
            raise OperationError("subtract", type(self), type(other))
        return type(self)(self.value - other.value)

    def __rsub__(self, other):
        # Order doesn't matter as any cases where you're actually adding two
        # units will be handled by __sub__, so this will only have error cases
        # where you're subtracting incompatible types
        return self.__sub__(other)

    def __eq__(self, other):
        """Check if this measurement is the same value and unit of another.

        :param other: Another measurement, with the same units.
        :return: Whether these two measurements are identical.
        """
        if self is other:
            return True
        if type(other) != type(self):
            return False
        return self.value == other.value

    def __mul__(self, other: UnitOperand) -> Union['UnitBase', Decimal]:
        """Multiply two measurements.

        If the two quantities completely cancel (like a frequency times a
        duration), the result will be returned as a plain number.

        Otherwise, produce the correct unit by combining the units of the two
        multiplicands. If the result has two base units that measure the same
        dimension but are not the same (say you're trying to multiply ``ft/s`` by
        ``m^2``, ``ft*m^2`` would be in the result) a TypeError will be thrown.
        Instead you should convert one of the measurements to be compatible with
        the other before multiplying. In the example, that could be converting the
        ``ft/s`` to ``m/s``.

        :param other: Another measurement, with any units including none.
        :raises TypeError: If base units are incompatible.
        :return: The result of the calculation, with the compound units.
        """
        if isinstance(other, (int, float, Decimal)):
            return type(self)(self.value * Decimal(other))
        result_value = self.value * other.value
        unit_composition = (self.composition * other.composition).units
        if len(unit_composition) == 0:
            return result_value
        result_unit = make_compound_unit(
            scale=self.scale * other.scale,
            exponents=unit_composition
        )
        return result_unit(result_value)

    def __rmul__(self, other: UnitOperand) -> 'UnitBase':
        return self.__mul__(other)

    def __truediv__(self, other: UnitOperand) -> Union['UnitBase', Decimal]:
        """Divide two measurements.

        If the two quantities completely cancel (like the derivation of radians
        dividing length by length), the result will be returned as a plain
        number.

        Otherwise, produce the correct unit by combining the units of the two
        divisors. If the result has two base units that measure the same
        dimension but are not the same (say you're trying to divide ``ft/s`` by
        ``m^2``, ``ft/m^2`` would be in the result) a TypeError will be thrown.
        Instead you should convert one of the measurements to be compatible with
        the other before multiplying. In the example, that could be converting the
        ``ft/s`` to ``m/s``.

        :param other: Another measurement, with any units including none.
        :raises TypeError: If base units are incompatible.
        :return: The result of the division, with correct units.
        """
        if isinstance(other, (int, float, Decimal)):
            return type(self)(self.value / Decimal(other))
        result_units = self.composition / other.composition
        result_value = self.value / other.value
        if len(result_units) == 0:
            return result_value
        result_unit = make_compound_unit(
            scale=self.scale / other.scale,
            exponents=result_units.to_pairs()
        )
        return result_unit(result_value)

    def __rtruediv__(self, other: Union[int, float, Decimal]) -> 'UnitBase':
        result_unit = type(self ** -1)
        return result_unit(Decimal(other) / self.value)

    def __pow__(self, other: Union[int, float, Decimal, Fraction, str]):
        """Raise this measurement to a power.

        For instance, ``meters(4) ** 2 == meters_squared(16)``. You can also
        compute the magnitude of a vector with
        ``vec = [meters(4), meters(3)]; mag = (vec[0] ** 2 + vec[1] ** 2) ** (1/2)``.

        While the power of 1/2 (square root) can be exactly represented as a
        float, in general fractional powers will not be. For these cases you can
        use :external:py:class:`fractions.Fraction`.

        Anything other than fractions will be run through the
        :external:py:class:`decimal.Decimal` constructor first, so you can use
        anything including strings to represent the number.

        :param other: Any integer, the power to raise this measurement to.
        :return: A measurement with the value and units raised to the power.
        """
        if isinstance(other, str):
            other = Decimal(other)
        result_composition = self.composition ** other
        result_value = self.value ** _frac_to_decimal(other)
        result_unit = make_compound_unit(
            scale=self.scale ** _frac_to_decimal(other),
            exponents=result_composition.to_pairs()
        )
        return result_unit(result_value)

    def __lt__(self, other):
        """Check if this measurement is less than another.

        :param other: The measurement to compare to.
        :raises TypeError: If the two arguments are different units and can
            therefore not be compared.
        :return: Whether the other measurement is less than this one.
        """
        if type(other) != type(self):
            raise TypeError(f"{self.abbreviation} and {other.abbreviation} cannot be compared")
        return self.value * self.scale < other.value * other.scale

    def __le__(self, other):
        """Check if this measurement is less than or equal to another.

        :param other: The measurement to compare to.
        :raises TypeError: If the two arguments are different units and can
            therefore not be compared.
        :return: Whether the other measurement is less than this one.
        """
        return self < other or self == other

    def __abs__(self):
        """Get the absolute value of this measurement.

        :return: A copy of this measurement as an absolute value.
        """
        return type(self)(abs(self.value))

    def __neg__(self):
        """Get the negative of this measurement.

        :return: A copy of this measurement with sign flipped.
        """
        return type(self)(-self.value)

    def __pos__(self):
        """No-op, return self.

        This is unlike any other math operation since it doesn't make a copy.
        """
        return self

    def __getattr__(self, key: str):
        """Forward conversion requests to the dimension.

        The dimension, being the one thing all compatible units have in common,
        is the logical place to store all conversion functions between different
        units.

        Any ``x.to_*`` method calls are therefore passed to the dimension.

        :param key: The method name.
        :return: A pseudo-bound method of the conversion function.
        :raise AttributeError: If the requested method doesn't look like a
            conversion function, or if there isn't a conversion function by that
            name.
        """
        if key.startswith("to_"):
            if not hasattr(self.dimension, key):
                composition = Compound.from_string(key[3:])
                base_scale = _base_scale(composition)
                unit = make_compound_unit(
                    name=key[3:],
                    scale=base_scale,
                    exponents=composition.to_pairs(),
                )
                if 'radian' in key:
                    from pyunitx.angle import Angle
                    angle = [(u, e) for u, e in self.composition if u.dimension == Angle]
                    assert len(angle) == 1
                    angular, exponent = angle[0]
                    factor = (Decimal(math.pi) / angular(180 / angular.scale)) ** exponent
                    converted = self * factor
                    return lambda: _make_converter(unit)(converted)
                key = "to_" + unit.__name__
                # It is automatically registered on the dimension on creation,
                # no need to explicitly use it
            return lambda: getattr(self.dimension, key)(self)
        raise AttributeError()

    def __str__(self):
        return f"{self.value} {self.abbreviation}"

    def __repr__(self):
        return str(self)

    def __format__(self, format_spec):
        """Format this measurement similar to a float.

        :param format_spec: The format specification, in a restricted subset of
            the python `string formatting mini-language. \
            <https://docs.python.org/3/library/string.html#format-specification-mini-language>`_
            Currently only supports ``.[precision]g`` to round to the specified
            number of significant figures.
        """
        if not format_spec:
            return str(self)
        match = re.fullmatch(r"\.(\d+)[gG]", format_spec)
        if match:
            precision = int(match.group(1))
            return f"{self.sig_figs(precision).value} {self.abbreviation}"
        raise ValueError("Invalid format specification")

    def is_dimension(self, dim: DimensionBase) -> bool:
        """Check if this unit is of the given dimension.

        Most useful for checking whether two measurements can be reasonably
        compared with ``.equivalent_to`` or converted into the other.

        :param dim: The dimension to check against.
        :return: Whether this unit is of the given dimension.
        """
        try:
            return dim.composition == self.dimension.composition
        except AttributeError:
            return False

    def equivalent_to(self, other: 'UnitBase', figs=5) -> bool:
        """Check if this measurement represents the same quantity as another,
        within a certain precision.

        This effectively converts both units to the base unit to get them on
        equal footing before rounding and checking equality.

        :param other: The other measurement.
        :param figs: How many significant figures to round to before comparison.
        :raises TypeError: If the two units do not represent the same dimension
            and therefore cannot be compared.
        :return: Whether the two measurements are approximately equal.
        """
        if not other.is_dimension(self.dimension):
            raise ImplicitConversionError(type(other), type(self))
        with warnings.catch_warnings():
            # sigfig.round raises warnings if the quantity being rounded has fewer significant
            # figures than are given, but for the purposes of this comparison, I don't care
            # so ignore them all
            warnings.simplefilter("ignore")
            a = sigfig.round(self.value * self.scale, sigfigs=figs)
            b = sigfig.round(other.value * other.scale, sigfigs=figs)
        return a == b

    def sig_figs(self, figs=3):
        """Produce a version of this measurement rounded to significant figures.

        :param figs: How many significant figures to round to.
        :return: A new measurement with a rounded value.
        """
        rounded = sigfig.round(self.value, sigfigs=figs)
        return type(self)(rounded)

    def to_latex(self, siunitx_major_version=SIUNITX_NEW):
        r"""Output this unit value as it would be used in LaTeX with siunitx.

        Maybe script your calculations, then write the output to a .tex file
        and include it in your main document.

        :param siunitx_major_version: siunitx changed the name of its macro
            that outputs a number with a unit in version 3.0. Prior, it was
            ``\SI{number}{units}``, and after it was ``\qty{number}{units}``.
            Defaults to the most recent version. If you're using an older one,
            for instance if your TeXLive distribution is a few years old, pass
            in :data:`pyunitx.SIUNITX_OLD`, an alias for 2. I doubt anyone is
            using version 1.
        :return: A string formatted for direct inclusion in LaTeX.
        """
        if siunitx_major_version >= 3:
            fmt = r"\qty{{{value}}}{{{unit}}}"
        else:
            fmt = r"\SI{{{value}}}{{{unit}}}"
        if re.match(r"^\w+$", self.abbreviation):
            # This unit has an elementary name, like J for joules
            return fmt.format(value=self.value, unit=self.abbreviation)
        units = []
        for u, e in self.composition.to_pairs():
            if e == 1:
                units.append(u.abbreviation)
            else:
                units.append(f"{u.abbreviation}^{{{e}}}")
        return fmt.format(value=self.value, unit=".".join(units))

    def to_natural_si(self):
        """Convert this value to the most natural SI prefix.

        For instance, a value of 12100 meters would be changed into 12.1
        kilometers.
        This only works on units that have a specific name. Elementary units
        like meters of course work, as do composite units like joules. However,
        if a unit can only be expressed by some combination of named units
        (say N*s) then a TypeError will be raised.

        Currently ignores 10^-2 through 10^2; that is, centi through hecto.
        These are not used nearly as often, with the exception of the
        centimeter.

        :raises TypeError: If this unit is not an SI unit.
        :raises ValueError: If the value of this unit is too big or too small
            to be directly expressed with an SI prefix. Instead you should
            probably express your value as scientific notation using the base
            unit of the dimension.
        :return: This value expressed in the unit that requires no extra
            scientific notation.
        """
        magnitude = math.log10(self.scale)
        if magnitude != int(magnitude):
            raise TypeError("This isn't an SI unit so prefixes can't be applied")
        pattern = re.compile(
            f"[{''.join(p for _, p, __ in _SI_PREFIXES)}]?" +
            "(m|g|s|A|K|cd|mol|J|Hz|C|Pa|V|Ω)"
        )
        if not pattern.match(self.abbreviation):
            raise TypeError("This isn't a base SI unit so prefixes can't be applied")
        order = (self.value * self.scale).adjusted()
        if order > 26 or order < -24:
            raise ValueError("SI prefixes only cover 48 orders of magnitude")
        mag = (order // 3) * 3
        family = [u for u in _EXTANT_UNITS.values()
                  if u.dimension == self.dimension and u.scale == Decimal(f"1e{mag}")]
        if len(family) != 1:
            # kelvin/celsius are a special case, being equal in scale
            k = [u for u in family if u.__name__ == "kelvin"]
            family = [k[0]]
        converter_name = f"to_{family[0].__name__}"
        return getattr(self, converter_name)()
