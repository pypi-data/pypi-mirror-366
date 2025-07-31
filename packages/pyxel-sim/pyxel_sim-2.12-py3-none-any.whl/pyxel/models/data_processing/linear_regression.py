#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Model to compute linear regressions."""

from typing import TYPE_CHECKING, Literal

import numpy as np

from pyxel.detectors import Detector

if TYPE_CHECKING:
    import xarray as xr

    from pyxel.data_structure import Image, Photon, Pixel, Signal


def linear_regression(
    detector: Detector,
    data_structure: Literal["pixel", "photon", "image", "signal"] = "image",
    name: str | None = None,
) -> None:
    """Compute a linear regression along 'readout_time' and store it in '.data' bucket.

    Parameters
    ----------
    detector : Detector
    data_structure : 'pixel', 'photon', 'image' or 'signal'
        Data bucket to use for the linear regression.
    name : str, optional
        Name to use for the result.

    Raises
    ------
    ValueError
        If less than 2 timing steps is used.

    Examples
    --------
    >>> import pyxel
    >>> config = pyxel.load("exposure_mode.yaml")
    >>> linear_regression(detector=detector)

    Run exposure mode with 'data_processing/linear_regression' model

    >>> data_tree = pyxel.run_mode(
    ...     mode=config.exposure,
    ...     detector=config.detector,
    ...     pipeline=config.pipeline,
    ... )

    Get results

    >>> data_tree["/data/linear_regression"]
    DataTree('linear_regression', parent="data")
    └── DataTree('image')
            Dimensions:        (y: 100, x: 100)
            Coordinates:
              * y              (y) int64 0 1 2 3 4 5 6 7 8 9 ... 91 92 93 94 95 96 97 98 99
              * x              (x) int64 0 1 2 3 4 5 6 7 8 9 ... 91 92 93 94 95 96 97 98 99
            Data variables:
                slope          (y, x) float64 396.8 396.2 396.7 397.0 ... 396.1 396.2 396.7
                intercept      (y, x) float64 8.363e+03 8.356e+03 ... 8.364e+03 8.36e+03
                r2             (y, x) float64 0.9313 0.9312 0.9316 ... 0.9309 0.931 0.9313
                slope_std      (y, x) float64 14.94 14.93 14.91 14.91 ... 14.96 14.96 14.94
                intercept_std  (y, x) float64 846.4 845.8 844.5 844.5 ... 847.7 847.6 846.1

    Display slope as a 2D map

    >>> data_tree["/data/linear_regression/image/slope"].plot(robust=True)

    .. figure:: _static/linear_regression_slope.png
        :scale: 70%
        :alt: Linear Regression Slope
        :align: center

    Notes
    -----
    For more information, you can find an example here:
    :external+pyxel_data:doc:`examples/models/data_processing/source_extractor/SEP_exposure`.
    """
    if detector.num_steps < 3:
        raise ValueError(f"Expecting at least 2 steps. Got: {detector.num_steps}")

    if name is None:
        name = data_structure

    # Extract data from 'detector'
    data_bucket: Pixel | Photon | Image | Signal = getattr(detector, data_structure)

    x: float = detector.absolute_time
    y: xr.DataArray = data_bucket.to_xarray(dtype=float)

    if detector.is_first_readout:
        detector.data[f"/linear_regression/{name}/partial/n"] = 1
        detector.data[f"/linear_regression/{name}/partial/sum_x"] = x
        detector.data[f"/linear_regression/{name}/partial/sum_y"] = y
        detector.data[f"/linear_regression/{name}/partial/sum_xy"] = x * y
        detector.data[f"/linear_regression/{name}/partial/sum_x2"] = x * x
        detector.data[f"/linear_regression/{name}/partial/sum_y2"] = y * y
    else:
        detector.data[f"/linear_regression/{name}/partial/n"] += 1
        detector.data[f"/linear_regression/{name}/partial/sum_x"] += x
        detector.data[f"/linear_regression/{name}/partial/sum_y"] += y
        detector.data[f"/linear_regression/{name}/partial/sum_xy"] += x * y
        detector.data[f"/linear_regression/{name}/partial/sum_x2"] += x * x
        detector.data[f"/linear_regression/{name}/partial/sum_y2"] += y * y

        if detector.is_last_readout:
            n = detector.data[f"/linear_regression/{name}/partial/n"]
            sum_x = detector.data[f"/linear_regression/{name}/partial/sum_x"]
            sum_y = detector.data[f"/linear_regression/{name}/partial/sum_y"]
            sum_xy = detector.data[f"/linear_regression/{name}/partial/sum_xy"]
            sum_x2 = detector.data[f"/linear_regression/{name}/partial/sum_x2"]
            sum_y2 = detector.data[f"/linear_regression/{name}/partial/sum_y2"]

            factor_x = n * sum_x2 - sum_x * sum_x
            factor_y = n * sum_y2 - sum_y * sum_y

            slope = (n * sum_xy - sum_x * sum_y) / factor_x
            intercept = (sum_y - slope * sum_x) / n

            r2 = slope * slope * factor_x / factor_y

            factor_var = factor_y - slope * slope * factor_x
            slope_var = factor_var / ((n - 2) * factor_x)
            intercept_var = sum_x2 * factor_var / (n * (n - 2) * factor_x)

            slope_std = np.sqrt(slope_var)
            intercept_std = np.sqrt(intercept_var)

            if y_unit := y.attrs.get("units"):
                x_unit = "s"
                slope.attrs["unit"] = f"{y_unit}/{x_unit}"
                intercept.attrs["unit"] = y_unit
                slope_std.attrs["unit"] = f"{y_unit}/{x_unit}"  # type: ignore
                intercept_std.attrs["unit"] = y_unit  # type: ignore

            detector.data[f"/linear_regression/{name}/slope"] = slope
            detector.data[f"/linear_regression/{name}/intercept"] = intercept
            detector.data[f"/linear_regression/{name}/r2"] = r2
            detector.data[f"/linear_regression/{name}/slope_std"] = slope_std
            detector.data[f"/linear_regression/{name}/intercept_std"] = intercept_std
            detector.data[f"/linear_regression/{name}"].attrs = {
                "long_name": f"Linear regression: {name}"
            }

            # Remove '/linear_regression/partial
            detector.data[f"/linear_regression/{name}/partial"].orphan()
