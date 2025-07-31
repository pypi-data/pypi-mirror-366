#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Subpackage to load images and tables."""

import csv
import sys
from collections.abc import Sequence
from contextlib import suppress
from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import numpy as np
from numpy.typing import DTypeLike

from pyxel.options import global_options
from pyxel.util import resolve_with_working_directory

if TYPE_CHECKING:
    import pandas as pd
    import xarray as xr
    from astropy.io import fits


def resolve_path(filename: Path) -> str:
    """Resolve the given path."""
    full_filename: Path = filename.expanduser().resolve()
    if not full_filename.exists():
        raise FileNotFoundError(f"Input file '{full_filename}' can not be found.")

    return str(full_filename)


def prepare_cache_path(url_path: str) -> tuple[str, dict]:
    """Prepare and return the cache path and fsspec's configuration extra."""
    extras = {}
    if global_options.cache_enabled:
        url_path = f"simplecache::{url_path}"

        if global_options.cache_folder:
            extras["simplecache"] = {"cache_storage": global_options.cache_folder}

    return url_path, extras


def load_header(
    filename: str | Path,
    section: int | str | None = None,
) -> Optional["fits.Header"]:
    """Load and return header information from a file.

    Parameters
    ----------
    filename : str or Path,
        Path to the file from which to load the header.
    section : int, str or None, optional
        Specifies the section of the file to extract the header.

    Returns
    -------
    dict or None
        A dictionary containing header information

    Examples
    --------
    >>> load_header("image.fits", section="RAW")
    CRPIX1  =      1024.6657050959 / Pixel coordinate of reference point
    CRPIX2  =      1024.6657050959 / Pixel coordinate of reference point
    PC1_1   =                 -1.0 / Coordinate transformation matrix element
    """
    # Late import to speedup start-up time
    from astropy.io import fits

    try:
        filename = resolve_with_working_directory(filename)
        # Extract suffix (e.g. '.txt', '.fits'...)
        suffix: str = Path(filename).suffix.lower()

        if isinstance(filename, Path):
            url_path: str = resolve_path(filename)
        else:
            url_path = filename

        # Define extra parameters to use with 'fsspec'
        url_path, extras = prepare_cache_path(url_path)

        if suffix.startswith(".fits"):
            match section:
                case int():
                    header = fits.getheader(
                        url_path, ext=section, use_fsspec=True, fsspec_kwargsdict=extras
                    )

                case str():
                    header = fits.getheader(
                        url_path,
                        extname=section,
                        use_fsspec=True,
                        fsspec_kwargsdict=extras,
                    )

                case _:
                    header = fits.getheader(
                        url_path, use_fsspec=True, fsspec_kwargsdict=extras
                    )

            keys_to_remove = [
                key
                for key in header
                if key in {"SIMPLE", "BITPIX"} or key.startswith("NAXIS")
            ]
            new_header = fits.Header(header)
            for key in keys_to_remove:
                del new_header[key]

            return new_header

        else:
            # Unknown type
            return None

    except Exception as exc:
        if sys.version_info >= (3, 11):
            exc.add_note(
                f"Raised when trying to load file '{filename}' and "
                f"{global_options.working_directory=}"
            )
        raise


def load_image(filename: str | Path) -> np.ndarray:
    """Load a 2D image.

    Parameters
    ----------
    filename : str or Path
        Filename to read an image.
        {.npy, .fits, .txt, .data, .jpg, .jpeg, .bmp, .png, .tiff} are accepted.

    Returns
    -------
    ndarray
        A 2D array.

    Raises
    ------
    FileNotFoundError
        If an image is not found.
    ValueError
        When the extension of the filename is unknown or separator is not found.

    Examples
    --------
    >>> from pyxel import load_image
    >>> load_image("frame.fits")
    array([[-0.66328494, -0.63205819, ...]])

    >>> load_image("https://hostname/folder/frame.fits")
    array([[-0.66328494, -0.63205819, ...]])

    >>> load_image("another_frame.npy")
    array([[-1.10136521, -0.93890239, ...]])

    >>> load_image("rgb_frame.jpg")
    array([[234, 211, ...]])
    """
    # Late import to speedup start-up time
    import fsspec

    try:
        filename = resolve_with_working_directory(filename=filename)
        # Extract suffix (e.g. '.txt', '.fits'...)
        suffix: str = Path(filename).suffix.lower()

        if isinstance(filename, Path):
            url_path: str = resolve_path(filename)
        else:
            url_path = filename

        # Define extra parameters to use with 'fsspec'
        url_path, extras = prepare_cache_path(url_path)

        if suffix.startswith(".fits"):
            # Late import to speed-up general import time
            from astropy.io import fits

            data_2d: np.ndarray = fits.getdata(
                url_path, use_fsspec=True, fsspec_kwargs=extras
            )

        elif suffix.startswith(".npy"):
            with fsspec.open(url_path, mode="rb", **extras) as file_handler:
                data_2d = np.load(file_handler)

        elif suffix.startswith((".txt", ".data")):
            for sep in ("\t", " ", ",", "|", ";"):
                with suppress(ValueError):
                    with fsspec.open(url_path, mode="r", **extras) as file_handler:
                        data_2d = np.loadtxt(file_handler, delimiter=sep, ndmin=2)
                    break
            else:
                raise ValueError(
                    f"Cannot find the separator for filename '{url_path}'."
                )

        elif suffix.startswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif")):
            with fsspec.open(url_path, mode="rb", **extras) as file_handler:
                # Late import to speedup start-up time
                from PIL import Image

                image_2d = Image.open(file_handler)
                image_2d_converted = image_2d.convert(
                    "LA"
                )  # RGB to grayscale conversion

            data_2d = np.array(image_2d_converted)[:, :, 0]

        else:
            raise ValueError(
                "Image format not supported. List of supported image formats: "
                ".npy, .fits, .txt, .data, .jpg, .jpeg, .bmp, .png, .tiff, .tif."
            )
    except Exception as exc:
        if sys.version_info >= (3, 11):
            exc.add_note(
                f"Raised when trying to load file '{filename}' and "
                f"{global_options.working_directory=}"
            )
        raise

    return data_2d


# TODO: needs tests!
# TODO: add units
# TODO: reduce complexity and remove ruff noqa.
# ruff: noqa: PTH123
def load_image_v2(
    filename: str | Path,
    rename_dims: dict,
    data_path: str | int | None = None,
) -> "xr.DataArray":
    # Late import to speedup start-up time
    import xarray as xr

    filename = resolve_with_working_directory(filename=filename)
    # Extract suffix (e.g. '.txt', '.fits'...)
    suffix: str = Path(filename).suffix.lower()

    if isinstance(filename, Path):
        url_path: str = resolve_path(filename)
    else:
        url_path = filename

    if suffix.startswith(".fits"):
        from astropy.io import fits

        with fits.open(url_path) as hdus:
            if data_path is None:
                data_path = 0
            assert isinstance(data_path, int)
            image_data: np.ndarray = hdus[data_path].data
            # TODO: check if hdus data_path is image hdu.
            if image_data.ndim == 2:
                data_array = xr.DataArray(image_data, dims=["y", "x"])
            elif image_data.ndim == 3:
                da_array = xr.DataArray(image_data)
                col_new = {value: key for key, value in rename_dims.items()}
                data_array = da_array.rename(col_new)
            else:
                raise NotImplementedError()

    elif suffix.startswith(".npy"):
        with open(url_path, mode="rb") as file_handler:
            data_2d: np.ndarray = np.load(file_handler)
            assert data_2d.ndim == 2
            data_array = xr.DataArray(data_2d, dims=["y", "x"])

    elif suffix.startswith((".txt", ".data")):
        for sep in ("\t", " ", ",", "|", ";"):
            with suppress(ValueError):
                with open(url_path) as file_handler:
                    data_2d = np.loadtxt(file_handler, delimiter=sep, ndmin=2)
                break

        else:
            raise ValueError(f"Cannot find the separator for filename '{url_path}'.")
        data_array = xr.DataArray(data_2d, dims=["y", "x"])

    elif suffix.startswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif")):
        with open(url_path, mode="rb") as file_handler:
            # Late import to speedup start-up time
            from PIL import Image

            image_2d = Image.open(file_handler)
            image_2d_converted = image_2d.convert("LA")  # RGB to grayscale conversion
            data_array = xr.DataArray(image_2d_converted, dims=["y", "x"])

    return data_array


def load_table(
    filename: str | Path,
    header: bool = False,
    dtype: DTypeLike = "float",
) -> "pd.DataFrame":
    """Load a table from a file and returns a pandas dataframe. No header is expected in xlsx.

    Parameters
    ----------
    filename : str or Path
        Filename to read the table.
        {.npy, .xlsx, .csv, .txt., .data} are accepted.
    header : bool, default: False
        Remove the header.
    dtype

    Returns
    -------
    DataFrame

    Raises
    ------
    FileNotFoundError
        If an image is not found.
    ValueError
        When the extension of the filename is unknown or separator is not found.
    """
    # Late import to speedup start-up time
    import fsspec
    import pandas as pd

    resolved_filename = resolve_with_working_directory(filename=filename)
    suffix: str = Path(resolved_filename).suffix.lower()

    if isinstance(resolved_filename, Path):
        url_path: str = resolve_path(resolved_filename)
    else:
        url_path = resolved_filename

    # Define extra parameters to use with 'fsspec'
    url_path, extras = prepare_cache_path(url_path)

    if suffix.startswith(".npy"):
        with fsspec.open(url_path, mode="rb", **extras) as file_handler:
            table = pd.DataFrame(np.load(file_handler), dtype=dtype)

    elif suffix.startswith(".xlsx"):
        with fsspec.open(url_path, mode="rb", **extras) as file_handler:
            table = pd.read_excel(
                file_handler,
                header=0 if header else None,
                dtype=float,
            )

    elif suffix.startswith((".txt", ".data", ".csv")):
        # Read file
        with fsspec.open(url_path, mode="r", **extras) as file_handler:
            data: str = file_handler.read()

        valid_delimiters: Sequence[str] = ("\t", " ", ",", "|", ";")
        valid_delimiters_str = "".join(valid_delimiters)

        # Find a delimiter
        try:
            dialect = csv.Sniffer().sniff(data, delimiters=valid_delimiters_str)
        except csv.Error:
            delimiter: str | None = None
        else:
            delimiter = dialect.delimiter

            if delimiter not in valid_delimiters:
                raise ValueError(f"Cannot find the separator. {delimiter=!r}")

        with StringIO(data) as file_handler:
            try:
                if suffix.startswith(".csv"):
                    table = pd.read_csv(
                        file_handler,
                        delimiter=delimiter,
                        header=0 if header else None,
                        dtype=dtype,
                    )
                else:
                    table = pd.read_table(
                        file_handler,
                        delimiter=delimiter,
                        header=0 if header else None,
                        dtype=dtype,
                    )
            except ValueError as exc:
                if delimiter is None:
                    raise ValueError(
                        f"Cannot find the separator. {delimiter=!r}"
                    ) from exc

                raise

    elif suffix.startswith(".fits"):
        from astropy.table import Table

        table = Table.read(url_path).to_pandas()

    else:
        raise ValueError("Only .npy, .xlsx, .csv, .txt and .data implemented.")

    return table


# TODO: needs tests!
# TODO: add units
def load_table_v2(
    filename: str | Path,
    rename_cols: dict | None = None,
    data_path: str | int | None = None,
    header: bool = False,
) -> "pd.DataFrame":
    # Late import to speedup start-up time
    import pandas as pd

    filename = resolve_with_working_directory(filename=filename)
    suffix: str = Path(filename).suffix.lower()

    if isinstance(filename, Path):
        url_path: str = resolve_path(filename)
    else:
        url_path = filename

    if suffix.startswith(".fits"):
        from astropy.table import Table

        # with fits.open(url_path) as hdus:
        #     if data_path is None:
        #         data_path = 0
        #     assert isinstance(data_path, int)
        #     assert isinstance(hdus[data_path], (fits.TableHDU, fits.BinTableHDU))
        table: pd.DataFrame = Table.read(url_path, hdu=data_path).to_pandas()
        if rename_cols:
            col_new = {value: key for key, value in rename_cols.items()}
            table_data = table.rename(columns=col_new)[list(rename_cols)]
        else:
            table_data = table

    elif suffix.startswith(".npy"):
        with open(url_path, mode="rb") as file_handler:
            table = pd.DataFrame(np.load(file_handler))
            if rename_cols:
                dims = []
                for ax in range(len(table.columns)):
                    for key, value in rename_cols.items():
                        if value == ax:
                            dims.append(key)
                            break
                    else:
                        raise KeyError(f"Missing columns. {rename_cols=}")

                table.columns = dims
                table_data = table.copy()
            else:
                table_data = table

    elif suffix.startswith((".txt", ".data", ".csv")):
        with open(url_path) as file_handler:
            data: str = file_handler.read()
        valid_delimiters: Sequence[str] = ("\t", " ", ",", "|", ";")
        valid_delimiters_str = "".join(valid_delimiters)

        # Find a delimiter
        try:
            dialect = csv.Sniffer().sniff(data, delimiters=valid_delimiters_str)
        except csv.Error as exc:
            raise ValueError("Cannot find the separator") from exc

        delimiter: str = dialect.delimiter

        if delimiter not in valid_delimiters:
            raise ValueError(f"Cannot find the separator. {delimiter=!r}")

        with StringIO(data) as file_handler:
            if suffix.startswith(".csv"):
                table = pd.read_csv(
                    file_handler,
                    delimiter=delimiter,
                    header=0 if header else None,
                    usecols=rename_cols.values() if rename_cols else None,
                )
            else:
                table = pd.read_table(
                    file_handler,
                    delimiter=delimiter,
                    header=0 if header else None,
                    usecols=rename_cols.values() if rename_cols else None,
                )
            if rename_cols:
                col_new = {value: key for key, value in rename_cols.items()}
                table_data = table.rename(columns=col_new)
            else:
                table_data = table
    else:
        raise NotImplementedError

    return table_data


def load_dataarray(filename: str | Path) -> "xr.DataArray":
    """Load a ``DataArray`` image.

    Parameters
    ----------
    filename : str of Path

    Returns
    -------
    DataArray
        A multi-dimensional array.

    Raises
    ------
    FileNotFoundError
        If an image is not found.
    """
    # Late import to speedup start-up time
    import fsspec
    import xarray as xr

    filename = resolve_with_working_directory(filename=filename)
    if isinstance(filename, Path):
        url_path: str = resolve_path(filename)
    else:
        url_path = filename

    # Define extra parameters to use with 'fsspec'
    url_path, extras = prepare_cache_path(url_path)

    with fsspec.open(url_path, mode="rb", **extras) as file_handler:
        data_array = xr.load_dataarray(file_handler)

    return data_array


def load_datacube(filename: str | Path) -> np.ndarray:
    """Load a 3D datacube.

    Parameters
    ----------
    filename : str or Path
        Filename to read a datacube.
        {.npy} are accepted.

    Returns
    -------
    array : ndarray
        A 3D array.

    Raises
    ------
    FileNotFoundError
        If an image is not found.
    ValueError
        When the extension of the filename is unknown or separator is not found.
    """
    # Late import to speedup start-up time
    import fsspec

    filename = resolve_with_working_directory(filename=filename)
    # Extract suffix (e.g. '.txt', '.fits'...)
    suffix: str = Path(filename).suffix.lower()

    if isinstance(filename, Path):
        url_path: str = resolve_path(filename)
    else:
        url_path = filename

    # Define extra parameters to use with 'fsspec'
    url_path, extras = prepare_cache_path(url_path)

    if suffix.startswith(".npy"):
        with fsspec.open(url_path, mode="rb", **extras) as file_handler:
            data_3d: np.ndarray = np.load(file_handler)
        if np.ndim(data_3d) != 3:
            raise ValueError("Input datacube is not 3-dimensional!")

    else:
        raise ValueError(
            "Image format not supported. List of supported image formats: .npy"
        )

    return data_3d
