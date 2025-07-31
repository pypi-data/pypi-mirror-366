#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Amplifier crosstalk model: https://arxiv.org/abs/1808.00790."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Union

import numba
import numpy as np

from pyxel import load_table
from pyxel.detectors import Channels, Matrix

if TYPE_CHECKING:
    from pyxel.detectors import APD, CCD, CMOS


# TODO: Put more info in documentation
@numba.njit
def flip_array(array: np.ndarray, direction: int) -> np.ndarray:
    """Flip the array for read direction as in case 1 or back.

    Parameters
    ----------
    array : ndarray
    direction : int

    Returns
    -------
    ndarray
    """
    if direction == 1:
        result: np.ndarray = array
    elif direction == 2:
        result = np.fliplr(array)
    elif direction == 3:
        result = np.flipud(array)
    elif direction == 4:
        result = np.fliplr(np.flipud(array))
    else:
        raise ValueError("Unknown readout direction.")

    return result


@numba.njit
def get_channel_slices(
    shape: tuple, channel_matrix: np.ndarray
) -> list[list[tuple[Any, Any]]]:
    """Get pairs of slices that correspond to the given channel matrix in numerical order of channels.

    Parameters
    ----------
    shape : tuple
    channel_matrix : ndarray

    Returns
    -------
    slices
    """
    j_x = channel_matrix.shape[0]
    j_y = 1
    if channel_matrix.ndim == 2:
        j_y = channel_matrix.shape[1]

    delta_x = shape[0] // j_x
    delta_y = shape[1] // j_y

    slices = []

    for j in range(1, channel_matrix.size + 1):
        channel_position = np.argwhere(channel_matrix == j)[0]
        if channel_position.size == 1:
            channel_position = np.append(np.array([0]), channel_position)
        channel_slice_x = (
            channel_position[1] * delta_x,
            (channel_position[1] + 1) * delta_x,
        )
        channel_slice_y = (
            channel_position[0] * delta_y,
            (channel_position[0] + 1) * delta_y,
        )
        slices.append([channel_slice_x, channel_slice_y])

    return slices


def convert_matrix_crosstalk(matrix: Matrix) -> np.ndarray:
    return np.arange(start=1, stop=matrix.size + 1, dtype=int)


def convert_readout_crosstalk(channels: Channels) -> np.ndarray:
    position_convert: Mapping[
        Literal["top-left", "top-right", "bottom-left", "bottom-right"],
        Literal[1, 2, 3, 4],
    ] = {"top-left": 1, "top-right": 2, "bottom-left": 3, "bottom-right": 4}

    all_positions = channels.readout_position.positions

    lst = []
    for channel in np.ravel(channels.matrix):
        position: Literal["top-left", "top-right", "bottom-left", "bottom-right"] = (
            all_positions[channel]
        )

        position_converted: Literal[1, 2, 3, 4] = position_convert[position]
        lst.append(position_converted)

    return np.array(lst, dtype=int)


def get_matrix(coupling_matrix: str | Path | Sequence) -> np.ndarray:
    """Get the coupling matrix either from configuration input or a file.

    Parameters
    ----------
    coupling_matrix : str, Path or sequence of numbers.
        Matrix to create.

    Returns
    -------
    array
        Matrix.
    """
    if isinstance(coupling_matrix, str | Path):
        return np.array(load_table(coupling_matrix))

    return np.array(coupling_matrix)


@numba.njit
def crosstalk_signal_ac(
    array: np.ndarray,
    coupling_matrix: np.ndarray,
    channel_matrix: np.ndarray,
    readout_directions: np.ndarray,
) -> np.ndarray:
    """Apply AC crosstalk signal to an array.

    Parameters
    ----------
    array : ndarray
    coupling_matrix : ndarray
        2D array.
    channel_matrix : ndarray
    readout_directions : ndarray

    Returns
    -------
    ndarray
    """
    amp_number = channel_matrix.size  # number of amplifiers

    slices: list[list[tuple[Any, Any]]] = get_channel_slices(
        shape=array.shape, channel_matrix=channel_matrix
    )

    array_copy = array.copy()

    for k in range(amp_number):
        for j in range(amp_number):
            if k != j and coupling_matrix[k][j] != 0:
                s_k = flip_array(
                    array_copy[
                        slices[k][1][0] : slices[k][1][1],
                        slices[k][0][0] : slices[k][0][1],
                    ],
                    readout_directions[k],
                )
                s_k_shift = np.hstack((s_k[:, 0:1], s_k[:, 0:-1]))
                delta_s = s_k - s_k_shift
                crosstalk_signal = coupling_matrix[k][j] * flip_array(
                    delta_s, readout_directions[j]
                )
                array[
                    slices[j][1][0] : slices[j][1][1], slices[j][0][0] : slices[j][0][1]
                ] += crosstalk_signal

    return array


@numba.njit
def crosstalk_signal_dc(
    array: np.ndarray,
    coupling_matrix: np.ndarray,
    channel_matrix: np.ndarray,
    readout_directions: np.ndarray,
) -> np.ndarray:
    """Apply DC crosstalk signal to an array.

    Parameters
    ----------
    array : ndarray
    coupling_matrix : ndarray
    channel_matrix : ndarray
    readout_directions : ndarray

    Returns
    -------
    ndarray
    """
    amp_number = channel_matrix.size  # number of amplifiers

    slices: list[list[tuple[Any, Any]]] = get_channel_slices(
        shape=array.shape, channel_matrix=channel_matrix
    )

    array_copy = array.copy()

    for k in range(amp_number):
        for j in range(amp_number):
            if k != j and coupling_matrix[k][j] != 0:
                s_k = flip_array(
                    array_copy[
                        slices[k][1][0] : slices[k][1][1],
                        slices[k][0][0] : slices[k][0][1],
                    ],
                    readout_directions[k],
                )
                crosstalk_signal = coupling_matrix[k][j] * flip_array(
                    s_k, readout_directions[j]
                )
                array[
                    slices[j][1][0] : slices[j][1][1], slices[j][0][0] : slices[j][0][1]
                ] += crosstalk_signal

    return array


@dataclass
class ChannelInfo:
    """Container for detector channel layout and readout directions."""

    ch_matrix: np.ndarray
    readout_directions: np.ndarray


def _get_channels_and_readout_directions(
    detector: Union["CCD", "CMOS", "APD"],
    channel_matrix: Sequence | None = None,
    readout_directions: Sequence | None = None,
) -> ChannelInfo:
    """Check and extract 'channel_matrix' and 'readout_directions'."""
    # Use provided channels or extract then from 'detector.geometry.channels'
    if channel_matrix is not None:
        ch_matrix: np.ndarray = np.array(channel_matrix)
    else:
        if not detector.geometry.channels:
            raise ValueError("Missing 'Channels' in 'geometry.channels'.")

        ch_matrix = convert_matrix_crosstalk(detector.geometry.channels.matrix)

    # Use provided readout_directions or extract then from 'detector.channels'
    if readout_directions is not None:
        directions: np.ndarray = np.array(readout_directions)
    else:
        if not detector.geometry.channels:
            raise ValueError("Missing 'Channels' in 'geometry.channels'.")

        directions = convert_readout_crosstalk(detector.geometry.channels)

    # Check array divisibility
    if detector.geometry.row % ch_matrix.shape[0] != 0:
        raise ValueError(
            "Can't split detector array horizontally for a given number of amplifiers."
        )
    if len(ch_matrix.shape) > 1 and detector.geometry.col % ch_matrix.shape[1] != 0:
        raise ValueError(
            "Can't split detector array vertically for a given number of amplifiers."
        )

    # Check channel vs direction size
    if ch_matrix.size != directions.size:
        raise ValueError(
            "Channel matrix and readout directions arrays not the same size."
        )

    return ChannelInfo(ch_matrix=ch_matrix, readout_directions=directions)


def dc_crosstalk(
    detector: Union["CCD", "CMOS", "APD"],
    coupling_matrix: str | Path | Sequence,
    channel_matrix: Sequence | None = None,
    readout_directions: Sequence | None = None,
) -> None:
    """Apply DC crosstalk signal to detector signal.

    Crosstalk occurs when signals in one channel interfere with others. This function
    modifies the detector signal based on a provided or derived coupling matrix,
    channel matrix, and readout directions.

    Parameters
    ----------
    detector : Detector
    coupling_matrix : ndarray
        2D matrix defining the signal coupling between amplifier channels.
        Can be a filename (to be loaded) or directly an array.
    channel_matrix : ndarray, optional
        Mapping from pixel positions to amplifier channels.
        If not provided it is taken from the detector geometry.
    readout_directions : ndarray, optional
        Array indicating the readout direction per channel.
        If not provided it is taken from the detector geometry.

    Raises
    ------
    ValueError
        If at least one parameter 'coupling_matrix', 'channel_matrix' or
        'readout_directions' does not have the right shape.

    Notes
    -----
    For more information, you can find examples here:

    * :external+pyxel_data:doc:`examples/models/amplifier_crosstalk/crosstalk`
    * :external+pyxel_data:doc:`use_cases/HxRG/h2rg`
    * :external+pyxel_data:doc:`examples/observation/sequential`

    For more information about the channels, click here:

    * :ref:`channels`
    * :ref:`channels_order`.
    """
    # Validation and convert coupling matrix
    cpl_matrix_2d: np.ndarray = get_matrix(coupling_matrix)
    if cpl_matrix_2d.ndim != 2:
        raise ValueError("Expecting 2D 'coupling_matrix'.")

    channel_info: ChannelInfo = _get_channels_and_readout_directions(
        detector=detector,
        channel_matrix=channel_matrix,
        readout_directions=readout_directions,
    )

    # Check coupling matrix size
    if cpl_matrix_2d.shape != (
        channel_info.ch_matrix.size,
        channel_info.ch_matrix.size,
    ):
        raise ValueError(
            f"Expecting a matrix of {channel_info.ch_matrix.size}x{channel_info.ch_matrix.size} "
            "elements for 'coupling_matrix'"
        )

    # Apply crosstalk correction
    signal_2d = crosstalk_signal_dc(
        array=detector.signal.array.copy(),
        coupling_matrix=cpl_matrix_2d,
        channel_matrix=channel_info.ch_matrix,
        readout_directions=channel_info.readout_directions,
    )

    detector.signal.array = signal_2d


def ac_crosstalk(
    detector: Union["CCD", "CMOS", "APD"],
    coupling_matrix: str | Path | Sequence,
    channel_matrix: Sequence | None = None,
    readout_directions: Sequence | None = None,
) -> None:
    """Apply AC crosstalk signal to detector signal.

    Crosstalk occurs when signals in one channel interfere with others. This function
    modifies the detector signal based on a provided or derived coupling matrix,
    channel matrix, and readout directions.

    Parameters
    ----------
    detector : Detector
    coupling_matrix : ndarray
        2D matrix defining the signal coupling between amplifier channels.
        Can be a filename (to be loaded) or directly an array.
    channel_matrix : ndarray, optional
        Mapping from pixel positions to amplifier channels.
        If not provided it is taken from the detector geometry.
    readout_directions : ndarray, optional
        Array indicating the readout direction per channel.
        If not provided it is taken from the detector geometry.

    Raises
    ------
    ValueError
        If at least one parameter 'coupling_matrix', 'channel_matrix' or
        'readout_directions' does not have the right shape.

    Notes
    -----
    For more information, you can find examples here:

    * :external+pyxel_data:doc:`examples/models/amplifier_crosstalk/crosstalk`
    * :external+pyxel_data:doc:`use_cases/HxRG/h2rg`
    * :external+pyxel_data:doc:`examples/observation/sequential`

    For more information about the channels, click here:

    * :ref:`channels`
    * :ref:`channels_order`.
    """
    # Validation and conversion
    cpl_matrix_2d: np.ndarray = get_matrix(coupling_matrix)
    if cpl_matrix_2d.ndim != 2:
        raise ValueError("Expecting 2D 'coupling_matrix'.")

    channel_info: ChannelInfo = _get_channels_and_readout_directions(
        detector=detector,
        channel_matrix=channel_matrix,
        readout_directions=readout_directions,
    )

    # Check coupling matrix size
    if cpl_matrix_2d.shape != (
        channel_info.ch_matrix.size,
        channel_info.ch_matrix.size,
    ):
        raise ValueError(
            f"Expecting a matrix of {channel_info.ch_matrix.size}x{channel_info.ch_matrix.size} "
            "elements for 'coupling_matrix'"
        )

    # Processing
    signal_2d = crosstalk_signal_ac(
        array=detector.signal.array.copy(),
        coupling_matrix=cpl_matrix_2d,
        channel_matrix=channel_info.ch_matrix,
        readout_directions=channel_info.readout_directions,
    )

    detector.signal.array = signal_2d
