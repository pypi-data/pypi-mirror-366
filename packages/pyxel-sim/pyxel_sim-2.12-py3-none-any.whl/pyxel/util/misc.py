#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Miscellaneous functions."""

import logging

import numpy as np


def round_convert_to_int(input_array: np.ndarray) -> np.ndarray:
    """Round list of floats in numpy array and convert to integers.

    Use on data before adding into DataFrame.

    :param input_array: numpy array object OR numpy array (float, int)
    :return:
    """
    array = input_array.astype(float)
    array = np.rint(array)
    array = array.astype(int)
    return array


def convert_to_int(input_array: np.ndarray) -> np.ndarray:
    """Convert numpy array to integer.

    Use on data after getting it from DataFrame.

    :param input_array: numpy array object OR numpy array (float, int)
    :return:
    """
    return input_array.astype(int)


class LogFilter(logging.Filter):
    """TBW."""

    def filter(self, record):
        """Filter or modify record."""
        return bool(
            record.threadName == "MainThread" or record.threadName.endswith("-0")
        )


def convert_unit(name: str) -> str:
    """Convert a unit name to its corresponding Unicode representation.

    Parameters
    ----------
    name : str
        A string representing a unit name.

    Returns
    -------
    str
        The unicode representation of the unit name.

    Examples
    --------
    >>> convert_unit("electron")
    'e⁻'
    """
    # Late import to speedup start-up time
    import astropy.units as u

    try:
        unit = u.Unit(name)
    except ValueError:
        return name
    else:
        return f"{unit:unicode}"


def get_dtype(bit_resolution: int) -> np.dtype:
    """Get NumPy data type based on a given bit resolution.

    Parameters
    ----------
    bit_resolution : int
        Number of bits representing the data.

    Returns
    -------
    np.dtype
        Numpy data type corresponding to the provided bit resolution.

    Raises
    ------
    ValueError
        Raised if the bit resolution does not fall within the supported range [1, 64]

    Examples
    --------
    >>> get_dtype(8)
    dtype('uint8')
    >>> get_dtype(12)
    dtype('uint16')
    """
    if 1 <= bit_resolution <= 8:
        return np.dtype(np.uint8)
    elif 9 <= bit_resolution <= 16:
        return np.dtype(np.uint16)
    elif 17 <= bit_resolution <= 32:
        return np.dtype(np.uint32)
    elif 33 <= bit_resolution <= 64:
        return np.dtype(np.uint64)
    else:
        raise ValueError(
            "Bit resolution does not fall within the supported range [1, 64]"
        )
