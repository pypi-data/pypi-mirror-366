#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""Reset noise models."""

import astropy.constants as const
import numpy as np

from pyxel.detectors import Detector
from pyxel.util import set_random_seed


def compute_ktc_noise(
    temperature: float, capacitance: float, shape: tuple[int, int]
) -> np.ndarray:
    """Compute KTC noise array. Formula from :cite:p:`Goebel_2018`.

    Parameters
    ----------
    temperature : float
        Temperature. Unit: K
    capacitance : float
        Node capacitance. Unit: F
    shape : tuple
        Shape of the output array.

    Returns
    -------
    np.ndarray
    """

    rms = np.sqrt(const.k_B.value * temperature / capacitance)

    return np.random.normal(scale=rms, size=shape)


def ktc_noise(
    detector: Detector,
    node_capacitance: float | None = None,
    seed: int | None = None,
) -> None:
    """Apply KTC reset noise to detector signal array.

    Parameters
    ----------
    detector : Detector
        Pyxel detector object.
    node_capacitance : float, optional
        Node capacitance. Unit: F
    seed : int, optional
        Random seed.

    Notes
    -----
    For more information, you can find examples here:

    * :external+pyxel_data:doc:`use_cases/CMOS/cmos`
    * :external+pyxel_data:doc:`use_cases/APD/saphira`
    """
    if node_capacitance is not None:
        if node_capacitance <= 0:
            raise ValueError("Node capacitance should be larger than 0!")

        capacitance: float = node_capacitance
    else:
        try:
            capacitance = detector.characteristics.node_capacitance
        except AttributeError as ex:
            raise AttributeError(
                "Characteristic node_capacitance not available for the detector"
                " used. Please specify node_capacitance in the model argument!"
            ) from ex

    if not detector.is_first_readout and detector.non_destructive_readout:
        # Do nothing when this is not the first readout and non-destructive mode
        return

    # This it the first readout or the destructive mode
    with set_random_seed(seed):
        noise_2d = compute_ktc_noise(
            temperature=detector.environment.temperature,
            capacitance=capacitance,
            shape=detector.geometry.shape,
        )

    detector.signal += noise_2d
