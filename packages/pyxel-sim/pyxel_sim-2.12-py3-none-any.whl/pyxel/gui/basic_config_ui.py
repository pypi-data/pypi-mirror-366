#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Sub-package to display a GUI to build a simple Configuration object."""

from collections.abc import Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import panel as pn
import param
from typing_extensions import overload

if TYPE_CHECKING:
    import xarray as xr

    from pyxel import Configuration


def get_icons_folder() -> Path:
    """Return the folder containing GUI icon resources."""
    from pyxel.gui import icons

    return Path(icons.__path__[0])


def display_header(text: str, doc: str | None = None) -> "pn.layout.Panel":
    """Create a header row for a Panel layout."""
    # Late import
    import panel as pn

    from pyxel.util import clean_text

    row = pn.Row(
        pn.widgets.StaticText(value=clean_text(text)),
        styles={"font-weight": "bold"},
        margin=(5, 10, 5, 0),
    )

    if doc:
        row.append(
            pn.widgets.TooltipIcon(
                value=clean_text(doc),
                margin=(0, 10, 0, -10),
            )
        )

    return row


class CCDGeometry(param.Parameterized):
    """Configuration parameters and a Panel-based used interface."""

    rows = param.Integer(100, bounds=(1, None))
    columns = param.Integer(100, bounds=(1, None))

    def view(self) -> "pn.layout.Panel":
        """Return a Panel layout to visualize the geometry fields."""
        # Late import
        import panel as pn

        from pyxel.util import get_schema

        schema = get_schema()["definitions"]["CCDGeometry"]

        return pn.Card(
            header=pn.Row(
                pn.pane.SVG(
                    get_icons_folder() / "adjustements_horizontal.svg",
                    width=18,
                    margin=(10, -5, 10, 0),
                    align="end",
                ),
                display_header(
                    schema["description"],
                    doc="Geometrical attributes of the detector.",
                ),
                margin=(0, 0, -10, 0),
            ),
            objects=[
                pn.Row(
                    pn.widgets.IntInput.from_param(
                        self.param.rows,
                        description=schema["properties"]["row"]["description"],
                        margin=(5, 10, 10, 10),
                        sizing_mode="stretch_width",
                    ),
                    pn.widgets.IntInput.from_param(
                        self.param.columns,
                        description=schema["properties"]["col"]["description"],
                        margin=(5, 10, 5, 10),
                        sizing_mode="stretch_width",
                    ),
                )
            ],
            collapsible=False,
            styles={"border": "2px solid black", "border_radius": "8px"},
            margin=(10, 10, 5, 10),
        )


# class CMOSGeometry(param.Parameterized):
#     header = param.String("Geometrical attributes of a CMOS detector", doc="XXX")
#     columns = param.Integer(100, bounds=(1, None), doc="Number of pixel columns")
#     rows = param.Integer(100, bounds=(1, None), doc="Number of pixel rows")

#     def view(self):
#         return pn.Column(
#             display_header(self.param.header),
#             pn.widgets.IntInput.from_param(
#                 self.param.columns,
#                 margin=(5, 10, 5, 10),
#                 sizing_mode="stretch_width",
#             ),
#             pn.widgets.IntInput.from_param(
#                 self.param.rows,
#                 margin=(5, 10, 10, 10),
#                 sizing_mode="stretch_width",
#             ),
#             styles={"border": "2px solid black", "border_radius": "8px"},
#             margin=(10, 10, 5, 10),
#         )


class Environment(param.Parameterized):
    """Configuration parameters and a Panel-based used interface."""

    temperature = param.Number(
        default=173.0,
        bounds=(0, None),
        inclusive_bounds=(False, False),
    )

    def view(self) -> "pn.layout.Panel":
        """Return a Panel layout to visualize the geometry fields."""
        # Late import
        import panel as pn

        from pyxel.util import get_schema

        schema = get_schema()["definitions"]["Environment"]

        return pn.Card(
            header=pn.Row(
                pn.pane.SVG(
                    get_icons_folder() / "thermometer.svg",
                    width=18,
                    margin=(10, -5, 10, 0),
                    align="end",
                ),
                display_header(
                    schema["description"],
                    doc="Environmental attributes of the detector",
                ),
                margin=(0, 0, -10, 0),
            ),
            objects=[
                pn.widgets.FloatInput.from_param(
                    self.param.temperature,
                    step=1.0,
                    start=1e-6,
                    placeholder="Add a temperature ...",
                    description=schema["properties"]["temperature"]["description"],
                    margin=(5, 10, 10, 10),
                    sizing_mode="stretch_width",
                )
            ],
            collapsible=False,
            styles={"border": "2px solid black", "border_radius": "8px"},
            margin=(5, 10, 10, 10),
        )


class Characteristics(param.Parameterized):
    """Configuration parameters and a Panel-based used interface."""

    full_well_capacity = param.Number(
        default=100_000,
        bounds=(0, None),
        inclusive_bounds=(False, False),
    )

    def view(self) -> "pn.layout.Panel":
        """Return a Panel layout to visualize the geometry fields."""
        # Late import
        import panel as pn

        from pyxel.util import get_schema

        schema = get_schema()["definitions"]["Characteristics"]

        return pn.Card(
            header=pn.Row(
                pn.pane.SVG(
                    get_icons_folder() / "wrench.svg",
                    width=18,
                    margin=(10, -5, 10, 0),
                    align="end",
                ),
                display_header(
                    schema["description"],
                    doc="Characteristic attributes of the detector",
                ),
                margin=(0, 0, -10, 0),
            ),
            objects=[
                pn.widgets.FloatInput.from_param(
                    self.param.full_well_capacity,
                    step=1000.0,
                    description=schema["properties"]["full_well_capacity"][
                        "description"
                    ],
                    margin=(5, 10, 10, 10),
                    sizing_mode="stretch_width",
                )
            ],
            collapsible=False,
            styles={"border": "2px solid black", "border_radius": "8px"},
            margin=(5, 10, 10, 10),
        )


class CCD(param.Parameterized):
    """Configuration parameters and a Panel-based used interface."""

    geometry = param.Parameter(CCDGeometry(), instantiate=True)
    environment = param.Parameter(Environment(), instantiate=True)
    characteristics = param.Parameter(Characteristics(), instantiate=True)

    def view(self) -> "pn.layout.Panel":
        """Return a Panel layout to visualize the geometry fields."""
        # Late import
        import panel as pn

        return pn.Card(
            header=pn.Row(
                pn.pane.SVG(
                    get_icons_folder() / "frame.svg",
                    width=18,
                    margin=(10, -5, 10, 0),
                    align="end",
                ),
                display_header("CCD Detector"),
                margin=(0, 0, -10, 0),
            ),
            objects=[
                self.geometry.view(),
                self.environment.view(),
                self.characteristics.view(),
            ],
            collapsible=False,
            styles={"border": "2px solid black", "border_radius": "8px"},
            margin=10,
        )


# class CMOS(param.Parameterized):
#     geometry = param.Parameter(CMOSGeometry(), instantiate=True)
#     environment = param.Parameter(Environment(), instantiate=True)

#     def view(self):
#         return pn.Column(
#             self.geometry.view(),
#             self.environment.view(),
#             styles={"border": "2px solid black", "border_radius": "8px"},
#             margin=10,
#         )

#
# class Readout(param.Parameterized):
#     """Configuration parameters and a Panel-based used interface."""
#
#     header = param.String("Readout mode", doc="XXX")
#     readout_time = param.Array(np.array([1.0, 2.0]), doc="Readout time")
#     non_destructive = param.Boolean(False, doc="Non-destructive readout mode")
#
#     def view(self) -> pn.layout.Panel:
#         """Return a Panel layout to visualize the geometry fields."""
#         return pn.Column(
#             display_param_header(self.param.header),
#             pn.Param(
#                 self.param.readout_time,
#                 sizing_mode="stretch_width",
#             ),
#             pn.Param(
#                 self.param.non_destructive,
#                 sizing_mode="stretch_width",
#             ),
#             styles={"border": "2px solid black", "border_radius": "8px"},
#             margin=10,
#         )


# TODO: Create a BaseClass or prototype
class ModelUSAF(param.Parameterized):
    """Configuration parameters and a Panel-based used interface."""

    enabled = param.Boolean(True)

    def view(self) -> "pn.layout.Panel":
        """Return a Panel layout to visualize the geometry fields."""
        # Late import
        import panel as pn

        return pn.Card(
            header=pn.Row(
                display_header("USAF-1951 illumination pattern"),
                margin=(0, 0, -10, 0),
            ),
            objects=[pn.Param(self.param.enabled, sizing_mode="stretch_width")],
            margin=10,
            # margin=(0, 0, -10, 0),
            styles={"border": "2px solid black", "border_radius": "8px"},
        )


# TODO: Create a BaseClass or prototype
class GroupPhotonCollection(param.Parameterized):
    """Configuration parameters and a Panel-based used interface."""

    models = param.List([ModelUSAF(name="usaf_illumination")], instantiate=True)

    def view(self) -> "pn.layout.Panel":
        """Return a Panel layout to visualize the geometry fields."""
        # Late import
        import panel as pn

        column = pn.Card(
            header=pn.Row(
                pn.pane.SVG(
                    get_icons_folder() / "layout_list.svg",
                    width=18,
                    margin=(10, -5, 10, 0),
                    align="end",
                ),
                display_header("Photon Collection group"),
                margin=(0, 0, -10, 0),
            ),
            collapsible=False,
            styles={"border": "2px solid black", "border_radius": "8px"},
            margin=(10, 10, 5, 10),
        )

        for el in self.models:
            column.append(el.view())

        return column


# TODO: Create a BaseClass or prototype
class ModelCosmix(param.Parameterized):
    """Configuration parameters and a Panel-based used interface."""

    # Add more parameters
    enabled = param.Boolean(True)

    def view(self) -> "pn.layout.Panel":
        """Return a Panel layout to visualize the geometry fields."""
        # Late import
        import panel as pn

        return pn.Card(
            header=pn.Row(
                display_header("CosmiX: Cosmic ray model"),
                margin=(0, 0, -10, 0),
            ),
            objects=[pn.Param(self.param.enabled, sizing_mode="stretch_width")],
            margin=10,
            styles={"border": "2px solid black", "border_radius": "8px"},
        )


# TODO: Create a BaseClass or prototype
class GroupChargeGeneration(param.Parameterized):
    """Configuration parameters and a Panel-based used interface."""

    models = param.List([ModelCosmix(name="cosmix")], instantiate=True)

    def view(self) -> "pn.layout.Panel":
        """Return a Panel layout to visualize the geometry fields."""
        # Late import
        import panel as pn

        column = pn.Card(
            header=pn.Row(
                pn.pane.SVG(
                    get_icons_folder() / "layout_list.svg",
                    width=18,
                    margin=(10, -5, 10, 0),
                    align="end",
                ),
                display_header("Charge Generation group"),
                margin=(0, 0, -10, 0),
            ),
            collapsible=False,
            styles={"border": "2px solid black", "border_radius": "8px"},
            margin=(10, 10, 5, 10),
        )

        for el in self.models:
            column.append(el.view())

        return column


# TODO: Create a BaseClass or prototype
class ModelSimpleFullWell(param.Parameterized):
    """Configuration parameters and a Panel-based used interface."""

    # Add more parameters
    enabled = param.Boolean(True)

    def view(self) -> "pn.layout.Panel":
        """Return a Panel layout to visualize the geometry fields."""
        # Late import
        import panel as pn

        return pn.Card(
            header=pn.Row(
                display_header("Simple Full Well Capacity"),
                margin=(0, 0, -10, 0),
            ),
            objects=[pn.Param(self.param.enabled, sizing_mode="stretch_width")],
            margin=10,
            styles={"border": "2px solid black", "border_radius": "8px"},
        )


# TODO: Create a BaseClass or prototype
class GroupChargeCollection(param.Parameterized):
    """Configuration parameters and a Panel-based used interface."""

    models = param.List(
        [ModelSimpleFullWell(name="simple_full_well")], instantiate=True
    )

    def view(self) -> "pn.layout.Panel":
        """Return a Panel layout to visualize the geometry fields."""
        # Late import
        import panel as pn

        column = pn.Card(
            header=pn.Row(
                pn.pane.SVG(
                    get_icons_folder() / "layout_list.svg",
                    width=18,
                    margin=(10, -5, 10, 0),
                    align="end",
                ),
                display_header("Charge Collection group"),
                margin=(0, 0, -10, 0),
            ),
            collapsible=False,
            styles={"border": "2px solid black", "border_radius": "8px"},
            margin=10,
        )

        for el in self.models:
            column.append(el.view())

        return column


# # TODO: Create a BaseClass or prototype
# class ModelCDM(param.Parameterized):
#     """Configuration parameters and a Panel-based used interface."""
#
#     # Add more parameters
#     enabled = param.Boolean(True)
#
#     def view(self) -> "pn.layout.Panel":
#         """Return a Panel layout to visualize the geometry fields."""
#         # Late import
#         import panel as pn
#
#         return pn.Card(
#             header=pn.Row(
#                 display_header("Charge Distortion Model"),
#                 margin=(0, 0, -10, 0),
#             ),
#             objects=[pn.Param(self.param.enabled, sizing_mode="stretch_width")],
#             margin=10,
#             styles={"border": "2px solid black", "border_radius": "8px"},
#         )
#
#
# # TODO: Create a BaseClass or prototype
# class GroupChargeTransfer(param.Parameterized):
#     """Configuration parameters and a Panel-based used interface."""
#
#     models = param.List([ModelCDM(name="charge_distortion_model")], instantiate=True)
#
#     def view(self) -> "pn.layout.Panel":
#         """Return a Panel layout to visualize the geometry fields."""
#         # Late import
#         import panel as pn
#
#         column = pn.Card(
#             header=pn.Row(
#                 pn.pane.SVG(
#                     get_icons_folder() / "layout_list.svg",
#                     width=18,
#                     margin=(10, -5, 10, 0),
#                     align="end",
#                 ),
#                 display_header("Charge Transfer Collection group"),
#                 margin=(0, 0, -10, 0),
#             ),
#             collapsible=False,
#             styles={"border": "2px solid black", "border_radius": "8px"},
#             margin=10,
#         )
#
#         for el in self.models:
#             column.append(el.view())
#
#         return column


class CCDPipeline(param.Parameterized):
    """Configuration parameters and a Panel-based used interface."""

    photon_collection = param.Parameter()
    charge_generation = param.Parameter()
    charge_collection = param.Parameter()


# TODO: Add CMOSPipeline


class BasicConfigGUI(pn.viewable.Viewer):
    """Graphical User Interface for configuring and executing a basic detector pipeline.

    Examples
    --------
    >>> gui_config = BasicConfigGUI()
    >>> gui_config.display()
    """

    detector: CCD = param.Parameter(default=None)  # TODO: Improve this
    # readout = param.Parameter(Readout(), instantiate=True)
    pipeline = param.Parameter(default=None)  # TODO: Improve this

    def __init__(self, *args, **kwargs):
        # Late import
        import hvplot.xarray  # noqa: F401
        import panel as pn

        pn.extension("codeeditor")

        super().__init__(*args, **kwargs)

        # TODO: Improve this
        self._detectors: Mapping[Literal["CCD"], CCD] = {
            "CCD": CCD(name="CCD"),
            # "CMOS": cmos_param,
        }

        # TODO: Improve this
        self._detectors_widget: Mapping[Literal["CCD"], pn.widgets.Widget] = {
            name: obj.view() for name, obj in self._detectors.items()
        }

        # TODO: Improve this
        selected_detector_name: Literal["CCD"] = "CCD"
        for obj in self._detectors_widget.values():
            obj.visible = False

        self.detector = self._detectors[selected_detector_name]

        # photon_collection = GroupPhotonCollection()  # TODO: Improve this
        self._ccd_pipeline = CCDPipeline(
            photon_collection=GroupPhotonCollection(),
            charge_generation=GroupChargeGeneration(),
            charge_collection=GroupChargeCollection(),
        )
        self.pipeline = self._ccd_pipeline
        self._pipeline_column = pn.Card(
            header=pn.Row(
                pn.pane.SVG(
                    get_icons_folder() / "layers.svg",
                    width=18,
                    margin=(10, -5, 10, 0),
                    align="end",
                ),
                display_header("Pipeline / Models"),
                margin=(0, 0, -10, 0),
            ),
            collapsible=False,
            styles={"border": "2px solid black", "border_radius": "8px"},
            margin=(5, 10, 5, 10),
        )

    @overload
    def to_yaml(self) -> str: ...
    @overload
    def to_yaml(self, filename: str | Path) -> None: ...

    def to_yaml(self, filename: str | Path | None = None) -> str | None:
        """Serialize the current configuration into YAML format.

        If ``filename`` is not provided, the YAML content is returned as a string.
        Otherwise, the YAML content is written to the specified file.

        Parameters
        ----------
        filename : str, Path. Optional
           Path to the output file.

        Returns
        -------
        str or None
           YAML-formatted configuration as a string if `filename` is not provided,
           otherwise returns `None`
        """
        config: "Configuration" = self.get_config()

        if filename is None:
            return config.to_yaml()

        return config.to_yaml(filename)

        # self.pipeline.append(photon_collection)

    # def _select_detector(self, detector_name: str) -> None:
    #     assert isinstance(detector_name, str)
    #     assert detector_name in self._detectors

    #     self._pipeline_column.clear()

    #     if detector_name == "CCD":  # TODO: Improve this
    #         self._detectors_widget["CCD"].visible = True
    #         self._detectors_widget["CMOS"].visible = False

    #         self._pipeline_column.append(self.pipeline.photon_collection.view())
    #         self._pipeline_column.append(self.pipeline.charge_transfer.view())

    #     else:
    #         self._detectors_widget["CCD"].visible = False
    #         self._detectors_widget["CMOS"].visible = True

    #         # self._pipeline_column.clear()
    #         self._pipeline_column.append(self.pipeline.photon_collection.view())
    #         # self._pipeline_column.append(self.pipeline.charge_transfer.view())

    #     self.detector = self._detectors[detector_name]

    def _run_pipeline(self, event):
        # Late import
        import pyxel
        from pyxel.gui import run_mode_gui

        config: "Configuration" = self.get_config()

        with self._button.param.update(loading=True):
            self._button.loading = True
            ds: xr.Dataset = run_mode_gui(config, tqdm_widget=self._progress_widget)
            image_tabs = pyxel.display_dataset(ds, orientation="vertical")

        num_tabs_to_be_removed = max(len(self._outputs_tabs) - 2, 0)
        if num_tabs_to_be_removed > 0:
            # Remove some tabs
            for _ in range(num_tabs_to_be_removed):
                self._outputs_tabs.pop()

        # Add new tabs
        self._outputs_tabs.append(("Image 2D", image_tabs[0]))
        self._outputs_tabs.append(("Histogram", image_tabs[1]))

        # code_editor_widget = pn.widgets.CodeEditor(
        #     value=self.get_source_code(config=config),
        #     name="Code",
        #     language="python",
        #     sizing_mode="stretch_width",
        #     readonly=True,
        # )
        #
        # yaml_widget = pn.widgets.CodeEditor(
        #     value=config.to_yaml(),
        #     name="Configuration",
        #     language="yaml",
        #     sizing_mode="stretch_width",
        #     readonly=True,
        # )
        #
        # image_tabs.append(code_editor_widget)
        # image_tabs.append(yaml_widget)

        # self._outputs_panel.append(image_tabs)

    def get_config(self) -> "Configuration":
        # Late import
        import pyxel
        from pyxel.pipelines import ModelFunction

        config: "Configuration" = pyxel.build_configuration(
            self.detector.name,
            num_rows=self.detector.geometry.rows,  # TODO: use '.row' instead
            num_cols=self.detector.geometry.columns,  # TODO: use '.column' instead
        )

        # config.detector.geometry.total_thickness = 40.0
        # config.detector.geometry.pixel_vert_size = 18.0
        # config.detector.geometry.pixel_horz_size = 18.0

        config.detector.characteristics.full_well_capacity = (
            self.detector.characteristics.full_well_capacity
        )

        if self.detector.environment.temperature is not None:
            config.detector.environment.temperature = (
                self.detector.environment.temperature
            )

        # config.running_mode.readout.times = [1.0, 2.0, 3.0]
        # config.running_mode.readout.non_destructive = True

        # Modify model 'usaf_illumination'
        # TODO: This should be done directly in 'Configuguration'. Improve this !

        assert config.pipeline.photon_collection is not None  # TODO: Fix this
        assert isinstance(
            config.pipeline.photon_collection.usaf_illumination, ModelFunction
        )

        config.pipeline.photon_collection.usaf_illumination.enabled = (
            self.pipeline.photon_collection.models[0].enabled
        )

        # Modify model 'cosmix'
        assert config.pipeline.charge_generation is not None  # TODO: Fix this
        assert isinstance(config.pipeline.charge_generation.cosmix, ModelFunction)

        config.pipeline.charge_generation.cosmix.enabled = (
            self.pipeline.charge_generation.models[0].enabled
        )

        # Modify model 'simple_full_well'
        assert config.pipeline.charge_collection is not None  # TODO: Fix this
        assert isinstance(
            config.pipeline.charge_collection.simple_full_well, ModelFunction
        )

        config.pipeline.charge_collection.simple_full_well.enabled = (
            self.pipeline.charge_collection.models[0].enabled
        )

        return config

    def get_source_code(self, config: "Configuration") -> str:
        # Late import
        import pyxel
        from pyxel.pipelines import ModelFunction

        # Python snippet code
        source_code_lst: list[str] = []
        source_code_lst.append(f"# Pyxel version: {pyxel.__version__}")
        source_code_lst.append("import pyxel")
        source_code_lst.append("")
        source_code_lst.append(
            f"# Build a basic 'Exposure' Configuration for a simulated {self.detector.name!r} with {self.detector.geometry.rows!r}x{self.detector.geometry.columns!r} pixels"
        )
        source_code_lst.append(
            f"config = pyxel.build_configuration({self.detector.name!r}, num_rows={self.detector.geometry.rows!r}, num_cols={self.detector.geometry.columns!r})"
        )
        source_code_lst.append("")

        source_code_lst.append(
            "# Add more information about the geometry of the detector"
        )
        source_code_lst.append("# These parameters are used for model 'cosmix'")
        source_code_lst.append(
            f"config.detector.geometry.total_thickness = {config.detector.geometry.total_thickness}  # Unit: [µm]"
        )
        source_code_lst.append(
            f"config.detector.geometry.pixel_vert_size = {config.detector.geometry.pixel_vert_size}  # Unit: [µm]"
        )
        source_code_lst.append(
            f"config.detector.geometry.pixel_horz_size = {config.detector.geometry.pixel_horz_size}  # Unit: [µm]"
        )
        source_code_lst.append(
            f"config.detector.characteristics.full_well_capacity = {config.detector.characteristics.full_well_capacity}  # Unit: [e⁻]"
        )

        source_code_lst.append("")

        if self.detector.environment.temperature:
            source_code_lst.append(
                "# Configure the environmental parameter(s) for the detector"
            )
            source_code_lst.append(
                f"config.detector.environment.temperature = {self.detector.environment.temperature!r}  # Unit: [K] (optional)"
            )
            source_code_lst.append("")

        source_code_lst.append("# Configure the readout mode")
        source_code_lst.append(
            f"config.running_mode.readout.times = {config.running_mode.readout.times.tolist()!r}  # Unit: [s]"
        )
        source_code_lst.append(
            f"config.running_mode.readout.non_destructive = {config.running_mode.readout.non_destructive!r}"
        )
        source_code_lst.append("")

        source_code_lst.append("# Configure the models")
        assert config.pipeline.photon_collection is not None
        assert isinstance(
            config.pipeline.photon_collection.usaf_illumination, ModelFunction
        )
        source_code_lst.append(
            f"config.pipeline.photon_collection.usaf_illumination.enabled = {config.pipeline.photon_collection.usaf_illumination.enabled!r}"
        )

        assert config.pipeline.charge_generation is not None
        source_code_lst.append(
            f"config.pipeline.charge_generation.cosmix.enabled = {config.pipeline.charge_generation.cosmix.enabled!r}"
        )

        assert config.pipeline.charge_collection is not None
        source_code_lst.append(
            f"config.pipeline.charge_collection.simple_full_well.enabled = {config.pipeline.charge_collection.simple_full_well.enabled!r}"
        )
        source_code_lst.append("")

        source_code_lst.append("# Save current Configuration to a YAML file")
        source_code_lst.append(f"config.to_yaml('demo_{self.detector.name}.yaml')")
        source_code_lst.append("")
        source_code_lst.append(
            "# Run the configured simulation and store the results in a Dataset"
        )
        source_code_lst.append("result = pyxel.run_mode_dataset(config)")
        source_code_lst.append("")
        source_code_lst.append("# Display the results")
        source_code_lst.append("pyxel.display_dataset(result)")

        source_code = "\n".join(source_code_lst)

        return source_code

    def _update_code_yaml(self, **kwargs) -> None:
        config: "Configuration" = self.get_config()

        self._code_panel.value = self.get_source_code(config)
        self._yaml_panel.value = config.to_yaml()

    def __panel__(self) -> pn.pane.Pane:
        """Display the GUI for simplified detector configuration."""
        # Select Detector
        # widget_detectors = pn.widgets.RadioButtonGroup(
        #     value="CCD",  # TODO: Improve this
        #     options=["CCD", "CMOS"],  # TODO: Improve this
        #     button_type="primary",
        #     button_style="outline",
        #     sizing_mode="stretch_width",
        # )
        # iref = pn.bind(self._select_detector, detector_name=widget_detectors)

        # Late import
        import panel as pn

        config_panel = pn.Column(
            width=400,
            margin=5,
            styles={
                "background": "WhiteSmoke",
                "border": "2px solid black",
                # "border": "1px solid #dee2e6",
                # "border": "1px solid black",
                # 'box_shadow':'0 1px 3px rgba(0 ,0, 0, 0.1)',
                "border_radius": "8px",
            },
        )
        config_panel.append(
            pn.pane.Markdown(
                "### Simplified Configuration: CCD + Exposure mode",
                align="center",
                margin=(5, 0, -5, 0),
            )
        )
        # column.append(widget_detectors)
        # column.append(iref)
        detector_widget = self._detectors_widget["CCD"]

        code_yaml_sync_callback = pn.bind(
            self._update_code_yaml,
            columns=self.detector.geometry.param.columns,
            rows=self.detector.geometry.param.rows,
            temperature=self.detector.environment.param.temperature,
            full_well_capacity=self.detector.characteristics.param.full_well_capacity,
            model_usaf_enabled=self.pipeline.photon_collection.models[0].param.enabled,
            model_cosmix_enabled=(
                self.pipeline.charge_generation.models[0].param.enabled
            ),
            model_simple_full_well_enabled=(
                self.pipeline.charge_collection.models[0].param.enabled
            ),
        )

        detector_widget.visible = True
        # self._detectors_widget["CMOS"].visible = False

        config_panel.append(detector_widget)  # TODO: Improve this
        # column.append(self._detectors_widget["CMOS"])  # TODO: Improve this

        # Readout
        # column.append(self.readout.view())

        # Model groups
        # self._pipeline_column = pn.Column(styles={"border": "2px solid black"}, margin=10)

        # TODO: Improve this
        # Only for CCDs
        self._pipeline_column.append(self.pipeline.photon_collection.view())
        self._pipeline_column.append(self.pipeline.charge_generation.view())
        self._pipeline_column.append(self.pipeline.charge_collection.view())

        config_panel.append(self._pipeline_column)

        self._button = pn.widgets.Button(
            name="Run pipeline",
            on_click=self._run_pipeline,
            button_type="primary",
            sizing_mode="stretch_width",
        )
        config_panel.append(self._button)

        # TODO: Move this to '__init__'
        self._code_panel = pn.widgets.CodeEditor(
            value="# Undef",
            name="Code",
            language="python",
            sizing_mode="stretch_both",
            readonly=True,
        )

        # TODO: Move this to '__init__'
        self._yaml_panel = pn.widgets.CodeEditor(
            value="# Undef",
            name="Code",
            language="yaml",
            sizing_mode="stretch_both",
            readonly=True,
        )

        # TODO: Move this to '__init__'
        self._progress_widget = pn.widgets.Tqdm(
            text="Pipeline not yet executed. Please click button 'run_pipeline'"
        )

        # TODO: Move this to '__init__'
        self._outputs_tabs = pn.Tabs(
            objects=[
                ("Python", self._code_panel),
                ("YAML", self._yaml_panel),
            ],
            tabs_location="above",
        )

        return pn.Row(
            config_panel,
            pn.Column(self._progress_widget, self._outputs_tabs),
            code_yaml_sync_callback,
            width=400 * 3,
            styles={"background": "WhiteSmoke"},
        )
