#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Model to generate charges in a SAPHIRA APD detector."""

import numpy as np

from pyxel.detectors import APD
from pyxel.util import set_random_seed


def calculate_dark_current_saphira(
    temperature: float,
    avalanche_gain: float,
    shape: tuple[int, int],
    exposure_time: float,
) -> np.ndarray:
    """Simulate dark current in a Saphira :term:`APD`.

    From: I. M. Baker et al., Linear-mode avalanche photodiode arrays in HgCdTe at Leonardo, UK: the
    current status, in Image Sensing Technologies: Materials, Devices, Systems, and Applications VI,
    2019, vol. 10980, no. May, p. 20.

    Parameters
    ----------
    temperature
    avalanche_gain
    shape
    exposure_time : float
        Length of the simulated exposure, in seconds.

    Returns
    -------
    ndarray
        An array the same shape and dtype as the input containing dark counts
        in units of charge (e-).
    """

    # We can split the dark current vs. gain vs. temp plot ([5] Fig. 3) into three linear
    # 'regimes': 1) low-gain, low dark current; 2) nominal; and 3) trap-assisted tunneling.
    # The following ignores (1) for now since this only applies at gains less than ~2.

    dark_nominal = (15.6e-12 * np.exp(0.2996 * temperature)) * (
        avalanche_gain
        ** ((-5.43e-4 * (temperature**2)) + (0.0669 * temperature) - 1.1577)
    )
    dark_tunnel = 3e-5 * (avalanche_gain**3.2896)

    # The value we want is the maximum of the two regimes (see the plot):
    dark = max(dark_nominal, dark_tunnel)

    # dark current for every pixel
    mean_dark_charge = dark * exposure_time

    # This random number generation should change on each call.
    dark_im_array_2d = np.random.poisson(mean_dark_charge, size=shape)

    return dark_im_array_2d


def dark_current_saphira(detector: APD, seed: int | None = None) -> None:
    """Simulate dark current in a Saphira APD detector.

    Reference: I. M. Baker et al., Linear-mode avalanche photodiode arrays in HgCdTe at Leonardo, UK: the
    current status, in Image Sensing Technologies: Materials, Devices, Systems, and Applications VI,
    2019, vol. 10980, no. May, p. 20.

    Parameters
    ----------
    detector : APD
        An APD detector object.
    seed : int, optional

    Notes
    -----
    For more information, you can find an example here:
    :external+pyxel_data:doc:`use_cases/APD/saphira`.
    """

    if not isinstance(detector, APD):
        raise TypeError("Expecting an APD object for detector.")
    if detector.environment.temperature > 100:
        raise ValueError(
            "Dark current estimation is inaccurate for temperatures more than 100 K!"
        )
    if detector.characteristics.avalanche_gain < 2:
        raise ValueError("Dark current is inaccurate for avalanche gains less than 2!")

    exposure_time = detector.time_step

    with set_random_seed(seed):
        dark_current_array: np.ndarray = calculate_dark_current_saphira(
            temperature=detector.environment.temperature,
            avalanche_gain=detector.characteristics.avalanche_gain,
            shape=detector.geometry.shape,
            exposure_time=exposure_time,
        ).astype(float)

    detector.charge.add_charge_array(dark_current_array)
