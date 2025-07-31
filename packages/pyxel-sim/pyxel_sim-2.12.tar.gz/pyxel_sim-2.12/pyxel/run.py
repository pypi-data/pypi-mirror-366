#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""CLI to run Pyxel."""

import logging
import platform
import sys
import time
import warnings
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union

import click
from typing_extensions import deprecated

import pyxel
from pyxel import Configuration
from pyxel import __version__ as version
from pyxel import copy_config_file, load, outputs
from pyxel.detectors import APD, CCD, CMOS, MKID, Detector
from pyxel.exposure import Exposure
from pyxel.observation import Observation
from pyxel.observation.deprecated import ObservationResult, _run_observation_deprecated
from pyxel.pipelines import DetectionPipeline, Processor
from pyxel.pipelines.processor import _get_obj_att
from pyxel.util import create_model, create_model_to_console, download_examples

if TYPE_CHECKING:
    import dask.dataframe as dd
    import pandas as pd
    import xarray as xr

    from pyxel.calibration import Calibration
    from pyxel.outputs import (
        CalibrationOutputs,
        ExposureOutputs,
        ObservationOutputs,
        Outputs,
    )


@deprecated("This function will be removed")
def exposure_mode(
    exposure: "Exposure",
    detector: Detector,
    pipeline: "DetectionPipeline",
) -> "xr.Dataset":  # pragma: no cover
    """Run an 'exposure' pipeline.

    .. deprecated:: 1.14
        `exposure_mode` will be removed in pyxel 2.0.0, it is replaced by `pyxel.run_mode`.

    For more information, see :ref:`exposure_mode`.

    Parameters
    ----------
    exposure: Exposure
    detector: Detector
    pipeline: DetectionPipeline

    Returns
    -------
    Dataset
        An multi-dimensional array database from `xarray <https://xarray.pydata.org>`_.

    Examples
    --------
    Load a configuration file

    >>> import pyxel
    >>> config = pyxel.load("configuration.yaml")
    >>> config
    Configuration(...)

    Run an exposure pipeline

    >>> dataset = pyxel.exposure_mode(
    ...     exposure=config.exposure,
    ...     detector=config.detector,
    ...     pipeline=config.pipeline,
    ... )
    >>> dataset
    <xarray.Dataset>
    Dimensions:       (readout_time: 1, y: 450, x: 450)
    Coordinates:
      * readout_time  (readout_time) int64 1
      * y             (y) int64 0 1 2 3 4 5 6 7 ... 442 443 444 445 446 447 448 449
      * x             (x) int64 0 1 2 3 4 5 6 7 ... 442 443 444 445 446 447 448 449
    Data variables:
        image         (readout_time, y, x) uint16 9475 9089 8912 ... 9226 9584 10079
        signal        (readout_time, y, x) float64 3.159 3.03 2.971 ... 3.195 3.36
        pixel         (readout_time, y, x) float64 1.053e+03 1.01e+03 ... 1.12e+03
    """
    warnings.warn("Use function 'pyxel.run_mode'", FutureWarning, stacklevel=1)

    logging.info("Mode: Exposure")

    # Create an output folder
    outputs: ExposureOutputs | None = exposure.outputs
    if outputs:
        outputs.create_output_folder()

    processor = Processor(detector=detector, pipeline=pipeline)

    result: xr.Dataset = exposure._run_exposure_deprecated(processor=processor)

    if outputs and outputs.save_exposure_data:
        outputs.save_exposure_outputs(dataset=result)

    return result


@deprecated("This function will be removed")
def _run_exposure_mode_without_datatree(
    exposure: "Exposure",
    processor: Processor,
) -> None:
    """Run an 'exposure' pipeline.

    For more information, see :ref:`exposure_mode`.

    Parameters
    ----------
    exposure : Exposure
    processor : Detector

    Returns
    -------
    None
    """

    logging.info("Mode: Exposure")

    # Create an output folder
    outputs: ExposureOutputs | None = exposure.outputs
    if outputs:
        outputs.create_output_folder()

    _ = exposure.run_exposure(
        processor=processor,
        debug=False,
        with_inherited_coords=False,
    )


@deprecated("This function will be removed")
def _run_exposure_mode(
    exposure: "Exposure",
    processor: Processor,
    debug: bool,
    with_inherited_coords: bool,
) -> "xr.DataTree":
    """Run an 'exposure' pipeline.

    For more information, see :ref:`exposure_mode`.

    Parameters
    ----------
    exposure : Exposure
    processor : Detector
    debug : bool

    Returns
    -------
    DataTree
        An multi-dimensional tree of arrays.

    Examples
    --------
    Load a configuration file

    >>> import pyxel
    >>> config = pyxel.load("configuration.yaml")
    >>> config
    Configuration(...)

    Run an exposure pipeline

    >>> data_tree = pyxel._run_exposure_mode(
    ...     exposure=config.exposure,
    ...     detector=config.detector,
    ...     pipeline=config.pipeline,
    ... )
    >>> data_tree
    DataTree('None', parent=None)
    │   Dimensions:  (time: 54, y: 100, x: 100)
    │   Coordinates:
    │     * time     (time) float64 0.02 0.06 0.12 0.2 0.3 ... 113.0 117.8 122.7 127.7
    │     * y        (y) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
    │     * x        (x) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
    │   Data variables:
    │       photon   (time, y, x) float64 102.0 108.0 79.0 ... 2.513e+04 2.523e+04
    │       charge   (time, y, x) float64 201.0 193.0 173.0 ... 2.523e+04 2.532e+04
    │       pixel    (time, y, x) float64 94.68 98.18 71.82 ... 2.388e+04 2.418e+04
    │       signal   (time, y, x) float64 0.001176 0.00129 0.0007866 ... 0.2946 0.2982
    │       image    (time, y, x) float64 20.0 22.0 13.0 ... 4.826e+03 4.887e+03
    │   Attributes:
    │       pyxel version:  1.9.1+104.g9da11bb2.dirty
    │       running mode:   Exposure
    └── DataTree('data')
        └── DataTree('mean_variance')
            └── DataTree('image')
                    Dimensions:   (mean: 54)
                    Coordinates:
                      * mean      (mean) float64 19.58 38.7 57.83 ... 4.586e+03 4.681e+03 4.776e+03
                    Data variables:
                        variance  (mean) float64 5.958 10.28 14.82 ... 1.25e+04 1.3e+04 1.348e+04
    """

    logging.info("Mode: Exposure")

    result: "xr.DataTree" = exposure.run_exposure(
        processor=processor,
        debug=debug,
        with_inherited_coords=with_inherited_coords,
    )

    return result


@deprecated("This function will be removed")
def observation_mode(
    observation: "Observation",
    detector: Detector,
    pipeline: "DetectionPipeline",
) -> ObservationResult:  # pragma: no cover
    """Run an 'observation' pipeline.

    .. deprecated:: 1.14
        `observation_mode` will be removed in pyxel 2.0.0, it is replaced by `pyxel.run_mode`.

    For more information, see :ref:`observation_mode`.

    Parameters
    ----------
    observation: Observation
    detector: Detector
    pipeline: DetectionPipeline

    Returns
    -------
    ObservationResult
        Result.

    Examples
    --------
    Load a configuration file

    >>> import pyxel
    >>> config = pyxel.load("configuration.yaml")
    >>> config
    Configuration(...)

    Run an observation pipeline

    >>> result = pyxel.observation_mode(
    ...     exposure=config.exposure,
    ...     detector=config.detector,
    ...     pipeline=config.pipeline,
    ... )
    >>> result
    ObservationResult(...)
    """
    warnings.warn("Use function 'pyxel.run_mode'", FutureWarning, stacklevel=1)

    logging.info("Mode: Observation")

    # Create an output folder
    outputs: ObservationOutputs | None = observation.outputs
    if outputs:
        outputs.create_output_folder()

    # TODO: This should be done during initializing of object `Configuration`
    # parametric_outputs.params_func(parametric)

    processor = Processor(detector=detector, pipeline=pipeline)

    result: "ObservationResult" = _run_observation_deprecated(
        observation, processor=processor
    )

    if outputs and outputs.save_observation_data:
        outputs._save_observation_datasets_deprecated(
            result=result, mode=observation.parameter_mode
        )

    return result


@deprecated("This function will be removed")
def calibration_mode(
    calibration: "Calibration",
    detector: Detector,
    pipeline: "DetectionPipeline",
    compute_and_save: bool = True,
) -> tuple["xr.Dataset", "pd.DataFrame", "pd.DataFrame", Sequence]:  # pragma: no cover
    """Run a 'calibration' pipeline.

    .. deprecated:: 1.14
        `calibration_mode` will be removed in pyxel 2.0.0, it is replaced by `pyxel.run_mode`.

    For more information, see :ref:`calibration_mode`.

    Parameters
    ----------
    calibration: Calibration
    detector: Detector
    pipeline: DetectionPipeline
    compute_and_save: bool

    Returns
    -------
    tuple of Dataset, DataFrame, DataFrame, Sequence

    Examples
    --------
    Load a configuration file

    >>> import pyxel
    >>> config = pyxel.load("configuration.yaml")
    >>> config
    Configuration(...)

    Run a calibration pipeline

    >>> ds, processors, logs, filenames = pyxel.calibration_mode(
    ...     exposure=config.exposure,
    ...     detector=config.detector,
    ...     pipeline=config.pipeline,
    ... )

    >>> ds
    <xarray.Dataset>
    Dimensions:              (island: 2, evolution: 2, param_id: 4, id_processor: 1, readout_time: 1, y: 100, x: 100)
    Coordinates:
      * island               (island) int64 1 2
      * evolution            (evolution) int64 1 2
      * id_processor         (id_processor) int64 0
      * readout_time         (readout_time) int64 1
      * y                    (y) int64 0 1 2 3 4 5 6 7 8 ... 92 93 94 95 96 97 98 99
      * x                    (x) int64 0 1 2 3 4 5 6 7 8 ... 92 93 94 95 96 97 98 99
      * param_id             (param_id) int64 0 1 2 3
    Data variables:
        champion_fitness     (island, evolution) float64 4.759e+06 ... 4.533e+06
        champion_decision    (island, evolution, param_id) float64 0.08016 ... 7....
        champion_parameters  (island, evolution, param_id) float64 0.08016 ... 7....
        simulated_image      (island, id_processor, readout_time, y, x) uint16 48...
        simulated_signal     (island, id_processor, readout_time, y, x) float64 4...
        simulated_pixel      (island, id_processor, readout_time, y, x) float64 6...
        target               (id_processor, y, x) >f8 4.834e+03 ... 4.865e+03
    Attributes:
        num_islands:      2
        population_size:  20
        num_evolutions:   2
        generations:      5
        topology:         unconnected
        result_type:      image

    >>> processors
           island  id_processor                                          processor
    0       0             0  Delayed('apply_parameters-c5da1649-766f-4ecb-a...
    1       1             0  Delayed('apply_parameters-c16f998f-f52f-4beb-b...

    >>> logs
        num_generations  ...  global_num_generations
    0                 1  ...                       1
    1                 2  ...                       2
    2                 3  ...                       3
    3                 4  ...                       4
    4                 5  ...                       5
    ..              ...  ...                     ...
    15                1  ...                       6
    16                2  ...                       7
    17                3  ...                       8
    18                4  ...                       9
    19                5  ...                      10

    >>> filenames
    []
    """
    # Late import to speedup start-up time
    import dask

    warnings.warn("Use function 'pyxel.run_mode'", FutureWarning, stacklevel=1)

    from pyxel.calibration import CalibrationResult

    logging.info("Mode: Calibration")

    # Create an output folder
    outputs: CalibrationOutputs | None = calibration.outputs
    if outputs:
        outputs.create_output_folder()

    processor = Processor(detector=detector, pipeline=pipeline)

    ds_results, df_processors, df_all_logs = calibration._run_calibration_deprecated(
        processor=processor,
        output_dir=outputs.current_output_folder if outputs else None,
    )

    # TODO: Save the processors from 'df_processors'
    # TODO: Generate plots from 'ds_results'

    # TODO: Do something with 'df_all_logs' ?

    # TODO: create 'output' object with .calibration_outputs
    # TODO: use 'fitting.get_simulated_data' ==> np.ndarray

    # geometry = processor.detector.geometry
    # calibration.post_processing(
    #     champions=champions,
    #     output=calibration_outputs,
    #     row=geometry.row,
    #     col=geometry.col,
    # )
    filenames = calibration._post_processing(
        ds=ds_results,
        df_processors=df_processors,
        output=outputs,
    )

    if compute_and_save:
        computed_ds, df_processors, df_logs, filenames = dask.compute(
            ds_results, df_processors, df_all_logs, filenames
        )

        if outputs and outputs._save_calibration_data_deprecated:
            outputs._save_calibration_outputs_deprecated(
                dataset=computed_ds, logs=df_logs
            )
            print(f"Saved calibration outputs to {outputs.current_output_folder}")

        result = CalibrationResult(
            dataset=computed_ds,
            processors=df_processors,
            logs=df_logs,
            filenames=filenames,
        )

    else:
        result = CalibrationResult(
            dataset=ds_results,
            processors=df_processors,
            logs=df_all_logs,
            filenames=filenames,
        )

    return result


@deprecated("This function will be removed")
def _run_calibration_mode_without_datatree(
    calibration: "Calibration",
    processor: Processor,
    with_buckets_separated: bool,
) -> None:
    """Run a 'Calibration' pipeline."""
    logging.info("Mode: Calibration")

    # Create an output folder
    outputs: CalibrationOutputs | None = calibration.outputs
    if outputs:
        outputs.create_output_folder()

    # TODO: Improve this
    calibration.run_calibration(
        processor=processor,
        output_dir=outputs.current_output_folder if outputs else None,
        with_inherited_coords=with_buckets_separated,
    )


def _run_calibration_mode(
    calibration: "Calibration",
    processor: Processor,
    with_inherited_coords: bool,
) -> "xr.DataTree":
    """Run a 'Calibration' pipeline.

    Notes
    -----
    This is a 'private' function called by 'run_mode'.

    Returns
    -------
    DataTree

    Examples
    --------
    >>> data_tree = _run_calibration_mode(calibration=..., detector=..., pipeline=...)
    >>> data_tree
    DataTree('None', parent=None)
    │   Dimensions:              (evolution: 5, island: 1, param_id: 4, individual: 10,
    │                             processor: 10, readout_time: 1, y: 235, x: 1)
    │   Coordinates:
    │     * evolution            (evolution) int64 0 1 2 3 4
    │     * island               (island) int64 0
    │     * param_id             (param_id) int64 0 1 2 3
    │     * individual           (individual) int64 0 1 2 3 4 5 6 7 8 9
    │     * processor            (processor) int64 0 1 2 3 4 5 6 7 8 9
    │     * readout_time         (readout_time) int64 1
    │     * y                    (y) int64 2065 2066 2067 2068 ... 2296 2297 2298 2299
    │     * x                    (x) int64 0
    │   Data variables:
    │       champion_fitness     (island, evolution) float64 3.271e+06 ... 4.641e+05
    │       champion_decision    (island, evolution, param_id) float64 -2.224 ... 3.662
    │       champion_parameters  (island, evolution, param_id) float64 0.00597 ... 4....
    │       best_fitness         (island, evolution, individual) float64 3.271e+06 .....
    │       best_decision        (island, evolution, individual, param_id) float64 -2...
    │       best_parameters      (island, evolution, individual, param_id) float64 0....
    │       simulated_photon     (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 235, 1), meta=np.ndarray>
    │       simulated_charge     (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 235, 1), meta=np.ndarray>
    │       simulated_pixel      (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 235, 1), meta=np.ndarray>
    │       simulated_signal     (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 235, 1), meta=np.ndarray>
    │       simulated_image      (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 235, 1), meta=np.ndarray>
    │       target               (processor, y, x) float64 13.75 0.4567 ... 0.2293 0.375
    │   Attributes:
    │       num_islands:      1
    │       population_size:  10
    │       num_evolutions:   5
    │       generations:      1
    │       topology:         fully_connected
    │       result_type:      pixel
    └── DataTree('full_size')
            Dimensions:           (island: 1, processor: 10, readout_time: 1, y: 2300, x: 1)
            Coordinates:
              * island            (island) int64 0
              * processor         (processor) int64 0 1 2 3 4 5 6 7 8 9
              * readout_time      (readout_time) int64 1
              * y                 (y) int64 0 1 2 3 4 5 6 ... 2294 2295 2296 2297 2298 2299
              * x                 (x) int64 0
            Data variables:
                simulated_photon  (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 2300, 1), meta=np.ndarray>
                simulated_charge  (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 2300, 1), meta=np.ndarray>
                simulated_pixel   (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 2300, 1), meta=np.ndarray>
                simulated_signal  (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 2300, 1), meta=np.ndarray>
                simulated_image   (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 2300, 1), meta=np.ndarray>
                target            (processor, y, x) float64 0.0 0.4285 ... 0.2293 0.375
    """
    logging.info("Mode: Calibration")

    # Create an output folder
    outputs: CalibrationOutputs | None = calibration.outputs
    if outputs:
        outputs.create_output_folder()

    data_tree: "xr.DataTree" = calibration.run_calibration(
        processor=processor,
        output_dir=outputs.current_output_folder if outputs else None,
        with_inherited_coords=with_inherited_coords,
    )

    return data_tree


@deprecated("This function will be removed")
def _run_observation_mode(
    observation: Observation,
    processor: Processor,
    with_inherited_coords: bool,
    debug: bool,
) -> "xr.DataTree":
    """Run the observation mode."""

    logging.info("Mode: Observation")

    if debug:
        raise NotImplementedError(
            "Parameter 'debug' is not implemented for 'Observation' mode."
        )

    if observation.with_dask and with_inherited_coords is False:
        warnings.warn(
            "Parameter 'with_inherited_coords' is forced to True !",
            stacklevel=1,
        )

        with_inherited_coords = True

    # Create an output folder (if needed)
    outputs: ObservationOutputs | None = observation.outputs
    if outputs:
        outputs.create_output_folder()

    # Run the observation mode
    # Note: When running sequentially (without dask enabled), a new node 'output' is added with the output filename(s)
    #       This node is not added with dask enabled
    result_dt: "xr.DataTree" = observation.run_pipelines(
        processor=processor,
        with_inherited_coords=with_inherited_coords,
    )

    return result_dt


@deprecated("This function will be removed")
def _run_exposure_or_calibration_mode(
    mode: Union[Exposure, "Calibration"],
    processor: Processor,
    debug: bool,
    with_inherited_coords: bool,
) -> "xr.DataTree":
    # Execute the appropriate processing function based on the mode type.
    if isinstance(mode, Exposure):
        return _run_exposure_mode(
            exposure=mode,
            processor=processor,
            debug=debug,
            with_inherited_coords=with_inherited_coords,
        )

    else:
        if debug:
            raise NotImplementedError(
                "Parameter 'debug' is not implemented for 'Calibration' mode."
            )

        # Late import.
        # Importing 'Calibration' can take up to 3 s !
        from pyxel.calibration import Calibration

        if isinstance(mode, Calibration):
            return _run_calibration_mode(
                calibration=mode,
                processor=processor,
                with_inherited_coords=with_inherited_coords,
            )
        else:
            raise TypeError("Please provide a valid simulation mode !")


def run_mode(
    config: Configuration | None = None,
    mode: Union[Exposure, Observation, "Calibration"] | None = None,
    detector: Detector | None = None,
    pipeline: DetectionPipeline | None = None,
    *,
    override_dct: Mapping[str, Any] | None = None,
    debug: bool = False,
    with_inherited_coords: bool = True,
) -> "xr.DataTree":
    """Execute a Pyxel simulation pipeline.

    You must provide at least parameter `config` or parameters `mode`, `detector` and `pipeline`.

    Parameters
    ----------
    config: Configuration, optional
        Full configuration object, typically loaded via 'pyxel.load(...)'
    mode : Exposure, Observation or Calibration, optional
        Mode to execute.
    detector : Detector, optional
        This object is the container for all the data used for the models.
    pipeline : DetectionPipeline, optional
        This is the core algorithm of Pyxel. This pipeline contains all the models to run.
    override_dct: dict, optional
        A dictionary of parameter(s) to override during processing.
    debug : bool, default: False
        Add all intermediate steps into the results as a ``DataTree``. This mode is used for debugging.
    with_inherited_coords : bool, default: False
        Return the results a DataTree with better hierarchical format. This parameter is provisional.

    Notes
    -----
    - Parameter ``debug`` and ``with_hiearchical_format`` are not (yet) stable and may change in the future.
    - Either `config` or all of (`mode`, `detector`, `pipeline`) must be provided.

    Returns
    -------
    DataTree
        An xarray `DataTree` containing simulation results.

    Raises
    ------
    TypeError
        Raised if the ``mode`` is not an instance of `Exposure`, `Observation` or `Calibration`.
    ValueError
        If one of the required parameters (`mode`, `detector`, `pipeline`) is not provided.
    NotImplementedError
        Raised if parameter ``debug`` is activated and `mode` is not an ``Exposure`` object.

    Examples
    --------
     Run an 'Exposure' pipeline

    >>> import pyxel
    >>> config = pyxel.load("exposure_configuration.yaml")
    >>> data_tree = pyxel.run_mode(
    ...     config,
    ...     override={  # optional
    ...         "exposure.outputs.output_folder": "new_folder",
    ...         "pipeline.photon_collection.load_image.arguments.image_file": "new_image.fits",
    ...     },
    ... )
    >>> data_tree
    <xarray.DataTree>
    Group: /
    │   Dimensions: ()
    │   Data variables:
    │       *empty*
    │   Attributes:
    │       pyxel version:  2.4.1+56.ga760893c.dirty
    │       running mode:   Exposure
    ├── Group: /bucket
    │   │   Dimensions:  (time: 54, y: 100, x: 100)
    │   │   Coordinates:
    │   │     * time     (time) float64 0.02 0.06 0.12 0.2 0.3 ... 113.0 117.8 122.7 127.7
    │   │     * y        (y) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
    │   │     * x        (x) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
    │   │   Data variables:
    │   │       photon   (time, y, x) float64 4MB 85.0 120.0 109.0 ... 2.533e+04 2.51e+04
    │   │       charge   (time, y, x) float64 4MB 201.0 196.0 202.0 ... 2.543e+04 2.52e+04
    │   │       pixel    (time, y, x) float64 4MB 77.38 110.0 99.09 ... 2.406e+04 2.406e+04
    │   │       signal   (time, y, x) float64 4MB 0.0009377 0.001322 0.00133 ... 0.2968 0.2968
    │   │       image    (time, y, x) float64 4MB 16.0 22.0 22.0 ... 4.863e+03 4.863e+03
    │   └── Group: /bucket/scene
    │       └── Group: /bucket/scene/list
    │           └── Group: /bucket/scene/list/0
    │                   Dimensions:     (ref: 345, wavelength: 343)
    │                   Coordinates:
    │                     * ref         (ref) int64 0 1 2 3 4 5 6 7 ... 337 338 339 340 341 342 343 344
    │                     * wavelength  (wavelength) float64 336.0 338.0 340.0 ... 1.018e+03 1.02e+03
    │                   Data variables:
    │                       x           (ref) float64 3KB 2.057e+05 2.058e+05 ... 2.031e+05 2.03e+05
    │                       y           (ref) float64 3KB 8.575e+04 8.58e+04 ... 8.795e+04 8.807e+04
    │                       weight      (ref) float64 3KB 11.49 14.13 15.22 14.56 ... 15.21 11.51 8.727
    │                       flux        (ref, wavelength) 1MB float64 0.03769 0.04137 ... 1.813 1.896
    └── Group: /data
        ├── Group: /data/mean_variance
        │   └── Group: /data/mean_variance/image
        │           Dimensions:   (mean: 54)
        │           Coordinates:
        │             * mean      (mean) float64 19.64 38.7 57.77 ... 4.586e+03 4.682e+03 4.777e+03
        │           Data variables:
        │               variance  (mean) float64 432B 5.893 10.36 15.13 ... 1.235e+04 1.297e+04 1.342e+04
        └── Group: /data/statistics
            └── Group: /data/statistics/pixel
                    Dimensions:  (time: 54)
                    Coordinates:
                      * time     (time) float64 0.02 0.06 0.12 0.2 0.3 ... 113.0 117.8 122.7 127.7
                    Data variables:
                        var      (time) float64 432B 92.4 197.8 317.2 ... 3.027e+05 3.175e+05 3.286e+05
                        mean     (time) float64 432B 94.64 189.1 283.5 ... 2.269e+04 2.316e+04 2.363e+04
                        min      (time) float64 432B 63.39 134.9 220.3 ... 2.135e+04 2.193e+04 2.24e+04
                        max      (time) float64 432B 134.8 248.1 359.7 ... 2.522e+04 2.569e+04 2.64e+04
                        count    (time) float64 432B 1e+04 1e+04 1e+04 1e+04 ... 1e+04 1e+04 1e+04 1e+04

    Run a 'Calibration' pipeline

    >>> config = pyxel.load("calibration_configuration.yaml")
    >>> data = pyxel.run_mode(
    ...     mode=config.exposure,
    ...     detector=config.detector,
    ...     pipeline=config.pipeline,
    ... )
    >>> data
    DataTree('None', parent=None)
    │   Dimensions:              (evolution: 5, island: 1, param_id: 4, individual: 10,
    │                             processor: 10, readout_time: 1, y: 235, x: 1)
    │   Coordinates:
    │     * evolution            (evolution) int64 0 1 2 3 4
    │     * island               (island) int64 0
    │     * param_id             (param_id) int64 0 1 2 3
    │     * individual           (individual) int64 0 1 2 3 4 5 6 7 8 9
    │     * processor            (processor) int64 0 1 2 3 4 5 6 7 8 9
    │     * readout_time         (readout_time) int64 1
    │     * y                    (y) int64 2065 2066 2067 2068 ... 2296 2297 2298 2299
    │     * x                    (x) int64 0
    │   Data variables:
    │       champion_fitness     (island, evolution) float64 3.271e+06 ... 4.641e+05
    │       champion_decision    (island, evolution, param_id) float64 -2.224 ... 3.662
    │       champion_parameters  (island, evolution, param_id) float64 0.00597 ... 4....
    │       best_fitness         (island, evolution, individual) float64 3.271e+06 .....
    │       best_decision        (island, evolution, individual, param_id) float64 -2...
    │       best_parameters      (island, evolution, individual, param_id) float64 0....
    │       simulated_photon     (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 235, 1), meta=np.ndarray>
    │       simulated_charge     (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 235, 1), meta=np.ndarray>
    │       simulated_pixel      (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 235, 1), meta=np.ndarray>
    │       simulated_signal     (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 235, 1), meta=np.ndarray>
    │       simulated_image      (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 235, 1), meta=np.ndarray>
    │       target               (processor, y, x) float64 13.75 0.4567 ... 0.2293 0.375
    │   Attributes:
    │       num_islands:      1
    │       population_size:  10
    │       num_evolutions:   5
    │       generations:      1
    │       topology:         fully_connected
    │       result_type:      pixel
    └── DataTree('full_size')
            Dimensions:           (island: 1, processor: 10, readout_time: 1, y: 2300, x: 1)
            Coordinates:
              * island            (island) int64 0
              * processor         (processor) int64 0 1 2 3 4 5 6 7 8 9
              * readout_time      (readout_time) int64 1
              * y                 (y) int64 0 1 2 3 4 5 6 ... 2294 2295 2296 2297 2298 2299
              * x                 (x) int64 0
            Data variables:
                simulated_photon  (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 2300, 1), meta=np.ndarray>
                simulated_charge  (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 2300, 1), meta=np.ndarray>
                simulated_pixel   (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 2300, 1), meta=np.ndarray>
                simulated_signal  (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 2300, 1), meta=np.ndarray>
                simulated_image   (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 2300, 1), meta=np.ndarray>
                target            (processor, y, x) float64 0.0 0.4285 ... 0.2293 0.375

    Run a pipeline with all intermediate steps

    >>> results = pyxel.run_mode(
    ...     mode=config.exposure,
    ...     detector=config.detector,
    ...     pipeline=config.pipeline,
    ...     debug=True,
    ... )
    >>> results["/intermediate"]
    DataTree('intermediate', parent="data")
    │   Dimensions:  ()
    │   Data variables:
    │       *empty*
    │   Attributes:
    │       long_name:  Store all intermediate results modified along a pipeline
    └── DataTree('time_idx_0')
        │   Dimensions:  ()
        │   Data variables:
        │       *empty*
        │   Attributes:
        │       long_name:       Pipeline for one unique time
        │       pipeline_count:  0
        │       time:            1.0 s
        ├── DataTree('photon_collection')
        │   │   Dimensions:  ()
        │   │   Data variables:
        │   │       *empty*
        │   │   Attributes:
        │   │       long_name:  Model group: 'photon_collection'
        │   └── DataTree('load_image')
        │           Dimensions:  (y: 100, x: 100)
        │           Coordinates:
        │             * y        (y) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
        │             * x        (x) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
        │           Data variables:
        │               photon   (y, x) float64 1.515e+04 1.592e+04 ... 1.621e+04 1.621e+04
        │           Attributes:
        │               long_name:  Group: 'load_image'
        ├── DataTree('charge_generation')
        │   │   Dimensions:  ()
        │   │   Data variables:
        │   │       *empty*
        │   │   Attributes:
        │   │       long_name:  Model group: 'charge_generation'
        │   └── DataTree('photoelectrons')
        │           Dimensions:  (y: 100, x: 100)
        │           Coordinates:
        │             * y        (y) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
        │             * x        (x) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
        │           Data variables:
        │               charge   (y, x) float64 1.515e+04 1.592e+04 ... 1.621e+04 1.621e+04
        │           Attributes:
        │               long_name:  Group: 'photoelectrons'
        ├── DataTree('charge_collection')
        │   │   Dimensions:  ()
        │   │   Data variables:
        │   │       *empty*
        │   │   Attributes:
        │   │       long_name:  Model group: 'charge_collection'
        │   └── DataTree('simple_collection')
        │           Dimensions:  (y: 100, x: 100)
        │           Coordinates:
        │             * y        (y) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
        │             * x        (x) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
        │           Data variables:
        │               pixel    (y, x) float64 1.515e+04 1.592e+04 ... 1.621e+04 1.621e+04
        │           Attributes:
        │               long_name:  Group: 'simple_collection'
        ├── DataTree('charge_measurement')
        │   │   Dimensions:  ()
        │   │   Data variables:
        │   │       *empty*
        │   │   Attributes:
        │   │       long_name:  Model group: 'charge_measurement'
        │   └── DataTree('simple_measurement')
        │           Dimensions:  (y: 100, x: 100)
        │           Coordinates:
        │             * y        (y) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
        │             * x        (x) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
        │           Data variables:
        │               signal   (y, x) float64 0.04545 0.04776 0.04634 ... 0.05004 0.04862 0.04862
        │           Attributes:
        │               long_name:  Group: 'simple_measurement'
        └── DataTree('readout_electronics')
            │   Dimensions:  ()
            │   Data variables:
            │       *empty*
            │   Attributes:
            │       long_name:  Model group: 'readout_electronics'
            └── DataTree('simple_adc')
                    Dimensions:  (y: 100, x: 100)
                    Coordinates:
                      * y        (y) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
                      * x        (x) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
                    Data variables:
                        image    (y, x) uint32 298 314 304 304 304 314 ... 325 339 339 328 319 319
                    Attributes:
                        long_name:  Group: 'simple_adc'
    """
    # Input validation
    if with_inherited_coords is False:
        warnings.warn(
            "Parameter 'with_inherited_coords' is deprecated",
            DeprecationWarning,
            stacklevel=1,
        )

    if config is None and mode is None and detector is None and pipeline is None:
        raise ValueError("Missing required argument: 'config'.")

    if config:
        if mode or detector or pipeline:
            raise ValueError(
                "Parameter 'config' is already provided. You cannot provide parameters 'mode', 'detector' or 'pipeline'."
            )

        mode = config.running_mode
        detector = config.detector
        pipeline = config.pipeline

    elif mode is None or detector is None or pipeline is None:
        raise ValueError(
            "Parameters 'mode', 'detector' and 'pipeline' must be provided."
        )

    if not isinstance(mode, Exposure) and debug:
        raise NotImplementedError(
            "Parameter 'debug' is not implemented for 'Observation' or 'Calibration' mode."
        )

    if (
        isinstance(mode, Observation)
        and mode.with_dask
        and with_inherited_coords is False
    ):
        warnings.warn(
            "Parameter 'with_inherited_coords' is forced to True !",
            stacklevel=1,
        )

        with_inherited_coords = True

    # Initialize the Processor object with the detector and pipeline.
    if isinstance(mode, Observation):
        processor = Processor(
            detector=detector,
            pipeline=pipeline,
            observation_mode=mode,  # TODO: See #836
        )
    else:
        processor = Processor(detector=detector, pipeline=pipeline)

    # Apply any overrides provided in the 'override_dct' to adjust processor settings.
    if override_dct is not None:
        apply_overrides(
            overrides=override_dct,
            processor=processor,
            mode=mode,
        )

    # Create an output folder (if needed)
    outputs: Outputs | None = mode.outputs
    if outputs:
        outputs.create_output_folder()

    match mode:
        case Exposure():
            data_tree = mode.run_exposure(
                processor=processor,
                debug=debug,
                with_inherited_coords=with_inherited_coords,
            )

        case Observation():
            data_tree = mode.run_pipelines(
                processor=processor,
                with_inherited_coords=with_inherited_coords,
            )

        case _:
            # Calibration mode
            data_tree = _run_calibration_mode(
                calibration=mode,
                processor=processor,
                with_inherited_coords=with_inherited_coords,
            )

    return data_tree


def run_mode_dataset(
    config: Configuration | None = None,
    mode: Union[Exposure, Observation, "Calibration"] | None = None,
    detector: Detector | None = None,
    pipeline: DetectionPipeline | None = None,
    *,
    override_dct: Mapping[str, Any] | None = None,
) -> "xr.Dataset":
    """Execute a Pyxel simulation pipeline and return the 'photon', 'signal',... in a simple xarray Dataset.

    Parameters
    ----------
    config: Configuration, optional
        Full configuration object, typically loaded via 'pyxel.load(...)'
    mode : Exposure, Observation or Calibration, optional
        Mode to execute.
    detector : Detector, optional
        This object is the container for all the data used for the models.
    pipeline : DetectionPipeline, optional
        This is the core algorithm of Pyxel. This pipeline contains all the models to run.
    override_dct: dict, optional
        A dictionary of parameter(s) to override during processing.

    Returns
    -------
    Dataset
        An xarray `Dataset` containing simulation results.

    Raises
    ------
    TypeError
        Raised if the ``mode`` is not an instance of `Exposure`, `Observation` or `Calibration`.
    ValueError
        If one of the required parameters (`mode`, `detector`, `pipeline`) is not provided.
    NotImplementedError
        Raised if parameter ``debug`` is activated and `mode` is not an ``Exposure`` object.

    Examples
    --------
    Run an 'Exposure' pipeline

    >>> import pyxel
    >>> config = pyxel.load("exposure_configuration.yaml")
    >>> result = pyxel.run_mode_dataset(
    ...     config,
    ...     override={  # optional
    ...         "exposure.outputs.output_folder": "new_folder",
    ...         "pipeline.photon_collection.load_image.arguments.image_file": "new_image.fits",
    ...     },
    ... )
    >>> result
    <xarray.Dataset>
    Dimensions:  (time: 54, y: 100, x: 100)
    Coordinates:
      * time     (time) float64 0.02 0.06 0.12 0.2 0.3 ... 113.0 117.8 122.7 127.7
      * y        (y) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
      * x        (x) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
    Data variables:
        photon   (time, y, x) float64 4MB 85.0 120.0 109.0 ... 2.533e+04 2.51e+04
        charge   (time, y, x) float64 4MB 201.0 196.0 202.0 ... 2.543e+04 2.52e+04
        pixel    (time, y, x) float64 4MB 77.38 110.0 99.09 ... 2.406e+04 2.406e+04
        signal   (time, y, x) float64 4MB 0.0009377 0.001322 0.00133 ... 0.2968 0.2968
        image    (time, y, x) float64 4MB 16.0 22.0 22.0 ... 4.863e+03 4.863e+03
    """
    data_tree: "xr.DataTree" = run_mode(
        config=config,
        mode=mode,
        detector=detector,
        pipeline=pipeline,
        override_dct=override_dct,
        debug=False,
        with_inherited_coords=True,
    )

    dataset: "xr.Dataset" = data_tree["/bucket"].to_dataset()
    return dataset


# TODO: Move this function ?
def get_all_filenames(
    data_tree: "xr.DataTree",
) -> Union["pd.DataFrame", "dd.DataFrame"]:
    """TBW.

    Parameters
    ----------
    data_tree

    Returns
    -------
    Pandas or Dask DataFrame

    Examples
    --------
    >>> data_tree
    <xarray.DataTree 'output'>
    Group: /output
    │   Dimensions:             (y: 100, x: 100, time: 1, level: 2,
    │                            coupling_matrix_id: 2, dim_0: 4, dim_1: 4)
    │   Coordinates:
    │       coupling_matrix     (coupling_matrix_id, dim_0, dim_1) float64 256B 1.0 ....
    │   Inherited coordinates:
    │     * y                   (y) int64 800B 0 1 2 3 4 5 6 7 ... 93 94 95 96 97 98 99
    │     * x                   (x) int64 800B 0 1 2 3 4 5 6 7 ... 93 94 95 96 97 98 99
    │     * time                (time) float64 8B 1.0
    │     * level               (level) int64 16B 1 1000000
    │     * coupling_matrix_id  (coupling_matrix_id) int64 16B 0 1
    │     * dim_0               (dim_0) int64 32B 0 1 2 3
    │     * dim_1               (dim_1) int64 32B 0 1 2 3
    └── Group: /output/image
            Dimensions:             (coupling_matrix_id: 2, level: 2, data_format: 1,
                                     dim_0: 4, dim_1: 4)
            Coordinates:
              * data_format         (data_format) <U3 12B 'npy'
                coupling_matrix     (coupling_matrix_id, dim_0, dim_1) float64 256B 1.0 ....
            Data variables:
                filename            (coupling_matrix_id, level, data_format) object 32B '...

    >>> get_all_filenames(data_tree)
       coupling_matrix_id    level data_format                    filename
    0                   0        1         npy  detector_image_array_1.npy
    1                   0  1000000         npy  detector_image_array_3.npy
    2                   1        1         npy  detector_image_array_2.npy
    3                   1  1000000         npy  detector_image_array_4.npy
    """

    # Late import
    import dask
    import dask.dataframe as dd
    import pandas as pd

    lst: list[pd.DataFrame | dd.DataFrame] = []
    for data_tree_filenames in data_tree.leaves:
        if "filename" not in data_tree_filenames:
            raise KeyError(f"Missing key 'filename' in {data_tree_filenames}")

        partial_filenames_data_array: "xr.DataArray" = data_tree_filenames[
            "filename"
        ].reset_coords(drop=True)

        if dask.is_dask_collection(partial_filenames_data_array):
            partial_dask_dataframe: dd.DataFrame = (
                partial_filenames_data_array.to_dask_dataframe()
            )
            lst.append(partial_dask_dataframe)
        else:
            partial_dataframe: pd.DataFrame = (
                partial_filenames_data_array.to_dataframe().reset_index()
            )
            lst.append(partial_dataframe)

    if isinstance(lst[0], pd.DataFrame):
        filenames_dataframe: pd.DataFrame = pd.concat(lst, ignore_index=True)

        return filenames_dataframe
    else:
        filenames_dask_dataframe: dd.DataFrame = dd.concat(lst)

        return filenames_dask_dataframe


def get_output_filenames(
    data_tree_output: "xr.DataTree",
    output_dir: Path,
) -> "pd.DataFrame":
    # Late import
    import pandas as pd

    df_filenames = pd.concat(
        [
            data_tree_leave.dataset.to_dataframe().reset_index()
            for data_tree_leave in data_tree_output.leaves
        ]
    )

    filenames: "pd.Series" = df_filenames["filename"].apply(
        lambda filename: Path(filename).relative_to(output_dir)
    )

    del df_filenames["filename"]
    df_filenames["filename"] = filenames

    return df_filenames


def run(
    input_filename: str | Path,
    override: Sequence[str] | None = None,
    random_seed: int | None = None,
) -> Optional["pd.DataFrame"]:
    """Run a YAML configuration file.

    For more information, see :ref:`running_modes`.

    Parameters
    ----------
    input_filename : str or Path
    override : list of str
    random_seed : int, optional

    Examples
    --------
    >>> import pyxel
    >>> pyxel.run("configuration.yaml")
    """
    logging.info("Pyxel version %s", version)
    logging.info("Pipeline started.")

    start_time = time.time()

    configuration: Configuration = load(Path(input_filename).expanduser().resolve())

    pipeline: DetectionPipeline = configuration.pipeline
    detector: CCD | CMOS | MKID | APD = configuration.detector
    running_mode: Exposure | Observation | "Calibration" = configuration.running_mode

    # Extract the parameters to override
    override_dct: dict[str, Any] = {}
    if override is not None:
        override_dct = {}
        for element in override:
            key, value = element.split("=")
            override_dct[key] = value

    try:
        # Late import
        import xarray as xr

        data_tree: xr.DataTree = run_mode(
            mode=running_mode,
            detector=detector,
            pipeline=pipeline,
            override_dct=override_dct,
            with_inherited_coords=True,
        )

        # if running_mode.outputs is None or running_mode.outputs.count_files_to_save() == 0:
        #     warnings.warn(
        #         "No outputs will be generated for this run. Processing continues.",
        #         UserWarning,
        #         stacklevel=1,
        #     )

        if not running_mode.outputs:
            logging.info("Pipeline completed. No output folder.")
            return None

        output_dir = running_mode.outputs.current_output_folder

        # TODO: Fix this, see issue #728
        copy_config_file(input_filename=input_filename, output_dir=output_dir)

        if "output" not in data_tree:
            logging.info("Pipeline completed. No output filenames.")
            return None

        output_dt: xr.DataTree | xr.DataArray = data_tree["/output"]
        if not isinstance(output_dt, xr.DataTree):
            raise TypeError

        df_output_filenames: "pd.DataFrame" = get_output_filenames(
            data_tree_output=output_dt, output_dir=output_dir
        )

        try:
            # Save the DataFrame to CSV
            df_output_filenames.to_csv(output_dir / "output_filenames.csv", index=False)
        except Exception:
            logging.exception(
                "Failed to save output filenames in folder %s.", output_dir
            )
            raise

        logging.info(
            "Pipeline completed. Generated: %d output file(s) in folder %s.",
            len(df_output_filenames),
            output_dir,
        )

        return df_output_filenames

    finally:
        logging.info("Running time: %.3f seconds", (time.time() - start_time))

        # Closing the logger in order to be able to move the file in the output dir
        logging.shutdown()

        if running_mode.outputs and running_mode.outputs._current_output_folder:
            output_dir = running_mode.outputs.current_output_folder
            if output_dir:
                outputs.save_log_file(output_dir)


# TODO: Use ExceptionGroup
# TODO: Add unit tests
def apply_overrides(
    overrides: Mapping[str, Any],
    processor: Processor,
    mode: Union[Exposure, Observation, "Calibration"],
) -> None:
    """Override attributes to a specified processor / running_mode.

    Parameters
    ----------
    overrides : Mapping[str, Any]
        A dictionary containing the override key(s) and value(s) to be applied.
    processor
    mode

    Notes
    -----
    'processor' and 'mode' are modified !

    Raises
    ------
    AttributeError
        If an attribute specified in the overrides does not exist in the given mode.

    Examples
    --------
    >>> overrides = {
    ...     "observation.outputs.output_folder": "my_folder",
    ...     "pipeline.photon_collection.load_image.arguments.image_file": "image.fits",
    ... }
    >>> apply_overrides(overrides=overrides, processor=processor, mode=mode)
    """
    for key, value in overrides.items():
        # Check if 'key' is specified for a running mode (exposure, observation or calibration)
        if (
            key.startswith("exposure.")
            or key.startswith("observation.")
            or key.startswith("calibration.")
        ):
            # Modify 'key' and apply it to 'running_mode'
            new_key: str = (
                key.removeprefix("exposure.")
                .removeprefix("observation.")
                .removeprefix("calibration.")
            )

            obj, att = _get_obj_att(obj=mode, key=new_key)
            if hasattr(obj, att):
                setattr(obj, att, value)
            else:
                raise AttributeError(f"Object {mode!r} has no attribute {new_key!r}")

        else:
            processor.set(key=key, value=value)


# TODO: Add an option to display colors ?
@click.group()
@click.version_option(
    version=version
    + f"\nPython ({platform.python_implementation()}) {platform.python_version()}"
)
def main():
    """Pyxel detector simulation framework.

    Pyxel is a detector simulation framework, that can simulate a variety of
    detector effects (e.g., cosmic rays, radiation-induced :term:`CTI` in :term:`CCDs<CCD>`, persistence
    in :term:`MCT`, charge diffusion, crosshatches, noises, crosstalk etc.) on a given image.
    """


@main.command(name="download-examples")
@click.argument("folder", type=click.Path(), default="pyxel-examples", required=False)
@click.option("-f", "--force", is_flag=True, help="Force flag for saving the examples.")
def download_pyxel_examples(folder, force: bool):
    """Install examples to a specified directory.

    Default folder is './pyxel-examples'.
    """
    download_examples(foldername=folder, force=force)


@main.command(name="gui")
def start_gui():
    """Launch a GUI to generate a YAML configuration file."""
    pyxel.launch_basic_gui().show(tile="Pyxel GUI")


@main.command(name="create-model")
@click.argument("model_name", type=str, required=False)
def create_new_model(model_name: str | None):
    """Create a new model.

    Use: arg1/arg2. Create a new module in ``pyxel/models/arg1/arg2`` using a template
    (``pyxel/templates/MODELTEMPLATE.py``)
    """
    if model_name is None:
        create_model_to_console()
    else:
        create_model(newmodel=model_name)


@main.command(name="run")
@click.argument("config", type=click.Path(exists=True))
@click.option(
    "--override",
    multiple=True,
    help="""
    Override entries from the YAML configuration file.
    This parameter can be repeated.\f
    Example:\f
    --override exposure.outputs.output_folder=new_folder""",
)
@click.option(
    "-v",
    "--verbosity",
    count=True,
    show_default=True,
    help="Increase output verbosity (-v/-vv/-vvv)",
)
def run_config(config: str, override: Sequence[str], verbosity: int):
    """Run Pyxel with a ``YAML`` configuration file."""
    logging_level = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG][
        min(verbosity, 3)
    ]
    log_format = (
        "%(asctime)s - %(name)s - %(threadName)30s - %(funcName)30s \t %(message)s"
    )
    logging.basicConfig(
        filename="pyxel.log",
        level=logging_level,
        format=log_format,
        datefmt="%d-%m-%Y %H:%M:%S",
    )

    # If user wants the log in stdout AND in file, use the three lines below
    stream_stdout = logging.StreamHandler(sys.stdout)
    stream_stdout.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(stream_stdout)

    df_filenames: "pd.DataFrame" | None = run(input_filename=config, override=override)

    if df_filenames is None:
        raise RuntimeError(
            "No output filename(s) generated.\n"
            "You must add an 'output_folder' in your YAML configuration file, for example:\n"
            "\n"
            "  exposure:  # or 'observation' or 'calibration'\n"
            "    outputs:\n"
            "      output_folder: 'output'\n"
        )


if __name__ == "__main__":
    main()
