#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Models to generate charge due to dark current process."""

import warnings
from typing import Literal

import numpy as np
from astropy import constants as const
from astropy.units import Quantity, Unit

from pyxel.detectors import Detector
from pyxel.util import set_random_seed


def calculate_band_gap_varshni(
    band_gap_0: Quantity,
    alpha: Quantity,
    beta: Quantity,
    temperature: Quantity,
) -> Quantity:
    """Return band gap based on Varshni empirical expression.

    Parameters
    ----------
    band_gap_0 : Quantity
        Parameter E_0. Unit: eV
    alpha : Quantity
        Alpha parameter. Unit: eV/K
    beta : Quantity
        Beta parameter. Unit: K
    temperature : Quantity
        Temperature. Unit K

    Notes
    -----
    This function is based on :cite:p:`VARSHNI1967149`

    Returns
    -------
    Quantity
        Band gap value. Unit: eV
    """

    gap = band_gap_0 - (alpha * temperature**2) / (temperature + beta)

    return gap.to("eV")


def calculate_band_gap(
    temperature: Quantity,
    material: Literal["silicon"],
) -> Quantity:
    """Estimate the band gap based on Varshni empirical expression.

    This function calculates the band of a specified semiconductor material.

    Parameters
    ----------
    temperature : Quantity
        The temperature at which the band gap is to be estimated.
        Unit: Kelvin

    material : str
        The material for which the band gap is to be estimated.
        Currently, only 'silicon' is supported.

    Returns
    -------
    Quantity
        The estimated band gap value.
        Unit: electron volts (eV)

    Raises
    ------
    ValueError
        If an unsupported material is specified.

    Notes
    -----
    The Varshni empirical expression (sis given by:
    Eg(T) = Eg(0) - α * T^2 / (T + β)
    where:
        - Eg(T) is the band gap at temperature T,
        - Eg(0) is the band gap at absolute zero temperature,
        - α is a temperature coefficient,
        - β is a fitting parameter.
    """
    if material == "silicon":
        # Constants for silicon based on literature values
        band_gap_0 = Quantity(1.1557, unit="eV")
        alpha = Quantity(7.021e-4, unit="eV / K")
        beta = Quantity(1108.0, unit="K")
    else:
        raise ValueError(f"Unknown 'material': {material!r}")

    # Calculate band gap using Varshni empirical expression
    return calculate_band_gap_varshni(
        band_gap_0=band_gap_0,
        alpha=alpha,
        beta=beta,
        temperature=temperature,
    )


def simulate_dark_signal(
    temperature: Quantity,
    pixel_area: Quantity,
    figure_of_merit: Quantity,
    band_gap: Quantity,
    band_gap_room_temperature: Quantity,
) -> Quantity:
    """Compute average dark current.

    Parameters
    ----------
    temperature : Quantity
        Temperature. Unit: K
    pixel_area : Quantity
        Pixel area. Unit: um^2/pix
    figure_of_merit : Quantity
        Dark current figure of merit. Unit: nA/cm^2
    band_gap : Quantity
        Semiconductor band_gap. Unit: eV
    band_gap_room_temperature : Quantity
        Semiconductor band gap at 300K. If none, the one for silicon is used. Unit: eV

    Returns
    -------
    Quantity
        Average dark current. Unit: e-/pixel/s
    """

    # boltzmann constant (in J / K)
    k_b: Quantity = Quantity(const.k_B)

    # electron charge (in C / electron)
    e_0: Quantity = Quantity(const.e) / Unit("electron")

    room_temperature = Quantity(300, unit="K")
    room_temperature_factor: Quantity = (room_temperature ** (3 / 2)) * np.exp(
        -band_gap_room_temperature / (2 * k_b * room_temperature)
    )  # unit: K^{3/2}

    temperature_factor: Quantity = temperature ** (3 / 2) * np.exp(
        -band_gap / (2 * k_b * temperature)
    )  # unit: K^{3/2}

    cste_dark_signal: Quantity = ((figure_of_merit * pixel_area) / e_0).to(
        "electron / (pix s)"
    )

    avg_dark_current: Quantity = (
        cste_dark_signal * temperature_factor / room_temperature_factor
    )  # unit: electron / (pix s)

    return avg_dark_current.to("electron / (pix s)")


def compute_dark_current(
    shape: tuple[int, int],
    time_step: Quantity,
    temperature: Quantity,
    pixel_area: Quantity,
    figure_of_merit: Quantity,
    band_gap: Quantity,
    band_gap_room_temperature: Quantity,
    spatial_noise_factor: float | None = None,
    temporal_noise: bool = True,
) -> np.ndarray:
    """Compute dark current.

    Based on:
    Konnik, Mikhail V. and James S. Welsh.
    “High-level numerical simulations of noise in CCD and CMOS photosensors: review and tutorial.”
    ArXiv abs/1412.4031 (2014): n. pag.

    Parameters
    ----------
    shape : tuple
        Output array shape.
    time_step : Quantity
        Time step. Unit: s
    temperature : Quantity
        Temperature. Unit: K
    pixel_area : Quantity
        Pixel area. Unit: um^2
    figure_of_merit : Quantity
        Dark current figure of merit. Unit: nA/cm^2
    band_gap : Quantity
        Semiconductor band_gap. Unit: eV
    band_gap_room_temperature : Quantity
        Semiconductor band gap at 300K. If none, the one for silicon is used. Unit: eV
    spatial_noise_factor: float
        Dark current fixed pattern noise factor.
    temporal_noise: bool
        Shot noise.

    Returns
    -------
    ndarray
        Dark current values. Unit: e-
    """
    # Simulation of dark signal (in electron / pixel)
    avg_dark_current: Quantity = simulate_dark_signal(
        temperature=temperature,
        pixel_area=pixel_area,
        figure_of_merit=figure_of_merit,
        band_gap=band_gap,
        band_gap_room_temperature=band_gap_room_temperature,
    )  # unit: electron / s

    dark_signal_2d: Quantity = (
        np.ones(shape) * avg_dark_current * time_step
    )  # unit: electron / pix

    # Simulation of dark current shot noise (in electron / pixel)
    if temporal_noise:
        # dark current shot noise
        # TODO: Use function 'calculate_simple_dark_current'
        dark_current_shot_noise_2d = np.random.poisson(np.asarray(dark_signal_2d))
        dark_current_2d = Quantity(dark_current_shot_noise_2d, unit="electron / pix")
    else:
        dark_current_2d = dark_signal_2d

    # Simulation of dark current fixed pattern noise (in electron / pixel)
    if spatial_noise_factor is not None:
        # sigma of fixed pattern noise distribution
        dark_current_fpn_sigma = time_step * avg_dark_current * spatial_noise_factor

        with np.errstate(all="ignore"):
            dark_current_fpn_2d = np.random.lognormal(
                sigma=np.asarray(dark_current_fpn_sigma),
            )

        dark_current_2d = dark_current_2d * (1 + dark_current_fpn_2d)

    if np.isinf(dark_current_2d).any():
        warnings.warn(
            "Unphysical high value for dark current from fixed pattern noise"
            " distribution will result in inf values. Enable a FWC model to ensure a"
            " physical limit.",
            RuntimeWarning,
            stacklevel=2,
        )

    return dark_current_2d


def dark_current(
    detector: Detector,
    figure_of_merit: float,
    spatial_noise_factor: float | None = None,
    band_gap: float | None = None,
    band_gap_room_temperature: float | None = None,
    seed: int | None = None,
    temporal_noise: bool = True,
) -> None:
    """Add dark current to the detector charge.

    Based on:
    Konnik, Mikhail V. and James S. Welsh.
    “High-level numerical simulations of noise in CCD and CMOS photosensors: review and tutorial.”
    ArXiv abs/1412.4031 (2014): n. pag.

    Parameters
    ----------
    detector : Detector
        Pyxel detector object.
    figure_of_merit : float
        Dark current figure of merit. Unit: nA/cm^2
    spatial_noise_factor : float
        Dark current fixed pattern noise factor.
    band_gap : float, optional
        Semiconductor band_gap. If none, the one for silicon is used. Unit: eV
    band_gap_room_temperature : float, optional
        Semiconductor band gap at 300K. If none, the one for silicon is used. Unit: eV
    seed : int, optional
        Random seed.
    temporal_noise : bool, optional
        Shot noise.

    Notes
    -----
    For more information, you can find an example here:
    :external+pyxel_data:doc:`examples/models/dark_current/dark_current_Si`.
    """
    geo = detector.geometry
    pixel_vert_size = Quantity(geo.pixel_vert_size, unit="um")
    pixel_horz_size = Quantity(geo.pixel_horz_size, unit="um")

    pixel_area = (pixel_vert_size * pixel_horz_size) / Unit("pix")  # unit: um^2/pix
    temperature = Quantity(detector.environment.temperature, unit="K")
    time_step = Quantity(detector.time_step, unit="s")

    if band_gap and band_gap_room_temperature:
        final_band_gap = Quantity(band_gap, unit="eV")
        final_band_gap_room_temperature = Quantity(band_gap_room_temperature, unit="eV")
    elif band_gap or band_gap_room_temperature:
        raise ValueError(
            "Both parameters 'band_gap' and 'band_gap_room_temperature' must be defined."
        )
    else:
        final_band_gap = calculate_band_gap(temperature, material="silicon")  # unit: eV

        room_temperature = Quantity(300, unit="K")
        final_band_gap_room_temperature = calculate_band_gap(
            temperature=room_temperature,
            material="silicon",
        )  # unit: eV

    with set_random_seed(seed):
        with warnings.catch_warnings():
            warnings.filterwarnings(action="ignore", category=RuntimeWarning)

            dark_current_2d = compute_dark_current(
                shape=geo.shape,
                time_step=time_step,
                temperature=temperature,
                pixel_area=pixel_area,
                figure_of_merit=Quantity(figure_of_merit, unit="nA / cm2"),
                band_gap=final_band_gap,
                band_gap_room_temperature=final_band_gap_room_temperature,
                spatial_noise_factor=spatial_noise_factor,
                temporal_noise=temporal_noise,
            )  # unit: electron / pix

    detector.charge.add_charge_array(np.asarray(dark_current_2d))
