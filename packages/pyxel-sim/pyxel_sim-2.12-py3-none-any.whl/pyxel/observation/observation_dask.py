#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Subpackage for running Observation mode with Dask enabled."""

from collections.abc import Hashable, Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Optional

import numpy as np
from toolz import dicttoolz

from pyxel.exposure import Readout, run_pipeline
from pyxel.observation import CustomMode, ProductMode, SequentialMode
from pyxel.pipelines import Processor

if TYPE_CHECKING:
    import xarray as xr

    from pyxel.outputs import ObservationOutputs


@dataclass
class OutputDimension:
    """Represent metadata for the output dimensions used by 'xarray.apply_ufunc'.

    Parameters
    ----------
    path : str
        Path of the output variable in the DataTree.
    prefix_name : str
        Prefix used for naming dimensions.
    core_dimensions : tuple[str, ...]
        Core dimension(s) for the output.
    sizes : dict[str, int]
        Sizes of each dimension.
    dtype : numpy.dtype
        Data type of the output variable

    Notes
    -----
    The `OutputDimensions` objects are created by function 'get_gufunc_info'.
    """

    path: str
    prefix_name: str
    core_dimensions: tuple[str, ...]
    sizes: Mapping[str, int]
    dtype: np.dtype


def get_gufunc_info(data_tree: "xr.DataTree") -> Sequence[OutputDimension]:
    """Extract metadata for the output dimensions used by 'xarray.apply_ufunc'."""
    lst: list[OutputDimension] = []

    sub_data_tree: "xr.DataTree"
    for sub_data_tree in data_tree.subtree:
        if not sub_data_tree.has_data:
            continue

        sub_path: str = sub_data_tree.path.removeprefix("/").replace("/", "_")

        data_name: str
        data_variable: "xr.DataArray"
        for data_name, data_variable in sub_data_tree.data_vars.items():
            output_dimension = OutputDimension(
                path=f"{sub_data_tree.path}/{data_name}",
                prefix_name=sub_path,
                core_dimensions=tuple(
                    [f"{sub_path}_{var_name}" for var_name in data_variable.dims]
                ),
                sizes={
                    f"{sub_path}_{var_name}": var_size
                    for var_name, var_size in sub_data_tree.sizes.items()
                },
                dtype=data_variable.dtype,
            )

            lst.append(output_dimension)

    return lst


def _run_pipelines_array_to_datatree(
    params_tuple: tuple,
    output_filename_suffix: int | str | None,
    *,
    dimension_names: Mapping[str, str],
    processor: Processor,
    readout: Readout,
    outputs: Optional["ObservationOutputs"],
    pipeline_seed: int | None,
    progress_bar,
) -> "xr.DataTree":
    """Execute a single pipeline to generate a DataTree output.

    Parameters
    ----------
    params_tuple
    output_filename_suffix
    dimension_names
    processor
    readout
    outputs
    pipeline_seed
    progress_bar

    Returns
    -------
    DataTree

    Examples
    --------
    >>> _run_pipelines_array_to_datatree(
    ...     params=(
    ...         0.3,  # parameter 'beta'
    ...         (3, 5, 6, 4),  # parameter 'trap_densities'
    ...     ),
    ...     dimension_names={
    ...         "pipeline.charge_transfer.cdm.arguments.beta": "beta",
    ...         "pipeline.charge_transfer.cdm.arguments.trap_densities": "trap_densities",
    ...     },
    ...     processor=Processor(...),
    ...     readout=Readout(...),
    ...     outputs=ObservationOutputs(...),
    ... )
    <xarray.DataTree>
    Group: /
    │   Attributes:
    │       pyxel version:  2.7+73.ge610114e.dirty
    ├── Group: /bucket
    │       Dimensions:  (y: 100, x: 100, time: 1)
    │       Coordinates:
    │         * y        (y) int64 800B 0 1 2 3 4 5 6 7 8 9 ... 91 92 93 94 95 96 97 98 99
    │         * x        (x) int64 800B 0 1 2 3 4 5 6 7 8 9 ... 91 92 93 94 95 96 97 98 99
    │         * time     (time) float64 8B 1.0
    │       Data variables:
    │           photon   (time, y, x) float64 80kB 7.376e+03 7.088e+03 ... 8.056e+03
    │           charge   (time, y, x) float64 80kB 7.376e+03 7.088e+03 ... 8.056e+03
    │           pixel    (time, y, x) float64 80kB 7.376e+03 7.088e+03 ... 8.056e+03
    │           signal   (time, y, x) float64 80kB 0.7376 0.7088 0.6624 ... 0.8056 0.8056
    │           image    (time, y, x) uint16 20kB 4833 4645 4341 4341 ... 5127 5279 5279
    ├── Group: /output
    │   └── Group: /output/image
    │           Dimensions:    (extension: 1)
    │           Coordinates:
    │             * extension  (extension) <U4 16B 'fits'
    │           Data variables:
    │               filename   (extension) StringDType() 16B ...
    ├── Group: /scene
    └── Group: /data
    """
    if len(dimension_names) != len(params_tuple):
        raise NotImplementedError

    # Create a new Processor object with modified parameters from dct
    # e.g. dct = {'pipeline.photon_collection.load_image.arguments.image_file': 'FITS/00001.fits'}
    dct: dict[str, tuple] = dict(zip(dimension_names, params_tuple, strict=False))
    new_processor: Processor = processor.replace(dct)

    # Adjust readout configuration if required
    # TODO: Move this to 'Processor' ? See #836
    new_readout: Readout = readout
    for key, value in dct.items():
        if key.startswith("observation.readout"):
            if key != "observation.readout.times":
                raise NotImplementedError(f"{key=}")

            new_readout = new_readout.replace(times=value)

    # Run a single pipeline with the adjusted configurations
    data_tree: "xr.DataTree" = run_pipeline(
        processor=new_processor,
        readout=new_readout,
        outputs=outputs,
        output_filename_suffix=output_filename_suffix,
        pipeline_seed=pipeline_seed,
        debug=False,  # Debug not supported in Observation mode
        with_inherited_coords=True,  # Ensure inherited coordinates
        progress_bar=progress_bar,
    )

    return data_tree


def _run_pipelines_tuple_to_array(
    params_tuple: tuple,
    output_filename_suffixes: int,
    *,
    dimension_names: Mapping[str, str],
    output_dimensions: Sequence[OutputDimension],
    processor: Processor,
    readout: Readout,
    outputs: Optional["ObservationOutputs"],
    pipeline_seed: int | None,
) -> tuple[np.ndarray, ...]:
    """Execute a single pipeline and generate a tuple of numpy arrays instead of a DataTree."""
    data_tree: "xr.DataTree" = _run_pipelines_array_to_datatree(
        params_tuple=params_tuple,
        dimension_names=dimension_names,
        processor=processor,
        readout=readout,
        outputs=outputs,
        output_filename_suffix=output_filename_suffixes,
        pipeline_seed=pipeline_seed,
        progress_bar=None,
    )

    # Extract numpy arrays from the DataTree
    output_data: list[np.ndarray] = [
        data_tree[output_dim.path].to_numpy() for output_dim in output_dimensions
    ]

    return tuple(output_data)


def _build_data_tree(
    data_array_lst: Sequence["xr.DataArray"],
    output_dimensions: Sequence[OutputDimension],
    output_data_tree_reference: "xr.DataTree",
) -> "xr.DataTree":
    """Build a DataTree from a sequence of DataArrays."""
    # Late import
    import xarray as xr

    final_datatree = xr.DataTree()

    for output_dim, data_array in zip(output_dimensions, data_array_lst, strict=False):
        path: str = output_dim.path

        data_array_reference: xr.DataArray = output_data_tree_reference[path]  # type: ignore[assignment]

        prefix_dim = f"{output_dim.prefix_name}_"

        dims_to_rename: Mapping[str, str] = {
            dim: dim.removeprefix(prefix_dim) for dim in output_dim.core_dimensions
        }
        new_coords: Mapping[str, xr.DataArray] = {
            new_dimension: data_array_reference.coords[new_dimension]
            for new_dimension in dims_to_rename.values()
        }

        new_data_array: xr.DataArray = (
            data_array.rename(dims_to_rename)
            .assign_coords(new_coords)
            .assign_attrs(**data_array_reference.attrs)
        )

        final_datatree[path] = new_data_array
    final_datatree["/"].attrs = output_data_tree_reference["/"].attrs
    return final_datatree


def run_pipelines_with_dask(
    dim_names: Mapping[str, str],
    parameter_mode: ProductMode | SequentialMode | CustomMode,
    processor: Processor,
    readout: Readout,
    outputs: Optional["ObservationOutputs"],
    pipeline_seed: int | None,
) -> "xr.DataTree":
    """Run observation pipelines using Dask for parallelized computation."""
    # Late import to speedup start-up time
    import xarray as xr

    # Generate parameters for the pipelines (as a DataArray)
    params_dataarray: xr.DataArray = parameter_mode.create_params(dim_names=dim_names)

    # Run the pipeline for the first parameter set to extract metadata
    first_param_tuple: tuple = (
        params_dataarray.head(1)  # Get the first parameter
        .squeeze()  # Remove all dimensions of length 1
        .to_numpy()  # Convert to a numpy array
        .tolist()  # Convert to a tuple
    )

    # Extract metadata from 'first_param'
    with TemporaryDirectory() as temp_folder:
        # Late import
        from tqdm.auto import tqdm

        from pyxel.outputs import ObservationOutputs

        # Create new temporary outputs
        temp_outputs: ObservationOutputs | None = None
        if outputs:
            temp_outputs = ObservationOutputs(
                output_folder=temp_folder,
                save_data_to_file=deepcopy(outputs.save_data_to_file),
            )

            temp_outputs.create_output_folder()

        progress_bar = tqdm()

        first_data_tree: xr.DataTree = _run_pipelines_array_to_datatree(
            params_tuple=first_param_tuple,
            output_filename_suffix=None,
            dimension_names=dim_names,
            processor=processor,
            readout=readout,
            outputs=temp_outputs,  # TODO: Create a new temporary outputs only for here
            pipeline_seed=pipeline_seed,
            progress_bar=progress_bar,
        )

    # Extract output dimensions metadata
    output_dimensions: Sequence[OutputDimension] = get_gufunc_info(first_data_tree)

    # Define core dimensions, data types, and sizes for the output
    output_core_dims: Sequence[tuple[str, ...]] = [
        output_dim.core_dimensions for output_dim in output_dimensions
    ]

    output_dtypes: Sequence[np.dtype] = [
        output_dim.dtype for output_dim in output_dimensions
    ]

    output_sizes: Mapping[Hashable, int] = dicttoolz.merge(
        *[output_dim.sizes for output_dim in output_dimensions]
    )

    # Prepare filename suffix indices for outputs
    output_filename_indices: xr.DataArray | None = None
    if outputs:
        # Generate indices for the filename(s)
        output_filename_indices = (
            xr.DataArray(
                np.arange(params_dataarray.size).reshape(params_dataarray.shape),
                dims=params_dataarray.dims,
                coords=params_dataarray.coords,
                name="filename",
            )
            .reset_coords(drop=True)
            .chunk(1)
        )

    # Apply the pipeline function using Dask for parallelization
    dask_dataarrays: tuple[xr.DataArray, ...] = xr.apply_ufunc(
        _run_pipelines_tuple_to_array,  # Function to apply
        params_dataarray.chunk(1),  # Argument 'params_tuple'
        output_filename_indices,  # Argument 'output_filename_suffixes'
        kwargs={  # other arguments
            "dimension_names": dim_names,
            "output_dimensions": output_dimensions,
            "processor": processor,
            "outputs": outputs,
            "readout": readout,
            "pipeline_seed": pipeline_seed,
        },
        input_core_dims=[[], []],
        output_core_dims=output_core_dims,
        vectorize=True,  # loop over non-core dims
        dask="parallelized",
        dask_gufunc_kwargs={"output_sizes": output_sizes},
        output_dtypes=output_dtypes,  # TODO: Move this to 'dask_gufunc_kwargs'
    )

    # Rebuild the DataTree from the Dask DataArrays
    final_datatree: "xr.DataTree" = _build_data_tree(
        data_array_lst=dask_dataarrays,
        output_dimensions=output_dimensions,
        output_data_tree_reference=first_data_tree,
    )

    # Post-process the DataTree to adjust readout time attributes
    if "observation.readout.times" in dim_names:
        # TODO: See #836
        final_datatree["/bucket"] = (
            final_datatree["/bucket"]
            .to_dataset()
            .squeeze("time", drop=True)  # Remove dimension 'time'
            .rename(readout_time="time")  # Rename dimension 'readout' to 'time
        )

        final_datatree["/bucket/time"].attrs = {
            "units": "s",
            "long_name": "Readout time",
        }

    return final_datatree
