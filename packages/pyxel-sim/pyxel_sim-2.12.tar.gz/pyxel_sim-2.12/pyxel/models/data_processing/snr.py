#  Copyright (c) European Space Agency, 2020.
#  #
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.
"""Simple model to compute signal-to-noise-ratio."""

from collections.abc import Sequence
from typing import TYPE_CHECKING, Literal

import xarray as xr

from pyxel.detectors import Detector

if TYPE_CHECKING:
    from pyxel.data_structure import Image, Photon, Pixel, Signal


def compute_snr(
    data_array: xr.DataArray,
    absolute_time: xr.DataArray,
    dimensions: str | Sequence[str] = ("x", "y"),
) -> xr.Dataset:
    """Compute signal-to-noise-ratio (SNR) for input array and save it to a Dataset.

    Parameters
    ----------
    data_array : DataArray
        Input array which contains the data.
    absolute_time : DataArray
        Absolute time(s) of the data.
    dimensions : str or Sequence of str
        Dimensions, where the SNR should be computed on. Default is ("x", "y").

    Returns
    -------
    Dataset
    """

    signal = data_array.mean(dim=dimensions)
    noise = data_array.var(dim=dimensions)

    dataset = xr.Dataset()
    dataset["signal"] = signal
    dataset["noise"] = noise
    dataset["snr"] = signal / noise

    dataset = dataset.expand_dims(dim="time").assign_coords(time=absolute_time)

    return dataset


def signal_to_noise_ratio(
    detector: Detector,
    data_structure: Literal["pixel", "photon", "signal", "image", "all"] = "signal",
):
    """Get signal-to-noise-ratio (SNR) for given data structure.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    data_structure : Literal
        Keyword to choose data structure. Can be any from:
        ("pixel", "photon", "signal", "image", "all").
        Default is "signal" and computes the SNR on "signal".

    Notes
    -----
    For more information, you can find an example here:
    :external+pyxel_data:doc:`examples/models/data_processing/source_extractor/SEP_exposure`.
    """
    if data_structure == "all":
        names = ["pixel", "photon", "signal", "image"]
    else:
        names = [data_structure]

    parent: str = "/snr"
    parent_partial: str = f"{parent}/partial"

    for name in names:
        # Extract data from 'detector'
        data_bucket: Pixel | Photon | Signal | Image = getattr(detector, name)
        data_array: xr.DataArray = data_bucket.to_xarray(dtype=float)

        # Get current absolute time
        absolute_time = xr.DataArray(
            [detector.absolute_time],
            dims=["time"],
            attrs={"units": "s"},
        )

        # Get SNR data
        snr: xr.Dataset = compute_snr(
            data_array=data_array, absolute_time=absolute_time
        )

        key: str = f"{parent}/{name}"
        key_partial: str = f"{parent_partial}/{name}"

        try:
            _ = detector.data[key_partial]
        except KeyError:
            has_key_partial = False
        else:
            has_key_partial = True

        if not has_key_partial:
            data_set: xr.Dataset = snr
        else:
            # Concatenate data
            previous_datatree = detector.data[key_partial]
            data_set = xr.merge([previous_datatree.to_dataset(), snr])

        if detector.pipeline_count == (detector.num_steps - 1):
            detector.data[key] = data_set
        else:
            detector.data[key_partial] = data_set

    # This is the last step and there is at least two steps
    if detector.num_steps > 1 and (detector.pipeline_count == (detector.num_steps - 1)):
        detector.data[parent_partial].orphan()
