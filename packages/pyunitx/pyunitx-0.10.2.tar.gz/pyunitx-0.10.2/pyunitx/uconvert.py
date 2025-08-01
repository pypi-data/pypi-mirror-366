import argparse
import decimal
import re

from pyunitx._api import _EXTANT_UNITS, Compound, _base_scale, make_compound_unit

_EXTANT_ABBREVS = {unit.abbreviation: unit for name, unit in _EXTANT_UNITS.items()}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--figures", default=6, type=int, help="The number of significant"
                                                                     " figures to output")
    parser.add_argument("quantity", help="The number of the source unit.")
    parser.add_argument(
        "src", help="""\
    The unit to convert from. Must be expressed as a series of unit symbols with exponents, 
    multiplied together using '.'. '/' for division can be used before each denominator unit,
    like J/kg/K for specific heat capacity. J/kg.K would instead be equivalent to J.K/kg. 
    If you don't like this ambiguity, the better way is to use a negative exponent on the unit. 
    As an example, you would give meters per second as 'm.s^-1'."""
    )
    parser.add_argument("dest", help="The unit to convert to, in the same format.")
    return parser.parse_args()


def parse_unit(spec):
    pattern = re.compile(r"([./])?([\w ]+)(\^-?\d+)?")
    pairs = []
    for match in re.finditer(pattern, spec):
        name = match.group(2)
        if name not in _EXTANT_ABBREVS:
            raise KeyError(f"{name} is not a recognized unit")
        if match.group(3):
            power = int(match.group(3)[1:])
        else:
            power = 1
        if match.group(1) == '/':
            power *= -1
        pairs.append((_EXTANT_ABBREVS[name], power))
    defined_scale = _base_scale(tuple(pairs))
    return Compound(tuple(pairs)), defined_scale


def main():
    args = parse_args()
    num = decimal.Decimal(args.quantity)
    sourcecomp, sscale = parse_unit(args.src)
    destcomp, dscale = parse_unit(args.dest)
    source = make_compound_unit(
        exponents=sourcecomp.to_pairs(),
        scale=sscale
    )
    dest = make_compound_unit(
        exponents=destcomp.to_pairs(),
        scale=dscale
    )
    if not source(num).is_dimension(dest.dimension):
        raise TypeError("Not the same dimension, cannot be converted")
    print(dest(num * source.scale / dest.scale).sig_figs(args.figures))


if __name__ == '__main__':
    main()
