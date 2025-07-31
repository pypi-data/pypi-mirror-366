#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Fix pattern noise model."""

from pathlib import Path
from typing import Literal

import numpy as np

from pyxel.detectors import Detector, Geometry
from pyxel.util import (
    load_cropped_and_aligned_image,
    resolve_with_working_directory,
    set_random_seed,
)


def fpn_from_file(
    geometry: Geometry,
    filename: Path | str,
    position: tuple[int, int] = (0, 0),
    align: (
        Literal["center", "top_left", "top_right", "bottom_left", "bottom_right"] | None
    ) = None,
) -> np.ndarray:
    """Get fixed pattern noise caused by pixel non-uniformity during charge collection from a file.

    Parameters
    ----------
    geometry : Geometry
        Geometry of detector.
    filename : str or Path
        Path to a file with an array or an image.
    position : tuple
        Indices of starting row and column, used when fitting noise to detector.
    align : Literal
        Keyword to align the noise to detector. Can be any from:
        ("center", "top_left", "top_right", "bottom_left", "bottom_right")

    Raises
    ------
    FileNotFoundError
        If the folder path is not found.

    Returns
    -------
    prnu_2d : ndarray
        Fixed pattern noise caused by pixel non-uniformity during charge collection.
    """
    position_y, position_x = position

    folder_path = Path(resolve_with_working_directory(filename)).expanduser().resolve()

    if not folder_path.exists():
        raise FileNotFoundError(f"Cannot find folder '{folder_path}' !")

    # Load charge profile as numpy array.
    prnu_2d: np.ndarray = load_cropped_and_aligned_image(
        shape=(geometry.row, geometry.col),
        filename=filename,
        position_x=position_x,
        position_y=position_y,
        align=align,
    )

    return prnu_2d


def compute_simple_prnu(
    shape: tuple[int, int],
    quantum_efficiency: float,
    fixed_pattern_noise_factor: float,
) -> np.ndarray:
    """Compute fixed pattern noise caused by pixel non-uniformity during charge collection.

    Parameters
    ----------
    shape : tuple
        Output array shape.
    quantum_efficiency : float
        Quantum efficiency of detector.
    fixed_pattern_noise_factor : float
        Fixed pattern noise factor.

    Returns
    -------
    prnu_2d : ndarray
        Fixed pattern noise caused by pixel non-uniformity during charge collection.
    """

    prnu_2d = np.ones(shape) * quantum_efficiency
    prnu_sigma = quantum_efficiency * fixed_pattern_noise_factor
    prnu_2 = prnu_2d * (1 + np.random.lognormal(sigma=prnu_sigma, size=shape))

    return prnu_2


def fixed_pattern_noise(
    detector: Detector,
    filename: Path | str | None = None,
    position: tuple[int, int] = (0, 0),
    align: (
        Literal["center", "top_left", "top_right", "bottom_left", "bottom_right"] | None
    ) = None,
    fixed_pattern_noise_factor: float | None = None,
    seed: int | None = None,
) -> None:
    """Add fixed pattern noise caused by pixel non-uniformity during charge collection.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    filename : str or Path or None
        Path to a file with an array or an image.
    position : tuple
        Indices of starting row and column, used when fitting noise to detector.
    align : Literal
        Keyword to align the noise to detector. Can be any from:
        ("center", "top_left", "top_right", "bottom_left", "bottom_right")
    fixed_pattern_noise_factor : float, optional
        Fixed pattern noise factor.
    seed : int, optional
        Random seed.

    Raises
    ------
    ValueError
        If no filename and no fixed_pattern_noise_factor is giving or both are giving.
    """

    geo = detector.geometry  # type: Geometry
    char = detector.characteristics

    with set_random_seed(seed):
        if filename is not None and fixed_pattern_noise_factor is None:
            prnu_2d = fpn_from_file(
                geometry=geo,
                filename=filename,
                position=position,
                align=align,
            )

        elif fixed_pattern_noise_factor is not None and filename is None:
            prnu_2d = compute_simple_prnu(
                shape=geo.shape,
                quantum_efficiency=char.quantum_efficiency,
                fixed_pattern_noise_factor=fixed_pattern_noise_factor,
            )

        else:
            raise ValueError(
                "Either filename or fixed_pattern_noise_factor has to be defined."
            )
    detector.pixel.array *= prnu_2d
