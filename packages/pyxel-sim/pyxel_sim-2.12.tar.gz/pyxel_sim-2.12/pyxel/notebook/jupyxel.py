#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Tools for jupyter notebook visualization."""

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Literal, Union

import numpy as np

from pyxel.data_structure import Persistence, SimplePersistence

if TYPE_CHECKING:
    import matplotlib.pyplot as plt
    import panel as pn
    import xarray as xr
    from hvplot.xarray import XArrayInteractive
    from panel.widgets import Widget

    from pyxel import Configuration
    from pyxel.data_structure import Scene, SceneCoordinates
    from pyxel.detectors import Detector
    from pyxel.pipelines import DetectionPipeline, ModelFunction, Processor

# ----------------------------------------------------------------------------------------------
# Those two methods are used to display the contents of the configuration once loaded in pyxel


def display_config(configuration: "Configuration", only: str = "all") -> None:
    """Display configuration.

    Parameters
    ----------
    cfg: Configuration
    only: str
    """
    # Late import to speedup start-up time
    from IPython.display import Markdown, display

    cfg: dict = configuration.__dict__
    for key in cfg:
        if cfg[key] is None:
            pass
        elif (only not in cfg) & (only != "all"):
            error = "Config file only contains following keys: " + str(list(cfg))
            display(Markdown(f"<font color=red> {error} </font>"))
            break
        elif (only == key) & (only != "all"):
            display(Markdown(f"## <font color=blue> {key} </font>"))
            display(Markdown("\t" + str(cfg[key])))
            if isinstance(cfg[key].__dict__, dict):
                display_dict(cfg[key].__dict__)
        elif only == "all":
            display(Markdown(f"## <font color=blue> {key} </font>"))
            display(Markdown("\t" + str(cfg[key])))
            if isinstance(cfg[key].__dict__, dict):
                display_dict(cfg[key].__dict__)


def display_dict(cfg: dict) -> None:
    """Display configuration dictionary.

    Parameters
    ----------
    cfg: dict
    """
    # Late import to speedup start-up time
    from IPython.display import Markdown, display

    for key in cfg:
        display(Markdown(f"#### <font color=#0088FF> {key} </font>"))
        display(Markdown("\t" + str(cfg[key])))


# ----------------------------------------------------------------------------------------------
# This method will display the parameters of a specific model


def display_model(configuration: "Configuration", model_name: str) -> None:
    """Display model from configuration dictionary or Processor object.

    Parameters
    ----------
    pipeline_container: Processor or dict
    model_name: str
    """
    # Late import to speedup start-up time
    from IPython.display import Markdown, display

    pipeline: DetectionPipeline = configuration.pipeline
    model: ModelFunction = pipeline.get_model(name=model_name)
    display(Markdown(f"## <font color=blue> {model_name} </font>"))
    display(Markdown(f"Model {model_name} enabled? {model.enabled}"))
    display_dict(dict(model.arguments))


def change_modelparam(
    processor: "Processor", model_name: str, argument: str, changed_value: Any
) -> None:
    """Change model parameter.

    Parameters
    ----------
    processor: Processor
    model_name: str
    argument:str
    changed_value
    """
    # Late import to speedup start-up time
    from IPython.display import Markdown, display

    display(Markdown(f"## <font color=blue> {model_name} </font>"))
    model: ModelFunction = processor.pipeline.get_model(name=model_name)
    model.arguments[argument] = changed_value
    display(Markdown(f"Changed {argument} to {changed_value}."))


def set_modelstate(processor: "Processor", model_name: str, state: bool = True) -> None:
    """Change model state (true/false).

    Parameters
    ----------
    processor: Processor
    model_name: str
    state: bool
    """
    # Late import to speedup start-up time
    from IPython.display import Markdown, display

    display(Markdown(f"## <font color=blue> {model_name} </font>"))
    model: ModelFunction = processor.pipeline.get_model(name=model_name)
    model.enabled = state
    display(Markdown(f"Model {model_name} enabled? {model.enabled}"))


# ----------------------------------------------------------------------------------------------
# These method are used to display the detector object (all of the array Photon, pixel, signal and image)


def _new_display_detector(
    detector: "Detector", custom_histogram: bool = True
) -> "pn.Tabs":
    """Display detector interactively.

    Notes
    -----
    This function is provisional and may change.
    """
    # Extract a 'dataset' from 'detector'
    ds: "xr.Dataset" = detector.to_xarray()

    # Extract names from the arrays
    array_names: list[str] = [str(name) for name in ds]
    if not array_names:
        raise ValueError("Detector object does not contain any arrays.")

    import colorcet as cc
    import hvplot.xarray  # To integrate 'hvplot' with 'xarray'
    import numpy as np
    import panel as pn
    import param as pm
    import xarray as xr
    from holoviews.selection import link_selections

    # pn.extension(nthreads=2)
    # pn.extension()

    class Parameters(pm.Parameterized):
        array = pm.Selector(objects=array_names)
        color_norm = pm.Selector(objects=["linear", "log"], doc="foo")
        color_map = pm.Selector(
            objects={
                "fire": cc.fire,
                "gray": cc.gray,  # linear colormaps, for plotting magnitudes
                "blues": cc.blues,  # linear colormaps, for plotting magnitudes
                "colorwheel": cc.colorwheel,  # cyclic colormaps for cyclic quantities like orientation or phase
                "coolwarm": cc.coolwarm,  # diverging colormap, for plotting magnitude increasing or decreasing from a central point
                "rainbow": cc.rainbow4,  # To highlight local differences in sequential data
                "isoluminant": cc.isolum,  # To highlight low spatial-frequency information
            }
        )
        flip_yaxis = pm.Boolean(default=True)

        # Histogram
        nbins = pm.Selector(objects=[10, 20, 50, 100, "auto"])
        logx = pm.Boolean(False)
        logy = pm.Boolean(False)

        @pm.depends("color_norm", watch=True)
        def _change_logx(self):
            self.logx = bool(self.color_norm == "log")

        def view(self):
            array_name: str = self.array
            data: xr.DataArray = ds[array_name]

            ####################
            # Display 2D image #
            ####################

            img = data.hvplot.image(
                title="Array",
                aspect=1.0,
                cnorm=self.color_norm,
                cmap=self.color_map,
                flip_yaxis=self.flip_yaxis,
                hover_cols=[array_name],
                colorbar=True,
                tools=[] if custom_histogram else ["box_select"],
                # datashade=True
            )

            #####################
            # Display Histogram #
            #####################

            # Get min, max range for the histogram
            min_range, percentile_95, max_range = data.quantile(
                q=(0.02, 0.95, 0.98)
            ).to_numpy()

            if np.abs(max_range / percentile_95) > 1e6:
                # Hack to avoid this issue https://github.com/numpy/numpy/issues/10297
                self.nbins = 10

            if custom_histogram:
                frequencies, edges = np.histogram(
                    data,
                    bins=self.nbins,
                    range=(min_range, max_range),
                )

                data_hist = xr.DataArray(
                    frequencies,
                    dims=array_name,
                    coords={array_name: edges[:-1]},
                    name="Count",
                )

                long_name = data.attrs.get("long_name", array_name)
                unit = data.attrs["units"]

                hist = data_hist.hvplot.step(
                    logx=self.logx,
                    logy=self.logy,
                    xlabel=f"{long_name} [{unit}]",
                    grid=True,
                    aspect=1.0,
                )

                return img + hist
            else:
                # Get number of bins
                if self.nbins == "auto":
                    nbins = len(
                        np.histogram_bin_edges(
                            data, bins="auto", range=(min_range, max_range)
                        ),
                    )
                else:
                    nbins = self.nbins

                hist = data.hvplot.hist(
                    aspect=1.0,
                    bins=nbins,
                    bin_range=(min_range, max_range),
                    logx=self.logx,
                    logy=self.logy,
                )

                link_selection = link_selections.instance()
                return link_selection(img + hist)
                # return pn.Row(pn.widgets.StaticText(value='Yo'),link_selection(img + hist))

            # return pn.Row(img, hist)

    # with param.parameterized.batch_call_watchers(p):
    #     p.a = 2
    #     p.a = 3
    #     p.a = 1
    #     p.a = 5

    params = Parameters()
    # obj = pn.Row(
    #     params.view,
    #     pn.Param(params.param, widgets={"color_map": pn.widgets.ColorMap}),
    # )
    obj = pn.Row(
        params.view,
        pn.Param(params.param, widgets={"color_map": pn.widgets.ColorMap}),
    )

    # return pn.Column(pn.widgets.StaticText(value='Yo'), obj)
    return obj


def display_detector(
    detector: "Detector",
    *,
    new_display: bool = False,
    custom_histogram: bool = True,
) -> "pn.Tabs":
    """Display detector interactively.

    Parameters
    ----------
    detector : Detector
    new_display : bool, default: False
        Enable new display.

        .. note:: This parameter is provisional and can be changed or removed.

    custom_histogram : bool, default: True
        Use a custom method to display the histogram.
        This parameter can only be used when `new_display` is enabled.

        .. note:: This parameter is provisional and can be changed or removed.

    Notes
    -----
    When using `new_display` parameter is enabled and trying to display the detector with the y-log scale,
    the histogram will not be displayed
    (see issue [#2591](https://github.com/holoviz/holoviews/issues/2591) in [Bokeh](https://docs.bokeh.org/).

    To resolve this issue, you need to set the `custom_histogram` parameter to `True`.

    Examples
    --------
    >>> import pyxel
    >>> from pyxel.detectors import CCD

    >>> detector = CCD(...)
    >>> pyxel.display_detector(detector)

    .. image:: _static/display_detector.jpg

    >>> pyxel.display_detector(detector, new_display=True)

    .. image:: _static/new_display_detector.jpg

    """
    if not new_display:
        return _display_detector(detector=detector)
    else:
        return _new_display_detector(
            detector=detector,
            custom_histogram=custom_histogram,
        )


# ruff: noqa: F401
def _display_detector(detector: "Detector") -> "pn.Tabs":
    """Display detector interactively.

    Parameters
    ----------
    detector: Detector

    Returns
    -------
    Tabs
    """
    # Late import to speedup start-up time
    import hvplot.xarray  # To integrate 'hvplot' with 'xarray'
    import panel as pn
    import param

    # Extract a 'dataset' from 'detector'
    ds: "xr.Dataset" = detector.to_xarray()

    # Extract names from the arrays
    array_names: list[str] = [
        str(name)
        for name, data_array in ds.items()
        if "wavelength" not in data_array.dims
    ]
    if not array_names:
        raise ValueError("Detector object does not contain any arrays.")

    first_array_name = array_names[0]

    # Create widget 'Array'
    array_widget: Widget = pn.widgets.Select(name="Array", options=array_names)
    array_widget.value = first_array_name

    # Create widget 'Color'
    color_widget: Widget = pn.widgets.Select(
        name="Color", options=["gray", "viridis", "fire"]
    )

    # Create an interactive widget
    ds_interactive: XArrayInteractive = ds.interactive(loc="right")
    selected_data: XArrayInteractive = ds_interactive[array_widget]

    # Create widget 'Color bar'
    colorbar_widget: Widget = pn.widgets.ToggleGroup(
        name="Color bar",
        options=["linear", "log"],
        behavior="radio",
    )

    # Create interactive 2D imge 'Array'
    img: XArrayInteractive = selected_data.hvplot(
        title="Array",
        aspect="equal",
        cmap=color_widget,
        cnorm=colorbar_widget,
    )

    def update_tabs_widget(*events: param.parameterized.Event) -> None:
        for event in events:
            if event.name != "value":
                continue

            tab_widgets.insert(index=1, pane=("Array", img))
            _ = tab_widgets.pop(0)

    # See https://panel.holoviz.org/how_to/links/watchers.html
    colorbar_widget.param.watch(fn=update_tabs_widget, parameter_names="value")

    num_bins_widget: Widget = pn.widgets.DiscreteSlider(
        name="Num bins",
        options=[10, 20, 50, 100, 200],
        value=50,
    )

    def configure_range_slider(name: str) -> None:
        data_2d = ds[name]
        start, val_low, val_high, end = np.asarray(
            data_2d.quantile(q=[0.0, 0.5, 0.95, 1.0])
        )

        step = (end - start) / 1000.0

        hist_range_widget.start = start
        hist_range_widget.end = end
        hist_range_widget.step = step

        hist_range_widget.value = (val_low, val_high)

    hist_range_widget: Widget = pn.widgets.EditableRangeSlider(name="Range Slider")
    configure_range_slider(name=first_array_name)

    hist: XArrayInteractive = selected_data.hvplot.hist(
        aspect=1.0,
        bins=num_bins_widget,
        logx=False,
        logy=False,
        title="Histogram",
        bin_range=hist_range_widget,
    )

    def update_array_widget(*events: param.parameterized.Event) -> None:
        for event in events:
            if event.name != "value":
                continue

            configure_range_slider(name=event.new)

    # See https://panel.holoviz.org/how_to/links/watchers.html
    array_widget.param.watch(fn=update_array_widget, parameter_names="value")

    # hist_widget = pn.Row(pn.WidgetBox(array_name, num_bins, range_slider), hist)
    tab_widgets = pn.Tabs(
        ("Array", img),
        ("Histogram", hist),
        dynamic=True,
    )

    return tab_widgets


def display_array(
    data: np.ndarray,
    axes: tuple["plt.Axes", "plt.Axes"],
    **kwargs,
) -> None:
    """For a pair of axes, display the image on the first one, the histogram on the second.

    Parameters
    ----------
    data: ndarray
        A 2D np.array.
    axes: list
        A list of two axes in a figure.
    """
    # Late import to speedup start-up time
    import matplotlib.pyplot as plt
    from mpl_toolkits.axes_grid1 import make_axes_locatable

    mini = np.nanpercentile(data, 1)
    maxi = np.nanpercentile(data, 99)
    im = axes[0].imshow(data, vmin=mini, vmax=maxi)
    axes[0].get_xaxis().set_visible(False)
    axes[0].get_yaxis().set_visible(False)
    divider = make_axes_locatable(axes[0])
    cax1 = divider.append_axes("left", size="5%", pad=0.05)
    axes[0].set_title(kwargs["label"])
    plt.colorbar(im, cax=cax1)
    cax1.yaxis.set_label_position("left")
    cax1.yaxis.set_ticks_position("left")
    if mini == maxi:
        bins: int | Sequence = 50
    else:
        bins = list(np.arange(start=mini, stop=maxi, step=(maxi - mini) / 50))

    axes[1].hist(data.flatten(), bins=bins, **kwargs)
    plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=45)
    axes[1].legend(fontsize=12)
    axes[1].grid(True, alpha=0.5)


# def display_detector(
#     detector: "Detector", array: Union[None, Photon, Pixel, Signal, Image] = None
# ) -> None:
#     """Display detector.
#
#     Parameters
#     ----------
#     detector: Detector
#     array: str
#
#     Returns
#     -------
#     None
#     """
#     if array is not None:
#         fig, axes = plt.subplots(1, 2, figsize=(15, 6))
#         display_array(array.array, axes, label=str(array).split("<")[0])
#     else:
#         arrays = [detector.photon, detector.pixel, detector.signal, detector.image]
#
#         fig, axes = plt.subplots(len(arrays), 2, figsize=(15, 6 * len(arrays)))
#
#         for idx, data in enumerate(arrays):
#             display_array(data.array, axes[idx], label=str(data).split("<")[0])
#
#     plt.show()


# ----------------------------------------------------------------------------------------------
# These method are used to display the detector memory


def display_persist(persistence: Persistence | SimplePersistence) -> None:
    """Plot all trapped charges using the detector persistence.

    Parameters
    ----------
    persistence: Persistence or SimplePersistence
    """
    # Late import to speedup start-up time
    import matplotlib.pyplot as plt

    trapped_charges: np.ndarray = persistence.trapped_charge_array

    _, axes = plt.subplots(
        len(trapped_charges), 2, figsize=(10, 5 * len(trapped_charges))
    )

    if isinstance(persistence, SimplePersistence):
        labels = [
            f"Trap time constant: {persistence.trap_time_constants[i]}; trap density:"
            f" {persistence.trap_densities[i]}"
            for i in range(len(trapped_charges))
        ]

    elif isinstance(persistence, Persistence):
        labels = [
            f"Trap time constant: {persistence.trap_time_constants[i]}; "
            + f"trap proportion: {persistence.trap_proportions[i]}"
            for i in range(len(trapped_charges))
        ]
    else:
        raise TypeError(
            "Persistence or SimplePersistence expected for argument 'persistence'!"
        )

    trapmap: np.ndarray
    for ax, trapmap, keyw in zip(axes, trapped_charges, labels, strict=False):
        display_array(data=trapmap, axes=ax, label=keyw)


def display_scene(
    detector: "Detector", figsize: tuple[int, int] = (8, 6)
) -> "plt.Axes":
    """Display the scene contained in 'detector' and the size of the detector.

    Examples
    --------
    >>> import pyxel
    >>> pyxel.display_scene(detector)

    .. image:: _static/display_scene.jpg
    """
    import matplotlib.pyplot as plt
    from astropy.units import Quantity

    scene: "Scene" = detector.scene
    scene_ds: xr.Dataset = scene.to_xarray()

    if not scene:
        raise ValueError("Scene not initialized in this detector")

    # Get the pointing coordinate from the scene
    scene_coord: "SceneCoordinates" = scene.get_pointing_coordinates()
    right_ascension = scene_coord.right_ascension
    declination = scene_coord.declination
    fov = scene_coord.fov

    middle_point_x = right_ascension.to(unit="arcsec")
    middle_point_y = declination.to(unit="arcsec")

    # Extract parameters from 'detector'
    pixel_scale = Quantity(detector.geometry.pixel_scale, unit="arcsec/pixel")
    detector_row = Quantity(detector.geometry.row, unit="pixel")
    detector_col = Quantity(detector.geometry.col, unit="pixel")

    x_factor = detector_row * pixel_scale / 2
    y_factor = detector_col * pixel_scale / 2

    l_x = middle_point_x - x_factor
    r_x = middle_point_x + x_factor
    t_y = middle_point_y + y_factor
    b_y = middle_point_y - y_factor

    _, ax = plt.subplots(figsize=figsize)
    scene_ds.plot.scatter(x="x", y="y", hue="weight", marker="o", ax=ax)

    ax.set_title(
        f"Right ascension: {right_ascension:latex}, "
        f"declination: {declination:latex}, "
        f"fov: {fov:latex}"
    )
    ax.hlines(y=t_y.value, xmin=l_x.value, xmax=r_x.value)
    ax.vlines(x=l_x.value, ymin=b_y.value, ymax=t_y.value)
    ax.hlines(y=b_y.value, xmin=l_x.value, xmax=r_x.value)
    ax.vlines(x=r_x.value, ymin=b_y.value, ymax=t_y.value)

    return ax


def display_dataset(
    dataset: Union["xr.Dataset", "xr.DataTree"],
    orientation: Literal["horizontal", "vertical"] = "horizontal",
) -> "pn.layout.Panel":
    """Display an interactive visualization of a 3D dataset.

    Parameters
    ----------
    dataset : Dataset
        An Xarray Dataset with at least the dimensions 'x', 'y' and 'time'.
    orientation : 'horizontal' or 'vertical'. Default: 'horizontal'
        Orientation of the plots.

    Returns
    -------
    Panel
        A Panel layout containing the widgets and plots.

    Raises
    ------
    TypeError
        If 'dataset' is not a Xarray dataset.
    ValueError
        If required dimensions 'x', 'y' or 'time' are missing for the dataset.

    Examples
    --------
    >>> import pyxel
    >>> config = pyxel.build_configuration(
    ...     detector_type="CCD",
    ...     num_rows=512,
    ...     num_cols=512,
    ... )
    >>> ds = pyxel.run_mode_dataset(config)
    >>> ds
    <xarray.Dataset>
    >>> pyxel.display_dataset(ds)
    """
    import colorcet as cc
    import holoviews as hv
    import hvplot.xarray
    import numpy as np
    import panel as pn
    import xarray as xr

    if isinstance(dataset, xr.DataTree):
        dataset = dataset.to_dataset()

    if not isinstance(dataset, xr.Dataset):
        raise TypeError(f"Expecting a 'dataset'. Got {dataset=}")

    if "x" not in dataset.dims:
        raise ValueError(f"Missing dimension 'x'. Got dimensions: {list(dataset.dims)}")
    if "y" not in dataset.dims:
        raise ValueError(f"Missing dimension 'y'. Got dimensions: {list(dataset.dims)}")
    if "time" not in dataset.dims:
        raise ValueError(
            f"Missing dimension 'time'. Got dimensions: {list(dataset.dims)}"
        )

    if not pn.extension._loaded:
        pn.extension()

    widget_width: int = 200

    # Determine plot aspect ratio
    aspect: float = dataset.sizes["x"] / dataset.sizes["y"]

    # Widget to select the data variable (e.g. 'photon', 'signal', ...)
    bucket_widget: pn.widgets.Widget = pn.widgets.Select(
        name="Bucket",
        options=list(dataset.data_vars),
        width=widget_width,
    )

    # Widget to select the color map
    cmap_widget: pn.widgets.Widget = pn.widgets.ColorMap(
        name="Color",
        options={
            "fire": cc.fire,
            "gray": cc.gray,  # linear colormaps, for plotting magnitudes
            "blues": cc.blues,  # linear colormaps, for plotting magnitudes
            "colorwheel": cc.colorwheel,  # cyclic colormaps for cyclic quantities like orientation or phase
            "coolwarm": cc.coolwarm,
            # diverging colormap for plotting magnitude increasing or decreasing from a central point
            "rainbow": cc.rainbow4,  # To highlight local differences in sequential data
            "isoluminant": cc.isolum,  # To highlight low spatial-frequency information
        },
        width=widget_width,
    )

    # Widget to select histogram range
    range_widget: pn.widgets.Widget = pn.widgets.EditableRangeSlider(
        name="range",
        start=0,
        end=100,
        width=widget_width,
    )

    # Widget to choose number of bins in histogram
    num_bins_widget: pn.widgets.Widget = pn.widgets.Select(
        name="Num bins",
        options=[10, 20, 50, 100],
        value=50,
        width=widget_width,
    )

    def get_image_2d_with_time(bucket_name: str, time_value: float) -> xr.DataArray:
        """Extract a 2D image from a bucket at a specific time."""
        data_array: xr.DataArray = dataset[bucket_name].sel(
            time=time_value, method="nearest"
        )

        # Update range widget for histogram
        start, end = float(data_array.min()), float(data_array.max())

        range_widget.start, range_widget.end = start, end
        range_widget.name = f"Range [{data_array.attrs.get('units', 'undefined')}]"

        range_widget.value = (start, end)
        range_widget.step = min((end - start) / 1000, 0.01)

        return data_array

    def get_image_2d_without_time(bucket_name: str) -> xr.DataArray:
        """Extract a 2D image from a bucket."""
        data_array: xr.DataArray = dataset[bucket_name].squeeze()

        # Update range widget for histogram
        start, end = float(data_array.min()), float(data_array.max())

        range_widget.start, range_widget.end = start, end
        range_widget.name = f"Range [{data_array.attrs.get('units', 'undefined')}]"

        range_widget.value = (start, end)
        range_widget.step = min((end - start) / 1000, 0.01)

        return data_array

    # Bind data selection to widgets
    if len(dataset["time"]) > 1:
        # Widget to select time
        time_widget: pn.widgets.Widget = pn.widgets.DiscreteSlider(
            name="Readout time [s]",
            options=np.array(dataset["time"]).tolist(),
            width=widget_width,
        )

        data_selected: xr.DataArray = hvplot.bind(
            get_image_2d_with_time,
            bucket_name=bucket_widget,
            time_value=time_widget,
        )
    else:
        data_selected = hvplot.bind(
            get_image_2d_without_time,
            bucket_name=bucket_widget,
        )

    # Enable interactive plotting
    data_selected_interactive = data_selected.interactive(
        width=widget_width,
        loc="left",
    )

    # Create 2D image plot
    image_plot_interactive: hvplot.xarray.XArrayInteractive = (
        data_selected_interactive.hvplot.image(
            aspect=aspect,
            cmap=cmap_widget,
            cnorm="linear",
            flip_yaxis=True,
            # frame_width=300,
            # width=700
        )
    )
    image_plot_holoview = image_plot_interactive.holoviews()
    image_plot_widget = image_plot_interactive.widgets()

    if len(dataset["time"]) > 1:

        def pixel_evolution(x: float | None, y: float | None):
            """Plot the time evolution of a pixel clicked in the image plot."""
            if x is None or y is None:
                return hv.Curve([]).opts(
                    title="Click on image to view pixel time series"
                )

            data = dataset[bucket_widget.value].sel(x=x, y=y, method="nearest")
            return data.hvplot.line(aspect=1.0) * data.hvplot.scatter(aspect=1.0)

        # Stream to get cursor coordinated from 'image_plot_holoview'
        pointer_stream = hv.streams.PointerXY(x=0, y=0, source=image_plot_holoview)

        # Dynamic map for pixel time evolution plot
        pixel_plot = hv.DynamicMap(pixel_evolution, streams=[pointer_stream])

        if orientation == "horizontal":
            images_layout = pn.Row(
                image_plot_widget,
                pn.Row(image_plot_holoview, pixel_plot),
            )
        else:
            images_layout = pn.Row(
                image_plot_widget,
                pn.Column(image_plot_holoview, pixel_plot),
            )
    else:
        images_layout = pn.Row(image_plot_widget, image_plot_holoview)

    # Create histogram of pixel values
    hist_plot = data_selected_interactive.hvplot.hist(
        aspect=1.0,
        logy=False,
        bins=num_bins_widget,
        bin_range=range_widget,
    )

    # Final layout with tabs
    return pn.Tabs(
        ("2D Image", images_layout),
        ("Histogram", pn.Row(hist_plot, align=("start", "start"))),
    )
