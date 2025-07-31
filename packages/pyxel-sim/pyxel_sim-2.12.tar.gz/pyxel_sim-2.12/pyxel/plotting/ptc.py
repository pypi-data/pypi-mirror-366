#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Plotting functions for Photon Transfer Curve."""

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from matplotlib.patches import Rectangle


def plot_ptc(
    dataset: xr.Dataset | xr.DataTree,
    text_base_fontsize: int = 8,
    alpha_rectangle: float = 0.05,
    ax: plt.Axes | None = None,
) -> None:
    """Plot Photon Transfer Curve (PTC) from a dataset containing 'mean' and 'variance' data.

    The PTC plot provides information about different noise regimes (read noise, shot noise, fixed pattern noise,
    and full well capacity) by calculating logarithmic slopes at key points and then
    plots these regimes along with the PTC on a log-log scale.
    You can find more information in :cite:p:`Janesick2007`

    **The four noise regimes**:

    1. **Read Noise Regime** (slope = 0): This regime occurs in total darkness or low illumination. It is characterized
    by random noise, which includes contributions such as thermal noise and darj current. Read noise dominates
    at very low signal levels.

    2. **Shot Noise Regime** (slope = ½): As the light levels increase, photon shot noise becomes the dominant form of noise.
    This regime appears as a linear segment in a log-log plot with a slope of 1/2.
    Shot noise is a natural consequence of the random arrival of photons, and its magnitude increases with the
    square root of the signal level.

    3. **Fixed Pattern Noise (FPN) Regime** (slope = 1): At even higher light levels, fixed-pattern noise (FPN) emerges.
    This noises stems from variations in pixel responses and sensor inhomogeneities.
    In this regime, the noise scales linearly with the signal, resulting in a slope of 1 in the PTC.
    FPN becomes more prominent as the pixel responses begin to diverge due to non-uniformities in the sensor.

    4. **Full-Well Saturation Regime** (slope = ∞): In the final regime, the subarray of pixels reaches saturation,
    referred to as the full-well regime. Here noise levels generally decrease as the pixels become saturated.
    A sharp deviation in noise from the expected 1/2 or 1 slope signals that the full-well condition has been reached.

    Parameters
    ----------
    dataset : Dataset or DataTree
        The dataset to plot. This dataset must contain a 'mean' and 'variance' variable.
        The dataset must also be 1D, containing only one dimension (e.g. 'time')

    text_base_fontsize : int, optional. Default is 8.
        Base font size used for text annotations on the plot

    alpha_rectangle : float, optional. Default is 0.05.
        Alpha transparency for the shaded rectangles that highlight different noise regimes.

    ax : Optional[plt.Axes], optional. Default is None.
        A pre-existing matplotlib axes object. If None, a new one is created.

    Returns
    -------
    matplotlib Figure
        The figure object of the PTC plot with labeled noise regimes.

    Raises
    ------
    TypeError
        If the provided 'dataset' is neither a `Dataset` nor a `DataTree`.
    ValueErorr
        If 'dataset' does not contain 'mean' and 'variance' variables or
        if 'dataset' is not 1D (i.e., contains more than one dimension)

    Examples
    --------
    >>> config = pyxel.load("configuration.yaml")
    >>> data_tree = pyxel.run_mode(
    ...     mode=config.running_mode,
    ...     detector=config.detector,
    ...     pipeline=config.pipeline,
    ... )

    >>> data_tree["/data/mean_variance/image"]
    <xarray.DataTree 'image'>
    Group: /data/mean_variance/image
        Dimensions:       (pipeline_idx: 100)
        Coordinates:
          * pipeline_idx  (pipeline_idx) int64 800B 0 1 2 3 4 5 6 ... 94 98 97 95 99 96
        Data variables:
            mean          (pipeline_idx) float64 800B 3.562 3.96 ... 5.568e+04 5.568e+04
            variance      (pipeline_idx) float64 800B 3.684 3.908 ... 8.099e+04

    >>> plot_ptc(data_tree["/data/mean_variance/image"])

    .. figure:: _static/ptc_plot.png
        :scale: 70%
        :alt: Linear Regression Slope
        :align: center
    """
    # Ensure that the data is of the correct type
    if not isinstance(dataset, xr.Dataset | xr.DataTree):
        raise TypeError(
            "Expecting a 'Dataset' or 'DataTree' object for parameter 'dataset'."
        )

    # Ensure that the dataset contains variables 'mean' and 'variance'
    if "mean" not in dataset:
        raise ValueError("Missing data variable 'mean' in 'dataset'.")
    if "variance" not in dataset:
        raise ValueError("Missing data variable 'variance' in 'dataset'.")

    # Ensure the that dataset is 1D
    if len(dataset.dims) != 1:
        raise ValueError(
            f"Expecting a 1D 'dataset', got the following dimensions: {list(dataset.dims)!r}."
        )

    dim_name, *_ = list(dataset.dims)
    data: xr.DataArray = (
        dataset.drop_vars(str(dim_name))  # Drop core dimension (e.g. 'time')
        .rename({dim_name: "mean"})  # Rename core dimension to 'mean'
        .set_coords("mean")["variance"]  # Set 'mean' as a coordinate
    )

    # Sort by 'variance'
    sorted_data: xr.DataArray = data.sortby(data)

    data_log10 = xr.Dataset()

    data_log10["variance"] = np.log10(sorted_data).assign_coords(  # type: ignore[attr-defined]
        mean=np.log10(sorted_data["mean"])
    )
    data_log10["slope"] = data_log10["variance"].differentiate(coord="mean")

    ###############################
    # Read noise regime (slope 0) #
    ###############################
    log_slope_0 = data_log10.isel(mean=0)

    # y = a * x + b
    # 10^y = (10^b) * (10^x) ^ a
    # Y = (10^b) * X ^ a
    # Compute intercept for the read noise regime (slope 0)
    intercept_0 = float(log_slope_0["variance"])
    log_intercept_0 = intercept_0

    #################################
    # Shot Noise Regime (slope 1/2) #
    #################################
    # Find slope close to 1/2
    log_slope_1_2 = data_log10.query(mean="0.45 <= slope <= 0.55").isel(mean=0)

    # Compute 'mean' and 'variance' for slope ½
    x_1_2 = float(log_slope_1_2["mean"])
    y_1_2 = float(log_slope_1_2["variance"])

    # Compute intercept for slope ½
    log_intercept_1_2 = y_1_2 - 0.5 * x_1_2

    ########################################
    # Fixed Pattern Noixe Regime (slope 1) #
    ########################################
    # Find slope close to 1
    log_slope_1 = data_log10.query(mean="0.95 <= slope <= 1.05").isel(mean=0)

    # Compute 'mean' and 'variance' for slope 1
    x_1 = float(log_slope_1["mean"])
    y_1 = float(log_slope_1["variance"])

    # Compute intercept for slope ½
    log_intercept_1 = y_1 - x_1

    ################################
    # Full Well Capacity (slope ∞) #
    ################################
    # Find slope ∞
    log_slope_inf = data_log10.sortby("variance", ascending=False).isel(mean=0)

    # Compute 'mean' for slope ∞
    x_inf = float(log_slope_inf["mean"])

    ########
    # Plot #
    ########
    # Set plot limits for the x-axis and y-axis in log scale
    log_x_min, log_x_max = -1, 6
    log_y_min, log_y_max = -1, 6

    if ax is None:
        # Get current axes
        ax = plt.gca()

    fig_width, _ = ax.get_figure().get_size_inches()  # type: ignore[union-attr]
    text_size = fig_width * text_base_fontsize / 6.4

    # Add minor and majoir grid lines
    ax.grid(True, "minor", color="0.85", linewidth=0.50, zorder=-20)
    ax.grid(True, "major", color="0.65", linewidth=0.75, zorder=-10)

    # Set log-scaled limits for x and y axes
    ax.set_xlim((10**log_x_min, 10**log_x_max))
    ax.set_ylim((10**log_y_min, 10**log_y_max))

    # Plot the 'variance' vs 'mean' on a log-log scale
    data.plot.line(xscale="log", yscale="log", ax=ax, zorder=10)
    ax.set_title("PTC with four classical noise regimes")

    ####################################
    # Plot Read Noise regime (slope 0) #
    ####################################
    log_x_slope_0 = 2 * (log_intercept_0 - log_intercept_1_2)

    # Plot the horizontal line representing slope 0
    x = np.logspace(start=log_x_min, stop=log_x_slope_0)
    ax.plot(
        x,
        10 ** np.full_like(x, fill_value=log_intercept_0),
        color="C1",
        label="slope 0",
        alpha=0.5,
        linestyle="--",
    )

    # Add vertical separating 'Read Noise Regime' and 'Shot Noise Regime'
    ax.axvline(x=10**log_x_slope_0, color="C1", alpha=0.5)

    # Add a shaded rectangle to highlight the 'Read Noise Regime'
    ax.add_patch(
        Rectangle(
            xy=(10**log_x_min, 10**log_y_min),
            width=10**log_x_slope_0 - 10**0,
            height=10**log_y_max,
            color="C1",
            alpha=alpha_rectangle,
        )
    )

    # Annotate the 'Read Noise Regime' on the plot
    ax.text(
        x=10 ** (log_x_min + (log_x_slope_0 - log_x_min) / 2),
        y=10**log_y_max,
        s="\nRead\nnoise\nregime\n(slope=0)",
        family="Monospace",
        wrap=True,
        size=text_size,
        horizontalalignment="center",
        verticalalignment="top",
    )

    ##########################################
    # Plot the 'Shot Noise Regime' (slope ½) #
    ##########################################
    log_x_slope_1_2 = 2 * (log_intercept_1_2 - log_intercept_1)

    # Plot the horizontal line representing slope ½
    x = np.logspace(start=log_x_min, stop=log_x_slope_1_2)
    ax.plot(
        x,
        (10**log_intercept_1_2) * (x**0.5),
        color="C2",
        label="slope ½",
        alpha=0.5,
        linestyle="--",
    )

    # Add vertical separating 'Shot Noise Regime' and 'Fixed Pattern Noise Regime'
    ax.axvline(x=10**log_x_slope_1_2, color="C2", alpha=0.5)

    # Add a shaded rectangle to highlight the 'Fixed Pattern Noise Regime'
    ax.add_patch(
        Rectangle(
            xy=(10**log_x_slope_0, 10**log_y_min),
            width=10**log_x_slope_1_2 - 10**log_x_slope_0,
            height=10**log_y_max,
            color="C2",
            alpha=alpha_rectangle,
        )
    )

    # Annotate the 'Shot Noise Regime' on the plot
    ax.text(
        x=(10**log_x_slope_1_2 - 10**log_x_slope_0) / 2,
        y=10**log_y_max,
        s="\nShot\nnoise\nregime\n(slope=½)",
        wrap=True,
        size=text_size,
        family="Monospace",
        horizontalalignment="center",
        verticalalignment="top",
    )

    ###################################################
    # Plot the 'Fixed Pattern Noise Regime' (slope 1) #
    ###################################################
    log_x_slope_1 = x_inf

    # Plot the horizontal line representing slope 1
    x = np.logspace(start=log_x_min, stop=x_inf)
    ax.plot(
        x,
        (10**log_intercept_1) * x,
        color="C3",
        label="slope 1",
        alpha=0.5,
        linestyle="--",
    )

    # Annotate the 'Fixed Pattern Noise Regime' on the plot
    ax.text(
        x=10 ** ((log_x_slope_1 + log_x_slope_1_2) / 2),
        y=10**log_y_max,
        s="\nFixed Pattern\nNoise\nregime\n(slope=1)",
        wrap=True,
        size=text_size,
        family="Monospace",
        horizontalalignment="center",
        verticalalignment="top",
    )

    # Add a shaded rectangle to highlight the 'Fixed Pattern Noise Regime'
    ax.add_patch(
        Rectangle(
            xy=(10**log_x_slope_1_2, 10**log_y_min),
            width=10**log_x_slope_1 - 10**log_x_slope_1_2,
            height=10**log_y_max,
            color="C3",
            alpha=alpha_rectangle,
        )
    )

    ###################################################
    # Plot the 'Full Well Regime' (slope ∞) #
    ###################################################
    # Add vertical for the 'Fixed Pattern Noise Regime'
    ax.axvline(x=10**x_inf, color="C4", alpha=0.5)

    # Add a shaded rectangle to highlight the 'Full Well Regime'
    ax.add_patch(
        Rectangle(
            (10**log_x_slope_1, 10**log_y_min),
            width=10**log_x_max - 10**log_x_slope_1,
            height=10**log_y_max,
            color="C4",
            alpha=alpha_rectangle,
        )
    )

    # Annotate the 'Full Well Regime' on the plot
    ax.text(
        10 ** ((log_x_max + log_x_slope_1) / 2),
        10**log_y_max,
        "\nFull\nWell\nregime\n(slope=∞)",
        wrap=True,
        size=text_size,
        family="Monospace",
        horizontalalignment="center",
        verticalalignment="top",
    )
