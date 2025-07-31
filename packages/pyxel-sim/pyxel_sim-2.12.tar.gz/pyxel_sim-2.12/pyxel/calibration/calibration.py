#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""

import logging
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Optional

import numpy as np
from dask.delayed import Delayed
from typing_extensions import deprecated

import pyxel
from pyxel.calibration import (
    Algorithm,
    ArchipelagoDataTree,
    CalibrationMode,
    DaskBFE,
    DaskIsland,
    FitRange3D,
    Island,
    MyArchipelago,
    to_fit_range,
)
from pyxel.calibration.fitting import ModelFitting
from pyxel.calibration.fitting_datatree import ModelFittingDataTree
from pyxel.exposure import Readout
from pyxel.observation import ParameterValues
from pyxel.pipelines import FitnessFunction, Processor, ResultId, get_result_id
from pyxel.util import resolve_with_working_directory

if TYPE_CHECKING:
    import pandas as pd
    import xarray as xr

    from pyxel.outputs import CalibrationOutputs


def to_path_list(filenames: Sequence[str | Path]) -> Sequence[Path]:
    """Convert a sequence of ``Path``-like into a sequence of ``Path``.

    Raises
    ------
    FileNotFoundError
        Raised if the filename does not exist.
    """
    lst: list[Path] = []
    for filename in filenames:
        full_filename = Path(resolve_with_working_directory(filename)).resolve()

        if not full_filename.exists():
            raise FileNotFoundError(f"File: {full_filename} does not exist !")

        lst.append(full_filename)

    return lst


class Calibration:
    """TBW."""

    def __init__(
        self,
        target_data_path: Sequence[str | Path],
        fitness_function: FitnessFunction,
        algorithm: Algorithm,
        parameters: Sequence[ParameterValues],
        outputs: Optional["CalibrationOutputs"] = None,
        readout: Optional["Readout"] = None,
        mode: Literal["pipeline", "single_model"] = "pipeline",
        result_type: Literal["image", "signal", "pixel"] = "image",
        result_fit_range: (
            tuple[int, int, int, int] | tuple[int, int, int, int, int, int] | None
        ) = None,
        result_input_arguments: Sequence[ParameterValues] | None = None,
        target_fit_range: (
            tuple[int, int, int, int] | tuple[int, int, int, int, int, int] | None
        ) = None,
        pygmo_seed: int | None = None,
        pipeline_seed: int | None = None,
        num_islands: int = 1,
        num_evolutions: int = 1,
        num_best_decisions: int | None = None,
        topology: Literal["unconnected", "ring", "fully_connected"] = "unconnected",
        type_islands: Literal[
            "multiprocessing", "multithreading", "ipyparallel"
        ] = "multiprocessing",
        weights_from_file: Sequence[str | Path] | None = None,
        weights: Sequence[float] | None = None,
        working_directory: str | None = None,
    ):
        if pygmo_seed is not None and pygmo_seed not in range(100001):
            raise ValueError("'Pygmo seed' must be between 0 and 100000.")

        if num_islands < 1:
            raise ValueError("'num_islands' must superior or equal to 1.")

        self._log = logging.getLogger(__name__)

        self.outputs: "CalibrationOutputs" | None = outputs
        self.readout: Readout = readout or Readout()
        self.working_directory: Path | None = (
            Path(working_directory) if working_directory else None
        )

        # Set 'working_directory'
        pyxel.set_options(working_directory=self.working_directory)

        self._calibration_mode = CalibrationMode(mode)

        self._result_type: ResultId = get_result_id(result_type)

        self._result_fit_range: Sequence[int] = result_fit_range or []

        self._result_input_arguments: Sequence[ParameterValues] = (
            result_input_arguments or []
        )

        # TODO: Write functional tests
        try:
            target_data_full_path: Sequence[Path] = to_path_list(target_data_path)
        except FileNotFoundError as exc:
            note = "A file was not found in parameter 'calibration.target_data_path'."
            if sys.version_info >= (3, 11):
                exc.add_note(note)
                raise
            else:
                raise FileNotFoundError(f"{exc}\n{note}") from exc

        self._target_data_path: Sequence[Path] = target_data_full_path
        self._target_fit_range: Sequence[int] = target_fit_range or []

        self._fitness_function: FitnessFunction = fitness_function
        self._algorithm: Algorithm = algorithm

        self._parameters: Sequence[ParameterValues] = parameters or []

        if pygmo_seed is None:
            rng = np.random.default_rng()
            self._pygmo_seed: int = int(rng.integers(100_000))
        else:
            self._pygmo_seed = pygmo_seed

        self._num_islands: int = num_islands
        self._num_evolutions: int = num_evolutions
        self._num_best_decisions: int | None = num_best_decisions
        self._type_islands: Island = Island(type_islands)
        self._pipeline_seed = pipeline_seed
        self._topology: Literal["unconnected", "ring", "fully_connected"] = topology

        if weights and weights_from_file:
            raise ValueError("Cannot define both weights and weights from file.")

        # TODO: Write functional tests
        # TODO: implement working_dir
        if not weights_from_file:
            weights_full_path: Sequence[Path] | None = None
        else:
            try:
                weights_full_path = to_path_list(weights_from_file)
            except FileNotFoundError as exc:
                note = (
                    "A file was not found in parameter 'calibration.weights_from_file'."
                )
                if sys.version_info >= (3, 11):
                    exc.add_note(note)
                    raise
                else:
                    raise FileNotFoundError(f"{exc}\n{note}") from exc

        self._weights_from_file: Sequence[Path] | None = weights_full_path
        self._weights: Sequence[float] | None = weights

    @property
    def calibration_mode(self) -> CalibrationMode:
        """TBW."""
        return self._calibration_mode

    @calibration_mode.setter
    def calibration_mode(self, value: CalibrationMode) -> None:
        """TBW."""
        self._calibration_mode = value

    @property
    def result_type(self) -> ResultId:
        """TBW."""
        return self._result_type

    @result_type.setter
    def result_type(self, value: ResultId) -> None:
        """TBW."""
        self._result_type = value

    @property
    def result_fit_range(self) -> Sequence[int]:
        """TBW."""
        return self._result_fit_range

    @result_fit_range.setter
    def result_fit_range(self, value: Sequence[int]) -> None:
        """TBW."""
        self._result_fit_range = value

    @property
    def result_input_arguments(self) -> Sequence[ParameterValues]:
        """TBW."""
        return self._result_input_arguments

    @result_input_arguments.setter
    def result_input_arguments(self, value: Sequence[ParameterValues]) -> None:
        """TBW."""
        self._result_input_arguments = value

    @property
    def target_data_path(self) -> Sequence[Path]:
        """TBW."""
        return self._target_data_path

    @target_data_path.setter
    def target_data_path(self, value: Sequence[Path]) -> None:
        """TBW."""
        self._target_data_path = value

    @property
    def target_fit_range(self) -> Sequence[int]:
        """TBW."""
        return self._target_fit_range

    @target_fit_range.setter
    def target_fit_range(self, value: Sequence[int]) -> None:
        """TBW."""
        self._target_fit_range = value

    @property
    def fitness_function(self) -> FitnessFunction:
        """TBW."""
        return self._fitness_function

    @fitness_function.setter
    def fitness_function(self, value: FitnessFunction) -> None:
        """TBW."""
        self._fitness_function = value

    @property
    def algorithm(self) -> Algorithm:
        """TBW."""
        return self._algorithm

    @algorithm.setter
    def algorithm(self, value: Algorithm) -> None:
        """TBW."""
        self._algorithm = value

    @property
    def parameters(self) -> Sequence[ParameterValues]:
        """TBW."""
        return self._parameters

    @parameters.setter
    def parameters(self, value: Sequence[ParameterValues]) -> None:
        """TBW."""
        self._parameters = value

    @property
    def pygmo_seed(self) -> int:
        """TBW."""
        return self._pygmo_seed

    @pygmo_seed.setter
    def pygmo_seed(self, value: int) -> None:
        """TBW."""
        if value not in range(100001):
            raise ValueError("Pygmo 'seed' must be between 0 and 100000.")

        self._pygmo_seed = value

    @property
    def pipeline_seed(self) -> int | None:
        """TBW."""
        return self._pipeline_seed

    @pipeline_seed.setter
    def pipeline_seed(self, value: int) -> None:
        """TBW."""
        self._pipeline_seed = value

    @property
    def num_islands(self) -> int:
        """TBW."""
        return self._num_islands

    @num_islands.setter
    def num_islands(self, value: int) -> None:
        """TBW."""
        if value < 1:
            raise ValueError("'num_islands' must superior or equal to 1.")

        self._num_islands = value

    @property
    def num_evolutions(self) -> int:
        """TBW."""
        return self._num_evolutions

    @num_evolutions.setter
    def num_evolutions(self, value: int) -> None:
        """TBW."""
        self._num_evolutions = value

    @property
    def num_best_decisions(self) -> int | None:
        """TBW."""
        return self._num_best_decisions

    @num_best_decisions.setter
    def num_best_decisions(self, value: int | None) -> None:
        """TBW."""
        if isinstance(value, int) and value < 0:
            raise ValueError(
                "'num_best_decisions' must be 'None' or a positive integer"
            )

        self._num_best_decisions = value

    @property
    def topology(self) -> Literal["unconnected", "ring", "fully_connected"]:
        """TBW."""
        return self._topology

    @topology.setter
    def topology(self, value: Any) -> None:
        if value not in ("unconnected", "ring", "fully_connected"):
            raise ValueError(
                "Expecting value: 'unconnected', 'ring' or 'fully_connected'"
            )

        self._topology = value

    @property
    def weights_from_file(self) -> Sequence[Path] | None:
        """TBW."""
        return self._weights_from_file

    @weights_from_file.setter
    def weights_from_file(self, value: Sequence[Path]) -> None:
        """TBW."""
        self._weights_from_file = value

    @property
    def weights(self) -> Sequence[float] | None:
        """TBW."""
        return self._weights

    @weights.setter
    def weights(self, value: Sequence[float]) -> None:
        """TBW."""
        self._weights = value

    @deprecated("This method will be removed")
    def get_problem(
        self,
        processor: Processor,
        output_dir: Path | None,
    ) -> ModelFitting:  # pragma: no cover
        """Convert a 'processor' object into a Pygmo Problem.

        Examples
        --------
        Create a 'Pygmo Problem'
        >>> calibration = Calibration(...)
        >>> problem = calibration.get_problem(processor=..., output_dir=...)

        Create a decision vector
        >>> problem.get_bounds()
        >>> decision_vector = [...]

        Compute fitness
        >>> problem.fitness(decision_vector)
        """
        problem = ModelFitting(
            processor=processor,
            variables=self.parameters,
            readout=self.readout,
            calibration_mode=CalibrationMode(self.calibration_mode),
            simulation_output=self.result_type,
            generations=self.algorithm.generations,
            population_size=self.algorithm.population_size,
            fitness_func=self.fitness_function,
            file_path=output_dir,
        )

        problem.configure(
            target_output=self.target_data_path,
            target_fit_range=self.target_fit_range,
            out_fit_range=self.result_fit_range,
            input_arguments=self.result_input_arguments,
            weights=self.weights,
            weights_from_file=self.weights_from_file,
        )

        return problem

    @deprecated("This method will be removed")
    def _run_calibration_deprecated(
        self,
        processor: Processor,
        output_dir: Path | None,
        with_progress_bar: bool = True,
    ) -> tuple["xr.Dataset", "pd.DataFrame", "pd.DataFrame"]:  # pragma: no cover
        """Run calibration pipeline."""
        try:
            import pygmo as pg
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "Missing optional package 'pygmo'.\n"
                "Please install it with 'pip install pyxel-sim[calibration]' "
                "or 'pip install pyxel-sim[all]'"
            ) from exc

        pg.set_global_rng_seed(seed=self.pygmo_seed)
        self._log.info("Pygmo seed: %d", self.pygmo_seed)

        # Create a Pygmo problem
        fitting: ModelFitting = self.get_problem(
            processor=processor,
            output_dir=output_dir,
        )

        # Create an archipelago
        user_defined_island = DaskIsland()
        user_defined_bfe = DaskBFE()

        if self.topology == "unconnected":
            topo = pg.unconnected()
        elif self.topology == "ring":
            topo = pg.ring()
        elif self.topology == "fully_connected":
            topo = pg.fully_connected()
        else:
            raise NotImplementedError(f"topology {self.topology!r}")

        # Create a new archipelago
        # This operation takes some time ...
        archipelago = MyArchipelago(
            num_islands=self.num_islands,
            udi=user_defined_island,
            algorithm=self.algorithm,
            problem=fitting,
            pop_size=self.algorithm.population_size,
            bfe=user_defined_bfe,
            topology=topo,
            pygmo_seed=self.pygmo_seed,
            with_bar=with_progress_bar,
        )

        # Run several evolutions in the archipelago
        ds, df_processors, df_all_logs = archipelago.run_evolve(
            readout=self.readout,
            num_evolutions=self._num_evolutions,
            num_best_decisions=self._num_best_decisions,
        )

        ds.attrs["topology"] = self.topology
        ds.attrs["result_type"] = str(fitting.sim_output)

        self._log.info("Calibration ended.")
        return ds, df_processors, df_all_logs

    def run_calibration(
        self,
        processor: Processor,
        output_dir: Path | None,
        with_inherited_coords: bool,
        with_progress_bar: bool = True,
    ) -> "xr.DataTree":
        """Run calibration pipeline."""
        try:
            import pygmo as pg
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "Missing optional package 'pygmo'.\n"
                "Please install it with 'pip install pyxel-sim[calibration]' "
                "or 'pip install pyxel-sim[all]'"
            ) from exc

        pg.set_global_rng_seed(seed=self.pygmo_seed)
        self._log.info("Pygmo seed: %d", self.pygmo_seed)

        target_fit_range = to_fit_range(self.target_fit_range)
        result_fit_range = FitRange3D.from_sequence(self.result_fit_range)

        fitting: ModelFittingDataTree = ModelFittingDataTree(
            processor=processor,
            variables=self.parameters,
            readout=self.readout,
            simulation_output=self.result_type,
            generations=self.algorithm.generations,
            population_size=self.algorithm.population_size,
            fitness_func=self.fitness_function,
            file_path=output_dir,
            target_filenames=self.target_data_path,
            target_fit_range=target_fit_range,
            out_fit_range=result_fit_range,
            input_arguments=self.result_input_arguments,
            weights=self.weights,
            weights_from_file=self.weights_from_file,
            with_inherited_coords=with_inherited_coords,
        )

        # Create an archipelago
        user_defined_island = DaskIsland()
        user_defined_bfe = DaskBFE()

        if self.topology == "unconnected":
            topo = pg.unconnected()
        elif self.topology == "ring":
            topo = pg.ring()
        elif self.topology == "fully_connected":
            topo = pg.fully_connected()
        else:
            raise NotImplementedError(f"topology {self.topology!r}")

        # Create a new archipelago
        # This operation takes some time ...
        archipelago = ArchipelagoDataTree(
            num_islands=self.num_islands,
            udi=user_defined_island,
            algorithm=self.algorithm,
            problem=fitting,
            pop_size=self.algorithm.population_size,
            bfe=user_defined_bfe,
            topology=topo,
            pygmo_seed=self.pygmo_seed,
            with_bar=with_progress_bar,
        )

        # Run several evolutions in the archipelago
        data_tree: "xr.DataTree" = archipelago.run_evolve(
            readout=self.readout,
            num_rows=processor.detector.geometry.row,
            num_cols=processor.detector.geometry.col,
            num_evolutions=self._num_evolutions,
            num_best_decisions=self._num_best_decisions,
        )

        data_tree.attrs["topology"] = self.topology
        data_tree.attrs["result_type"] = str(fitting.sim_output)

        self._log.info("Calibration ended.")
        return data_tree

    @deprecated("This method will be removed")
    def _post_processing(
        self,
        ds: "xr.Dataset",
        df_processors: "pd.DataFrame",
        output: Optional["CalibrationOutputs"],
    ) -> Sequence[Delayed]:  # pragma: no cover
        if output:
            filenames: Sequence[Delayed] = output._save_processors_deprecated(
                processors=df_processors
            )
        else:
            filenames = []

        # TODO: Use output.fitting_plot ?
        # TODO: Use output.fitting_plot_close ?
        # TODO: Use output.calibration_plots ?

        return filenames

    @classmethod
    def from_json(cls, dct: Mapping) -> "Calibration":
        """Create a new object from a JSON dictionary."""
        from pyxel.outputs import CalibrationOutputs

        def _from_json(
            outputs: Mapping,
            target_data_path: Sequence[str],
            fitness_function: Mapping,
            algorithm: Mapping,
            parameters: Sequence[Mapping],
            readout: Mapping | None = None,
            result_input_arguments: Sequence[Mapping] | None = None,
            **kwargs,
        ) -> "Calibration":
            """Create a new object from an unpacked JSON dictionary."""
            return cls(
                outputs=CalibrationOutputs(**outputs),
                target_data_path=target_data_path,
                fitness_function=FitnessFunction(func=fitness_function["func"]),
                algorithm=Algorithm(**algorithm),
                parameters=[ParameterValues(**el) for el in parameters],
                readout=(Readout(**readout) if readout else None),
                result_input_arguments=(
                    [ParameterValues(**el) for el in result_input_arguments]
                    if result_input_arguments
                    else None
                ),
                **kwargs,
            )

        return _from_json(**dct)
