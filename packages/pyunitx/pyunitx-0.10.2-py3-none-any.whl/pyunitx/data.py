from pyunitx._api import make_unit, make_dimension, si_unit

Data = make_dimension("Data")

bits = make_unit(
    name="bits",
    abbrev="b",
    dimension=Data,
    scale=1,
    doc="""\
    A bit is the smallest possible unit of data, representing the state of a 
    system that has exactly two possible states.
    """
)
bytes = make_unit(
    name="bytes",
    abbrev="B",
    dimension=Data,
    scale=8,
    doc="""\
    The modern definition of a byte is 8 bits. Originally, this just meant "the
    smallest addressable unit of memory" and could vary between different 
    computers.
    """
)
nybbles = make_unit(
    name="nybbles",
    abbrev="N",
    dimension=Data,
    scale=4,
    doc="""\
    One nybble is half a byte, 4 bits. It is generally not used for bulk data,
    only really for low-level work where every bit counts. Some CPU 
    architectures allow nybble-level manipulations.
    """
)
kibibytes = make_unit(
    name="kibibytes",
    abbrev="KiB",
    dimension=Data,
    scale=8 * 1024,
    doc="""\
    One KiB is 1024 bytes.
    
    Use of the SI prefixes ``kilo``, etc. are discouraged with data as the most
    natural set of scales are based on powers of two. Thus prefixes are selected
    using 2\\ :sup:`10` = 1024, which is close to 1000.
    """
)
mebibytes = make_unit(
    name="mebibytes",
    abbrev="MiB",
    dimension=Data,
    scale=8 * 1024 ** 2,
    doc="""\
    One MiB is 1024\\ :sup:`2` bytes.
    
    Use of the SI prefixes ``kilo``, etc. are discouraged with data as the most
    natural set of scales are based on powers of two. Thus prefixes are selected
    using 2\\ :sup:`10` = 1024, which is close to 1000.
    """
)
gibibytes = make_unit(
    name="gibibytes",
    abbrev="GiB",
    dimension=Data,
    scale=8 * 1024 ** 3,
    doc="""\
    One GiB is 1024\\ :sup:`3` bytes.
    
    Use of the SI prefixes ``kilo``, etc. are discouraged with data as the most
    natural set of scales are based on powers of two. Thus prefixes are selected
    using 2\\ :sup:`10` = 1024, which is close to 1000.
    """
)
tebibytes = make_unit(
    name="tebibytes",
    abbrev="TiB",
    dimension=Data,
    scale=8 * 1024 ** 4,
    doc="""\
    One TiB is 1024\\ :sup:`4` bytes.
    
    Use of the SI prefixes ``kilo``, etc. are discouraged with data as the most
    natural set of scales are based on powers of two. Thus prefixes are selected
    using 2\\ :sup:`10`, which is close to 1000.
    """
)
pebibytes = make_unit(
    name="pebibytes",
    abbrev="PiB",
    dimension=Data,
    scale=8 * 1024 ** 5,
    doc="""\
    One PiB is 1024\\ :sup:`5` bytes.
    
    Use of the SI prefixes ``kilo``, etc. are discouraged with data as the most
    natural set of scales are based on powers of two. Thus prefixes are selected
    using 2\\ :sup:`10` = 1024, which is close to 1000.
    """
)
exbibytes = make_unit(
    name="exbibytes",
    abbrev="EiB",
    dimension=Data,
    scale=8 * 1024 ** 6,
    doc="""\
    One EiB is 1024\\ :sup:`6` bytes.

    Use of the SI prefixes ``kilo``, etc. are discouraged with data as the most
    natural set of scales are based on powers of two. Thus prefixes are selected
    using 2\\ :sup:`10` = 1024, which is close to 1000.
    """
)

generated = si_unit(base_unit=bytes)
globals().update(generated)

__all__ = [
    "Data",
    "bits",
    "bytes",
    "nybbles",
    "kibibytes",
    "mebibytes",
    "gibibytes",
    "tebibytes",
    "exbibytes",
    *generated.keys(),
]
