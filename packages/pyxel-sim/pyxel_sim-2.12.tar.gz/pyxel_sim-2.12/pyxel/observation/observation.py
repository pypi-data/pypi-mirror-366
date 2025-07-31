#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Parametric mode class and helper functions."""

import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional

import numpy as np

import pyxel
from pyxel.exposure import Readout, run_pipeline
from pyxel.observation import (
    CustomMode,
    CustomParameterEntry,
    ParameterEntry,
    ParametersType,
    ParameterType,
    ParameterValues,
    ProductMode,
    SequentialMode,
    _get_short_name_with_model,
    create_new_processor,
    run_pipelines_with_dask,
    short,
)
from pyxel.pipelines import Processor, ResultId, get_result_id

if TYPE_CHECKING:
    import xarray as xr

    from pyxel.outputs import ObservationOutputs


# TODO: Add unit tests
def _get_short_dimension_names_new(
    types: Mapping[str, ParameterType],
) -> Mapping[str, str]:
    # Create potential names for the dimensions
    potential_dim_names: dict[str, str] = {}
    for param_name in types:
        if param_name == "observation.readout.times":
            # TODO: Move this to function 'short'
            short_name: str = "readout_time"  # TODO: See #836
        else:
            short_name = short(param_name)

        potential_dim_names[param_name] = short_name

    # Find possible duplicates
    count_dim_names: Mapping[str, int] = Counter(potential_dim_names.values())

    duplicate_dim_names: Sequence[str] = [
        name for name, freq in count_dim_names.items() if freq > 1
    ]

    if duplicate_dim_names:
        dim_names: dict[str, str] = {}
        for param_name in types:
            short_name = potential_dim_names[param_name]

            if short_name in duplicate_dim_names:
                new_short_name: str = _get_short_name_with_model(param_name)
                dim_names[param_name] = new_short_name

            else:
                dim_names[param_name] = short_name

        return dim_names

    return potential_dim_names


def build_parameter_mode(
    mode: Literal["product", "sequential", "custom"],
    parameters: Sequence[ParameterValues],
    custom_filename: str | None = None,
    column_range: tuple[int, int] | None = None,
) -> ProductMode | SequentialMode | CustomMode:
    """Build a new parameter mode object.

    Parameters
    ----------
    mode : 'product', 'sequential' or 'custom'
        Define the type of mode to be returned.
    parameters
        A list or tuple of ``ParameterValues`` objects.
    custom_filename : str, optional
        Provide a valid filename for 'custom' mode.
    column_range : tuple[int, int], optional
        Range of columns for 'custom' mode, defined by a tuple (start, end).
    """
    match mode:
        case "product":
            return ProductMode(parameters)

        case "sequential":
            return SequentialMode(parameters)

        case "custom":
            custom_columns: slice | None = (
                slice(*column_range) if column_range else None
            )
            assert custom_filename is not None

            return CustomMode.build(
                parameters,
                custom_file=custom_filename,
                custom_columns=custom_columns,
            )

        case _:
            raise NotImplementedError


class Observation:
    """Observation class."""

    def __init__(
        self,
        parameters: Sequence[ParameterValues],
        outputs: Optional["ObservationOutputs"] = None,
        readout: Readout | None = None,
        mode: Literal["product", "sequential", "custom"] = "product",
        from_file: str | None = None,  # Note: Only For 'custom' mode
        column_range: tuple[int, int] | None = None,  # Note: Only For 'custom' mode
        with_dask: bool = False,
        result_type: str = "all",
        pipeline_seed: int | None = None,
        working_directory: str | None = None,
    ):
        self.outputs: "ObservationOutputs" | None = outputs
        self.readout: Readout = readout or Readout()

        self.parameter_mode: ProductMode | SequentialMode | CustomMode = (
            build_parameter_mode(
                mode=mode,
                parameters=parameters,
                custom_filename=from_file,
                column_range=column_range,
            )
        )

        self.working_directory: Path | None = (
            Path(working_directory) if working_directory else None
        )

        # Set 'working_directory'
        pyxel.set_options(working_directory=self.working_directory)

        self.with_dask = with_dask
        self.parameter_types: dict[str, ParameterType] = {}
        self._result_type: ResultId = get_result_id(result_type)
        self._pipeline_seed = pipeline_seed

    def __repr__(self):
        cls_name: str = self.__class__.__name__
        return f"{cls_name}<mode={self.parameter_mode!s}, num_parameters={len(self.parameter_mode.parameters)}>"

    @property
    def result_type(self) -> ResultId:
        """TBW."""
        return self._result_type

    @result_type.setter
    def result_type(self, value: ResultId) -> None:
        """TBW."""
        self._result_type = get_result_id(value)

    @property
    def pipeline_seed(self) -> int | None:
        """TBW."""
        return self._pipeline_seed

    @pipeline_seed.setter
    def pipeline_seed(self, value: int) -> None:
        """TBW."""
        self._pipeline_seed = value

    def _get_parameter_types(self) -> Mapping[str, ParameterType]:
        """Check for each step if parameters can be used as dataset coordinates (1D, simple) or not (multi).

        Examples
        --------
        >>> observation._get_parameter_types()
        {'pipeline.charge_transfer.cdm.arguments.beta': <ParameterType.Multi: 'multi'>,
         'pipeline.charge_transfer.cdm.arguments.trap_densities': <ParameterType.Multi: 'multi'>}
        """
        for step in self.parameter_mode.enabled_steps:
            self.parameter_types.update({step.key: step.type})
        return self.parameter_types

    def validate_steps(self, processor: Processor) -> None:
        """Validate enabled parameter steps in processor before running the pipelines.

        Parameters
        ----------
        processor: Processor

        Raises
        ------
        KeyError
            If a 'step' is missing in the configuration.
        ValueError
            If a model referenced in the configuration has not been enabled.
        """
        step: ParameterValues
        for step in self.parameter_mode.enabled_steps:
            key: str = step.key
            if not processor.has(key):
                raise KeyError(f"Missing parameter: {key!r} in steps.")

            # TODO: the string literal expressions are difficult to maintain.
            #     Example: 'pipeline.', '.arguments', '.enabled'
            #     We may want to consider an API for this.
            # Proposed API:
            # value = operator.attrgetter(step.key)(processor)
            if "pipeline." in key:
                model_name: str = key[: key.find(".arguments")]
                model_enabled: str = model_name + ".enabled"
                if not processor.get(model_enabled):
                    raise ValueError(
                        f"The '{model_name}' model referenced in Observation"
                        " configuration has not been enabled in yaml config!"
                    )

            if any(x == "_" for x in step.values[:]) and not isinstance(
                self.parameter_mode, CustomMode
            ):
                raise ValueError(
                    "Either define 'custom' as parametric mode or "
                    "do not use '_' character in 'values' field"
                )

    def run_pipelines(
        self,
        processor: Processor,
        with_inherited_coords: bool,
    ) -> "xr.DataTree":
        """Run the observation pipelines and return a `DataTree` object."""
        # Late import to speedup start-up time
        import xarray as xr
        from tqdm.auto import tqdm

        # Validate the processor steps before running the pipeline
        self.validate_steps(processor)

        # Extract the types of parameters and assign short dimension names
        types: Mapping[str, ParameterType] = self._get_parameter_types()
        dim_names: Mapping[str, str] = _get_short_dimension_names_new(types)

        if self.with_dask:
            # Run observation mode using 'dask' (in parallel)
            if with_inherited_coords is False:
                raise NotImplementedError

            final_datatree: "xr.DataTree" = run_pipelines_with_dask(
                dim_names=dim_names,
                parameter_mode=self.parameter_mode,
                processor=processor,
                readout=self.readout,
                outputs=self.outputs,
                pipeline_seed=self.pipeline_seed,
            )

        else:
            # Run observation mode sequentially (not in parallel)
            # Note: output files are generated at this stage

            # TODO: Create new class for 'Sequence[Union[ParameterItem, CustomParameterItem]]'
            # Fetch the observation parameters to be passed to the pipeline
            if isinstance(self.parameter_mode, ProductMode):
                parameters = self.parameter_mode.get_parameters_item()
            else:
                parameters = self.parameter_mode.get_parameters_item(
                    processor=processor
                )

            # If Dask is not enabled, process each parameter sequentially
            datatree_list: Sequence["xr.DataTree"] = [
                self._run_single_pipeline(
                    el,
                    dimension_names=dim_names,
                    processor=processor,
                    types=types,
                    with_inherited_coords=with_inherited_coords,
                )
                for el in tqdm(parameters)
            ]

            # Merge the sequentially processed DataTrees into the final result
            final_datatree = xr.map_over_datasets(
                lambda *data: xr.merge(data), *datatree_list
            )

        # Assign the running mode to the final DataTree attributes
        parameter_name: str = str(self.parameter_mode.__class__)
        final_datatree.attrs["running mode"] = f"Observation - {parameter_name}"

        # See issue #276. TODO: Is this still valid ?
        # if not isinstance(final_dataset, xr.Dataset):
        #     raise TypeError("Expecting 'Dataset'.")

        return final_datatree

    def _run_single_pipeline(
        self,
        param_item: ParameterEntry | CustomParameterEntry,
        dimension_names: Mapping[str, str],
        processor: Processor,
        types: Mapping[str, ParameterType],
        with_inherited_coords: bool,
        with_outputs: bool = True,  # TODO: Refactor this
        with_extra_dims: bool = True,  # TODO: Refactor this
    ) -> "xr.DataTree":
        """Run a single exposure pipeline for a given parameter item.

        Notes
        -----
        This method is only called when running Observation mode sequentially (without dask).
        """
        # Create a new processor using the given parameters
        new_processor = create_new_processor(
            processor=processor,
            parameter_dict=param_item.parameters,
        )

        # Run a single pipeline for the given parameters
        try:
            data_tree: "xr.DataTree" = run_pipeline(
                processor=new_processor,
                readout=self.readout,
                outputs=self.outputs,
                pipeline_seed=self.pipeline_seed,
                debug=False,  # Not supported in Observation mode
                with_inherited_coords=with_inherited_coords,
            )
        except Exception as exc:
            # In Python 3.11+, add context notes to the exception
            if sys.version_info >= (3, 11):
                exc.add_note(
                    "This error occurred in 'Observation' mode with the following parameters:"
                )

                for key, value in param_item.parameters.items():
                    exc.add_note(f"  - {key!r}: {value!r}")

            raise

        # Save the outputs (if configured)
        if with_outputs and self.outputs:
            data_tree["/output"] = self.outputs.save_to_file(
                processor=new_processor,
                run_number=param_item.run_index,
            )

        if not with_extra_dims:
            return data_tree

        else:
            # Can also be done outside dask in a loop
            if isinstance(param_item, ParameterEntry):
                final_data_tree = _add_product_parameters(
                    data_tree=data_tree,
                    parameter_dict=param_item.parameters,
                    indexes=param_item.index,
                    dimension_names=dimension_names,
                    types=types,
                )

            else:
                final_data_tree = _add_custom_parameters(
                    data_tree=data_tree,
                    parameter_dict=param_item.parameters,
                    index=param_item.index,
                    dimension_names=dimension_names,
                    types=types,
                )

            return final_data_tree


def _add_custom_parameters(
    data_tree: "xr.DataTree",
    parameter_dict: ParametersType,
    index: int,
    dimension_names: Mapping[str, str],
    types: Mapping[str, ParameterType],
) -> "xr.DataTree":
    """Add coordinate "index" to the dataset.

    Parameters
    ----------
    data_tree: Dataset
    index: int

    Returns
    -------
    DataTree
    """
    # Late import to speedup start-up time
    import pandas as pd
    import xarray as xr

    data_tree = data_tree.map_over_datasets(  # type: ignore[assignment]
        lambda dataset: dataset.expand_dims({"id": [index]})
    )

    for coordinate_name, param_value in parameter_dict.items():
        short_name: str = dimension_names[coordinate_name]

        #  assigning the right coordinates based on type
        if types[coordinate_name] == ParameterType.Simple:
            data_tree = data_tree.map_over_datasets(  # type: ignore[assignment]
                lambda dataset: dataset.assign_coords(
                    {short_name: ("id", pd.Index([param_value]))}
                )
            )

        elif types[coordinate_name] == ParameterType.Multi:
            data = np.array(param_value)
            data_array = xr.DataArray(data).expand_dims({"id": [index]})
            data_tree = data_tree.map_over_datasets(  # type: ignore[assignment]
                lambda dataset: dataset.assign_coords({short_name: data_array})
            )

        else:
            raise NotImplementedError

    return data_tree


def _add_product_parameters(
    data_tree: "xr.DataTree",
    parameter_dict: ParametersType,
    indexes: tuple[int, ...],
    dimension_names: Mapping[str, str],
    types: Mapping[str, ParameterType],
) -> "xr.DataTree":
    """Add true coordinates or index to product mode dataset.

    Parameters
    ----------
    data_tree : DataTree
    parameter_dict : dict
    types : dict

    Returns
    -------
    DataTree
    """
    import xarray as xr

    dim_idx = 0

    # TODO: join 'indexes' and 'parameter_dict'
    for index, (coordinate_name, param_value) in zip(
        indexes, parameter_dict.items(), strict=False
    ):
        short_name: str = dimension_names[coordinate_name]

        #  assigning the right coordinates based on type
        if types[coordinate_name] == ParameterType.Simple:
            data_tree = data_tree.map_over_datasets(  # type: ignore[assignment]
                lambda dataset: dataset.expand_dims(dim={short_name: [param_value]})
            )

        elif types[coordinate_name] == ParameterType.Multi:
            data = np.array(param_value)

            if data.ndim == 1:
                data_array = xr.DataArray(
                    data,
                    dims=f"dim_{dim_idx}",
                    coords={f"dim_{dim_idx}": range(len(data))},
                ).expand_dims(dim={f"{short_name}_id": [index]})

                dim_idx += 1

            elif data.ndim == 2:
                shape_0, shape_1 = data.shape
                data_array = xr.DataArray(
                    data,
                    dims=[f"dim_{dim_idx}", f"dim_{dim_idx + 1}"],
                    coords={
                        f"dim_{dim_idx}": range(shape_0),
                        f"dim_{dim_idx + 1}": range(shape_1),
                    },
                ).expand_dims(dim={f"{short_name}_id": [index]})

                dim_idx += 2

            else:
                raise NotImplementedError

            data_tree = data_tree.map_over_datasets(  # type: ignore[assignment]
                lambda dataset: dataset.expand_dims(
                    {f"{short_name}_id": [index]}
                ).assign_coords({short_name: data_array})
            )

        else:
            raise NotImplementedError

    return data_tree
