#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Simple models to generate charge due to dark current process."""

import warnings

import numpy as np

from pyxel.detectors import CCD, CMOS
from pyxel.util import set_random_seed

warnings.filterwarnings("once", category=RuntimeWarning, append=True)


def lambda_e(lambda_cutoff: float) -> float:
    """Compute the effective wavelength (lambda_e) based on a detector's wavelength cut-off.

    Parameters
    ----------
    lambda_cutoff : float
        The wavelength Cut-off of the detector in micrometers (µm).

    Returns
    -------
    float
        The effective wavelength (lambda_e) value in micrometers (µm).
    """
    lambda_scale = 0.200847413  # Scaling factor for the correction (µm)
    lambda_threshold = 4.635136423  # Cut-off threshold (µm)
    pwr = 0.544071282  # Power factor for the correction

    if lambda_cutoff < lambda_threshold:
        le = lambda_cutoff / (
            1
            - ((lambda_scale / lambda_cutoff) - (lambda_scale / lambda_threshold))
            ** pwr
        )
    else:
        le = lambda_cutoff

    return le


def average_dark_current_rule07(
    pitch: float,
    temperature: float,
    cut_off: float,
) -> float:
    """Compute the average dark current for a detector using the Rule07 empirical law.

    Parameters
    ----------
    pitch : float
        the pixel size (pitch) the pixel in micrometer (µm).
    temperature : float
        the operating temperature of the detector in Kelvin (K).
    cut_off : float
        the wavelength cut-off of the detector in micrometers (µm).

    Returns
    -------
    float
        The average dark current in electrons per pixel per second (e⁻ pix⁻¹ s⁻¹).

    Notes
    -----
    Based on Rule07 paper by W.E. Tennant Journal of Electronic Materials volume 37, pages1406–1410 (2008).
    """
    c = 1.16  # activation energy factor
    q = 1.602e-19  # Charge of one electron (in A.s)
    k = 1.3806504e-23  # Constant of Boltzmann (in m2.kg/s2/K)

    j0 = 8367  # obtained through fit of experimental data, see paper

    # Energy gap [eV] the optical gap extracted from the mid response cut-off wavelength
    e_c = 1.24 / lambda_e(cut_off)

    # Rule07 exponential relationship for dark current density (in A/cm3)
    rule07 = j0 * np.exp(-c * q * e_c / (k * temperature))

    # Conversion factions
    amp_to_eps = 6.242e18  # Convert amperes to electrons per second (e⁻/s)
    um2_to_cm2 = 1.0e-8  # Convert µm² to cm²

    # Final dark current conversion to electrons per pixel per second (e⁻ pix⁻¹ s⁻¹)
    factor = amp_to_eps * pitch * pitch * um2_to_cm2
    avg_dark_current_rule07 = rule07 * factor

    return avg_dark_current_rule07


def compute_mct_dark_rule07(
    shape: tuple[int, int],
    pitch: float,
    time_step: float,
    temperature: float,
    cut_off: float,
    spatial_noise_factor: float | None = None,
    temporal_noise: bool = True,
) -> np.ndarray:
    """Compute the dark current array for a detector using the Rule07 model.

    Parameters
    ----------
    shape : tuple[int, int]
        Output array shape.
    pitch : float
        the pixel size (pitch) in micrometer. Unit: µm
    time_step : float
       The time interval for dark current accumulation. Unit: s
    temperature : float
        The operating temperature of the detector. Unit: K
    cut_off : float
        the wavelength cut-off of the detector. Unit: µm
    spatial_noise_factor : float, optional
        The fixed pattern noise (FPN) factor applied to simulate spatial
        variations in dark current.
    temporal_noise: bool, optional
        If True, shot noise (Poisson noise) is added to the dark current.

    Returns
    -------
    ndarray
        2D array of Dark current values. Unit: e-

    Notes
    -----
    The function can optionally introduce spatial noise (FPN) and temporal noise (shot noise)
    to simulate real-world detector behavior.
    """

    avg_dark_current_rule07 = average_dark_current_rule07(
        pitch=pitch,
        temperature=temperature,
        cut_off=cut_off,
    )

    # Base dark current signal for each pixel (without noise)
    dark_signal_2d_rule07 = np.ones(shape) * avg_dark_current_rule07 * time_step

    # Add temporal noise (shot noise) if enabled
    if temporal_noise:
        # dark current shot noise
        dark_current_shot_noise_2d_rule07 = np.random.poisson(dark_signal_2d_rule07)
        dark_current_2d_rule07 = dark_current_shot_noise_2d_rule07.astype(float)
    else:
        dark_current_2d_rule07 = dark_signal_2d_rule07

    # Add spatial noise (FPN) if specified
    if spatial_noise_factor is not None:
        # sigma of fpn distribution
        dark_current_fpn_sigma_rule07 = (
            time_step * avg_dark_current_rule07 * spatial_noise_factor
        )

        dark_current_2d_rule07 = dark_current_2d_rule07 * (
            1 + np.random.lognormal(sigma=dark_current_fpn_sigma_rule07, size=shape)
        )

    # Warn if unphysically large values are generated
    if np.isinf(dark_current_2d_rule07).any():
        warnings.warn(
            "Unphysical high value for dark current from fixed pattern noise"
            " distribution will result in inf values. Enable a FWC model to ensure a"
            " physical limit.",
            RuntimeWarning,
            stacklevel=2,
        )

    return dark_current_2d_rule07


def dark_current_rule07(
    detector: CCD | CMOS,
    cutoff_wavelength: float = 2.5,  # unit: µm
    spatial_noise_factor: float | None = None,
    seed: int | None = None,
    temporal_noise: bool = True,
) -> None:
    """Generate charge from dark current process based on the Rule07 model.

    The relationship between dark current and the temperature can often be modeled by exponential function,
    which follows a rule of thumb known as "Rule 7".
    This rule states that the dark current approximately doubles for every 7°K increase in temperature.

    Based on Rule07 paper by W.E. Tennant Journal of Electronic Materials volume 37, pages1406–1410 (2008).

    Parameters
    ----------
    detector : Detector
        The detector object (must be either a CCD or CMOS detector).
    cutoff_wavelength : float, optional. Default: 2.5
        The wavelength cut-off for the detector (default is 2.5 µm). Unit: µm
    spatial_noise_factor : float, optional
        Factor for introducing spatial noise (fixed pattern noise) in the dark current.
    seed : int, optional
        Seed for random number generation to allow reproducibility of noise patterns.
    temporal_noise : bool, optional
        If True, shot noise (Poisson noise) is added to the dark current.

    Raises
    ------
    TypeError
        If the detector is not an instance of either CCD or CMOS.
    ValueError
        If the cut-off wavelength is not within the range of 1.7 to 15.0 µm.

    Notes
    -----
    This function simulates dark current generation in a detector, considering both spatial noise
    (fixed pattern noise) and temporal noise (shot noise).

    For more information, you can find an example here:
    :external+pyxel_data:doc:`examples/models/dark_current/dark_current_rule07`.
    """
    # TODO: investigate on the knee of rule07 for higher 1/le*T values
    if not isinstance(detector, CCD | CMOS):
        raise TypeError("Expecting a CCD or CMOS object for detector.")
    if not (1.7 <= cutoff_wavelength <= 15.0):
        raise ValueError("'cutoff' must be between 1.7 and 15.0.")

    geo = detector.geometry

    pitch = geo.pixel_vert_size  # assuming a square pitch
    temperature = detector.environment.temperature
    time_step = detector.time_step

    with set_random_seed(seed):
        dark_current_array_rule07 = compute_mct_dark_rule07(
            pitch=pitch,
            temperature=temperature,
            cut_off=cutoff_wavelength,
            shape=geo.shape,
            time_step=time_step,
            spatial_noise_factor=spatial_noise_factor,
            temporal_noise=temporal_noise,
        )

    # Add the generated dark current charge to the detector's charge array
    detector.charge.add_charge_array(dark_current_array_rule07)
