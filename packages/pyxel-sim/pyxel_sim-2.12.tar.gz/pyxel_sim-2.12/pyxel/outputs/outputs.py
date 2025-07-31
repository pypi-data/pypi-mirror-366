#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Classes for creating outputs."""

import logging
from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Optional, Union

import numpy as np
from typing_extensions import deprecated

from pyxel import __version__ as version
from pyxel.options import global_options
from pyxel.outputs import SaveToFileProtocol, ValidFormat, apply_run_number
from pyxel.outputs.utils import to_csv, to_fits, to_hdf, to_jpg, to_npy, to_png, to_txt
from pyxel.util import complete_path

if TYPE_CHECKING:
    import pandas as pd
    import xarray as xr
    from astropy.io import fits

    from pyxel.detectors import Detector
    from pyxel.pipelines import Processor


ValidName = Literal[
    "detector.photon.array",
    "detector.charge.array",
    "detector.pixel.array",
    "detector.signal.array",
    "detector.image.array",
]


@deprecated("This will be removed")
def _save_data_2d(
    data_2d: "np.ndarray",
    run_number,
    data_formats: Sequence[ValidFormat],
    current_output_folder: Path,
    name: str,
    prefix: str | None = None,
) -> np.ndarray[Any, np.dtype[np.object_]]:
    save_methods: Mapping[ValidFormat, "SaveToFileProtocol"] = {
        "fits": to_fits,
        "hdf": to_hdf,
        "npy": to_npy,
        "txt": to_txt,
        "csv": to_csv,
        "png": to_png,
        "jpg": to_jpg,
        "jpeg": to_jpg,
    }

    if prefix:
        full_name: str = f"{prefix}_{name}"
    else:
        full_name = name

    filenames: list[str] = []
    for output_format in data_formats:
        func = save_methods[output_format]

        filename = func(
            current_output_folder=current_output_folder,
            data=data_2d,
            name=full_name,
            # with_auto_suffix=with_auto_suffix,
            run_number=run_number,
            # header=header,
        )

        filenames.append(str(filename.relative_to(current_output_folder)))

    return np.array(filenames, dtype=np.object_)


@deprecated("This will be removed")
def save_dataarray(
    data_array: "xr.DataArray",
    name: str,
    full_name: str,
    data_formats: Sequence["ValidFormat"],
    current_output_folder: Path,
) -> "xr.Dataset":
    # Late import
    import numpy as np
    import xarray as xr

    num_elements = int(data_array.isel(y=0, x=0).size)

    if (
        "data_format" in data_array.dims
        or "bucket_name" in data_array.dims
        or "filename" in data_array.dims
    ):
        raise NotImplementedError

    shape_run_number: tuple[int, ...] = tuple(
        {
            dim_name: dim_size
            for dim_name, dim_size in data_array.sizes.items()
            if dim_name not in ("x", "y")
        }.values()
    )

    run_number = np.arange(num_elements, dtype=int).reshape(shape_run_number)
    output_data_array: xr.DataArray = xr.apply_ufunc(
        _save_data_2d,
        data_array.reset_coords(drop=True).rename("filename"),  # parameter 'data_2d'
        run_number,  # parameter 'run_number'
        kwargs={
            "data_formats": data_formats,
            "current_output_folder": current_output_folder,
            "name": full_name,
        },
        input_core_dims=[
            ["y", "x"],  # for parameter 'data_2d'
            [],  # for parameter 'run_number'
        ],
        output_core_dims=[["data_format"]],
        vectorize=True,  # loop over non-core dims
        dask="parallelized",
        dask_gufunc_kwargs={"output_sizes": {"data_format": len(data_formats)}},
        output_dtypes=[np.object_],  # TODO: Move this to 'dask_gufunc_kwargs'
    )

    output_dataset: xr.Dataset = (
        output_data_array.expand_dims("bucket_name")
        .assign_coords(bucket_name=[name], data_format=data_formats)
        .to_dataset()
    )
    return output_dataset


@deprecated("This will be removed")
def _datasets_to_datatree(filenames_ds: list["xr.Dataset"]) -> Optional["xr.DataTree"]:
    import xarray as xr

    if not filenames_ds:
        return None

    first_dataset, *_ = filenames_ds
    dims = [
        dim for dim in first_dataset.dims if dim not in ("bucket_name", "data_format")
    ]

    dct = {"/": first_dataset[dims]}
    for partial_dataset in filenames_ds:
        bucket_name: str = str(partial_dataset["bucket_name"][0].data)

        dct[f"/{bucket_name}"] = partial_dataset.squeeze("bucket_name")

    final_datatree = xr.DataTree.from_dict(dct)

    return final_datatree


@deprecated("This will be removed")
def save_datatree(
    data_tree: "xr.DataTree",
    outputs: Sequence[Mapping[ValidName, Sequence[ValidFormat]]],
    current_output_folder: Path,
    with_inherited_coords: bool,
) -> Optional["xr.DataTree"]:
    """Save output file(s) from a DataTree.

    Parameters
    ----------
    data_tree
    outputs
    current_output_folder
    with_inherited_coords

    Returns
    -------
    Dask DataFrame, optional

    Examples
    --------
    >>> save_datatree(...)
    <xarray.DataTree>
    Group: /
    │   Dimensions:  (id: 6)
    │   Coordinates:
    │     * id       (id) int64 48B 0 1 2 3 4 5
    ├── Group: /image
    │       Dimensions:      (id: 6, data_format: 2)
    │       Coordinates:
    │         * id           (id) int64 48B 0 1 2 3 4 5
    │           bucket_name  <U5 20B 'image'
    │         * data_format  (data_format) <U4 32B 'fits' 'npy'
    │       Data variables:
    │           filename     (id, data_format) object 96B dask.array<chunksize=(1, 2), meta=np.ndarray>
    └── Group: /pixel
            Dimensions:      (id: 6, data_format: 1)
            Coordinates:
              * id           (id) int64 48B 0 1 2 3 4 5
                bucket_name  <U5 20B 'pixel'
              * data_format  (data_format) <U3 12B 'npy'
            Data variables:
                filename     (id, data_format) object 48B dask.array<chunksize=(1, 1), meta=np.ndarray>
    """
    # Late import
    import xarray as xr

    if not outputs:
        raise NotImplementedError

    filenames_ds: list[xr.Dataset] = []

    dct: Mapping["ValidName", Sequence["ValidFormat"]]
    for dct in outputs:
        full_name: "ValidName"
        data_formats: Sequence["ValidFormat"]
        for full_name, data_formats in dct.items():
            name: str = full_name.removeprefix("detector.").removesuffix(".array")

            # Get a node name
            if with_inherited_coords:
                node_name: str = f"/bucket/{name}"
            else:
                node_name = name

            # TODO: Create a function 'has_node' ??
            # Check if 'node_name' exists in 'data_tree'
            try:
                partial_path = "/"
                for partial_node_name in node_name.removeprefix("/").split("/"):
                    if partial_node_name not in data_tree[partial_path]:
                        raise KeyError(
                            f"Cannot find node '{partial_path}/{partial_node_name}'"
                        )

                    partial_path += partial_node_name

            except KeyError:
                logging.exception(
                    "Cannot find node '%s/%s'", partial_path, partial_node_name
                )
                continue

            data_array: xr.DataArray | xr.DataTree = data_tree[node_name]
            if not isinstance(data_array, xr.DataArray):
                raise TypeError

            output_dataframe: xr.Dataset = save_dataarray(
                data_array=data_array,
                name=name,
                full_name=full_name,
                data_formats=data_formats,
                current_output_folder=current_output_folder,
            )

            filenames_ds.append(output_dataframe)

    final_datatree = _datasets_to_datatree(filenames_ds)
    return final_datatree


@deprecated("This will be removed")
def _dict_to_datatree(all_filenames: Mapping[str, Mapping[str, str]]) -> "xr.DataTree":
    import xarray as xr

    datatree_dct = {}

    full_bucket_name: str
    bucket_dct: Mapping[str, str]
    for full_bucket_name, bucket_dct in all_filenames.items():
        bucket_name: str = full_bucket_name.removeprefix("detector.").removesuffix(
            ".array"
        )

        datatree_dct[f"/{bucket_name}"] = (
            xr.concat(
                [
                    xr.DataArray(
                        [filename],
                        dims=["data_format"],
                        coords={"data_format": [data_format]},
                    )
                    for data_format, filename in bucket_dct.items()
                ],
                dim="data_format",
            )
            .rename("filename")
            .to_dataset()
        )

    return xr.DataTree.from_dict(datatree_dct)


# TODO: Create a new class that will contain the parameter 'save_data_to_file'
# TODO: Refactor 'Outputs' with a new class 'ExportData'. See #566
class Outputs:
    """Collection of methods to save the data buckets from a Detector.

    Parameters
    ----------
    output_folder : str or Path
        Folder where sub-folder(s) that will be created to save data buckets.
    custom_dir_name : str, optional
        Prefix of the sub-folder name that will be created in the 'output_folder' folder.
        The default prefix is `run_`.
    save_data_to_file : Dict
        Dictionary where key is a 'data bucket' name (e.g. 'detector.photon.array') and value
        is the data format (e.g. 'fits').

        Example:
        {'detector.photon.array': 'fits', 'detector.charge.array': 'hdf', 'detector.image.array':'png'}

    Examples
    --------
    >>> import pyxel
    >>> config = pyxel.load("my_config.yaml")
    >>> mode = config.running_mode
    >>> detector = config.detector
    >>> pipeline = config.pipeline

    Run and get 'output_dir'

    >>> result = pyxel.run_mode(mode=mode, detector=detector, pipeline=pipeline)
    >>> result.mode.outputs.current_output_folder
    Path('./output/run_20231219_0920000')

    Change 'output_dir'

    >>> result.mode.outputs.output_folder = "folder1/folder2"
    >>> result.mode.outputs.custom_dir_name = "foo_"
    >>> result = pyxel.run_mode(mode=mode, detector=detector, pipeline=pipeline)
    >>> result.mode.outputs.current_output_folder
    Path('./folder1/folder2/foo_20231219_0922000')
    """

    def __init__(
        self,
        output_folder: str | Path,
        custom_dir_name: str = "",
        save_data_to_file: (
            Sequence[Mapping[ValidName, Sequence[ValidFormat]]] | None
        ) = None,
    ):
        self._log = logging.getLogger(__name__)

        self._current_output_folder: Path | None = None

        self._output_folder: Path = Path(output_folder)
        self._custom_dir_name: str = custom_dir_name

        # TODO: Not related to a plot. Use by 'single' and 'parametric' modes.
        if save_data_to_file is None:
            save_data_to_file = [{"detector.image.array": ["fits"]}]

        self.save_data_to_file: (
            Sequence[Mapping[ValidName, Sequence[ValidFormat]]] | None
        ) = save_data_to_file

    def __repr__(self):
        cls_name: str = self.__class__.__name__

        if self._current_output_folder is None:
            return (
                f"{cls_name}<NO OUTPUT DIR, num_files={self.count_files_to_save()!r}>"
            )
        else:
            return f"{cls_name}<output_dir='{self.current_output_folder!s}', num_files={self.count_files_to_save()!r}>"

    def count_files_to_save(self) -> int:
        """Count number of file(s) to be saved."""
        if self.save_data_to_file is None:
            return 0

        num_files = 0
        for dct in self.save_data_to_file:
            for value in dct.values():
                num_files += len(value)

        return num_files

    @property
    def current_output_folder(self) -> Path:
        """Get directory where all outputs are saved."""
        if self._current_output_folder is None:
            raise RuntimeError("'current_output_folder' is not defined.")

        return self._current_output_folder

    @property
    def output_folder(self) -> Path:
        return self._output_folder

    @output_folder.setter
    def output_folder(self, folder: str | Path) -> None:
        if not isinstance(folder, str | Path):
            raise TypeError(
                "Wrong type for parameter 'folder'. Expecting 'str' or 'Path'."
            )

        self._output_folder = Path(folder)

    @property
    def custom_dir_name(self) -> str:
        return self._custom_dir_name

    @custom_dir_name.setter
    def custom_dir_name(self, name: str) -> None:
        if not isinstance(name, str):
            raise TypeError("Wrong type for parameter 'name'. Expecting 'str'.")

        self._custom_dir_name = name

    def create_output_folder(self) -> None:
        """Create the output folder."""
        output_folder: Path = complete_path(
            filename=self._output_folder,
            working_dir=global_options.working_directory,
        ).expanduser()

        self._current_output_folder = create_output_directory(
            output_folder=output_folder,
            custom_dir_name=self._custom_dir_name,
        )

    def build_filenames(
        self,
        filename_suffix: int | str | None = None,
    ) -> Sequence[Path]:
        """Generate a list of output filename(s).

        Examples
        --------
        >>> output = Outputs(
        ...     output_folder="output",
        ...     save_data_to_file=[
        ...         {"detector.photon.array": ["fits", "hdf"]},
        ...         {"detector.charge.array": ["png"]},
        ...     ],
        ... )

        >>> output.build_filenames()
        [Path('detector_photon.fits'), Path('detector_photon.hdf'),  Path('detector_charge.png')]
        """
        if self.save_data_to_file is None:
            raise NotImplementedError

        # Extract filenames
        filenames: list[Path] = []

        file_config: Mapping[ValidName, Sequence[ValidFormat]]
        for file_config in self.save_data_to_file:
            name: str
            formats: Sequence[str]
            for name, formats in file_config.items():
                bucket_name: str = name.removeprefix("detector.").removesuffix(".array")

                for extension in formats:
                    if filename_suffix is None:
                        filename = Path(f"detector_{bucket_name}.{extension}")
                    else:
                        filename = Path(
                            f"detector_{bucket_name}_{filename_suffix}.{extension}"
                        )

                    filenames.append(filename)

        return filenames

    @deprecated("Please use function 'to_fits'.")
    def save_to_fits(
        self,
        data: np.ndarray,
        name: str,
        with_auto_suffix: bool = True,
        run_number: int | None = None,
        header: Optional["fits.Header"] = None,
    ) -> Path:
        """Write array to :term:`FITS` file."""
        name = name.replace(".", "_")

        current_output_folder: Path = complete_path(
            filename=self.current_output_folder,
            working_dir=global_options.working_directory,
        )

        if with_auto_suffix:
            filename = apply_run_number(
                template_filename=current_output_folder.joinpath(f"{name}_?.fits"),
                run_number=run_number,
            )
        else:
            filename = current_output_folder / f"{name}.fits"

        full_filename: Path = filename.resolve()
        self._log.info("Save to FITS - filename: '%s'", full_filename)

        from astropy.io import fits  # Late import to speed-up general import time

        if header is None:
            header = fits.Header()

        header["PYXEL_V"] = (version, "Pyxel version")

        hdu = fits.PrimaryHDU(data, header=header)
        hdu.writeto(full_filename, overwrite=False, output_verify="exception")

        return full_filename

    @deprecated("Please use function 'to_hdf'.")
    def save_to_hdf(
        self,
        data: "Detector",
        name: str,
        with_auto_suffix: bool = True,
        run_number: int | None = None,
    ) -> Path:
        """Write detector object to HDF5 file."""
        # Late import to speedup start-up time
        import h5py as h5

        name = name.replace(".", "_")

        current_output_folder: Path = complete_path(
            filename=self.current_output_folder,
            working_dir=global_options.working_directory,
        )

        if with_auto_suffix:
            filename = apply_run_number(
                template_filename=current_output_folder.joinpath(f"{name}_?.h5"),
                run_number=run_number,
            )
        else:
            filename = current_output_folder / f"{name}.h5"

        full_filename: Path = filename.resolve()

        with h5.File(full_filename, "w") as h5file:
            h5file.attrs["pyxel-version"] = version
            if name == "detector":
                detector_grp = h5file.create_group("detector")
                for array, name in zip(
                    [
                        data.signal.array,
                        data.image.array,
                        data.photon.array,
                        data.pixel.array,
                        data.charge.frame,
                    ],
                    ["Signal", "Image", "Photon", "Pixel", "Charge"],
                    strict=False,
                ):
                    dataset = detector_grp.create_dataset(name, shape=np.shape(array))
                    dataset[:] = array
            else:
                raise NotImplementedError
                # detector_grp = h5file.create_group("data")
                # dataset = detector_grp.create_dataset(name, shape=np.shape(data))
                # dataset[:] = data
        return filename

    @deprecated("Please use function 'to_txt'.")
    def save_to_txt(
        self,
        data: np.ndarray,
        name: str,
        with_auto_suffix: bool = True,
        run_number: int | None = None,
    ) -> Path:
        """Write data to txt file."""
        name = name.replace(".", "_")

        current_output_folder: Path = complete_path(
            filename=self.current_output_folder,
            working_dir=global_options.working_directory,
        )

        if with_auto_suffix:
            filename = apply_run_number(
                template_filename=current_output_folder.joinpath(f"{name}_?.txt"),
                run_number=run_number,
            )
        else:
            filename = current_output_folder / f"{name}.txt"

        full_filename: Path = filename.resolve()
        np.savetxt(full_filename, data, delimiter=" | ", fmt="%.8e")

        return full_filename

    @deprecated("Please use function 'to_csv'")
    def save_to_csv(
        self,
        data: "pd.DataFrame",
        name: str,
        with_auto_suffix: bool = True,
        run_number: int | None = None,
    ) -> Path:
        """Write Pandas Dataframe or Numpy array to a CSV file."""
        name = name.replace(".", "_")

        current_output_folder: Path = complete_path(
            filename=self.current_output_folder,
            working_dir=global_options.working_directory,
        )

        if with_auto_suffix:
            filename = apply_run_number(
                template_filename=current_output_folder.joinpath(f"{name}_?.csv"),
                run_number=run_number,
            )
        else:
            filename = current_output_folder / f"{name}.csv"

        full_filename = filename.resolve()
        try:
            data.to_csv(full_filename, float_format="%g")
        except AttributeError:
            np.savetxt(full_filename, data, delimiter=",", fmt="%.8e")

        return full_filename

    @deprecated("Please use function 'to_npy'.")
    def save_to_npy(
        self,
        data: np.ndarray,
        name: str,
        with_auto_suffix: bool = True,
        run_number: int | None = None,
    ) -> Path:
        """Write Numpy array to Numpy binary npy file."""
        name = name.replace(".", "_")

        current_output_folder: Path = complete_path(
            filename=self.current_output_folder,
            working_dir=global_options.working_directory,
        )

        if with_auto_suffix:
            filename = apply_run_number(
                template_filename=current_output_folder.joinpath(f"{name}_?.npy"),
                run_number=run_number,
            )
        else:
            filename = current_output_folder / f"{name}.npy"

        full_filename: Path = filename.resolve()

        if full_filename.exists():
            raise FileExistsError(f"File {full_filename} already exists!")

        np.save(file=full_filename, arr=data)
        return full_filename

    @deprecated("Please use function 'to_png'.")
    def save_to_png(
        self,
        data: np.ndarray,
        name: str,
        with_auto_suffix: bool = True,
        run_number: int | None = None,
    ) -> Path:
        """Write Numpy array to a PNG image file."""
        # Late import to speedup start-up time
        from PIL import Image

        name = name.replace(".", "_")

        current_output_folder: Path = complete_path(
            filename=self.current_output_folder,
            working_dir=global_options.working_directory,
        )

        if with_auto_suffix:
            filename = apply_run_number(
                template_filename=current_output_folder.joinpath(f"{name}_?.png"),
                run_number=run_number,
            )
        else:
            filename = current_output_folder / f"{name}.png"

        full_filename: Path = filename.resolve()

        if full_filename.exists():
            raise FileExistsError(f"File {full_filename} already exists!")

        im = Image.fromarray(data)
        im.save(full_filename)

        return full_filename

    @deprecated("Please use function 'to_jpg'.")
    def save_to_jpeg(
        self,
        data: np.ndarray,
        name: str,
        with_auto_suffix: bool = True,
        run_number: int | None = None,
    ) -> Path:
        """Write Numpy array to a JPEG image file."""
        # Late import to speedup start-up time
        from PIL import Image

        name = name.replace(".", "_")

        current_output_folder: Path = complete_path(
            filename=self.current_output_folder,
            working_dir=global_options.working_directory,
        )

        if with_auto_suffix:
            filename = apply_run_number(
                template_filename=current_output_folder.joinpath(f"{name}_?.jpeg"),
                run_number=run_number,
            )
        else:
            filename = current_output_folder / f"{name}.jpeg"

        full_filename: Path = filename.resolve()

        if full_filename.exists():
            raise FileExistsError(f"File {full_filename} already exists!")

        im = Image.fromarray(data)
        im.save(full_filename)

        return full_filename

    @deprecated("Please use function 'to_jpg'.")
    def save_to_jpg(
        self,
        data: np.ndarray,
        name: str,
        with_auto_suffix: bool = True,
        run_number: int | None = None,
    ) -> Path:
        """Write Numpy array to a JPG image file."""
        # Late import to speedup start-up time
        from PIL import Image

        name = name.replace(".", "_")

        current_output_folder: Path = complete_path(
            filename=self.current_output_folder,
            working_dir=global_options.working_directory,
        )

        if with_auto_suffix:
            filename = apply_run_number(
                template_filename=current_output_folder.joinpath(f"{name}_?.jpg"),
                run_number=run_number,
            )
        else:
            filename = current_output_folder / f"{name}.jpg"

        full_filename: Path = filename.resolve()

        if full_filename.exists():
            raise FileExistsError(f"File {full_filename} already exists!")

        im = Image.fromarray(data)
        im.save(full_filename)

        return full_filename

    @deprecated("Will be replaced by function 'save_to_files'")
    def save_to_file(
        self,
        processor: "Processor",
        prefix: str | None = None,
        with_auto_suffix: bool = True,
        run_number: int | None = None,
    ) -> "xr.DataTree":
        if not self.save_data_to_file:
            raise NotImplementedError

        save_methods: Mapping[ValidFormat, SaveToFileProtocol] = {
            "fits": to_fits,
            "hdf": to_hdf,
            "npy": to_npy,
            "txt": to_txt,
            "csv": to_csv,
            "png": to_png,
            "jpg": to_jpg,
            "jpeg": to_jpg,
        }

        all_filenames: dict[str, dict[str, str]] = {}

        dct: Mapping[ValidName, Sequence[ValidFormat]]
        for dct in self.save_data_to_file:
            # TODO: Why looking at first entry ? Check this !
            # Get first entry of `dict` 'item'
            first_item: tuple[ValidName, Sequence[ValidFormat]]
            first_item, *_ = dct.items()

            valid_name: ValidName
            format_list: Sequence[ValidFormat]
            valid_name, format_list = first_item

            value: np.ndarray | None = processor.get(valid_name, default=None)
            if value is None:
                continue

            data: np.ndarray = np.array(value)

            if prefix:
                name: str = f"{prefix}_{valid_name}"
            else:
                name = valid_name

            partial_filenames: dict[str, str] = {}
            out_format: ValidFormat
            for out_format in format_list:
                func: SaveToFileProtocol = save_methods[out_format]

                if out_format in ("png", "jpg", "jpeg"):
                    if valid_name != "detector.image.array":
                        raise ValueError(
                            "Cannot save non-digitized data into image formats."
                        )
                    maximum = (
                        2**processor.detector.characteristics.adc_bit_resolution - 1
                    )
                    rescaled_data = (255.0 / maximum * data).astype(np.uint8)

                    filename: Path = func(
                        current_output_folder=self.current_output_folder,
                        data=rescaled_data,
                        name=name,
                        with_auto_suffix=with_auto_suffix,
                        run_number=run_number,
                    )

                elif out_format == "fits":
                    # Create FITS header
                    from astropy.io import fits

                    header = fits.Header()
                    header.update(processor.detector.header)

                    line: str
                    for line in processor.pipeline.describe():
                        header.add_history(line)

                    # previous_header: Optional[fits.Header] = (
                    #     processor.detector._headers.get(valid_name)
                    # )
                    # if previous_header is not None:
                    #     for card in previous_header.cards:
                    #         key, *_ = card
                    #
                    #         if key in ("SIMPLE", "BITPIX") or key.startswith("NAXIS"):
                    #             continue
                    #
                    #         header.append(card)

                    filename = func(
                        current_output_folder=self.current_output_folder,
                        data=data,
                        name=name,
                        with_auto_suffix=with_auto_suffix,
                        run_number=run_number,
                        header=header,
                    )

                else:
                    filename = func(
                        current_output_folder=self.current_output_folder,
                        data=data,
                        name=name,
                        with_auto_suffix=with_auto_suffix,
                        run_number=run_number,
                    )

                partial_filenames[out_format] = filename.name

            all_filenames[valid_name] = partial_filenames

        datatree: "xr.DataTree" = _dict_to_datatree(all_filenames)
        return datatree

    @deprecated("Please use function 'to_netcdf'.")
    def save_to_netcdf(
        self,
        data: Union["xr.Dataset", "xr.DataTree"],
        name: str,
        with_auto_suffix: bool = False,
    ) -> Path:
        """Write Xarray dataset to NetCDF file.

        Parameters
        ----------
        data: Dataset
        name: str

        Returns
        -------
        filename: Path
        """
        name = name.replace(".", "_")
        current_output_folder: Path = complete_path(
            filename=self.current_output_folder,
            working_dir=global_options.working_directory,
        )
        filename = current_output_folder.joinpath(name + ".nc")
        data.to_netcdf(filename, engine="h5netcdf")
        return filename


# TODO: the log file should directly write in 'output_dir'
def save_log_file(output_dir: Path) -> None:
    """Move log file to the outputs directory of the simulation."""
    log_file: Path = Path("pyxel.log").resolve()
    if log_file.exists():
        new_log_filename = output_dir.joinpath("pyxel.log")
        log_file.rename(new_log_filename)


def create_output_directory(
    output_folder: str | Path, custom_dir_name: str | None = None
) -> Path:
    """Create output directory in the output folder.

    Parameters
    ----------
    output_folder: str or Path
    custom_dir_name

    Returns
    -------
    Path
        Output dir.
    """

    add = ""
    count = 0

    date_str: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    if not custom_dir_name:
        prefix_dir: str = "run_"
    else:
        prefix_dir = custom_dir_name

    while True:
        try:
            output_dir: Path = (
                Path(output_folder).joinpath(f"{prefix_dir}{date_str}{add}").resolve()
            )

            output_dir.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            count += 1
            add = "_" + str(count)
            continue

        else:
            return output_dir
