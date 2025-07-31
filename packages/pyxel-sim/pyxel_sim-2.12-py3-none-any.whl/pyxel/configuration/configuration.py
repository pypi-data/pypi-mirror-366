#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
"""Configuration loader."""

import warnings
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from shutil import copy2
from typing import IO, TYPE_CHECKING, Any, Literal, Optional, Union

from typing_extensions import overload

from pyxel import __version__ as version
from pyxel.detectors import (
    APD,
    CCD,
    CMOS,
    MKID,
    APDCharacteristics,
    APDGeometry,
    CCDGeometry,
    Characteristics,
    CMOSGeometry,
    Environment,
    MKIDGeometry,
)
from pyxel.exposure import Exposure, Readout
from pyxel.observation import Observation, ParameterValues
from pyxel.outputs import CalibrationOutputs, ExposureOutputs, ObservationOutputs
from pyxel.pipelines import DetectionPipeline, FitnessFunction, ModelFunction

if TYPE_CHECKING:
    from pyxel.calibration import Algorithm, Calibration


# ruff: noqa: C901
def _add_comments(text: str) -> str:
    """Add comments."""

    units = {
        "row": "pix",
        "col": "pix",
        "times": "s",
        "start_time": "s",
        "total_thickness": "µm",
        "pixel_vert_size": "µm",
        "pixel_horz_size": "µm",
        "pixel_scale": "arcsec / pix",
        "charge_to_volt_conversion": "V / e⁻",
        "pre_amplification": "V / V",
        "adc_voltage_range": "V",
        "adc_bit_resolution": "bit",
        "full_well_capacity": "e⁻",
        "temperature": "K",
        "wavelength": "nm",
        # For model 'cosmix'
        "particles_per_second": "s",
        # For model ???
        "fwc": "e⁻",
        # For model 'cdm'
        "trap_release_times": "s",
        "transfer_period": "s",
        "trap_densities": "cm⁻³",
    }

    new_lines = []
    for line in text.splitlines():
        clean_line: str = line.strip()

        for name, unit in units.items():
            if clean_line.startswith(f"{name}:"):
                result = f"{line}  # Unit: [{unit}]"
                break
        else:
            result = line

        if (
            clean_line.startswith("readout")
            or clean_line.startswith("outputs")
            or clean_line.startswith("geometry")
            or clean_line.startswith("environment")
            or clean_line.startswith("characteristics")
            or clean_line.startswith("photon_collection")
            or clean_line.startswith("charge_generation")
            or clean_line.startswith("charge_collection")
            or clean_line.startswith("charge_transfer")
            or clean_line.startswith("charge_measurement")
            or clean_line.startswith("readout_electronics")
            or clean_line.startswith("- func:")
        ):
            new_lines.append("")

        if clean_line.startswith("photon_collection"):
            new_lines.append(
                "# Generate and manipulate photon flux within the `Photon` bucket"
            )
            new_lines.append("# -> Photon [photon]")

        elif clean_line.startswith("charge_generation"):
            new_lines.append(
                "# Generate and manipulate charge in electrons within the `Charge` bucket"
            )
            new_lines.append("# Photon [photon] -> Charge [e⁻]")

        elif clean_line.startswith("charge_collection"):
            new_lines.append(
                "# Transfer and manipulate charge in electrons stored in the `Pixel` bucket"
            )
            new_lines.append("# Charge [e⁻] -> Pixel [e⁻]")

        elif clean_line.startswith("charge_transfer"):
            new_lines.append(
                "# Manipulate pixel charge in electrons during transfer in the `Pixel` bucket"
            )
            new_lines.append("# Pixel [e⁻] -> Pixel [e⁻]")

        elif clean_line.startswith("charge_measurement"):
            new_lines.append(
                "# Convert and manipulate signal in Volt stored in the `Signal` bucket"
            )
            new_lines.append("# Pixel [e⁻] -> Signal [V]")

        elif clean_line.startswith("readout_electronics"):
            new_lines.append(
                "# Convert and manipulate signal into image data in ADUs in the `Image` bucket"
            )
            new_lines.append("# Signal [V] -> Image [adu]")

        if clean_line.startswith("- func:"):
            if clean_line.endswith("usaf_illumination"):
                new_lines.append(
                    "    # Add photons by applying USAF-1951 illumination pattern"
                )
            elif clean_line.endswith("optical_psf"):
                new_lines.append("    # Convolve photons with a PSF")
            elif clean_line.endswith("simple_conversion"):
                new_lines.append(
                    "    # Generate charges (in e⁻) from incident photon via simple photoelectric effect"
                )
            elif clean_line.endswith("cosmix"):
                new_lines.append(
                    "    # Generate Cosmic rays effects (in e⁻) using CosmiX model"
                )
            elif clean_line.endswith("charge_collection.simple_collection"):
                new_lines.append(
                    "    # Collect charges (in e⁻) by assigning them to nearest pixels (in e⁻)"
                )
            elif clean_line.endswith("simple_full_well"):
                new_lines.append(
                    "    # Clip pixel charges (in e⁻) to Full Well Capacity"
                )
            elif clean_line.endswith("simple_measurement"):
                new_lines.append("    # Convert pixel charges (in e⁻) to Signal (in V)")
            elif clean_line.endswith("simple_amplifier"):
                new_lines.append(
                    "    # Amplify signal (in V) using gain factors from output amplifier"
                )
            elif clean_line.endswith("simple_adc"):
                new_lines.append(
                    "    # Convert signal (in V) to image (in ADU) using ideal ADC"
                )

        new_lines.append(result)

    return "\n".join(new_lines)


@dataclass
class Configuration:
    """Configuration class."""

    pipeline: DetectionPipeline

    # Running modes
    exposure: Exposure | None = None
    observation: Observation | None = None
    calibration: Optional["Calibration"] = None

    # Detectors
    ccd_detector: CCD | None = None
    cmos_detector: CMOS | None = None
    mkid_detector: MKID | None = None
    apd_detector: APD | None = None

    def __post_init__(self):
        # Sanity checks
        running_modes = [self.exposure, self.observation, self.calibration]
        num_running_modes: int = sum(el is not None for el in running_modes)

        if num_running_modes != 1:
            raise ValueError(
                "Expecting only one running mode: "
                "'exposure', 'observation' or 'calibration'."
            )

        detectors = [
            self.ccd_detector,
            self.cmos_detector,
            self.mkid_detector,
            self.apd_detector,
        ]
        num_detectors = sum(el is not None for el in detectors)

        if num_detectors != 1:
            raise ValueError(
                "Expecting only one detector: 'ccd_detector', 'cmos_detector',"
                " 'mkid_detector' or 'apd_detector'."
            )

    def __repr__(self) -> str:
        cls_name: str = self.__class__.__name__

        params: list[str] = [f"pipeline={self.pipeline!r}"]

        # Get mode
        if self.exposure is not None:
            params.append(f"exposure={self.exposure!r}")
        elif self.observation is not None:
            params.append(f"observation={self.observation!r}")
        elif self.calibration is not None:
            params.append(f"calibration={self.calibration!r}")
        else:
            # Do nothing
            pass

        # Get detector
        if self.ccd_detector is not None:
            params.append(f"ccd_detector={self.ccd_detector!r}")
        elif self.cmos_detector is not None:
            params.append(f"cmos_detector={self.cmos_detector!r}")
        elif self.mkid_detector is not None:
            params.append(f"mkid_detector={self.mkid_detector!r}")
        elif self.apd_detector is not None:
            params.append(f"apd_detector={self.apd_detector!r}")
        else:
            # Do nothing
            pass

        return f"{cls_name}({', '.join(params)})"

    @property
    def running_mode(self) -> Union[Exposure, Observation, "Calibration"]:
        """Get current running mode."""
        if self.exposure is not None:
            return self.exposure
        elif self.observation is not None:
            return self.observation
        elif self.calibration is not None:
            return self.calibration
        else:
            raise NotImplementedError

    @property
    def detector(self) -> CCD | CMOS | MKID | APD:
        """Get current detector."""
        if self.ccd_detector is not None:
            return self.ccd_detector
        elif self.cmos_detector is not None:
            return self.cmos_detector
        elif self.mkid_detector is not None:
            return self.mkid_detector
        elif self.apd_detector is not None:
            return self.apd_detector
        else:
            raise NotImplementedError

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
        import yaml

        class IndentDumper(yaml.Dumper):
            def increase_indent(self, flow: bool = False, indentless: bool = False):
                # Force indentation
                return super().increase_indent(flow=flow, indentless=False)

        content = "# yaml-language-server: $schema=https://esa.gitlab.io/pyxel/doc/latest/pyxel_schema.json\n\n"

        content += "##########################################################################################\n"
        content += "# Pyxel configuration file                                                               #\n"
        content += f"# Generated by Pyxel version {version:60s}#\n"
        content += "#                                                                                        #\n"
        content += "# Usage from Python:                                                                     #\n"
        content += "#  >>> import pyxel                                                                      #\n"
        content += "#  >>> cfg = pyxel.load('config.yaml')                                                   #\n"
        content += "#  >>> result = pyxel.run_mode(cfg)                                                      #\n"
        content += "##########################################################################################\n"

        content += "\n"
        if self.exposure:
            content += "##########################################################################################\n"
            content += "# Exposure running mode                                                                  #\n"
            content += "# More information here:                                                                 #\n"
            content += "#   https://esa.gitlab.io/pyxel/doc/stable/background/running_modes/exposure_mode.html   #\n"
            content += "##########################################################################################\n"
            content += yaml.dump(
                {"exposure": self.exposure.dump()},
                sort_keys=False,
                Dumper=IndentDumper,
            )

        if self.observation or self.calibration:
            raise NotImplementedError

        content += "\n"
        if self.ccd_detector:
            content += "# Define detector to use\n"
            content += yaml.dump(
                {"ccd_detector": self.ccd_detector.dump()},
                sort_keys=False,
                Dumper=IndentDumper,
            )

        if self.cmos_detector or self.mkid_detector or self.apd_detector:
            raise NotImplementedError

        content += "\n"
        content += "##########################################################################################\n"
        content += "# Define Pipeline                                                                        #\n"
        content += "# More information here: https://esa.gitlab.io/pyxel/doc/stable/background/pipeline.html #\n"
        content += "##########################################################################################\n"
        content += yaml.dump(
            {"pipeline": self.pipeline.dump()},
            sort_keys=False,
            Dumper=IndentDumper,
        )

        content_with_comments = _add_comments(content)

        if filename is None:
            return content_with_comments
        else:
            _ = Path(filename).write_text(content_with_comments, encoding="utf-8")
            return None


def load(yaml_file: str | Path) -> Configuration:
    """Load configuration from a ``YAML`` file."""
    filename = Path(yaml_file).resolve()
    if not filename.exists():
        raise FileNotFoundError(f"Cannot find configuration file '{filename}'.")

    dct = load_yaml(filename.read_text(encoding="utf-8"))
    return _build_configuration(dct)


def loads(yaml_string: str) -> Configuration:
    """Load configuration from a ``YAML`` string."""
    dct = load_yaml(yaml_string)
    return _build_configuration(dct)


def load_yaml(stream: str | IO) -> Any:
    """Load a ``YAML`` document."""
    # Late import to speedup start-up time
    import yaml

    result = yaml.load(stream, Loader=yaml.SafeLoader)
    return result


def build_configuration(
    detector_type: Literal["CCD", "CMOS", "MKID", "APD"],
    num_rows: int,
    num_cols: int,
) -> Configuration:
    """Build a default Pyxel ``Configuration`` object for a specified detector type.

    Parameters
    ----------
    detector_type : 'CCD', 'CMOS', 'MKID', 'APD'
        Type of detector for which the configuration should be built.
    num_rows : int
        Number of pixel row in the detector.
    num_cols : int
        Number of pixel columns in the detector.

    Returns
    -------
    Configuration
        A fully defined ``Configuration`` object with pre-filled basic models.

    Examples
    --------
    >>> import pyxel
    >>> config = pyxel.build_configuration(
    ...     detector_type="CCD",
    ...     num_rows=512,
    ...     num_cols=512,
    ... )
    >>> config.detector.geometry.row
    512
    >>> print(config.to_yaml())
    # yaml-language-server: $schema=https://esa.gitlab.io/pyxel/doc/latest/pyxel_schema.json
    ...
    >>> result = pyxel.run_mode(config)
    """
    match detector_type:
        case "CCD":
            # Define a default configuration for a CCD detector
            config = Configuration(
                exposure=Exposure(
                    readout=Readout(times=[1.0, 2.0, 3.0], non_destructive=True)
                ),
                ccd_detector=CCD(
                    geometry=CCDGeometry(
                        row=num_rows,
                        col=num_cols,
                        total_thickness=40.0,
                        pixel_vert_size=18.0,
                        pixel_horz_size=18.0,
                        pixel_scale=0.01,
                    ),
                    environment=Environment(temperature=173.0),
                    characteristics=Characteristics(
                        quantum_efficiency=0.8,
                        charge_to_volt_conversion=1e-6,
                        pre_amplification=100.0,
                        full_well_capacity=100_000,
                        adc_bit_resolution=16,
                        adc_voltage_range=(0.0, 10.0),
                    ),
                ),
                pipeline=DetectionPipeline(
                    # Generate photons with a USAF pattern
                    photon_collection=[
                        ModelFunction(
                            name="usaf_illumination",
                            func="pyxel.models.photon_collection.usaf_illumination",
                            enabled=True,
                            arguments={
                                "position": [0, 0],
                                "convert_to_photons": True,
                                "bit_resolution": 16,
                                "multiplier": 100.0,
                            },
                        ),
                        ModelFunction(
                            name="optical_psf",
                            func="pyxel.models.photon_collection.optical_psf",
                            enabled=False,
                            arguments={
                                "fov_arcsec": 5,  # FOV in arcseconds
                                "wavelength": 600,  # wavelength in nanometer
                                "apply_jitter": True,
                                "jitter_sigma": 0.5,
                                "optical_system": [
                                    {
                                        "item": "CircularAperture",
                                        "radius": 3.0,  # radius in meters
                                    }
                                ],
                            },
                        ),
                    ],
                    # Convert photons to electrons
                    charge_generation=[
                        ModelFunction(
                            name="simple_conversion",
                            func="pyxel.models.charge_generation.simple_conversion",
                            enabled=True,
                        ),
                        ModelFunction(
                            name="cosmix",
                            func="pyxel.models.charge_generation.cosmix",
                            enabled=True,
                            arguments={
                                "simulation_mode": "cosmic_ray",
                                "running_mode": "stepsize",
                                "particle_type": "proton",
                                "initial_energy": 200.0,  # MeV
                                "particles_per_second": 100,
                                "incident_angles": None,
                                "starting_position": None,
                                "spectrum_file": None,
                                "progressbar": False,
                            },
                        ),
                    ],
                    charge_collection=[
                        ModelFunction(
                            name="simple_collection",
                            func="pyxel.models.charge_collection.simple_collection",
                            enabled=True,
                        ),
                        ModelFunction(
                            name="simple_full_well",
                            func="pyxel.models.charge_collection.simple_full_well",
                            enabled=True,
                        ),
                    ],
                    # charge_transfer=[
                    #     ModelFunction(
                    #         name="cdm",
                    #         func="pyxel.models.charge_transfer.cdm",
                    #         enabled=True,
                    #         arguments={
                    #             "direction": "parallel",
                    #             "trap_release_times": [0.1, 1.0],
                    #             "trap_densities": [0.307, 0.175],
                    #             "sigma": [1.0e-15, 1.0e-15],
                    #             "beta": 0.3,
                    #             "max_electron_volume": 1.0e-10,
                    #             "transfer_period": 1.0e-4,
                    #             "charge_injection": True,  # only used for parallel mode
                    #             "full_well_capacity": 1000.0*10,  # optional (otherwise one from detector characteristics is used))
                    #         },
                    #     )
                    # ],
                    # Convert electrons to volt
                    charge_measurement=[
                        ModelFunction(
                            name="simple_measurement",
                            func="pyxel.models.charge_measurement.simple_measurement",
                            enabled=True,
                        )
                    ],
                    readout_electronics=[
                        ModelFunction(
                            name="simple_amplifier",
                            func="pyxel.models.readout_electronics.simple_amplifier",
                            enabled=True,
                        ),
                        ModelFunction(
                            name="simple_adc",
                            func="pyxel.models.readout_electronics.simple_adc",
                            enabled=True,
                        ),
                    ],
                ),
            )

        case _:
            raise NotImplementedError("Currently only 'CCD' detector is implemented.")

    return config


def launch_basic_gui():
    """Launch the Graphical User Interface for a pre-defined detector pipeline configuration.

    Examples
    --------
    >>> import pyxel
    >>> pyxel.launch_basic_gui()

    .. image:: _static/launch_basic_gui.jpeg
    """
    from pyxel.gui import BasicConfigGUI

    return BasicConfigGUI()


def to_exposure_outputs(dct: dict | None) -> ExposureOutputs:
    """Create a ExposureOutputs class from a dictionary."""
    if dct:
        new_dct = dct.copy()
    else:
        new_dct = {}

    if "output_folder" not in new_dct:
        new_dct["output_folder"] = Path().cwd().as_posix()

    return ExposureOutputs(**new_dct)


def to_readout(dct: dict | None = None) -> Readout:
    """Create a Readout class from a dictionary."""
    if dct is None:
        dct = {}
    return Readout(**dct)


def to_exposure(dct: dict | None) -> Exposure:
    """Create a Exposure class from a dictionary."""
    if dct is None:
        dct = {}

    if "outputs" in dct:
        dct.update({"outputs": to_exposure_outputs(dct["outputs"])})

    dct.update({"readout": to_readout(dct.get("readout"))})

    return Exposure(**dct)


def to_observation_outputs(dct: dict | None) -> ObservationOutputs | None:
    """Create a ObservationOutputs class from a dictionary."""
    if dct is None:
        return None

    output_folder = dct["output_folder"]
    custom_dir_name = dct.get("custom_dir_name", "")
    save_data_to_file = dct.get("save_data_to_file")

    if "save_observation_data" in dct:
        warnings.warn(
            "Deprecated. Will be removed in future version",
            DeprecationWarning,
            stacklevel=1,
        )

        save_observation_data = dct.get("save_observation_data")

        return ObservationOutputs(
            output_folder=output_folder,
            custom_dir_name=custom_dir_name,
            save_data_to_file=save_data_to_file,
            save_observation_data=save_observation_data,
        )
    else:
        return ObservationOutputs(
            output_folder=output_folder,
            custom_dir_name=custom_dir_name,
            save_data_to_file=save_data_to_file,
        )


def to_parameters(dct: Mapping[str, Any]) -> ParameterValues:
    """Create a ParameterValues class from a dictionary."""
    return ParameterValues(**dct)


def to_observation(dct: dict) -> Observation:
    """Create a Parametric class from a dictionary."""
    parameters: Sequence[Mapping[str, Any]] = dct.get("parameters", [])

    if not parameters:
        raise ValueError(
            "Missing entry 'parameters' in the YAML configuration file !\n"
            "Consider adding the following YAML snippet in the configuration file:\n"
            "  parameters:\n"
            "    - key: pipeline.photon_collection.illumination.arguments.level\n"
            "      value: [1, 2, 3, 4]\n",
        )

    dct.update({"parameters": [to_parameters(param_dict) for param_dict in parameters]})

    if "outputs" in dct:
        dct.update({"outputs": to_observation_outputs(dct["outputs"])})

    dct.update({"readout": to_readout(dct.get("readout"))})

    return Observation(**dct)


def to_calibration_outputs(dct: dict) -> CalibrationOutputs:
    """Create a CalibrationOutputs class from a dictionary."""
    return CalibrationOutputs(**dct)


def to_algorithm(dct: dict) -> "Algorithm":
    """Create an Algorithm class from a dictionary."""
    # Late import to speedup start-up time
    from pyxel.calibration import Algorithm

    return Algorithm(**dct)


def to_fitness_function(dct: dict) -> FitnessFunction:
    """Create a callable from a dictionary."""
    func: str = dct["func"]
    arguments: Mapping[str, Any] | None = dct.get("arguments")

    return FitnessFunction(func=func, arguments=arguments)


def to_calibration(dct: dict) -> "Calibration":
    """Create a Calibration class from a dictionary."""
    # Late import to speedup start-up time
    from pyxel.calibration import Calibration

    if "outputs" in dct:
        dct.update({"outputs": to_calibration_outputs(dct["outputs"])})

    dct.update({"fitness_function": to_fitness_function(dct["fitness_function"])})
    dct.update({"algorithm": to_algorithm(dct["algorithm"])})
    dct.update(
        {"parameters": [to_parameters(param_dict) for param_dict in dct["parameters"]]}
    )
    dct["result_input_arguments"] = [
        to_parameters(value) for value in dct.get("result_input_arguments", {})
    ]
    dct.update({"readout": to_readout(dct.get("readout"))})

    return Calibration(**dct)


def to_ccd_geometry(dct: dict) -> CCDGeometry:
    """Create a CCDGeometry class from a dictionary."""
    return CCDGeometry.from_dict(dct)


def to_cmos_geometry(dct: dict) -> CMOSGeometry:
    """Create a CMOSGeometry class from a dictionary."""
    return CMOSGeometry.from_dict(dct)


def to_mkid_geometry(dct: dict) -> MKIDGeometry:
    """Create a MKIDGeometry class from a dictionary."""
    return MKIDGeometry(**dct)


def to_apd_geometry(dct: dict) -> APDGeometry:
    """Create a APDGeometry class from a dictionary."""
    return APDGeometry.from_dict(dct)


def to_environment(dct: dict | None) -> Environment:
    """Create an Environment class from a dictionary."""
    if dct is None:
        dct = {}
    return Environment.from_dict(dct)


def to_ccd_characteristics(dct: dict | None) -> Characteristics:
    """Create a CCDCharacteristics class from a dictionary."""
    if dct is None:
        dct = {}
    return Characteristics(**dct)


def to_cmos_characteristics(dct: dict | None) -> Characteristics:
    """Create a CMOSCharacteristics class from a dictionary."""
    if dct is None:
        dct = {}
    return Characteristics(**dct)


def to_mkid_characteristics(dct: dict | None) -> Characteristics:
    """Create a MKIDCharacteristics class from a dictionary."""
    if dct is None:
        dct = {}
    return Characteristics(**dct)


def to_apd_characteristics(dct: dict | None) -> APDCharacteristics:
    """Create a APDCharacteristics class from a dictionary."""
    if dct is None:
        new_dct = {}
    else:
        new_dct = dct.copy()

    if "roic_gain" not in new_dct:
        raise KeyError("Missing parameter 'roic_gain' in APD Characteristics")

    roic_gain = new_dct.pop("roic_gain")
    return APDCharacteristics(roic_gain=roic_gain, **new_dct)


def to_ccd(dct: dict) -> CCD:
    """Create a CCD class from a dictionary."""
    return CCD(
        geometry=to_ccd_geometry(dct["geometry"]),
        environment=to_environment(dct.get("environment")),
        characteristics=to_ccd_characteristics(dct.get("characteristics")),
    )


def to_cmos(dct: dict) -> CMOS:
    """Create a :term:`CMOS` class from a dictionary."""
    return CMOS(
        geometry=to_cmos_geometry(dct["geometry"]),
        environment=to_environment(dct.get("environment")),
        characteristics=to_cmos_characteristics(dct.get("characteristics")),
    )


def to_mkid_array(dct: dict) -> MKID:
    """Create an MKIDarray class from a dictionary."""
    return MKID(
        geometry=to_mkid_geometry(dct["geometry"]),
        environment=to_environment(dct.get("environment")),
        characteristics=to_mkid_characteristics(dct.get("characteristics")),
    )


def to_apd(dct: dict) -> APD:
    """Create an APDarray class from a dictionary."""
    return APD(
        geometry=to_apd_geometry(dct["geometry"]),
        environment=to_environment(dct.get("environment")),
        characteristics=to_apd_characteristics(dct.get("characteristics")),
    )


def to_model_function(dct: Mapping) -> ModelFunction:
    """Create a ModelFunction class from a dictionary."""
    return ModelFunction(**dct)


def to_pipeline(
    dct: Mapping[str, Sequence[Mapping] | None] | None,
) -> DetectionPipeline:
    """Create a DetectionPipeline class from a dictionary."""
    new_dct = {}

    if dct:
        for model_group_name, model_group in dct.items():
            models_list: Sequence[Mapping] | None = model_group

            if models_list is None:
                models: Sequence[ModelFunction] | None = None
            else:
                models = [to_model_function(model_dict) for model_dict in models_list]

            new_dct[model_group_name] = models

    return DetectionPipeline(**new_dct)


def _build_configuration(dct: dict) -> Configuration:
    """Create a Configuration class from a dictionary."""
    pipeline: DetectionPipeline = to_pipeline(dct.get("pipeline"))

    # Sanity checks
    keys_running_mode: Sequence[str] = [
        "exposure",
        "observation",
        "calibration",
    ]
    num_running_modes: int = sum(key in dct for key in keys_running_mode)
    if num_running_modes != 1:
        keys = ", ".join(map(repr, keys_running_mode))
        raise ValueError(f"Expecting only one running mode: {keys}")

    keys_detectors: Sequence[str] = [
        "ccd_detector",
        "cmos_detector",
        "mkid_detector",
        "apd_detector",
    ]
    num_detector: int = sum(key in dct for key in keys_detectors)
    if num_detector != 1:
        keys = ", ".join(map(repr, keys_detectors))

        if num_detector == 0:
            raise ValueError(f"Got no detector. Expected values: {keys}")
        else:
            raise ValueError(
                f"Expecting only one detector, got {num_detector} detectors. "
                f"Expected values: {keys}"
            )

    running_mode: dict[str, Exposure | Observation | "Calibration"] = {}
    if "exposure" in dct:
        running_mode["exposure"] = to_exposure(dct["exposure"])
    elif "observation" in dct:
        running_mode["observation"] = to_observation(dct["observation"])
    elif "calibration" in dct:
        running_mode["calibration"] = to_calibration(dct["calibration"])
    else:
        raise ValueError("No mode configuration provided.")

    detector: dict[str, CCD | CMOS | MKID | APD] = {}
    if "ccd_detector" in dct:
        detector["ccd_detector"] = to_ccd(dct["ccd_detector"])
    elif "cmos_detector" in dct:
        detector["cmos_detector"] = to_cmos(dct["cmos_detector"])
    elif "mkid_detector" in dct:
        detector["mkid_detector"] = to_mkid_array(dct["mkid_detector"])
    elif "apd_detector" in dct:
        detector["apd_detector"] = to_apd(dct["apd_detector"])
    else:
        raise ValueError("No detector configuration provided.")

    configuration: Configuration = Configuration(
        pipeline=pipeline,
        **running_mode,  # type: ignore
        **detector,  # type: ignore
    )

    return configuration


def copy_config_file(input_filename: str | Path, output_dir: Path) -> Path:
    """Save a copy of the input ``YAML`` file to output directory.

    Parameters
    ----------
    input_filename: str or Path
    output_dir: Path

    Returns
    -------
    Path
    """

    input_file = Path(input_filename)
    copy2(input_file, output_dir)

    # TODO: sort filenames ?
    pattern: str = f"*{input_file.suffix}"
    copied_input_file_it: Iterator[Path] = output_dir.glob(pattern)
    copied_input_file: Path = next(copied_input_file_it)

    with copied_input_file.open("a") as file:
        file.write("\n#########")
        file.write(f"\n# Pyxel version: {version}")
        file.write("\n#########")

    return copied_input_file
