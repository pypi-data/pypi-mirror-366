#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Geometry class for detector."""

from collections.abc import Mapping

import numpy as np
from typing_extensions import Self

from pyxel.detectors import Channels
from pyxel.util import get_size, get_uninitialized_error


def get_vertical_pixel_center_pos(
    num_rows: int,
    num_cols: int,
    pixel_vertical_size: float,
) -> np.ndarray:
    """Generate vertical position list of all pixel centers in detector imaging area."""
    init_ver_position = np.arange(0.0, num_rows, 1.0) * pixel_vertical_size
    init_ver_position += pixel_vertical_size / 2.0

    return np.repeat(init_ver_position, num_cols)


def get_horizontal_pixel_center_pos(
    num_rows: int,
    num_cols: int,
    pixel_horizontal_size: float,
) -> np.ndarray:
    """Generate horizontal position list of all pixel centers in detector imaging area."""
    init_hor_position = np.arange(0.0, num_cols, 1.0) * pixel_horizontal_size
    init_hor_position += pixel_horizontal_size / 2.0

    return np.tile(init_hor_position, reps=num_rows)


class Geometry:
    """Geometrical attributes of the detector.

    Parameters
    ----------
    row : int
        Number of pixel rows.
    col : int
        Number of pixel columns.
    total_thickness : float, optional
        Thickness of detector. Unit: um
    pixel_vert_size : float, optional
        Vertical dimension of pixel. Unit: um
    pixel_horz_size : float, optional
        Horizontal dimension of pixel. Unit: um
    pixel_scale : float, optional
        Dimension of how much of the sky is covered by one pixel. Unit: arcsec/pixel
    channels : Channels, None
        Channel layout for the detector, including number of channels, position, and readout direction.
    """

    def __init__(
        self,
        row: int,
        col: int,
        total_thickness: float | None = None,  # unit: um
        pixel_vert_size: float | None = None,  # unit: um
        pixel_horz_size: float | None = None,  # unit: um
        pixel_scale: float | None = None,  # unit: arcsec/pixel
        channels: Channels | None = None,
    ):
        if row <= 0:
            raise ValueError("'row' must be strictly greater than 0.")

        if col <= 0:
            raise ValueError("'col' must be strictly greater than 0.")

        if total_thickness and not (0.0 <= total_thickness <= 10000.0):
            raise ValueError("'total_thickness' must be between 0.0 and 10000.0.")

        if pixel_vert_size and not (0.0 <= pixel_vert_size <= 1000.0):
            raise ValueError("'pixel_vert_size' must be between 0.0 and 1000.0.")

        if pixel_horz_size and not (0.0 <= pixel_horz_size <= 1000.0):
            raise ValueError("'pixel_horz_size' must be between 0.0 and 1000.0.")

        # TODO: Create a new class in channels to measure the matrix
        if channels is not None:
            # Vertical length: number of rows
            vertical_channels, horizontal_channels = channels.matrix.shape

            # vertical_channels = channels.matrix.shape[0]
            # Horizontal lengths: number of elements in a row
            # horizontal_channels = channels.matrix.shape[1]

            if vertical_channels > row:
                raise ValueError(
                    "Vertical size of the channel must be at least one pixel"
                )

            if horizontal_channels > col:
                raise ValueError(
                    "Horizontal size of the channel must be at least one pixel"
                )

        self._row: int = row
        self._col: int = col
        self._total_thickness: float | None = total_thickness
        self._pixel_vert_size: float | None = pixel_vert_size
        self._pixel_horz_size: float | None = pixel_horz_size
        self._pixel_scale: float | None = pixel_scale

        # if channels:
        #     channels.validate(geometry=self)

        self.channels: Channels | None = channels

        self._numbytes = 0

    def __repr__(self) -> str:
        cls_name: str = self.__class__.__name__
        return (
            f"{cls_name}(row={self._row!r}, col={self._col!r}, "
            f"total_thickness={self._total_thickness!r}, "
            f"pixel_vert_size={self._pixel_vert_size!r}, "
            f"pixel_horz_size={self._pixel_horz_size}), "
            f"pixel_scale={self._pixel_scale},"
            f"channels={self.channels!r})"
        )

    def __eq__(self, other) -> bool:
        return type(self) is type(other) and (
            self.row,
            self.col,
            self._total_thickness,
            self._pixel_vert_size,
            self._pixel_horz_size,
            self._pixel_scale,
            self.channels,
        ) == (
            other.row,
            other.col,
            other._total_thickness,
            other._pixel_vert_size,
            other._pixel_horz_size,
            other._pixel_scale,
            other.channels,
        )

    # def _repr_html_(self):
    #     """TBW."""
    #     return "Hello World"

    @property
    def row(self) -> int:
        """Get Number of pixel rows."""
        return self._row

    @row.setter
    def row(self, value: int) -> None:
        """Set Number of pixel rows."""
        if value <= 0:
            raise ValueError("'row' must be strictly greater than 0.")

        self._row = value

    @property
    def col(self) -> int:
        """Get Number of pixel columns."""
        return self._col

    @col.setter
    def col(self, value: int) -> None:
        """Set Number of pixel columns."""
        if value <= 0:
            raise ValueError("'col' must be strictly greater than 0.")

        self._col = value

    @property
    def shape(self) -> tuple[int, int]:
        """Return detector shape."""
        return self.row, self.col

    @property
    def total_thickness(self) -> float:
        """Get Thickness of detector."""
        if self._total_thickness is None:
            raise ValueError(
                get_uninitialized_error(
                    name="total_thickness",
                    parent_name="geometry",
                )
            )

        return self._total_thickness

    @total_thickness.setter
    def total_thickness(self, value: float) -> None:
        """Set Thickness of detector."""
        if not (0.0 <= value <= 10000.0):
            raise ValueError("'total_thickness' must be between 0.0 and 10000.0.")

        self._total_thickness = value

    @property
    def pixel_vert_size(self) -> float:
        """Get Vertical dimension of pixel."""
        if self._pixel_vert_size is None:
            raise ValueError(
                get_uninitialized_error(
                    name="pixel_vert_size",
                    parent_name="geometry",
                )
            )

        return self._pixel_vert_size

    @pixel_vert_size.setter
    def pixel_vert_size(self, value: float) -> None:
        """Set Vertical dimension of pixel."""
        if not (0.0 <= value <= 1000.0):
            raise ValueError("'pixel_vert_size' must be between 0.0 and 1000.0.")

        self._pixel_vert_size = value

    @property
    def pixel_horz_size(self) -> float:
        """Get Horizontal dimension of pixel."""
        if self._pixel_horz_size is None:
            raise ValueError(
                get_uninitialized_error(
                    name="pixel_horz_size",
                    parent_name="geometry",
                )
            )

        return self._pixel_horz_size

    @pixel_horz_size.setter
    def pixel_horz_size(self, value: float) -> None:
        """Set Horizontal dimension of pixel."""
        if not (0.0 <= value <= 1000.0):
            raise ValueError("'pixel_horz_size' must be between 0.0 and 1000.0.")

        self._pixel_horz_size = value

    @property
    def pixel_scale(self) -> float:
        """Get pixel scale."""
        if self._pixel_scale is None:
            raise ValueError(
                get_uninitialized_error(
                    name="pixel_scale",
                    parent_name="geometry",
                )
            )
        return self._pixel_scale

    @pixel_scale.setter
    def pixel_scale(self, value: float) -> None:
        """Set pixel scale."""
        if not (0.0 <= value <= 1000.0):
            raise ValueError("'pixel_scale' must be between 0.0 and 1000.0.")

        self._pixel_scale = value

    @property
    def horz_dimension(self) -> float:
        """Get total horizontal dimension of detector. Calculated automatically.

        Return
        ------
        float
            horizontal dimension
        """
        return self.pixel_horz_size * self.col

    @property
    def vert_dimension(self) -> float:
        """Get total vertical dimension of detector. Calculated automatically.

        Return
        ------
        float
            vertical dimension
        """
        return self.pixel_vert_size * self.row

    def vertical_pixel_center_pos_list(self) -> np.ndarray:
        """Generate horizontal position list of all pixel centers in detector imaging area."""
        return get_vertical_pixel_center_pos(
            num_rows=self.row,
            num_cols=self.col,
            pixel_vertical_size=self.pixel_vert_size,
        )

    def horizontal_pixel_center_pos_list(self) -> np.ndarray:
        """Generate horizontal position list of all pixel centers in detector imaging area."""
        return get_horizontal_pixel_center_pos(
            num_rows=self.row,
            num_cols=self.col,
            pixel_horizontal_size=self.pixel_horz_size,
        )

    def get_channel_coord(self, channel: int | str) -> tuple[slice, slice]:
        if self.channels is None:
            raise RuntimeError("Missing 'channels' in Geometry configuration.")

        # Convert the matrix to a NumPy array for easy searching
        matrix_array = np.array(self.channels.matrix)
        found_indices = np.argwhere(matrix_array == channel)

        # Check if the channel was found
        if found_indices.size == 0:
            raise KeyError(f"Cannot find channel {channel!r}")

        # Extract the first (and should be only) matching index
        position_y, position_x = found_indices[0]
        vertical_channels, horizontal_channels = matrix_array.shape
        channel_vertical_size = self.row // vertical_channels
        channel_horizontal_size = self.col // horizontal_channels

        # Calculate the start and stop positions for the slices
        start_x = position_x * channel_horizontal_size
        start_y = position_y * channel_vertical_size
        stop_x = start_x + channel_horizontal_size
        stop_y = start_y + channel_vertical_size

        # Return the slices for the y and x dimensions
        return (slice(int(start_y), int(stop_y)), slice(int(start_x), int(stop_x)))

    @property
    def numbytes(self) -> int:
        """Recursively calculates object size in bytes using Pympler library.

        Returns
        -------
        int
            Size of the object in bytes.
        """
        self._numbytes = get_size(self)
        return self._numbytes

    def to_dict(self) -> Mapping:
        """Get the attributes of this instance as a `dict`."""
        return {
            "row": self.row,
            "col": self.col,
            "total_thickness": self._total_thickness,
            "pixel_vert_size": self._pixel_vert_size,
            "pixel_horz_size": self._pixel_horz_size,
            "pixel_scale": self._pixel_scale,
            "channels": self.channels.to_dict() if self.channels else None,
        }

    @classmethod
    def from_dict(cls, dct: dict) -> Self:
        """Create a new instance of `Geometry` from a `dict`."""
        # TODO: This is a simplistic implementation. Improve this.
        new_dct: dict = dct.copy()

        if "channels" in new_dct and new_dct["channels"] is not None:
            channels_dct: Mapping = new_dct.pop("channels")

            channels: Channels = Channels.from_dict(channels_dct)
            return cls(**new_dct, channels=channels)

        else:
            return cls(**new_dct)

    def dump(self) -> dict[str, int | float | None]:
        return {
            "row": self._row,
            "col": self._col,
            "total_thickness": self._total_thickness,
            "pixel_vert_size": self._pixel_vert_size,
            "pixel_horz_size": self._pixel_horz_size,
            "pixel_scale": self._pixel_scale,
        }
