#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Simple model to convert photon into photo-electrons inside detector."""

from pathlib import Path
from typing import Literal

import numpy as np
import xarray as xr

from pyxel.detectors import Detector
from pyxel.util import load_cropped_and_aligned_image, set_random_seed


# TODO: move this function in class Photon
def integrate_photon(photon: xr.DataArray) -> xr.DataArray:
    # integrate flux along coordinate wavelength
    integrated_photon = photon.integrate(coord="wavelength")

    # integrated_photon.attrs["units"] = str(u.Unit(photon.units) * u.nm)

    return integrated_photon


def apply_qe(
    array: np.ndarray, qe: float | np.ndarray, binomial_sampling: bool = True
) -> np.ndarray:
    """Apply quantum efficiency to an array.

    Parameters
    ----------
    array : np.ndarray
    qe : ndarray or float
        Quantum efficiency.
    binomial_sampling : bool
        Binomial sampling. Default is True.

    Returns
    -------
    ndarray
    """
    if binomial_sampling:
        output = np.random.binomial(n=array.astype(int), p=qe).astype(float)
    else:
        output = array * qe
    return output


def simple_conversion(
    detector: Detector,
    quantum_efficiency: float | None = None,
    seed: int | None = None,
    binomial_sampling: bool = True,
) -> None:
    """Generate charge from incident photon via photoelectric effect, simple model.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    quantum_efficiency : float, optional
        Quantum efficiency.
    seed : int, optional
    binomial_sampling : bool
        Binomial sampling. Default is True.
    """
    if quantum_efficiency is not None:
        final_qe: float = quantum_efficiency
    else:
        try:
            final_qe = detector.characteristics.quantum_efficiency
        except ValueError as exc:
            raise ValueError(
                "Quantum efficiency is not defined. It must be either provided in the detector characteristics "
                "or as model argument."
            ) from exc

    if not 0 <= final_qe <= 1:
        raise ValueError("Quantum efficiency not between 0 and 1.")

    if detector.photon.ndim == 3:
        photon_2d: np.ndarray = integrate_photon(detector.photon.array_3d).to_numpy()
    else:
        photon_2d = detector.photon.array_2d

    with set_random_seed(seed):
        detector_charge = apply_qe(
            array=photon_2d,
            qe=final_qe,
            binomial_sampling=binomial_sampling,
        )
    detector.charge.add_charge_array(detector_charge)


def conversion_with_qe_map(
    detector: Detector,
    filename: str | Path,
    position: tuple[int, int] = (0, 0),
    align: (
        Literal["center", "top_left", "top_right", "bottom_left", "bottom_right"] | None
    ) = None,
    seed: int | None = None,
    binomial_sampling: bool = True,
) -> None:
    """Generate charge from incident photon via photoelectric effect, simple model with custom :term:`QE` map.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    filename : str or Path
        File path.
    position : tuple
        Indices of starting row and column, used when fitting :term:`QE` map to detector.
    align : Literal
        Keyword to align the :term:`QE` map to detector. Can be any from:
        ("center", "top_left", "top_right", "bottom_left", "bottom_right")
    seed : int, optional
    binomial_sampling : bool
        Binomial sampling. Default is True.

    Notes
    -----
    For more information, you can find an example here:
    :external+pyxel_data:doc:`use_cases/HxRG/h2rg`.
    """
    geo = detector.geometry
    position_y, position_x = position

    # Load charge profile as numpy array.
    qe: np.ndarray = load_cropped_and_aligned_image(
        shape=(geo.row, geo.col),
        filename=filename,
        position_x=position_x,
        position_y=position_y,
        align=align,
    )

    if not np.all((qe >= 0) & (qe <= 1)):
        raise ValueError("Quantum efficiency values not between 0 and 1.")

    with set_random_seed(seed):
        detector_charge = apply_qe(
            array=detector.photon.array, qe=qe, binomial_sampling=binomial_sampling
        )
    detector.charge.add_charge_array(detector_charge)
