#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel USAF-1951 illumination pattern."""

from typing import Literal

import pooch

from pyxel.detectors import Detector
from pyxel.models.photon_collection import load_image


def usaf_illumination(
    detector: Detector,
    position: tuple[int, int] = (0, 0),
    align: (
        Literal["center", "top_left", "top_right", "bottom_left", "bottom_right"] | None
    ) = None,
    convert_to_photons: bool = False,
    multiplier: float = 1.0,
    time_scale: float = 1.0,
    bit_resolution: int | None = None,
) -> None:
    r"""Apply USAF-1951 illumination pattern.

    Parameters
    ----------
    detector : Detector
    position : tuple
        Indices of starting row and column, used when fitting image to detector.
    align : Literal
        Keyword to align the image to detector. Can be any from:
        ("center", "top_left", "top_right", "bottom_left", "bottom_right")
    convert_to_photons : bool
        If ``True``, the model converts the values of loaded image array from ADU to
        photon numbers for each pixel using the Photon Transfer Function:
        :math:`\mathit{PTF} = \mathit{quantum\_efficiency} \cdot \mathit{charge\_to\_voltage\_conversion}
        \cdot \mathit{pre\_amplification} \cdot \mathit{adc\_factor}`.
    multiplier : float
        Multiply photon array level with a custom number.
    time_scale : float
        Time scale of the photon flux, default is 1 second. 0.001 would be ms.
    bit_resolution : int
        Bit resolution of the loaded image.
    """
    # Download the PNG file and save it locally.
    # Running this again will not cause a download
    filename: str = pooch.retrieve(
        url="https://gitlab.com/esa/pyxel-data/-/raw/master/samples/USAF-1951-optical-calibration-target.png",
        known_hash="md5:0a62eda6187aded13aca0e453db60665",
    )

    load_image(  # type: ignore[operator]
        detector=detector,
        image_file=filename,
        position=position,
        align=align,
        convert_to_photons=convert_to_photons,
        multiplier=multiplier,
        time_scale=time_scale,
        bit_resolution=bit_resolution,
    )
