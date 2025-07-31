#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Sampling detector properties class."""

from collections.abc import Sequence

import numpy as np

from pyxel.exposure.readout import calculate_steps


class ReadoutProperties:
    """Readout sampling detector properties related to the readout process of a detector.

    These properties include sampling times, readout steps, and other simulation parameters.

    Parameters
    ----------
    times : Sequence[Number]
        A sequence of increasing numerical values representing the times at which
        the detector samples are read.
    start_time : float, optional. default: 0.0
        The start time for the readout process.
        All value in ``times`` must be greater that ``start_time``.
    non_destructive : bool, optional. Default: False
        A boolean flag indicating whether the readout simulation is non-destructive.
        If set to ``True``, the readout process will not modify the underlying data.

    Examples
    --------
    >>> readout_properties = ReadoutProperties(times=[1, 2, 4, 7, 10], start_time=0.0)
    >>> readout_properties.times
    array([ 1.,  2.,  4.,  7., 10.])
    >>> readout_properties.steps
    array([0., 1., 2., 3., 3.])
    >>> readout_properties.num_steps
    5
    >>> readout_properties.absolute_time
    0.0
    """

    def __init__(
        self,
        times: Sequence[float] | np.ndarray,
        start_time: float = 0.0,
        non_destructive: bool = False,
    ):
        times_1d = np.array(times, dtype=float)

        if times_1d.ndim != 1:
            raise ValueError("Readout times must be 1D")
        elif times_1d[0] == 0:
            raise ValueError("Readout times should be non-zero values.")
        elif start_time >= times_1d[0]:
            raise ValueError("Readout times should be greater than start time.")
        elif not np.all(np.diff(times_1d) > 0):
            raise ValueError("Readout times must be strictly increasing")

        steps = calculate_steps(times=times_1d, start_time=start_time)

        self._times: np.ndarray = times_1d
        self._steps: np.ndarray = steps

        self._times.flags.writeable = False
        self._steps.flags.writeable = False

        # Fixed at beginning
        self._num_steps: int = len(self._steps)
        self._start_time: float = start_time
        self._end_time: float = self._times[-1]
        self._non_destructive: bool = non_destructive
        self._times_linear: bool = bool(np.all(self._steps == self._steps[0]))

        # Changing
        self._time: float = 0.0
        self._time_step: float = 1.0
        self._read_out: bool = True
        self._pipeline_count: int = 0

    @property
    def times(self) -> np.ndarray:
        """Return the sampling times for readout process.

        Examples
        --------
        >>> readout_properties = ReadoutProperties(
        ...     times=[1, 2, 4, 7, 10], start_time=0.0
        ... )
        >>> readout_properties.times
        array([ 1.,  2.,  4.,  7., 10.])
        """
        return self._times

    @property
    def steps(self) -> np.ndarray:
        """Return the time interval between consecutive readout samples.

        Examples
        --------
        >>> readout_properties = ReadoutProperties(
        ...     times=[1, 2, 4, 7, 10], start_time=0.0
        ... )
        >>> readout_properties.steps
        array([0., 1., 2., 3., 3.])
        """
        return self._steps

    @property
    def num_steps(self) -> int:
        """Return the total number of readout steps.

        Examples
        --------
        >>> readout_properties = ReadoutProperties(
        ...     times=[1, 2, 4, 7, 10], start_time=0.0
        ... )
        >>> readout_properties.num_steps
        5
        """
        return self._num_steps

    @property
    def start_time(self) -> float:
        """Get the start time for the readout simulation.

        Examples
        --------
        >>> readout_properties = ReadoutProperties(
        ...     times=[1, 2, 4, 7, 10], start_time=0.0
        ... )
        >>> readout_properties.start_time
        0.0
        """
        return self._start_time

    @start_time.setter
    def start_time(self, value: float) -> None:
        """Set a new start time for the readout simulation.

        Parameters
        ----------
        value : float
            The new start time to set.

        Examples
        --------
        >>> readout_properties = ReadoutProperties(
        ...     times=[1, 2, 4, 7, 10], start_time=0.0
        ... )
        >>> readout_properties.start_time = 0.5
        >>> readout_properties.start_time
        0.5
        """
        self._start_time = value

    @property
    def end_time(self) -> float:
        """Return the last time in the readout sequence.

        Examples
        --------
        >>> readout_properties = ReadoutProperties(
        ...     times=[1, 2, 4, 7, 10], start_time=0.0
        ... )
        >>> readout_properties.end_time
        10.0
        """
        return self._end_time

    @property
    def non_destructive(self) -> bool:
        """Check if the readout process is non-destructive.

        Returns
        -------
        bool
            True if the readout does not alter the underlying data.
            False otherwise.

        Examples
        --------
        >>> readout_properties = ReadoutProperties(
        ...     times=[1, 2, 4, 7, 10], start_time=0.0
        ... )
        >>> readout_properties.non_destructive
        False
        """
        return self._non_destructive

    @property
    def times_linear(self) -> bool:
        """Check if the time intervals between readout samples are uniform.

        Returns
        -------
        bool
            True is all readout steps are equal (i.e., time intervals are linear),
            False otherwise.

        Examples
        --------
        >>> readout_properties = ReadoutProperties(
        ...     times=[1, 2, 4, 7, 10], start_time=0.0
        ... )
        >>> readout_properties.times_linear
        False

        >>> readout_properties = ReadoutProperties(
        ...     times=[1, 2, 3, 4, 5], start_time=0.0
        ... )
        >>> readout_properties.times_linear
        True
        """
        return self._times_linear

    @property
    def time(self) -> float:
        """Get the current time within the readout simulation.

        Returns
        -------
        float
            The current time during the readout process.

        Examples
        --------
        >>> readout_properties = ReadoutProperties(
        ...     times=[1, 2, 3, 4, 5], start_time=0.5
        ... )
        >>> readout_properties.time
        0.0
        """
        return self._time

    @time.setter
    def time(self, value: float) -> None:
        """Set the current time within the readout simulation.

        Parameters
        ----------
        value : float
            The new current time to set in the simulation.
        """
        self._time = value

    @property
    def absolute_time(self) -> float:
        """Get the absolute time relative to the simulation start.

        Returns
        -------
        float
            The absolute time, calculated as `start_time` + `time`.

        Examples
        --------
        >>> readout_properties = ReadoutProperties(
        ...     times=[1, 2, 3, 4, 5], start_time=0.5
        ... )
        >>> readout_properties.absolute_time
        0.5
        """
        return self._start_time + self._time

    @property
    def time_step(self) -> float:
        """Get the step size used for advancing in the simulation.

        Returns
        -------
        float
            The current time step value for advancing time.

        Examples
        --------
        >>> readout_properties = ReadoutProperties(
        ...     times=[1, 2, 3, 4, 5], start_time=0.5
        ... )
        >>> readout_properties.time_step = 1.0
        """
        return self._time_step

    @time_step.setter
    def time_step(self, value: float) -> None:
        """Set the time step size for advancing the simulation.

        Parameters
        ----------
        value : float
            The time step size to set.
        """
        self._time_step = value

    @property
    def read_out(self) -> bool:
        """Get the status of the readout process.

        Returns
        -------
        bool
            True if the readout process is active,
            False otherwise.

        Examples
        --------
        >>> readout_properties = ReadoutProperties(
        ...     times=[1, 2, 3, 4, 5], start_time=0.5
        ... )
        >>> readout_properties.read_out
        True
        """
        return self._read_out

    @read_out.setter
    def read_out(self, value: bool) -> None:
        """Set the readout status.

        Parameters
        ----------
        value : bool
            Boolean flag indicating whether the readout process is active.
        """
        self._read_out = value

    @property
    def pipeline_count(self) -> int:
        """Get the current readout pipeline count.

        This count indicates the number of times the readout process has advanced.

        Returns
        -------
        int
            The number of completed readout steps.
        """
        return self._pipeline_count

    @pipeline_count.setter
    def pipeline_count(self, value: int) -> None:
        """Set the pipeline count for the readout process.

        Parameters
        ----------
        value : int
        The new value for the number of completed readout steps.
        """
        self._pipeline_count = value

    @property
    def is_first_readout(self) -> bool:
        """Check if the current step is the first readout time.

        Returns
        -------
        bool
            True if this is the first readout time,
            False otherwise.

        Examples
        --------
        >>> readout_properties = ReadoutProperties(
        ...     times=[1, 2, 3, 4, 5], start_time=0.5
        ... )
        >>> readout_properties.is_first_readout
        True
        """
        return bool(self.pipeline_count == 0)

    @property
    def is_last_readout(self) -> bool:
        """Check if the current step is the last readout time.

        Returns
        -------
        bool
            True if this is the last readout time, False otherwise.

        Examples
        --------
        >>> readout_properties = ReadoutProperties(
        ...     times=[1, 2, 3, 4, 5], start_time=0.5
        ... )
        >>> readout_properties.is_last_readout
        False
        """
        return bool(self.pipeline_count == (self.num_steps - 1))
