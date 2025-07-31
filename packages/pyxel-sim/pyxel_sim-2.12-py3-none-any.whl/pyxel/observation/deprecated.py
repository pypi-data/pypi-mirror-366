#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Subpackage for deprecated functions for Observation mode."""

from collections import Counter
from collections.abc import Iterable, Iterator, Mapping, Sequence
from typing import TYPE_CHECKING, NamedTuple, Union

import numpy as np
from typing_extensions import deprecated

from pyxel.exposure import _run_exposure_pipeline_deprecated
from pyxel.observation import (
    CustomMode,
    ParametersType,
    ParameterType,
    ProductMode,
    SequentialMode,
    _get_short_name_with_model,
    create_new_processor,
    short,
)

if TYPE_CHECKING:
    import xarray as xr

    from pyxel.observation import Observation
    from pyxel.pipelines import Processor


class ObservationResult(NamedTuple):
    """Result class for observation class."""

    dataset: Union["xr.Dataset", dict[str, "xr.Dataset"]]
    parameters: "xr.Dataset"
    logs: "xr.Dataset"


@deprecated("This function will be removed")
def _id(s: str) -> str:  # pragma: no cover
    """Add _id to the end of a string."""
    out = s + "_id"
    return out


@deprecated("This function will be removed")
def parameter_to_dataset(
    parameter_dict: dict,
    dimension_names: Mapping[str, str],
    index: int,
    coordinate_name: str,
) -> "xr.Dataset":  # pragma: no cover
    """Return a specific parameter dataset from a parameter dictionary.

    Parameters
    ----------
    parameter_dict: dict
    dimension_names
    index: int
    coordinate_name: str

    Returns
    -------
    Dataset
    """

    # Late import to speedup start-up time
    import xarray as xr

    parameter_ds = xr.Dataset()
    parameter = xr.DataArray(parameter_dict[coordinate_name])

    # TODO: Dirty hack. Fix this !
    short_name: str = dimension_names[coordinate_name]

    if short_name.endswith("_id"):
        short_coord_name = short_name[:-3]
        short_coord_name_id = short_name
    else:
        short_coord_name = short_name
        short_coord_name_id = f"{short_name}_id"

    parameter = parameter.assign_coords({short_coord_name_id: index})
    parameter = parameter.expand_dims(dim=short_coord_name_id)
    parameter_ds[short_coord_name] = parameter

    return parameter_ds


@deprecated("This function will be removed")
def _add_custom_parameters_deprecated(
    ds: "xr.Dataset", index: int
) -> "xr.Dataset":  # pragma: no cover
    """Add coordinate "index" to the dataset.

    Parameters
    ----------
    ds: Dataset
    index: int

    Returns
    -------
    Dataset
    """
    ds = ds.assign_coords({"id": index})
    ds = ds.expand_dims(dim="id")

    return ds


@deprecated("This function will be removed")
def _get_final_short_name(
    name: str, param_type: ParameterType
) -> str:  # pragma: no cover
    if param_type == ParameterType.Simple:
        return name
    elif param_type == ParameterType.Multi:
        return _id(name)
    else:
        raise NotImplementedError


@deprecated("This function will be removed")
def _get_short_dimension_names(
    types: Mapping[str, ParameterType],
) -> Mapping[str, str]:  # pragma: no cover
    # Create potential names for the dimensions
    potential_dim_names: dict[str, str] = {}
    for param_name, param_type in types.items():
        short_name: str = short(param_name)

        potential_dim_names[param_name] = _get_final_short_name(
            name=short_name, param_type=param_type
        )

    # Find possible duplicates
    count_dim_names: Mapping[str, int] = Counter(potential_dim_names.values())

    duplicate_dim_names: Sequence[str] = [
        name for name, freq in count_dim_names.items() if freq > 1
    ]

    if duplicate_dim_names:
        dim_names: dict[str, str] = {}
        for param_name, param_type in types.items():
            short_name = potential_dim_names[param_name]

            if short_name in duplicate_dim_names:
                new_short_name: str = _get_short_name_with_model(param_name)
                dim_names[param_name] = _get_final_short_name(
                    name=new_short_name, param_type=param_type
                )

            else:
                dim_names[param_name] = short_name

        return dim_names

    return potential_dim_names


@deprecated("This function will be removed")
def log_parameters(
    processor_id: int, parameter_dict: dict
) -> "xr.Dataset":  # pragma: no cover
    """Return parameters in the current processor in a xarray dataset.

    Parameters
    ----------
    processor_id: int
    parameter_dict: dict

    Returns
    -------
    Dataset
    """
    # Late import to speedup start-up time
    import xarray as xr

    out = xr.Dataset()
    for key, value in parameter_dict.items():
        da = xr.DataArray(value)
        da = da.assign_coords(coords={"id": processor_id})
        da = da.expand_dims(dim="id")
        out[short(key)] = da
    return out


@deprecated("This function will be removed")
def _add_sequential_parameters_deprecated(
    ds: "xr.Dataset",
    parameter_dict: ParametersType,
    dimension_names: Mapping[str, str],
    index: int,
    coordinate_name: str,
    types: Mapping[str, ParameterType],
) -> "xr.Dataset":  # pragma: no cover
    """Add true coordinates or index to sequential mode dataset.

    Parameters
    ----------
    ds : Dataset
    parameter_dict : dict
    dimension_names
    index : int
    coordinate_name : str
    types : dict

    Returns
    -------
    Dataset
    """
    #  assigning the right coordinates based on type
    short_name: str = dimension_names[coordinate_name]

    if types[coordinate_name] == ParameterType.Simple:
        ds = ds.assign_coords(coords={short_name: parameter_dict[coordinate_name]})
        ds = ds.expand_dims(dim=short_name)

    elif types[coordinate_name] == ParameterType.Multi:
        ds = ds.assign_coords({short_name: index})
        ds = ds.expand_dims(dim=short_name)

    return ds


@deprecated("This function will be removed")
def _add_product_parameters_deprecated(  # pragma: no cover
    ds: "xr.Dataset",
    parameter_dict: ParametersType,
    dimension_names: Mapping[str, str],
    indices: tuple[int, ...],
    types: Mapping[str, ParameterType],
) -> "xr.Dataset":  # pragma: no cover
    """Add true coordinates or index to product mode dataset.

    Parameters
    ----------
    ds: Dataset
    parameter_dict: dict
    indices: tuple
    types: dict

    Returns
    -------
    Dataset
    """
    # TODO: Implement for coordinate 'multi'
    for i, (coordinate_name, param_value) in enumerate(parameter_dict.items()):
        short_name: str = dimension_names[coordinate_name]

        #  assigning the right coordinates based on type
        if types[coordinate_name] == ParameterType.Simple:
            ds = ds.assign_coords(coords={short_name: param_value})
            ds = ds.expand_dims(dim=short_name)

        elif types[coordinate_name] == ParameterType.Multi:
            ds = ds.assign_coords({short_name: indices[i]})
            ds = ds.expand_dims(dim=short_name)

        else:
            raise NotImplementedError

    return ds


@deprecated("This function will be removed")
def to_tuples(data: Iterable) -> tuple:  # pragma: no cover
    lst: list = []
    for el in data:
        if isinstance(el, Iterable) and not isinstance(el, str):
            lst.append(to_tuples(el))
        else:
            lst.append(el)

    return tuple(lst)


@deprecated("This function will be removed")
def compute_final_sequential_dataset(
    list_of_index_and_parameter: list,
    list_of_datasets: list,
    dimension_names: Mapping[str, str],
) -> dict[str, "xr.Dataset"]:  # pragma: no cover
    """Return a dictionary of result datasets where keys are different parameters.

    Parameters
    ----------
    list_of_index_and_parameter: list
    list_of_datasets: list
    dimension_names

    Returns
    -------
    dict
    """
    # Late import to speedup start-up time
    import xarray as xr

    final_dict: dict[str, list[xr.Dataset]] = {}

    for _, parameter_dict, n in list_of_index_and_parameter:
        coordinate = str(next(iter(parameter_dict)))
        coordinate_short: str = dimension_names[coordinate]

        if short(coordinate) not in final_dict:
            final_dict.update({coordinate_short: []})
            final_dict[coordinate_short].append(list_of_datasets[n])
        else:
            final_dict[coordinate_short].append(list_of_datasets[n])

    final_datasets: dict[str, xr.Dataset] = {}
    for key, value in final_dict.items():
        ds = xr.combine_by_coords(value)
        # see issue #276
        if not isinstance(ds, xr.Dataset):
            raise TypeError("Expecting 'Dataset'.")

        final_datasets.update({key: ds})

    return final_datasets


@deprecated("This function will be removed")
def _run_debug_mode_deprecated(
    observation: "Observation", processor: "Processor"
) -> tuple[list["Processor"], "xr.Dataset"]:  # pragma: no cover
    """Run observation pipelines in debug mode and return list of processors and parameter logs.

    Parameters
    ----------
    processor: Processor

    Returns
    -------
    processors: list
    final_logs: Dataset
    """
    # Late import to speedup start-up time
    import xarray as xr
    from tqdm.auto import tqdm

    processors = []
    logs: list[xr.Dataset] = []

    for processor_id, (proc, _index, parameter_dict) in enumerate(
        tqdm(_processors_it(observation, processor=processor))
    ):
        log: xr.Dataset = log_parameters(
            processor_id=processor_id, parameter_dict=parameter_dict
        )
        logs.append(log)
        _ = _run_exposure_pipeline_deprecated(
            processor=proc,
            readout=observation.readout,
            outputs=observation.outputs,
            pipeline_seed=observation.pipeline_seed,
        )
        processors.append(processor)

    # See issue #276
    final_logs = xr.combine_by_coords(logs)
    if not isinstance(final_logs, xr.Dataset):
        raise TypeError("Expecting 'Dataset'.")

    return processors, final_logs


# ruff: noqa: C901
@deprecated("This function will be removed")
def _run_observation_deprecated(
    observation: "Observation", processor: "Processor"
) -> ObservationResult:  # pragma: no cover
    """Run the observation pipelines.

    Parameters
    ----------
    processor : Processor

    Returns
    -------
    Result
    """
    # Late import to speedup start-up time
    import dask.bag as db
    import xarray as xr
    from tqdm.auto import tqdm

    # validation
    observation.validate_steps(processor)

    types: Mapping[str, ParameterType] = observation._get_parameter_types()

    dim_names: Mapping[str, str] = _get_short_dimension_names(types)

    y = range(processor.detector.geometry.row)
    x = range(processor.detector.geometry.col)
    times = observation.readout.times

    if isinstance(observation.parameter_mode, ProductMode):

        def _apply_pipeline(index_and_parameter):
            return _apply_exposure_pipeline_product(
                observation,
                index_and_parameter=index_and_parameter,
                dimension_names=dim_names,
                x=x,
                y=y,
                processor=processor,
                times=times,
                types=types,
            )

        lst = [
            (index, parameter_dict, n)
            for n, (index, parameter_dict) in enumerate(_parameter_it(observation))
        ]

        if observation.with_dask:
            dataset_list = db.from_sequence(lst).map(_apply_pipeline).compute()
        else:
            dataset_list = list(map(_apply_pipeline, tqdm(lst)))

        # prepare lists for to-be-merged datasets
        parameters: list[list[xr.Dataset]] = [
            [] for _ in range(len(observation.parameter_mode.enabled_steps))
        ]
        logs = []

        for processor_id, (indices, parameter_dict, _) in enumerate(lst):
            # log parameters for this pipeline
            log = log_parameters(
                processor_id=processor_id, parameter_dict=parameter_dict
            )
            logs.append(log)

            # save parameters with appropriate product mode indices
            for i, coordinate in enumerate(parameter_dict):
                parameter_ds = parameter_to_dataset(
                    parameter_dict=parameter_dict,
                    dimension_names=dim_names,
                    index=indices[i],
                    coordinate_name=coordinate,
                )
                parameters[i].append(parameter_ds)

        # merging/combining the outputs
        final_parameters_list: list[xr.Dataset] = []
        for p in parameters:
            # See issue #276
            new_dataset = xr.combine_by_coords(p)
            if not isinstance(new_dataset, xr.Dataset):
                raise TypeError("Expecting 'Dataset'.")

            final_parameters_list.append(new_dataset)

        final_parameters_merged = xr.merge(final_parameters_list)

        # See issue #276
        final_logs = xr.combine_by_coords(logs)
        if not isinstance(final_logs, xr.Dataset):
            raise TypeError("Expecting 'Dataset'.")

        # See issue #276
        final_dataset = xr.combine_by_coords(dataset_list)
        if not isinstance(final_dataset, xr.Dataset):
            raise TypeError("Expecting 'Dataset'.")

        result = ObservationResult(
            dataset=final_dataset,
            parameters=final_parameters_merged,
            logs=final_logs,
        )

        return result

    elif isinstance(observation.parameter_mode, SequentialMode):

        def _apply_pipeline(index_and_parameter):
            return _apply_exposure_pipeline_sequential(
                observation,
                index_and_parameter=index_and_parameter,
                dimension_names=dim_names,
                x=x,
                y=y,
                processor=processor,
                times=times,
                types=types,
            )

        lst = [
            (index, parameter_dict, n)
            for n, (index, parameter_dict) in enumerate(_parameter_it(observation))
        ]

        if observation.with_dask:
            dataset_list = db.from_sequence(lst).map(_apply_pipeline).compute()
        else:
            dataset_list = list(map(_apply_pipeline, tqdm(lst)))

        # prepare lists/dictionaries for to-be-merged datasets
        parameters = [[] for _ in range(len(observation.parameter_mode.enabled_steps))]
        logs = []

        # overflow to next parameter step counter
        step_counter = -1

        for processor_id, (index, parameter_dict, _) in enumerate(lst):
            # log parameters for this pipeline
            # TODO: somehow refactor logger so that default parameters
            #  from other steps are also logged in sequential mode
            log = log_parameters(
                processor_id=processor_id, parameter_dict=parameter_dict
            )
            logs.append(log)

            # Figure out current coordinate
            coordinate = str(next(iter(parameter_dict)))
            # Check for overflow to next parameter
            if index == 0:
                step_counter += 1

            # save sequential parameter with appropriate index
            parameter_ds = parameter_to_dataset(
                parameter_dict=parameter_dict,
                dimension_names=dim_names,
                index=index,
                coordinate_name=coordinate,
            )
            parameters[step_counter].append(parameter_ds)

        # merging/combining the outputs
        # See issue #276
        final_logs = xr.combine_by_coords(logs)
        if not isinstance(final_logs, xr.Dataset):
            raise TypeError("Expecting 'Dataset'.")

        final_datasets = compute_final_sequential_dataset(
            list_of_index_and_parameter=lst,
            list_of_datasets=dataset_list,
            dimension_names=dim_names,
        )

        final_parameters_list = []
        for p in parameters:
            # See issue #276
            new_dataset = xr.combine_by_coords(p)
            if not isinstance(new_dataset, xr.Dataset):
                raise TypeError("Expecting 'Dataset'.")

            final_parameters_list.append(new_dataset)

        final_parameters_merged = xr.merge(final_parameters_list)

        result = ObservationResult(
            dataset=final_datasets,
            parameters=final_parameters_merged,
            logs=final_logs,
        )
        return result

    elif isinstance(observation.parameter_mode, CustomMode):

        def _apply_pipeline(index_and_parameter):
            return _apply_exposure_pipeline_custom(
                observation,
                index_and_parameter=index_and_parameter,
                x=x,
                y=y,
                processor=processor,
                times=times,
            )

        lst = [
            (index, parameter_dict, n)
            for n, (index, parameter_dict) in enumerate(_parameter_it(observation))
        ]

        if observation.with_dask:
            dataset_list = db.from_sequence(lst).map(_apply_pipeline).compute()
        else:
            dataset_list = list(map(_apply_pipeline, tqdm(lst)))

        # prepare lists for to-be-merged datasets
        logs = []

        for index, parameter_dict, _ in lst:
            # log parameters for this pipeline
            log = log_parameters(processor_id=index, parameter_dict=parameter_dict)
            logs.append(log)

        # merging/combining the outputs
        final_ds = xr.combine_by_coords(dataset_list)
        final_log = xr.combine_by_coords(logs)

        # See issue #276
        if not isinstance(final_ds, xr.Dataset):
            raise TypeError("Expecting 'Dataset'.")
        if not isinstance(final_log, xr.Dataset):
            raise TypeError("Expecting 'Dataset'.")

        final_parameters = final_log  # parameter dataset same as logs

        result = ObservationResult(
            dataset=final_ds, parameters=final_parameters, logs=final_log
        )
        return result

    else:
        raise TypeError("Parametric mode not specified.")


@deprecated("This function will be removed")
def _processors_it(
    observation: "Observation", processor: "Processor"
) -> Iterator[tuple["Processor", int | tuple[int], dict]]:  # pragma: no cover
    """Generate processors with different product parameters.

    Parameters
    ----------
    processor: Processor

    Yields
    ------
    new_processor: Processor
    index: tuple of int
    parameter_dict: dict
    """
    for index, parameter_dict in _parameter_it(observation):
        new_processor = create_new_processor(
            processor=processor,
            parameter_dict=parameter_dict,
        )
        yield new_processor, index, parameter_dict


@deprecated("This function will be removed")
def _parameter_it(observation: "Observation") -> Iterator[tuple]:  # pragma: no cover
    """Return the method for generating parameters based on parametric mode."""
    if isinstance(observation.parameter_mode, ProductMode):
        yield from observation.parameter_mode._product_parameters()

    elif isinstance(observation.parameter_mode, SequentialMode):
        yield from observation.parameter_mode._sequential_parameters()

    elif isinstance(observation.parameter_mode, CustomMode):
        yield from observation.parameter_mode._custom_parameters()
    else:
        raise NotImplementedError


@deprecated("This function will be removed")
def _apply_exposure_pipeline_product(
    observation: "Observation",
    index_and_parameter: tuple[
        tuple[int, ...],
        ParametersType,
        int,
    ],
    dimension_names: Mapping[str, str],
    processor: "Processor",
    x: range,
    y: range,
    times: np.ndarray,
    types: Mapping[str, ParameterType],
) -> "xr.Dataset":  # pragma: no cover
    index, parameter_dict, n = index_and_parameter

    new_processor = create_new_processor(
        processor=processor, parameter_dict=parameter_dict
    )

    # run the pipeline
    _ = _run_exposure_pipeline_deprecated(
        processor=new_processor,
        readout=observation.readout,
        result_type=observation.result_type,
        pipeline_seed=observation.pipeline_seed,
    )

    if observation.outputs:
        _ = observation.outputs.save_to_file(processor=new_processor, run_number=n)

    ds: xr.Dataset = new_processor.result_to_dataset(
        x=x,
        y=y,
        times=times,
        result_type=observation.result_type,
    )

    # Can also be done outside dask in a loop
    ds = _add_product_parameters_deprecated(
        ds=ds,
        parameter_dict=parameter_dict,
        dimension_names=dimension_names,
        indices=index,
        types=types,
    )

    ds.attrs.update({"running mode": "Observation - Product"})

    return ds


@deprecated("This function will be removed")
def _apply_exposure_pipeline_custom(
    observation: "Observation",
    index_and_parameter: tuple[
        int,
        ParametersType,
        int,
    ],
    processor: "Processor",
    x: range,
    y: range,
    times: np.ndarray,
):  # pragma: no cover
    index, parameter_dict, n = index_and_parameter

    new_processor = create_new_processor(
        processor=processor,
        parameter_dict=parameter_dict,
    )

    # run the pipeline
    _ = _run_exposure_pipeline_deprecated(
        processor=new_processor,
        readout=observation.readout,
        result_type=observation.result_type,
        pipeline_seed=observation.pipeline_seed,
    )

    if observation.outputs:
        _ = observation.outputs.save_to_file(processor=new_processor, run_number=n)

    ds: xr.Dataset = new_processor.result_to_dataset(
        x=x, y=y, times=times, result_type=observation.result_type
    )

    # Can also be done outside dask in a loop
    ds = _add_custom_parameters_deprecated(
        ds=ds,
        index=index,
    )
    ds.attrs.update({"running mode": "Observation - Custom"})

    return ds


@deprecated("This function will be removed")
def _apply_exposure_pipeline_sequential(
    observation: "Observation",
    index_and_parameter: tuple[
        int,
        ParametersType,
        int,
    ],
    dimension_names: Mapping[str, str],
    processor: "Processor",
    x: range,
    y: range,
    times: np.ndarray,
    types: Mapping[str, ParameterType],
):  # pragma: no cover
    index, parameter_dict, n = index_and_parameter

    new_processor = create_new_processor(
        processor=processor,
        parameter_dict=parameter_dict,
    )

    coordinate = str(next(iter(parameter_dict)))

    # run the pipeline
    _ = _run_exposure_pipeline_deprecated(
        processor=new_processor,
        readout=observation.readout,
        result_type=observation.result_type,
        pipeline_seed=observation.pipeline_seed,
    )

    if observation.outputs:
        _ = observation.outputs.save_to_file(processor=new_processor, run_number=n)

    ds: xr.Dataset = new_processor.result_to_dataset(
        x=x, y=y, times=times, result_type=observation.result_type
    )

    # Can also be done outside dask in a loop
    ds = _add_sequential_parameters_deprecated(
        ds=ds,
        parameter_dict=parameter_dict,
        dimension_names=dimension_names,
        index=index,
        coordinate_name=coordinate,
        types=types,
    )

    ds.attrs.update({"running mode": "Observation - Sequential"})

    return ds
