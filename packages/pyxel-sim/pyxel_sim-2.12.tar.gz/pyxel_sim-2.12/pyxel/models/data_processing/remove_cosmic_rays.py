#  Copyright (c) European Space Agency, 2020.
#
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.

"""Remove cosmic rays from an astronomical image using the LA Cosmic algorithm.

References,

* https://esa.gitlab.io/pyxel/doc/stable/references/model_groups/data_processing_models.html
* http://www.astro.yale.edu/dokkum/lacosmic/
* https://lacosmic.readthedocs.io/en/stable/
* https://www.astropy.org/ccd-reduction-and-photometry-guide/v/dev/notebooks/08-03-Cosmic-ray-removal.html

"""

import numpy as np
import xarray as xr

from pyxel.detectors import Detector


def compute_cosmic_rays(
    data_2d: np.ndarray,
    contrast: float = 1.0,
    cr_threshold: float = 50.0,
    neighbor_threshold: float = 50.0,
    effective_gain: float = 1.0,
    readnoise: float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute the image with cosmics removed, including the cosmic rays mask images.

    Refer to lacosmic documentation for parameter descriptions.
    https://lacosmic.readthedocs.io/en/stable/api/lacosmic.lacosmic.html#lacosmic.lacosmic

    Parameters
    ----------
    data_2d : np.ndarray
        2D image array
    contrast : float
        Contrast threshold between the Laplacian image and the fine-structure image.
    cr_threshold : float
        The Laplacian signal-to-noise ratio threshold for cosmic-ray detection.
    neighbor_threshold : float
        The Laplacian signal-to-noise ratio threshold for detection of cosmic rays in
        pixels neighboring the initially-identified cosmic rays.
    effective_gain : float
        Ratio of counts (e.g., electrons or photons) to the units of data.
    readnoise : float
        The read noise (in electrons) in the input data.
    """

    try:
        from lacosmic.core import lacosmic
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Missing optional package 'lacosmic'.\n"
            "Please install it with 'pip install pyxel-sim[model]'"
            "or 'pip install pyxel-sim[all]' or 'pip install lacosmic'"
        ) from exc

    cleaned_image, cr_mask = lacosmic(
        data_2d,
        contrast=contrast,
        cr_threshold=cr_threshold,
        neighbor_threshold=neighbor_threshold,
        effective_gain=effective_gain,
        readnoise=readnoise,
    )

    return cleaned_image, cr_mask


def remove_cosmic_rays(
    detector: Detector,
    contrast: float = 1.0,
    cr_threshold: float = 50.0,
    neighbor_threshold: float = 50.0,
    effective_gain: float = 1.0,
    readnoise: float = 0.0,
) -> None:
    """Extract the roi data converts it to xarray dataset and saves the information to the final result.

    Refer to lacosmic documentation for parameter descriptions.
    https://lacosmic.readthedocs.io/en/stable/api/lacosmic.lacosmic.html#lacosmic.lacosmic

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    contrast : float
        Contrast threshold between the Laplacian image and the fine-structure image.
    cr_threshold : float
        The Laplacian signal-to-noise ratio threshold for cosmic-ray detection.
    neighbor_threshold : float
        The Laplacian signal-to-noise ratio threshold for detection of cosmic rays in
        pixels neighboring the initially-identified cosmic rays.
    effective_gain : float
        Ratio of counts (e.g., electrons or photons) to the units of data.
    readnoise : float
        The read noise (in electrons) in the input data.
    """
    cleaned_image, cr_mask = compute_cosmic_rays(
        data_2d=detector.pixel.array,
        contrast=contrast,
        cr_threshold=cr_threshold,
        neighbor_threshold=neighbor_threshold,
        effective_gain=effective_gain,
        readnoise=readnoise,
    )
    detector.pixel.array = cleaned_image

    # Get current absolute time
    absolute_time = xr.DataArray(
        [detector.absolute_time],
        dims=["time"],
        attrs={"units": "s"},
    )
    cosmic_rays = xr.Dataset()
    cosmic_rays["cosmic_ray_mask"] = xr.DataArray(cr_mask, dims=["y", "x"])
    cosmic_rays["cosmic_ray_clean"] = detector.pixel.to_xarray()
    cosmic_rays = cosmic_rays.expand_dims(dim="time").assign_coords(time=absolute_time)

    key = "lacosmic"
    key_partial = "lacosmic_partial"

    try:
        _ = detector.data[key_partial]
    except KeyError:
        has_key_partial = False
    else:
        has_key_partial = True

    if not has_key_partial:
        data_set: xr.Dataset = cosmic_rays
    else:
        # Concatenate data
        previous_datatree = detector.data[key_partial]
        data_set = xr.merge([previous_datatree.to_dataset(), cosmic_rays])

    if detector.pipeline_count == (detector.num_steps - 1):
        detector.data[key] = data_set
    else:
        detector.data[key_partial] = data_set

    # This is the last step and there is at least two steps
    if detector.num_steps > 1 and (detector.pipeline_count == (detector.num_steps - 1)):
        detector.data[key_partial].orphan()


# TODO: document the parameters and reference lacosmic
# TODO: investigate if astroscrappy can be used. It's provided with anaconda.
# TODO: add a switch to choose between astroscrappy and lacosmic
