#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Fitness functions for model fitting."""

import numba
import numpy as np


@numba.njit
def sum_of_abs_residuals(
    simulated: np.ndarray,
    target: np.ndarray,
    weighting: np.ndarray,
) -> float:
    """Calculate the sum of absolute residuals between simulated and target values.

    Parameters
    ----------
    simulated : np.ndarray
        An array containing simulated values.
    target : np.ndarray
        An array containing target (observed) values.
    weighting : np.ndarray
        An array containing weights for each data point.
        These weights adjust the contribution of each residual
        to the final sum.

    Returns
    -------
    float
        The sum of absolute residuals, considering the provided weighting.
    """
    diff = target - simulated
    diff *= weighting

    result = float(np.nansum(np.abs(diff)))
    return result


@numba.njit
def sum_of_squared_residuals(
    simulated: np.ndarray,
    target: np.ndarray,
    weighting: np.ndarray,
) -> float:
    """Calculate the sum of squared residuals between simulated and target values.

    Parameters
    ----------
    simulated : np.ndarray
        An array containing simulated values.
    target : np.ndarray
        An array containing target (observed) values.
    weighting : np.ndarray
        An array containing weights for each data point.
        These weights adjust the contribution of each squared residual
        to the final sum.

    Returns
    -------
    float
        The sum of squared residuals, considering the provided weighting.
    """
    diff = target - simulated
    diff_square = diff * diff
    diff_square *= weighting

    result = float(np.nansum(diff_square))
    return result


@numba.njit
def reduced_chi_squared(
    simulated: np.ndarray,
    target: np.ndarray,
    weighting: np.ndarray,
    free_parameters: int,
) -> float:
    r"""Compute the reduced chi-square error statistic.

    Notes
    -----
    You can find more information at this link
    https://en.wikipedia.org/wiki/Goodness_of_fit

    Parameters
    ----------
    simulated : np.ndarray
        An array containing simulated values.
    target : np.ndarray
        An array containing target (observed) values.
    weighting : np.ndarray
        An array containing weights for each data point.
        These weights adjust the contribution of each squared deviation
        to the final statistic.
    free_parameters : int
        Number of free parameters in the model.

    Returns
    -------
    float
        The reduced :math:`\chi^{2}`.
    """
    diff = target - simulated
    deviation2 = np.square(diff / weighting)

    size = np.isfinite(diff).sum()

    degrees_of_freedom = size - free_parameters
    reduced_chi2 = float(np.nansum(deviation2)) / degrees_of_freedom

    return reduced_chi2
