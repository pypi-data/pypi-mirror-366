#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""TBW."""

from collections.abc import Iterator, Mapping, Sequence
from numbers import Number
from typing import Any

import numpy as np

from pyxel import load_table
from pyxel.evaluator import eval_range


class Readout:
    """Readout configuration that contains parameters for a time-domain process.

    This class supports both linear and custom sampling times, which can be loaded from a
    file or defined directly.

    Parameters
    ----------
    times : Sequence[Number] or str, optional
        A sequence of numeric values or a string representing the sampling times for the
        readout simulation. It can be a list, tuple, or other iterable containing numerical
        values (e.g. [1.0, 2.0, 3.0]). Alternatively, it can be a string representing a range of numbers using
        Python's syntax (e.g. 'numpy.linspace(0, 10, 100)').
        If not provided, the default readout/exposure time is 1 second.

    times_from_file : str, optional
        A string specifying the path to a file containing the sampling times for the readout.
        Parameters ``times`` and ``times_from_file`` cannot be provided at the same time.

    start_time : float, optional. Default: 0.0
        A float representing the starting time of the readout simulation.
        The readout time(s) should be greater that this ``start_time``.

    non_destructive : bool, optional. Default: False
        A boolean flag indicating whether the readout simulation is non-destructive.
        If set to ``True``, the readout process will not modify the underlying data.

    Raises
    ------
    ValueError
        Raises if both ``times`` and ``times_from_file`` parameters are provided or if neither
        of them is specified.
        Raises if the readout times are not strictly increasing or the first readout time is zero.
        Raises if the ``start_time`` parameter is greater than or equal to the first readout time.

    Examples
    --------
    Example 1: Using linearly spaced readout times

    >>> readout1 = Readout(times=[1, 2, 3, 4, 5], start_time=0.5, non_destructive=False)

    Example 2: Loading readout times from a file

    >>> readout2 = Readout(
    ...     times_from_file="readout_times.csv",
    ...     start_time=0.0,
    ...     non_destructive=True,
    ... )
    """

    def __init__(
        self,
        times: Number | Sequence | str | None = None,
        times_from_file: str | None = None,
        start_time: float = 0.0,
        non_destructive: bool = False,
    ):
        self._time_domain_simulation = True

        if times is not None and times_from_file is not None:
            raise ValueError("Both times and times_from_file specified. Choose one.")
        elif times is times_from_file is None:
            # by convention default readout/exposure time is 1 second
            self._times = np.array([1])
            self._time_domain_simulation = False
        elif times_from_file:
            self._times = load_table(times_from_file).to_numpy(dtype=float).flatten()
        elif times:
            self._times = np.array(eval_range(times), dtype=float)
        else:
            raise ValueError("Sampling times not specified.")

        if self._times[0] == 0:
            raise ValueError("Readout times should be non-zero values.")
        elif start_time >= self._times[0]:
            raise ValueError("Readout times should be greater than start time.")

        if not np.all(np.diff(self._times) > 0):
            raise ValueError("Readout times must be strictly increasing")

        self._non_destructive = non_destructive

        self._times_linear: bool = True
        self._start_time: float = start_time
        self._steps: np.ndarray = np.array([])
        self._num_steps: int = 0
        self._set_steps()

    def __repr__(self) -> str:
        cls_name: str = self.__class__.__name__
        return f"{cls_name}<num_steps={self._num_steps}>"

    def _set_steps(self) -> None:
        """TBW."""
        self._steps = calculate_steps(times=self._times, start_time=self._start_time)
        self._times_linear = bool(np.all(self._steps == self._steps[0]))
        self._num_steps = len(self._times)

    def time_step_it(self) -> Iterator[tuple[float, float]]:
        """TBW."""
        return zip(self._times, self._steps, strict=False)

    @property
    def start_time(self) -> float:
        """Return start time of the readout."""
        return self._start_time

    @start_time.setter
    def start_time(self, value: float) -> None:
        """Set start time of the readout."""
        if value >= self._times[0]:
            raise ValueError("Readout times should be greater than start time.")
        self._start_time = value
        self._set_steps()

    @property
    def times(self) -> np.ndarray:
        """Return readout times."""
        return self._times

    @times.setter
    def times(self, value: Number | Sequence | np.ndarray) -> None:
        """Set readout times.

        Parameters
        ----------
        value
        """
        if isinstance(value, Number):
            values: np.ndarray = np.array([value])
        else:
            values = np.array(value)

        if values.ndim != 1:
            raise ValueError

        if values.size == 0:
            raise ValueError

        if values[0] == 0:
            raise ValueError("Readout times should be non-zero values.")

        elif self._start_time >= values[0]:
            raise ValueError("Readout times should be greater than start time.")

        self._times = values
        self._set_steps()

    @property
    def time_domain_simulation(self) -> bool:
        """TBW."""
        return self._time_domain_simulation

    @property
    def steps(self) -> np.ndarray:
        """TBW."""
        return self._steps

    @property
    def non_destructive(self) -> bool:
        """Get non-destructive readout mode."""
        return self._non_destructive

    @non_destructive.setter
    def non_destructive(self, value: bool) -> None:
        """Set non-destructive mode."""
        self._non_destructive = value

    def replace(self, **changes) -> "Readout":
        """Create a new 'Readout' object with modified parameters."""
        parameters = {
            "times": self._times,
            "start_time": self._start_time,
            "non_destructive": self._non_destructive,
        }

        new_parameters = {**parameters, **changes}
        return Readout(**new_parameters)

    def dump(self) -> Mapping[str, Any]:
        return {
            "times": self._times.tolist(),
            "start_time": self._start_time,
            "non_destructive": self._non_destructive,
        }


def calculate_steps(times: np.ndarray, start_time: float) -> np.ndarray:
    """Calculate time steps between consecutive time points.

    Parameters
    ----------
    times : ndarray
        A numpy array representing the time points for which the time steps will be calculated.
        The array should contain numerical values and must be one-dimensional (1D).
    start_time : float
        A float representing the starting time for which the time steps will be computed.
        This value serves as the reference for the first time step.

    Returns
    -------
    ndarray
        An array containing the time steps between consecutive time points in the ``times`` array.

    Examples
    --------
    >>> calculate_steps(times=np.array([1, 2, 4, 7, 10]), start_time=0.0)
    array([1., 1., 2., 3., 3.])

    >>> calculate_steps(times=np.array([1, 2, 4, 7, 10]), start_time=0.5)
    array([0.5, 1., 2., 3., 3.])
    """
    steps = np.diff(
        np.concatenate((np.array([start_time]), times), axis=0),
        axis=0,
    )

    return steps
