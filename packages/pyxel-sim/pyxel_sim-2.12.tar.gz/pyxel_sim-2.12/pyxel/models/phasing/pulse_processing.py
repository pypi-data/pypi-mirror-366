#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Phase-pulse processing model."""

import astropy.constants as const
import numpy as np

from pyxel.detectors import MKID


def convert_to_phase(
    array_2d: np.ndarray,
    wavelength: float,
    responsivity: float,
    scaling_factor: float = 2.5e2,
) -> np.ndarray:
    """Convert an array of charges into an array of phase pulses.

    Parameters
    ----------
    array_2d : ndarray
    wavelength : float
    responsivity : float
    scaling_factor : float

    Returns
    -------
    ndarray
    """
    from pyxel.models.phasing.mkid_models import SC as sclib  # noqa: N811
    from pyxel.models.phasing.mkid_models import SCtheory as sctheory  # noqa: N813

    if not wavelength > 0.0:
        raise ValueError("Only positive values accepted for wavelength.")
    if not scaling_factor > 0.0:
        raise ValueError("Only positive values accepted for scaling_factor.")
    if not responsivity > 0:
        raise ValueError("Only positive values accepted for responsivity.")

    # Tc = 1.2  # Critical temperature, for Aluminium [K]
    # TD = 433  # Debye temperature, for Aluminium [K]
    # N0 = 1.72e4  # Electronic density of states at Fermi surface, for Aluminium [µeV^-1 µm^-3]
    # lbd0 = 0.092  # Penetration depth at T = 0 [µm] (0.092 for Aluminium, by default)

    # Boltzmann's constant * bath temperature [µeV]
    constant_boltzmann_t0 = 86.17 * 0.2

    # Boltzmann's constant * quasi-particle temperature [µeV]
    constant_boltzmann_t = 86.17 * 0.2

    # Reduced Planck’s constant * angular resonance frequency at T0
    hw0 = 0.6582 * 5 * 2 * np.pi

    ak = 0.0268  # Kinetic inductance fraction
    beta = 2  # = 2 in the thin-film limit (= 1 in the bulk) [CHECK FUNCTION BELOW]
    coupling_quality_factor = 2e4  # Coupling quality factor

    superconductor_volume: sclib.Vol = sclib.Vol(SC=sclib.Al, d=0.05, V=15.0)
    superconductor: sclib.Superconductor = superconductor_volume.SC
    # d = SCvol.d  # Film thickness [µm]
    volume: float = superconductor_volume.V  # Superconductor's volume [µm]

    # kbTc = Tc * const.Boltzmann / const.e * 1e6  # Critical temperature [µeV]
    # kbTD = TD * const.Boltzmann / const.e * 1e6  # Debye's energy [µeV]
    # D0 = 1.76 * kbTc  # BSC relation for the energy gap at
    delta_0: float = sctheory.D(kbT=constant_boltzmann_t, SC=superconductor)

    # Gives the read frequency such that it is equal to the resonance frequency
    hwread: float = sctheory.hwread(
        hw0=hw0,
        kbT0=constant_boltzmann_t0,
        ak=ak,
        kbT=constant_boltzmann_t,
        D=delta_0,
        SCvol=superconductor_volume,
    )

    s_0: tuple[float, float] = sctheory.cinduct(
        hw=hwread, D=delta_0, kbT=constant_boltzmann_t
    )
    qi_0: float = 2 * s_0[1] / (ak * beta * s_0[0])
    q: float = qi_0 * coupling_quality_factor / (qi_0 + coupling_quality_factor)

    row_of_pixels, column_of_pixels = array_2d.shape
    linearised_delta_a = np.zeros((row_of_pixels, column_of_pixels))
    linearised_theta = np.zeros((row_of_pixels, column_of_pixels))

    for row_idx in range(row_of_pixels):
        for col_idx in range(column_of_pixels):
            nqp: float = array_2d[row_idx, col_idx]

            kb_teff = sctheory.kbTeff(nqp_value=nqp / volume, SC=superconductor)

            # Energy gap
            d = sctheory.D(kbT=kb_teff, SC=superconductor)
            s1, s2 = sctheory.cinduct(hw=hwread, D=d, kbT=kb_teff)

            # Calculate changes in amplitude and phase
            linearised_delta_a[row_idx, col_idx] = (
                ak * beta * q * (s1 - s_0[0]) / s_0[1]
            )
            linearised_theta[row_idx, col_idx] = -ak * beta * q * (s2 - s_0[1]) / s_0[1]

    output = linearised_theta * scaling_factor

    return output.astype("float64")


def pulse_processing(
    detector: MKID,
    wavelength: float,
    responsivity: float,
    scaling_factor: float = 2.5e2,
    t_c: float = 1.26,
    eta_pb: float = 0.59,
    f: float = 0.2,
) -> None:
    """Phase-pulse processor.

    This model is derived from :cite:p:`Dodkins`; more information can be found on the website :cite:p:`Mazin`.

    Parameters
    ----------
    detector : MKID
        Pyxel :term:`MKID` detector object.
    wavelength : float
        Wavelength. Unit: um.
    responsivity : float
        Responsivity of the pixel.
    scaling_factor : float
        Scaling factor taking into account the missing pieces of superconducting physics,
        as well as the resonator quality factor, the bias power,
        the quasi-particle losses, etc.
    t_c : float [used also in /pyxel/models/readout_electronics/dead_time.py]
        Material dependent critical temperature. Unit: K
    eta_pb : float
        Superconducting pair-breaking efficiency.
    f : float
        Fano's factor.
    """
    if not isinstance(detector, MKID):
        raise TypeError("Expecting an MKID object for the detector.")
    if not wavelength > 0.0:
        raise ValueError("Only positive values accepted for wavelength.")

    detector.phase.array = convert_to_phase(
        array_2d=detector.charge.array,
        wavelength=wavelength,
        responsivity=responsivity,
        scaling_factor=scaling_factor,
    )

    # IN FIERI:

    # Boltzmann's constant [J K^-1]
    boltzmann_cst: float = const.k_B.value

    # Planck's constant [J s]
    planck_cst: float = const.h.value

    # Speed of light in vacuum [m s^-1]
    c_cst: float = const.c.value

    delta = (
        1.76 * boltzmann_cst * t_c
    )  # [used also in /pyxel/models/readout_electronics/dead_time.py]

    r = np.sqrt(eta_pb * planck_cst * c_cst / (wavelength * 1.0e-6 * f * delta)) / (
        2.0 * np.sqrt(2.0 * np.log(2.0))
    )

    sigma_lambda = wavelength / (r * (2 * np.sqrt(2 * np.log(2))))

    mu, sigma = wavelength, sigma_lambda

    np.random.seed(42)

    _gaussian_samples = np.random.normal(
        mu, sigma, detector.phase.array[0][0]
    )  # To be continued...
