#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Model to generate charges due to simple dark current process."""

import numpy as np

from pyxel.detectors import Detector
from pyxel.util import set_random_seed


def calculate_simple_dark_current(
    num_rows: int, num_cols: int, current: float, exposure_time: float
) -> np.ndarray:
    """Simulate dark current in a :term:`CCD`.

    This function generates a simulated detector image by dark current noise.

    Parameters
    ----------
    num_rows : int
        Number of rows for the generated image.
    num_cols : int
        Number of columns for the generated image.
    current : float
        Dark current, in e⁻/pixel/second
    exposure_time : float
        Length of the simulated exposure, in seconds.

    Returns
    -------
    ndarray
        An array the same shape and dtype as the input containing dark counts
        in units of charge (e-).
    """
    # Calculate mean dark charge for every pixel
    mean_dark_charge = current * exposure_time

    # Generate dark current noise using poisson distribution
    # This random number generation should change on each call.
    dark_im_array_2d = np.random.poisson(mean_dark_charge, size=(num_rows, num_cols))
    return dark_im_array_2d


def simple_dark_current(
    detector: Detector, dark_rate: float, seed: int | None = None
) -> None:
    """Simulate dark current in a detector.

    Parameters
    ----------
    detector : Detector
        Any detector object.
    dark_rate : float
        Dark current, in e⁻/pixel/second, which is the way
        manufacturers typically report it.
    seed : int, optional
    """

    exposure_time = detector.time_step
    geo = detector.geometry

    with set_random_seed(seed):
        dark_current_array: np.ndarray = calculate_simple_dark_current(
            num_rows=geo.row,
            num_cols=geo.col,
            current=dark_rate,
            exposure_time=exposure_time,
        ).astype(float)

    detector.charge.add_charge_array(dark_current_array)
