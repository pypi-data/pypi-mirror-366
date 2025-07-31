#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""

from collections.abc import Mapping, MutableSequence, Sequence
from dataclasses import dataclass
from enum import Enum
from numbers import Integral, Real
from pathlib import Path
from typing import Any, NamedTuple

import numpy as np
import pandas as pd
import xarray as xr

from pyxel import load_datacube, load_image

#  from pyxel.pipelines import Processor
__all__ = [
    "CalibrationMode",
    "CalibrationResult",
    "FitRange2D",
    "FitRange3D",
    "Island",
    "check_fit_ranges",
    "check_ranges",
    "create_processor_data_array",
    "list_to_3d_slice",
    "list_to_slice",
    "read_data",
    "read_datacubes",
    "sanitize",
    "to_fit_range",
]


class CalibrationResult(NamedTuple):
    """Result class for calibration class."""

    dataset: xr.Dataset
    processors: pd.DataFrame
    logs: pd.DataFrame
    filenames: Sequence


# TODO: 'SingleModel' is never used. Remove this class ?
class CalibrationMode(Enum):
    """Enumeration for different modes of Calibration."""

    Pipeline = "pipeline"
    SingleModel = "single_model"  # TODO: This is never used


class Island(Enum):
    """User defines num_islands provides by Pygmo."""

    MultiProcessing = "multiprocessing"
    MultiThreading = "multithreading"
    IPyParallel = "ipyparallel"


def read_single_data(filename: Path) -> np.ndarray:
    """Read a numpy array from a FITS or NPY file."""
    # Late import to avoid circular import

    data = load_image(filename)

    # # TODO: Is it the right manner ?
    # if data is None:
    #     raise OSError(f"Input file '{filename}' can not be read by Pyxel.")

    return data


def read_single_datacube(filename: Path) -> np.ndarray:
    """Read a numpy data cube array from a FITS or NPY file."""

    data = load_datacube(filename)

    # # TODO: Is it the right manner ?
    # if data is None:
    #     raise OSError(f"Input file '{filename}' can not be read by Pyxel.")

    return data


def read_datacubes(filenames: Sequence[Path]) -> Sequence[np.ndarray]:
    """Read numpy array(s) from several FITS or NPY files."""
    output: Sequence[np.ndarray] = [
        read_single_datacube(Path(filename)) for filename in filenames
    ]

    return output


def read_data(filenames: Sequence[Path]) -> Sequence[np.ndarray]:
    """Read numpy array(s) from several FITS or NPY files."""
    output: Sequence[np.ndarray] = [
        read_single_data(Path(filename)) for filename in filenames
    ]

    return output


def sanitize(data: Any) -> Any:
    """Sanitize the input 'data'.

    Parameters
    ----------
    data : Any

    Examples
    --------
    >>> from pathlib import Path
    >>> import numpy as np
    >>> from astropy.units import Quantity
    >>> sanitize({"a": "1", "b": 2, "c": 3.14, "d": np.float64(1.2)})
    {'a': '1', 'b': 2, 'c': 3.14, 'd': 1.2}
    >>> sanitize({"a": [Path("foo"), True], "b": (Quantity(1.1, unit="m"), "hello")})
    {'a': ['foo': True], 'b': ('1.1 m', 'hello')}
    """
    if isinstance(data, Mapping):
        return {sanitize(key): sanitize(value) for key, value in data.items()}

    elif isinstance(data, MutableSequence):
        return [sanitize(key) for key in data]

    elif isinstance(data, Sequence) and not isinstance(data, str):
        return tuple([sanitize(key) for key in data])

    elif isinstance(data, Integral):
        return int(data)

    elif isinstance(data, Real):
        return float(data)

    elif isinstance(data, bool) or data is None:
        return data

    else:
        return str(data)


def create_processor_data_array(filenames: Sequence[Path]) -> xr.DataArray:
    """Create a 3D data array from FITS or NPY files for several processor(s).

    This DataArray will have dimensions 'processor', 'y' and 'x'

    Examples
    --------
    >>> create_processor_data_array(filenames=...)
    <xarray.DataArray (processor: 10, y: 2300, x: 1)>
    array(...)
    Coordinates:
      * processor  (processor) int64 0 1 2 3 4 5 6 7 8 9
      * y          (y) int64 0 1 2 3 4 5 6 7 ... 2293 2294 2295 2296 2297 2298 2299
      * x          (x) int64 0
    """
    data_3d = np.array([read_single_data(Path(filename)) for filename in filenames])

    num_processors, num_y, num_x = data_3d.shape

    data_array = xr.DataArray(
        data_3d,
        dims=["processor", "y", "x"],
        coords={
            "processor": range(num_processors),
            "y": range(num_y),
            "x": range(num_x),
        },
        attrs={"filenames": sanitize(filenames)},
    )
    return data_array


# TODO: Refactor and add more unit tests. See #327
def list_to_slice(
    input_list: Sequence[int] | None = None,
) -> tuple[slice, slice] | tuple[slice, slice, slice]:
    if not input_list:
        return slice(None), slice(None)

    elif len(input_list) == 4:
        return slice(input_list[0], input_list[1]), slice(input_list[2], input_list[3])

    elif len(input_list) == 6:
        return (
            slice(input_list[0], input_list[1]),
            slice(input_list[2], input_list[3]),
            slice(input_list[4], input_list[5]),
        )

    else:
        raise ValueError("Fitting range should have 4 or 6 values")


# TODO: Refactor and add more unit tests. See #327
def list_to_3d_slice(
    input_list: Sequence[int] | None = None,
) -> tuple[slice, slice, slice]:
    """TBW.

    :return:
    """
    if not input_list:
        return slice(None), slice(None), slice(None)

    elif len(input_list) == 6:
        return (
            slice(input_list[0], input_list[1]),
            slice(input_list[2], input_list[3]),
            slice(input_list[4], input_list[5]),
        )

    else:
        raise ValueError("Fitting range should have 6 values")


def slice_to_range(data: slice) -> range:
    """Convert a slice to a range.

    Examples
    --------
    >>> slice_to_range(slice(10))
    range(10)
    >>> slice_to_range(slice(10, 20))
    range(10, 20)
    >>> slice_to_range(slice(10, 20, 2))
    ValueError("Cannot use parameter 'step' in the slice object.")

    Raises
    ------
    ValueError
        If the input slice is not correct.
    """
    if data.step is not None:
        raise ValueError("Cannot use parameter 'step' in the slice object.")
    if data.stop is None:
        raise ValueError("Missing 'stop' parameter in the slice object")

    if data.start is None:
        result = range(data.stop)

        if data.stop <= 0:
            raise ValueError("Parameter 'stop' must be strictly greater than 'start'")
    else:
        if data.start < 0:
            raise ValueError("Parameter 'start' must be strictly positive")
        if data.start >= data.stop:
            raise ValueError("Parameter 'stop' must be strictly greater than 'start'")

        result = range(data.start, data.stop)

    return result


def _check_out_ranges(
    target_fit_range: Sequence[int],
    out_fit_range: Sequence[int],
) -> None:
    if len(out_fit_range) not in (4, 6):
        raise ValueError

    if (target_fit_range[1] - target_fit_range[0]) != (
        out_fit_range[1] - out_fit_range[0]
    ):
        raise ValueError("Fitting ranges have different lengths in 1st dimension")

    # TODO: Refactor and add more unit tests. See #328
    if len(target_fit_range) == len(out_fit_range) == 4 and (
        (target_fit_range[3] - target_fit_range[2])
        != (out_fit_range[3] - out_fit_range[2])
    ):
        raise ValueError("Fitting ranges have different lengths in 2nd dimension")

    if len(target_fit_range) == len(out_fit_range) == 6 and (
        (target_fit_range[5] - target_fit_range[4])
        != (out_fit_range[5] - out_fit_range[4])
    ):
        raise ValueError("Fitting ranges have different lengths in third dimension")


# TODO: Refactor and add more unit tests. See #328
def check_ranges(
    target_fit_range: Sequence[int],
    out_fit_range: Sequence[int],
    rows: int,
    cols: int,
    readout_times: int | None = None,
) -> None:
    """TBW."""
    if not target_fit_range:
        return

    if len(target_fit_range) not in (4, 6):
        raise ValueError

    if out_fit_range:
        _check_out_ranges(
            target_fit_range=target_fit_range, out_fit_range=out_fit_range
        )

    # for i in [0, 1]:
    #     # TODO: Refactor and add more unit tests. See #328
    #     if not (0 <= target_fit_range[i] <= rows):
    #         raise ValueError("Value of target fit range is wrong")

    for i in (-3, -4):
        if not (0 <= target_fit_range[i] <= rows):
            raise ValueError("Value of target fit range is wrong")

    for i in (-1, -2):
        if not (0 <= target_fit_range[i] <= cols):
            raise ValueError("Value of target fit range is wrong")

    if len(target_fit_range) == 6:
        if readout_times is None:
            raise ValueError("Target data is not a 3 dimensional array")

        for i in (0, 1):
            # TODO: Refactor and add more unit tests. See #328
            if not (0 <= target_fit_range[i] <= readout_times):
                raise ValueError("Value of target fit range is wrong")


@dataclass(frozen=True)
class FitRange2D:
    """Represent a 2D range or slice with a row range and a column range.

    Parameters
    ----------
    row : slice
        Range of rows in the 2D range
    col : slice
        Range of columns in the 2D range

    Examples
    --------
    >>> range2d = FitRange2D(row=slice(0, 5), col=slice(2, 7))
    >>> row_slice, col_slice = range2d.to_slices()
    >>> row_slice
    slice(0, 5)
    >>> col_slice
    slice(2,7)

    >>> FitRange2D.from_sequence([0, 5, 2, 7])
    FitRange2D(slice(0, 5),slice(2,7))
    """

    row: slice
    col: slice

    @classmethod
    def from_sequence(cls, data: Sequence[int | None]) -> "FitRange2D":
        if not data:
            data = [None] * 4

        if len(data) != 4:
            raise ValueError("Fitting range should have 4 values")

        y_start, y_stop, x_start, x_stop = data
        return cls(row=slice(y_start, y_stop), col=slice(x_start, x_stop))

    def to_dict(self) -> Mapping[str, slice]:
        return {"y": self.row, "x": self.col}

    def to_slices(self) -> tuple[slice, slice]:
        return self.row, self.col

    def check(self, rows: int, cols: int):
        if not self.row.stop <= rows:
            raise ValueError("Value of target fit range is wrong")

        if not self.col.stop <= cols:
            raise ValueError("Value of target fit range is wrong")


@dataclass(frozen=True)
class FitRange3D:
    """Represent a 3D range or slice with a time range, row range and a column range.

    Parameters
    ----------
    time : FitSlice
         Range of time in the 3D range
    row : FitSlice
        Range of rows in the 3D range
    col : FitSlice
        Range of columns in the 3D range

    Examples
    --------
    >>> range3d = FitRange3D(time=slice(0, 10), row=slice(0, 5), col=slice(2, 7))
    >>> time_slice, row_slice, col_slice = range3d.to_slices()
    >>> time_slice
    slice(0, 10)
    >>> row_slice
    slice(0, 5)
    >>> col_slice
    slice(2,7)

    >>> FitRange3D.from_sequence([0, 10, 0, 5, 2, 7])
    FitRange3D(time=slice(0,10), row=slice(0, 5), col=slice(2,7))
    """

    time: slice
    row: slice
    col: slice

    @classmethod
    def from_sequence(cls, data: Sequence[int | None]) -> "FitRange3D":
        if not data:
            data = [None] * 6

        if len(data) == 4:
            data = [None, None, *data]

        if len(data) != 6:
            raise ValueError("Fitting range should have 6 values")

        time_start, time_stop, y_start, y_stop, x_start, x_stop = data
        return cls(
            time=slice(time_start, time_stop),
            row=slice(y_start, y_stop),
            col=slice(x_start, x_stop),
        )

    def to_dict(self) -> Mapping[str, slice]:
        return {"time": self.time, "y": self.row, "x": self.col}

    def to_slices(self) -> tuple[slice, slice, slice]:
        return self.time, self.row, self.col

    def check(self, rows: int, cols: int, readout_times: int | None = None):
        if not self.row.stop <= rows:
            raise ValueError("Value of target fit range is wrong")

        if not self.col.stop <= cols:
            raise ValueError("Value of target fit range is wrong")

        if readout_times is None:
            raise ValueError("Target data is not a 3 dimensional array")

        if not self.time.stop <= readout_times:
            raise ValueError("Value of target fit range is wrong")


def to_fit_range(
    input_list: Sequence[int] | None = None,
) -> FitRange2D | FitRange3D:
    if not input_list:
        return FitRange2D(row=slice(None), col=slice(None))

    elif len(input_list) == 4:
        return FitRange2D.from_sequence(input_list)

    elif len(input_list) == 6:
        return FitRange3D.from_sequence(input_list)

    else:
        raise ValueError("Fitting range should have 4 or 6 values")


def _check_out_fit_ranges(
    target_fit_range: FitRange2D | FitRange3D,
    out_fit_range: FitRange2D | FitRange3D,
):
    if (
        isinstance(target_fit_range, FitRange3D)
        and isinstance(out_fit_range, FitRange3D)
        and target_fit_range.time.stop != out_fit_range.time.stop
    ):
        raise ValueError(
            "Fitting ranges have different lengths in dimension 'readout time'"
        )

    if target_fit_range.row.stop != out_fit_range.row.stop:
        raise ValueError("Fitting ranges have different lengths in dimension 'y'")

    if target_fit_range.col.stop != out_fit_range.col.stop:
        raise ValueError("Fitting ranges have different lengths in dimension 'x'")


# TODO: Refactor and add more unit tests. See #328
def check_fit_ranges(
    target_fit_range: FitRange2D | FitRange3D | None,
    out_fit_range: FitRange2D | FitRange3D | None,
    rows: int,
    cols: int,
    readout_times: int | None = None,
) -> None:
    """Check if ``target_fit_range`` and ``out_fit_range`` are valid.

    This functions checks if ``target_fit_range`` is valid for the specified ``rows`` and ``columns``
    and if ``out_fit_range`` is compatible with ``target_fit_range``.

    Parameters
    ----------
    target_fit_range : FitRange2D, FitRange3D. Optional
        A target range to check if it's valid or not.
    out_fit_range : FitRange2D, FitRange3D. Optional
        An output range to check whether it's compatible with the target fit range.
    rows : int
        Number of rows.
    cols : int
        Number of columns
    readout_times : int, Optional
        Number of readout times. This parameter is only used if the target fit range is
        a 3D range.

    Raises
    ------
    ValueError
        If ``target_fit_range`` is not valid or not compatible with ``out_fit_range``.
    """
    if not target_fit_range:
        return

    if out_fit_range:
        _check_out_fit_ranges(
            target_fit_range=target_fit_range, out_fit_range=out_fit_range
        )

    if isinstance(target_fit_range, FitRange2D):
        target_fit_range.check(rows=rows, cols=cols)
    else:
        target_fit_range.check(rows=rows, cols=cols, readout_times=readout_times)
