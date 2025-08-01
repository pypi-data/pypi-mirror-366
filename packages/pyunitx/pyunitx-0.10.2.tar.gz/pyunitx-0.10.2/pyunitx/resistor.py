import argparse

from pyunitx.resistance import from_color
from pyunitx.temperature import kelvin


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--tolerance",
        action="store_true",
        help="Indicate the absolute tolerance in the output."
    )
    parser.add_argument(
        "-c",
        "--coefficient",
        action="store_true",
        help="Indicate both temperature coefficient and absolute tolerance in the output."
    )
    parser.add_argument(
        "spec",
        help="""The color code to read. Each color is represented by one letter, capitalized 
        here in the word:
        blacK, Brown, Red, Orange, Yellow, grEen, blUe, Violet, Gray, White, goLd, Silver.
        """
    )
    return parser.parse_args()


def main():
    args = parse_args()
    values = from_color(args.spec, args.tolerance, args.coefficient)
    if args.coefficient:
        sensitivity = str((values[2] * kelvin(1)).to_natural_si())
        print(
            f"{values[0].to_natural_si()} + {sensitivity}/K ± {values[1].to_natural_si()}"
        )
    elif args.tolerance:
        print(f"{values[0].to_natural_si()} ± {values[1].to_natural_si()}")
    else:
        print(values.to_natural_si())


if __name__ == '__main__':
    main()
