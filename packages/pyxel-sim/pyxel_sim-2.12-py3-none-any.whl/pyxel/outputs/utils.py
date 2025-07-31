#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""General purpose functions to save data."""

import logging
import re
from collections import defaultdict
from collections.abc import Mapping, Sequence
from glob import glob
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Optional, Protocol

import numpy as np

from pyxel import __version__ as version
from pyxel.options import global_options
from pyxel.util import complete_path

if TYPE_CHECKING:
    import xarray as xr
    from astropy.io import fits

    from pyxel.pipelines import Processor


class SaveToFileProtocol(Protocol):
    """Protocol defining a callable to save data into a file."""

    def __call__(
        self,
        current_output_folder: Path,
        data: Any,
        name: str,
        with_auto_suffix: bool = True,
        run_number: int | None = None,
        header: Mapping | None = None,
    ) -> Path: ...


ValidFormat = Literal["fits", "hdf", "npy", "txt", "csv", "png", "jpg", "jpeg"]


# TODO: Refactor this in 'def apply_run_number(folder, template_filename) -> Path'.
#       See #332.
def apply_run_number(template_filename: Path, run_number: int | None = None) -> Path:
    """Convert the file name numeric placeholder to a unique number.

    Parameters
    ----------
    template_filename
    run_number

    Returns
    -------
    output_path: Path
    """
    template_str = str(template_filename)

    def get_number(string: str) -> int:
        search = re.search(r"\d+$", string.split(".")[-2])
        if not search:
            return 0

        return int(search.group())

    if "?" in template_str:
        if run_number is not None:
            path_str = template_str.replace("?", "{}")
            output_str = path_str.format(run_number + 1)
        else:
            path_str_for_glob = template_str.replace("?", "*")
            dir_list = glob(path_str_for_glob)
            num_list: list[int] = sorted(get_number(d) for d in dir_list)
            if num_list:
                next_num = num_list[-1] + 1
            else:
                next_num = 1
            path_str = template_str.replace("?", "{}")
            output_str = path_str.format(next_num)

    output_path = Path(output_str)

    return output_path


def write_to_fits(
    filename: Path,
    data: np.ndarray,
    header: Optional["fits.Header"],
    overwrite: bool,
) -> None:
    """Write a 2D numpy array to a FITS file.

    Parameters
    ----------
    filename : Path
        Output filename.
    data  : np.ndarray
        The 2D array to write in the file.
    header : fits.Header, Optional.
        The FITS header to include in the file.
    overwrite : bool
        If True, overwrite the existing file if it exists

    Returns
    -------
    ValueError
        If the input data is not a 2D array
    """
    # Check if the file exists
    if filename.exists() and not overwrite:
        logging.info("File exists and overwrite is set to False")
        return

    # Ensure the data is a 2D array
    if data.ndim != 2:
        raise ValueError(f"Only 2D data arrays are supported. {data.shape=}")

    logging.info("Save to FITS - filename: '%s'", filename)

    from astropy.io import fits  # Late import to speed-up general import time

    # Create a default header if none is provided
    if header is None:
        header = fits.Header()

    header["PYXEL_V"] = (version, "Pyxel version")

    try:
        fits.writeto(
            filename=filename,
            data=data,
            header=header,
            output_verify="exception",
            overwrite=False,
        )
    except Exception as exc:
        raise OSError(f"Failed to write FITS file: '{filename}'") from exc


def write_to_jpg(
    filename: Path,
    data: np.ndarray,
    overwrite: bool,
) -> None:
    """Write a 2D numpy array to a JPG file.

    Parameters
    ----------
    filename : Path
        Output filename.
    data  : np.ndarray
        The 2D array to write in the file.
    overwrite : bool
        If True, overwrite the existing file if it exists

    Returns
    -------
    ValueError
        If the input data is not a 2D array
    """
    # Check if the file exists
    if filename.exists() and not overwrite:
        logging.info("File exists and overwrite is set to False")
        return

    # Ensure the data is a 2D array
    if data.ndim != 2:
        raise ValueError(f"Only 2D data arrays are supported. {data.shape=}")

    # Late import to speedup start-up time
    from astropy.visualization import ZScaleInterval
    from PIL import Image

    zscale = ZScaleInterval()

    rescaled_data = (255 * zscale(data)).astype(np.uint8)

    try:
        img = Image.fromarray(rescaled_data)
        img.save(filename)
    except Exception as exc:
        raise OSError(f"Failed to write JPG file: '{filename}'") from exc


def write_to_npy(
    filename: Path,
    data: np.ndarray,
    overwrite: bool,
) -> None:
    """Write a 2D numpy array to a NPY file.

    Parameters
    ----------
    filename : Path
        Output filename.
    data  : np.ndarray
        The 2D array to write in the file.
    overwrite : bool
        If True, overwrite the existing file if it exists

    Returns
    -------
    ValueError
        If the input data is not a 2D array
    """
    # Check if the file exists
    if filename.exists() and not overwrite:
        logging.info("File exists and overwrite is set to False")
        return

    # Ensure the data is a 2D array
    if data.ndim != 2:
        raise ValueError(f"Only 2D data arrays are supported. {data.shape=}")

    np.save(filename, arr=data)


def save_to_files(
    folder: Path,
    processor: "Processor",
    filenames: Sequence[str | Path],
    header: Optional["fits.Header"],
    overwrite: bool = False,
) -> "xr.DataTree":
    """Save processed data to files in specified formats.

    Parameters
    ----------
    folder : Path
    processor : Processor
        The processor object used to retrieve the data buckets.
    filenames : Sequence of str
        List of filenames specifying where the data should be saved.
    header : fits.Header, Optional.
        Header to include when saving files (not specific for FITS files)
    overwrite : bool, default: False
        If True, existing files with the same name will be overwritten.

    Examples
    --------
    >>> save_to_files(
    ...     folder=Path("./output/run_20250109_174315"),
    ...     processor=...,
    ...     filenames=[
    ...         "detector_image.fits",
    ...         "detector_image.jpg",
    ...         "detector_pixel.npy",
    ...     ],
    ... )
    <xarray.DataTree>
    Group: /
    ├── Group: /image
    │       Dimensions:    (extension: 2)
    │       Coordinates:
    │         * extension  (extension) <U4 32B 'fits' 'jpg'
    │       Data variables:
    │           filename   (extension) StringDType() 32B ...
    └── Group: /pixel
            Dimensions:    (extension: 1)
            Coordinates:
              * extension  (extension) <U3 12B 'npy'
            Data variables:
                filename   (extension) StringDType() 16B ...
    """
    # Late import
    import xarray as xr

    dct: Mapping[str, list[xr.DataArray]] = defaultdict(list)

    for filename in filenames:
        full_filename: Path = folder.joinpath(filename).resolve()

        first_arg, bucket_name, *_ = full_filename.stem.split("_")
        valid_name = f"{first_arg}.{bucket_name}"

        # Retrieve data from the processor.
        data_2d = processor.get(valid_name, default=None)
        if data_2d is None:
            raise NotImplementedError(f"Unknown {valid_name=}")

        if data_2d._array is None:
            # TODO: Improve error message
            raise ValueError(f"Bucket {data_2d=} is uninitialized !")

        # Save data to the appropriate format
        extension: str = full_filename.suffix.removeprefix(".")

        match extension:
            case "fits":
                write_to_fits(
                    filename=full_filename,
                    data=np.asarray(data_2d),
                    header=header,
                    overwrite=overwrite,
                )

            case "npy":
                write_to_npy(
                    filename=full_filename,
                    data=np.asarray(data_2d),
                    overwrite=overwrite,
                )

            case "hdf" | "txt" | "csv" | "png":
                raise NotImplementedError(
                    f"Saving to '{full_filename.suffix}' is not yet implemented."
                )

            case "jpg" | "jpeg":
                write_to_jpg(
                    filename=full_filename,
                    data=np.asarray(data_2d),
                    overwrite=overwrite,
                )

            case _:
                raise NotImplementedError(
                    f"Unsupported file format: '{full_filename.suffix}'."
                )

        filename_dataarray = xr.DataArray(
            str(full_filename), coords={"extension": extension}
        )

        dct[bucket_name].append(filename_dataarray)

    if np.__version__ >= "2":
        dtype = np.dtypes.StringDType()  # type: ignore[attr-defined,unused-ignore]
    else:
        dtype = np.object_  # type: ignore[assignment,unused-ignore]

    dct_datasets: Mapping[str, xr.Dataset] = {
        key: xr.concat(value, dim="extension").astype(dtype).to_dataset(name="filename")
        for key, value in dct.items()
    }

    return xr.DataTree.from_dict(dct_datasets)


def to_fits(
    current_output_folder: Path,
    data: Any,
    name: str,
    with_auto_suffix: bool = True,
    run_number: int | None = None,
    header: Optional["fits.Header"] = None,
) -> Path:
    """Write array to :term:`FITS` file."""
    if not isinstance(data, np.ndarray):
        raise TypeError

    name = name.replace(".", "_")

    full_output_folder: Path = complete_path(
        filename=current_output_folder,
        working_dir=global_options.working_directory,
    )

    if with_auto_suffix:
        filename = apply_run_number(
            template_filename=full_output_folder.joinpath(f"{name}_?.fits"),
            run_number=run_number,
        )
    else:
        filename = full_output_folder / f"{name}.fits"

    full_filename: Path = filename.resolve()
    logging.info("Save to FITS - filename: '%s'", full_filename)

    from astropy.io import fits  # Late import to speed-up general import time

    if header is None:
        header = fits.Header()

    header["PYXEL_V"] = (version, "Pyxel version")

    hdu = fits.PrimaryHDU(data, header=header)
    hdu.writeto(full_filename, overwrite=False, output_verify="exception")

    return full_filename


def to_hdf(
    current_output_folder: Path,
    data: Any,
    name: str,
    with_auto_suffix: bool = True,
    run_number: int | None = None,
    header: Mapping | None = None,
) -> Path:
    """Write detector object to HDF5 file."""
    # Late import to speedup start-up time
    import h5py as h5

    from pyxel.detectors import Detector

    if not isinstance(data, Detector):
        raise TypeError

    name = name.replace(".", "_")

    full_output_folder: Path = complete_path(
        filename=current_output_folder,
        working_dir=global_options.working_directory,
    )

    if with_auto_suffix:
        filename = apply_run_number(
            template_filename=full_output_folder.joinpath(f"{name}_?.h5"),
            run_number=run_number,
        )
    else:
        filename = full_output_folder / f"{name}.h5"

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


def to_npy(
    current_output_folder: Path,
    data: Any,
    name: str,
    with_auto_suffix: bool = True,
    run_number: int | None = None,
    header: Mapping | None = None,
) -> Path:
    """Write Numpy array to Numpy binary npy file."""
    if not isinstance(data, np.ndarray):
        raise TypeError

    name = name.replace(".", "_")

    full_output_folder: Path = complete_path(
        filename=current_output_folder,
        working_dir=global_options.working_directory,
    )

    if with_auto_suffix:
        filename = apply_run_number(
            template_filename=full_output_folder.joinpath(f"{name}_?.npy"),
            run_number=run_number,
        )
    else:
        filename = full_output_folder / f"{name}.npy"

    full_filename: Path = filename.resolve()

    if full_filename.exists():
        raise FileExistsError(f"File {full_filename} already exists!")

    np.save(file=full_filename, arr=data)
    return full_filename


def to_txt(
    current_output_folder: Path,
    data: Any,
    name: str,
    with_auto_suffix: bool = True,
    run_number: int | None = None,
    header: Mapping | None = None,
) -> Path:
    """Write data to txt file."""
    if not isinstance(data, np.ndarray):
        raise TypeError

    name = name.replace(".", "_")

    full_output_folder: Path = complete_path(
        filename=current_output_folder,
        working_dir=global_options.working_directory,
    )

    if with_auto_suffix:
        filename = apply_run_number(
            template_filename=full_output_folder.joinpath(f"{name}_?.txt"),
            run_number=run_number,
        )
    else:
        filename = full_output_folder / f"{name}.txt"

    full_filename: Path = filename.resolve()
    np.savetxt(full_filename, data, delimiter=" | ", fmt="%.8e")

    return full_filename


def to_csv(
    current_output_folder: Path,
    data: Any,
    name: str,
    with_auto_suffix: bool = True,
    run_number: int | None = None,
    header: Mapping | None = None,
) -> Path:
    """Write Pandas Dataframe or Numpy array to a CSV file."""
    # Late import
    import pandas as pd

    if not isinstance(data, pd.DataFrame):
        raise TypeError

    name = name.replace(".", "_")

    full_output_folder: Path = complete_path(
        filename=current_output_folder,
        working_dir=global_options.working_directory,
    )

    if with_auto_suffix:
        filename = apply_run_number(
            template_filename=full_output_folder.joinpath(f"{name}_?.csv"),
            run_number=run_number,
        )
    else:
        filename = full_output_folder / f"{name}.csv"

    full_filename = filename.resolve()
    try:
        data.to_csv(full_filename, float_format="%g")
    except AttributeError:
        np.savetxt(full_filename, data, delimiter=",", fmt="%.8e")

    return full_filename


def to_png(
    current_output_folder: Path,
    data: Any,
    name: str,
    with_auto_suffix: bool = True,
    run_number: int | None = None,
    header: Mapping | None = None,
) -> Path:
    """Write Numpy array to a PNG image file."""
    if not isinstance(data, np.ndarray):
        raise TypeError

    # Late import to speedup start-up time
    from PIL import Image

    name = name.replace(".", "_")

    full_output_folder: Path = complete_path(
        filename=current_output_folder,
        working_dir=global_options.working_directory,
    )

    if with_auto_suffix:
        filename = apply_run_number(
            template_filename=full_output_folder.joinpath(f"{name}_?.png"),
            run_number=run_number,
        )
    else:
        filename = full_output_folder / f"{name}.png"

    full_filename: Path = filename.resolve()

    if full_filename.exists():
        raise FileExistsError(f"File {full_filename} already exists!")

    im = Image.fromarray(data)
    im.save(full_filename)

    return full_filename


def to_jpg(
    current_output_folder: Path,
    data: Any,
    name: str,
    with_auto_suffix: bool = True,
    run_number: int | None = None,
    header: Mapping | None = None,
) -> Path:
    """Write Numpy array to a JPG image file."""
    if not isinstance(data, np.ndarray):
        raise TypeError

    # Late import to speedup start-up time
    from PIL import Image

    name = name.replace(".", "_")

    full_output_folder: Path = complete_path(
        filename=current_output_folder,
        working_dir=global_options.working_directory,
    )

    if with_auto_suffix:
        filename = apply_run_number(
            template_filename=full_output_folder.joinpath(f"{name}_?.jpg"),
            run_number=run_number,
        )
    else:
        filename = full_output_folder / f"{name}.jpg"

    full_filename: Path = filename.resolve()

    if full_filename.exists():
        raise FileExistsError(f"File {full_filename} already exists!")

    im = Image.fromarray(data)
    im.save(full_filename)

    return full_filename


def to_netcdf(
    current_output_folder: Path,
    data: Any,
    name: str,
    with_auto_suffix: bool = False,
    run_number: int | None = None,
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
    # Late import
    import xarray as xr

    if not isinstance(data, xr.Dataset | xr.DataTree):
        raise TypeError

    name = name.replace(".", "_")
    full_output_folder: Path = complete_path(
        filename=current_output_folder,
        working_dir=global_options.working_directory,
    )
    filename = full_output_folder.joinpath(name + ".nc")
    data.to_netcdf(filename, engine="h5netcdf")
    return filename


def to_file(
    out_format: ValidFormat,
    current_output_folder: Path,
    data: Any,
    name: str,
    with_auto_suffix: bool = False,
    run_number: int | None = None,
) -> Path:
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

    func: SaveToFileProtocol = save_methods[out_format]

    filename = func(
        current_output_folder=current_output_folder,
        data=data,
        name=name,
        with_auto_suffix=with_auto_suffix,
        run_number=run_number,
        # header=header,
    )

    return filename
