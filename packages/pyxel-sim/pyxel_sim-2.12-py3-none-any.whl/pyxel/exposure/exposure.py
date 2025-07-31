#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""Observation class and functions."""

import logging
import warnings
from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Protocol, Union

import numpy as np
from typing_extensions import deprecated

import pyxel
from pyxel import __version__
from pyxel.data_structure import Charge, Image, Photon, Pixel, Scene, Signal
from pyxel.outputs.utils import save_to_files
from pyxel.pipelines import Processor, ResultId, get_result_id, result_keys
from pyxel.util import set_random_seed

if TYPE_CHECKING:
    import xarray as xr

    from pyxel.detectors import Detector
    from pyxel.exposure import Readout
    from pyxel.outputs import CalibrationOutputs, ExposureOutputs, ObservationOutputs


class TqdmProgressBar(Protocol):
    """Protocol for a tqdm-like progress bar interface."""

    def set_description_str(
        self, desc: str | None = None, refresh: bool = True
    ) -> None: ...
    def set_postfix(
        self, ordered_dict: dict | None = None, refresh: bool = True, **kwargs
    ) -> None: ...
    def reset(self, total: int | None = None) -> None: ...
    def update(self, n: int = 1) -> None: ...
    def close(self) -> None: ...


class Exposure:
    """TBW."""

    def __init__(
        self,
        readout: "Readout",
        outputs: Optional["ExposureOutputs"] = None,
        result_type: str = "all",
        pipeline_seed: int | None = None,
        working_directory: str | None = None,
    ):
        self.outputs: "ExposureOutputs" | None = outputs
        self.readout = readout
        self.working_directory: Path | None = (
            Path(working_directory) if working_directory else None
        )
        self._result_type: ResultId = get_result_id(result_type)
        self._pipeline_seed = pipeline_seed

        # Set 'working_directory'
        pyxel.set_options(working_directory=self.working_directory)

    def __repr__(self) -> str:
        cls_name: str = self.__class__.__name__
        if self.outputs is None:
            return f"{cls_name}<no outputs>"
        else:
            return f"{cls_name}<outputs={self.outputs!r}>"

    @property
    def result_type(self) -> ResultId:
        """TBW."""
        return self._result_type

    @result_type.setter
    def result_type(self, value: ResultId) -> None:
        """TBW."""
        self._result_type = value

    @property
    def pipeline_seed(self) -> int | None:
        """TBW."""
        return self._pipeline_seed

    @pipeline_seed.setter
    def pipeline_seed(self, value: int | None) -> None:
        """TBW."""
        self._pipeline_seed = value

    # TODO: This function will be deprecated
    @deprecated("This method will be removed")
    def _run_exposure_deprecated(self, processor: Processor) -> "xr.Dataset":
        """Run an observation pipeline.

        Parameters
        ----------
        processor : Processor

        Returns
        -------
        Dataset
        """
        progressbar = self.readout._num_steps != 1
        y = range(processor.detector.geometry.row)
        x = range(processor.detector.geometry.col)
        times = self.readout.times

        # Unpure changing of processor
        _ = _run_exposure_pipeline_deprecated(
            processor=processor,
            readout=self.readout,
            outputs=self.outputs,
            progressbar=progressbar,
            result_type=self.result_type,
            pipeline_seed=self.pipeline_seed,
        )

        ds: "xr.Dataset" = processor.result_to_dataset(
            x=x,
            y=y,
            times=times,
            result_type=self.result_type,
        )

        ds.attrs.update({"running mode": "Exposure"})

        return ds

    def run_exposure(
        self,
        processor: Processor,
        debug: bool,
        with_inherited_coords: bool,
    ) -> "xr.DataTree":
        """Run an exposure pipeline.

        Parameters
        ----------
        processor : Processor
        debug : bool
        with_inherited_coords : bool

        Returns
        -------
        DataTree
        """
        progress_bar = None
        if self.readout._num_steps != 1:
            from tqdm.auto import tqdm

            progress_bar = tqdm()

        # Unpure changing of processor
        data_tree: "xr.DataTree" = run_pipeline(
            processor=processor,
            readout=self.readout,
            outputs=self.outputs,
            pipeline_seed=self.pipeline_seed,
            debug=debug,
            with_inherited_coords=with_inherited_coords,
            progress_bar=progress_bar,
        )

        data_tree.attrs["running mode"] = "Exposure"

        return data_tree

    def dump(self) -> Mapping[str, Any]:
        return {
            "readout": self.readout.dump(),
            "outputs": self.outputs.dump() if self.outputs else None,
            "result_type": self._result_type,
            "pipeline_seed": self._pipeline_seed,
            "working_directory": (
                self.working_directory.as_posix() if self.working_directory else None
            ),
        }


# TODO: This function will be deprecated
@deprecated("This function will be removed")
def _run_exposure_pipeline_deprecated(
    processor: Processor,
    readout: "Readout",
    outputs: Union[
        "CalibrationOutputs", "ObservationOutputs", "ExposureOutputs", None
    ] = None,
    progressbar: bool = False,
    result_type: ResultId = ResultId("all"),  # noqa: B008
    pipeline_seed: int | None = None,
) -> Processor:
    """Run standalone exposure pipeline.

    Parameters
    ----------
    pipeline_seed: int
        Random seed for the pipeline.
    result_type: ResultId
    processor: Processor
    readout: Readout
    outputs: DynamicOutputs
        Sampling outputs.
    progressbar: bool
        Sets visibility of progress bar.

    Returns
    -------
    processor: Processor
    """
    # Late import to speedup start-up time
    from tqdm.auto import tqdm

    # if isinstance(detector, CCD):
    #    dynamic.non_destructive_readout = False
    with set_random_seed(seed=pipeline_seed):
        num_steps = readout._num_steps
        readout._times[-1]
        readout.time_step_it()

        detector = processor.detector

        detector.set_readout(
            times=readout.times,
            start_time=readout.start_time,
            non_destructive=readout.non_destructive,
        )

        # The detector should be reset before exposure
        detector.empty()

        if progressbar:
            pbar = tqdm(total=num_steps, desc="Readout time: ")

        keys = result_keys(result_type)

        unstacked_result: dict[str, list] = defaultdict(list)
        i: int
        time: float
        step: float
        for i, (time, step) in enumerate(
            zip(
                detector.readout_properties.times,
                detector.readout_properties.steps,
                strict=False,
            )
        ):
            detector.time = time
            detector.time_step = step
            detector.pipeline_count = i

            logging.info("time = %.3f s", time)

            if detector.non_destructive_readout:
                empty_all = False
            else:
                empty_all = True

            detector.empty(empty_all)

            processor.run_pipeline(
                debug=False,  # Not supported here
            )

            if outputs and detector.read_out:
                outputs.save_to_file(processor)

            for key in keys:
                if key in ("data", "scene"):
                    continue

                obj: Scene | Photon | Pixel | Image | Signal | Charge = getattr(
                    detector, key
                )

                # TODO: Is this necessary ?
                if not isinstance(obj, Photon | Pixel | Image | Signal | Charge):
                    raise TypeError(
                        f"Wrong type from attribute 'detector.{key}'. Type: {type(obj)!r}"
                    )

                if isinstance(obj, Photon):
                    if obj._array is not None:
                        data_arr: np.ndarray = np.array(obj)
                        unstacked_result[key].append(data_arr)
                elif obj._array is not None:
                    data_arr = np.array(obj)
                    unstacked_result[key].append(data_arr)
            if progressbar:
                pbar.update(1)

        # TODO: Refactor '.result'. See #524
        processor.result = {
            key: np.stack(value)
            for key, value in unstacked_result.items()
            if key != "data"
        }

        if progressbar:
            pbar.close()

    return processor


def _extract_datatree_2d(detector: "Detector") -> "xr.DataTree":
    """Extract 2D data from a detector object into a `DataTree`.

    The buckets 'data' and 'scene' are skipped.

    Parameters
    ----------
    detector : Detector

    Returns
    -------
    DataTree

    Notes
    -----
    This function is used internally.

    Examples
    --------
    >>> _extract_datatree_2d(detector=detector)
    DataTree('None', parent=None)
        Dimensions:  (time: 1, y: 100, x: 100, wavelength: 201)
        Coordinates:
          * time     (time) float64 1.0
          * y        (y) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
          * x        (x) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
          * wavelength  (wavelength) float64 500.0 502.0 504.0 ... 896.0 898.0 900.0
        Data variables:
            photon   (time, y, x) float64 1.515e+04 1.592e+04 ... 1.621e+04 1.621e+04
            charge   (time, y, x) float64 1.515e+04 1.592e+04 ... 1.621e+04 1.621e+04
            pixel    (time, y, x) float64 1.515e+04 1.592e+04 ... 1.621e+04 1.621e+04
            signal   (time, y, x) float64 0.04545 0.04776 0.04634 ... 0.04862 0.04862
            image    (time, y, x) uint32 298 314 304 304 304 314 ... 339 339 328 319 319
    """
    # Late import to speedup start-up time
    import xarray as xr

    dataset: xr.Dataset = xr.Dataset()

    keys: Sequence[str] = (
        "scene",
        "photon",
        "charge",
        "pixel",
        "signal",
        "image",
        "data",
    )

    for key in keys:
        if key.startswith("data") or key.startswith("scene"):
            continue

        obj: Photon | Pixel | Image | Signal | Charge = getattr(detector, key)

        # TODO: Is this necessary ?
        if not isinstance(obj, Photon | Pixel | Image | Signal | Charge):
            raise TypeError(
                f"Wrong type from attribute 'detector.{key}'. Type: {type(obj)!r}"
            )

        data_array: xr.DataArray = obj.to_xarray()
        data_array.name = "value"  # TODO: Is is necessary ?

        dataset[key] = data_array

    # Get current absolute time
    absolute_time = xr.DataArray(
        [detector.absolute_time],
        dims="time",
        attrs={"units": "s", "long_name": "Readout time"},
    )

    # Add dimension 'time'
    dataset_with_time: xr.Dataset = dataset.expand_dims(dim="time").assign_coords(
        time=absolute_time
    )

    return xr.DataTree(dataset_with_time)


def run_pipeline(
    processor: Processor,
    readout: "Readout",
    outputs: Union["ExposureOutputs", "ObservationOutputs", None],
    debug: bool,
    with_inherited_coords: bool,
    output_filename_suffix: int | str | None = None,
    pipeline_seed: int | None = None,
    progress_bar: TqdmProgressBar | None = None,
) -> "xr.DataTree":
    """Run standalone exposure pipeline.

    Parameters
    ----------
    processor : Processor
    readout : Readout
        Contains timing for the detector's readout process, including non-destructive or
        destructive readout behavior.
    debug : bool
        If True, captures intermediate data for debugging purposes.
    with_inherited_coords : bool
        If True, the results are formatted hierarchically in the returned `DataTree`.
    pipeline_seed : int
        An optional random seed to ensure reproducibility of the pipeline.

    Returns
    -------
    DataTree
    """
    # Late import to speedup start-up time
    import xarray as xr
    from dask.utils import format_bytes

    # if isinstance(detector, CCD):
    #    dynamic.non_destructive_readout = False

    with set_random_seed(seed=pipeline_seed):
        detector = processor.detector

        # Configure the detector's readout properties
        detector.set_readout(
            times=readout.times,
            start_time=readout.start_time,
            non_destructive=readout.non_destructive,
        )

        # The detector should be reset before exposure
        detector.empty()

        if progress_bar is not None:
            num_total_steps = (
                detector.readout_properties.num_steps * processor.num_steps()
            )

            progress_bar.set_description_str(desc="Run pipeline: ")
            progress_bar.set_postfix({"size": format_bytes(0)})
            progress_bar.reset(total=num_total_steps)

        buckets_data_tree: xr.DataTree = xr.DataTree()

        # Iterate over the readout steps (time and step) for processing.
        i: int
        time: float
        step: float
        for i, (time, step) in enumerate(
            zip(
                detector.readout_properties.times,
                detector.readout_properties.steps,
                strict=False,
            )
        ):
            # Update the detector's current time and time step for this iteration.
            detector.readout_properties.time = time
            detector.readout_properties.time_step = step
            detector.readout_properties.pipeline_count = i

            logging.info("time = %.3f s", time)

            # If the readout is destructive, the detector needs to be emptied.
            is_destructive_readout: bool = not detector.non_destructive_readout
            detector.empty(is_destructive_readout)

            # Execute the pipeline for this step.
            processor.run_pipeline(debug=debug, progress_bar=progress_bar)

            # Extract the results from the 'detector' into a partial 'DataTree'
            partial_datatree_2d: xr.DataTree = _extract_datatree_2d(detector=detector)

            # Concatenate all 'partial_datatree'
            if buckets_data_tree.is_empty:
                buckets_data_tree = partial_datatree_2d
            else:
                buckets_data_tree = xr.map_over_datasets(
                    lambda *data: xr.merge(data),  # function
                    buckets_data_tree,
                    partial_datatree_2d,
                )

                # Fix the data type of the 'image' container to match the detector's image dtype.
                # See #652
                image_dtype: np.dtype = buckets_data_tree["image"].dtype
                exp_dtype: np.dtype = detector.image.dtype

                if image_dtype != exp_dtype:
                    buckets_data_tree["image"] = buckets_data_tree["image"].astype(
                        dtype=exp_dtype
                    )

            # Update the progress bar after each step.
            if progress_bar is not None:
                num_bytes = buckets_data_tree.nbytes
                num_bytes += detector.scene.data.nbytes

                if debug:
                    num_bytes += detector.intermediate.nbytes

                if detector._data is not None:
                    num_bytes += detector.data.nbytes

                progress_bar.set_postfix({"size": format_bytes(num_bytes)})

        # Prepare the final dictionary to construct the `DataTree`.
        dct: dict[str, xr.Dataset | xr.DataTree | None] = {}

        if not detector.scene.data.is_empty and not with_inherited_coords:
            warnings.warn(
                "The 'Scene' container is not empty.\n"
                "To ensure proper behavior, the 'with_inherited_coords' parameter must be set to True when calling 'pyxel.run_mode'.\n"
                "Please use the following syntax:\n"
                "\n"
                "    pyxel.run_mode(..., with_inherited_coords=True)\n"
                "\n"
                "This will ensure that inherited coordinates are applied correctly in the current 'Scene'.",
                stacklevel=5,
            )
            with_inherited_coords = True

        # Add the final buckets data to the tree.
        if with_inherited_coords:
            dct["/bucket"] = buckets_data_tree
        else:
            dct["/"] = buckets_data_tree

        # If debug is enabled, add intermediate data to the `DataTree`.
        if debug:
            datatree_intermediate: xr.DataTree = detector.intermediate

            # Remove temporary data_tree '/last' from 'datatree_intermediate'
            dct["/intermediate"] = datatree_intermediate.drop_nodes(
                "last", errors="ignore"
            )

        if outputs and outputs.save_data_to_file:
            filenames: Sequence[Path] = outputs.build_filenames(
                filename_suffix=output_filename_suffix
            )
            outputs_datatree: "xr.DataTree" = save_to_files(
                folder=outputs.current_output_folder,
                processor=processor,
                filenames=filenames,
                header=processor.detector.header,
            )

            dct["/output"] = outputs_datatree

        # Add additional data
        dct["/scene"] = detector.scene.data
        dct["/data"] = detector.data

        # Create the final `DataTree` from the dictionary.
        data_tree = xr.DataTree.from_dict(dct)
        data_tree.attrs["pyxel version"] = __version__

        if progress_bar:
            progress_bar.close()

    return data_tree
