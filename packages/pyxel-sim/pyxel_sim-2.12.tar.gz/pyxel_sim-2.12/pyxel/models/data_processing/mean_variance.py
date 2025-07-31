#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Model to compute Mean-Variance metrics.

This module provides functions to calculate and store the mean and variance of detector data.
The results are stored in xarray Dataset objects, which can be further analyzed or visualized.
"""

from typing import TYPE_CHECKING, Literal

import xarray as xr

from pyxel.detectors import Detector

if TYPE_CHECKING:
    from pyxel.data_structure import Image, Photon, Pixel, Signal


def compute_mean_variance(data_array: xr.DataArray) -> xr.Dataset:
    """Compute the mean and variance into a Dataset.

    This functions calculates the mean and variance across the dimension 'x' and 'y'.

    Parameters
    ----------
    data_array : DataArray

    Returns
    -------
    Dataset

    Examples
    --------
    >>> data_array
    <xarray.DataArray 'image' (y: 100, x: 100)>
    array([[10406, 10409, 10472, ..., 10394, 10302, 10400],
           [10430, 10473, 10443, ..., 10427, 10446, 10452],
           [10456, 10524, 10479, ..., 10502, 10435, 10499],
           ...,
           [10381, 10385, 10552, ..., 10471, 10443, 10468],
           [10381, 10396, 10381, ..., 10472, 10380, 10509],
           [10455, 10431, 10382, ..., 10405, 10429, 10491]], dtype=uint32)
    Coordinates:
      * y        (y) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
      * x        (x) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
    Attributes:
        units:      adu
        long_name:  Image

    >>> mean_variance = compute_mean_variance(data_array)
    >>> mean_variance
    <xarray.Dataset> Size: 16B
    Dimensions:   ()
    Data variables:
        mean      float64 8B 1.177
        variance  float64 8B 2.719

    Notes
    -----
    For more information, you can find an example here:
    :external+pyxel_data:doc:`examples/models/data_processing/source_extractor/SEP_exposure`.
    """
    mean_variance = xr.Dataset()
    mean_variance["mean"] = data_array.mean(dim=["y", "x"])
    mean_variance["variance"] = data_array.var(dim=["y", "x"])

    # Assign units to mean and variance if the data array has a 'units' attribute
    if "units" in data_array.attrs:
        unit = data_array.attrs["units"]
        mean_variance["mean"].attrs["units"] = unit
        mean_variance["variance"].attrs["units"] = f"{unit}²"

    return mean_variance


def mean_variance(
    detector: Detector,
    data_structure: Literal["pixel", "photon", "image", "signal"] = "image",
    name: str | None = None,
) -> None:
    """Compute the mean and variance and store the result it in '.data' bucket.

    Parameters
    ----------
    detector : Detector
    data_structure : 'pixel', 'photon', 'image' or 'signal', optional. Default: 'image'
        Data bucket to use to compute the mean and variance.
    name : str, optional
        Name to use for the result.

    Examples
    --------
    >>> import pyxel
    >>> config = pyxel.load("exposure_mode.yaml")

    Run exposure mode with 'mean-variance' model

    >>> data_tree = pyxel.run_mode(
    ...     mode=config.exposure,
    ...     detector=config.detector,
    ...     pipeline=config.pipeline,
    ... )

    Get results

    >>> data_tree["/data/mean_variance"]
    <xarray.DataTree 'data'>
    Group: /data
    └── Group: /data/mean_variance
        └── Group: /data/mean_variance/image
                Dimensions:      (pipeline_idx: 100)
                Coordinates:
                  * pipeline_idx (pipeline_idx) int64 0 1 ... 98 99
                Data variables:
                    mean         (pipeline_idx) float64 5.723e+03 1.144e+04 ... 5.238e+04 5.238e+04
                    variance     (pipeline_idx) float64 3.238e+06 1.294e+07 2.91e+07 ... 4.03e+05 3.778e+05

    >>> mean_variance = data_tree["/data/mean_variance/image"]
    >>> mean_variance
    <xarray.DataTree 'image'>
    Group: /data/mean_variance/image
        Dimensions:      (pipeline_idx: 100)
        Coordinates:
          * pipeline_idx (pipeline_idx) int64 0 1 ... 98 99
        Data variables:
            mean         (pipeline_idx) float64 5.723e+03 1.144e+04 ... 5.238e+04 5.238e+04
            variance     (pipeline_idx) float64 3.238e+06 1.294e+07 2.91e+07 ... 4.03e+05 3.778e+05

    Display mean-variance plot

    >>> (
    ...     data_tree["/data/mean_variance/image"]
    ...     .to_dataset()
    ...     .plot.scatter(x="mean", y="variance", xscale="log", yscale="log")
    ... )
    .. figure:: _static/mean_variance_plot.png
        :scale: 70%
        :alt: Mean-Variance plot
        :align: center
    """
    if name is None:
        name = data_structure

    # Extract data from 'detector'
    data_bucket: Pixel | Photon | Image | Signal = getattr(detector, data_structure)
    data_array: xr.DataArray = data_bucket.to_xarray(dtype=float)

    # Computer the mean and variance
    mean_variance_1d: xr.Dataset = compute_mean_variance(data_array)
    mean_variance = mean_variance_1d.expand_dims(pipeline_idx=[detector.pipeline_count])

    # Prepare paths for storing the results
    parent: str = "/mean_variance"
    parent_partial: str = f"{parent}/partial"
    key: str = f"{parent}/{name}"
    key_partial: str = f"{parent_partial}/{name}"

    # If no partial data exists, create a new DataTree
    if key_partial not in detector.data.groups:
        data_set: xr.Dataset = mean_variance
    else:
        # Concatenate new data with existing partial data
        data_set = xr.merge([detector.data[key_partial].to_dataset(), mean_variance])

    # If pipeline is at its final step, clean up partial results and store the full result
    if detector.pipeline_count == (detector.num_steps - 1):
        # TODO: Find better solution (e.g. check if node parent_partial exists)
        if detector.num_steps == 1:
            detector.data[key] = data_set.squeeze(drop=True)

        else:
            # Detach node parent_partial
            detector.data[parent_partial].orphan()
            detector.data[key] = data_set.sortby("mean")

    else:
        # Otherwise, continue storing partial results
        detector.data[key_partial] = data_set
