# Copyright or © or Copr. Thibault Pichon, CEA Paris-Saclay (2023)
#
# thibault.pichon@cea.fr
#
# This file is part of the Pyxel general simulator framework.
#
# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.


"""Pyxel photon generator models for ARIEL AIRS."""

import logging
from pathlib import Path

import astropy.io.ascii
import numpy as np
import pandas as pd
from astropy import units as u
from astropy.io import fits
from astropy.units import Quantity
from scipy.integrate import cumulative_trapezoid

from pyxel.detectors import Detector
from pyxel.util import resolve_with_working_directory


def read_star_flux_from_file(
    filename: str,
) -> tuple[np.ndarray, np.ndarray]:
    """Read star flux file.

    # TODO: Read the unit from the text file.

    Parameters
    ----------
    filename: type string,
        Name of the target file. Different extension can be considered.

    Returns
    -------
    wavelength: type array 1D
        Wavelength associated with the flux of the star.
    flux: type array 1D
        Flux of the target considered, in  ph/s/m2/µm.
    """
    extension = Path(filename).suffix
    if extension == ".txt":
        wavelength, flux = np.loadtxt(resolve_with_working_directory(filename)).T
        # set appropriate unit here um
        wavelength = wavelength * u.micron
        # set appropriate units
        flux = flux * u.photon / u.s / u.m / u.m / u.micron

    elif extension == ".ecsv":
        data = astropy.io.ascii.read(filename)
        flux = data["flux"].data * data["flux"].unit
        wavelength = data["wavelength"].data * data["wavelength"].unit

    elif extension == ".dat":
        """ExoNoodle file"""
        df_topex = pd.read_csv(filename, header=11)
        wavelength, flux = (
            np.zeros(len(df_topex["wavelength flux "])),
            np.zeros(len(df_topex["wavelength flux "])),
        )
        for i in range(len(df_topex["wavelength flux "])):
            wavelength[i] = float(df_topex["wavelength flux "][i].split("        ")[0])
            conv = 1.51 * 1e3 * 1e4 / wavelength[i]
            flux[i] = (
                float(df_topex["wavelength flux "][i].split("        ")[1])
                * conv
                * 1e-6
            )  # Attention aux unités
        wavelength = wavelength * u.micron
        flux = flux * u.photon / u.s / u.m / u.m / u.micron
    else:
        logging.debug("ERROR while converting, extension not readable")

    return wavelength, flux


def convert_flux(
    wavelength: np.ndarray,
    flux: Quantity,
    telescope_diameter_m1: float,
    telescope_diameter_m2: float,
) -> np.ndarray:
    """Convert the flux of the target in ph/s/µm.

    Parameters
    ----------
    wavelength: 1D array
        Wavelength sampling of the considered target.
    flux: 1D array
        Flux of the target considered in ph/s/m2/µm.
    telescope_diameter_m1: float
        Diameter of the M1 mirror of the TA in m.
    telescope_diameter_m2: float
        Diameter of the M2 mirror of the TA in m.

    Returns
    -------
    conv_flux: 1D array
        Flux of the target considered in ph/s/µm.
    """

    logging.debug("Incident photon flux is being converted into ph/s/um.")
    # use of astropy code
    flux.to(
        u.photon / u.m**2 / u.micron / u.s,
        equivalencies=u.spectral_density(wavelength),
    )

    diameter_m2 = (
        telescope_diameter_m2 * u.meter
    )  # TODO: define a class to describe the optic of the telescope ?
    diameter_m1 = telescope_diameter_m1 * u.meter
    collecting_area = np.pi * diameter_m1 * diameter_m2 / 4
    conv_flux = np.copy(flux) * collecting_area

    return conv_flux


def compute_bandwidth(
    psf_wavelength: Quantity,
) -> tuple[Quantity, Quantity]:
    """Compute the bandwidth for non-even distributed values.

    First we put the poles, each pole is at the center of the previous wave and the next wave.
    We add the first pole and the last pole using symmetry. We get nw+1 poles

    Parameters
    ----------
    psf_wavelength : Quantity
       PSF object.

    Returns
    -------
    bandwidth : quantity array
        Bandwidth. Usually in microns.
    all_poles : quantity array
        Pole wavelengths. Dimension: nw
    """
    poles = (psf_wavelength[1:] + psf_wavelength[:-1]) / 2
    first_pole = psf_wavelength[0] - (psf_wavelength[1] - psf_wavelength[0]) / 2
    last_pole = psf_wavelength[-1] + (psf_wavelength[-1] - psf_wavelength[-2]) / 2
    all_poles = np.concatenate(([first_pole], poles, [last_pole]))
    bandwidth = all_poles[1:] - all_poles[:-1]

    return bandwidth, all_poles


# TODO: Add units
def integrate_flux(
    wavelength: np.ndarray,
    flux: np.ndarray,
    psf_wavelength: Quantity,
) -> np.ndarray:
    """Integrate flux on each bin around the psf.

    The trick is to integrate first, and interpolate after (and not vice-versa).

    Parameters
    ----------
    wavelength : quantity array
        Wavelength. Unit: usually micron. Dimension: small_n.
    flux : quantity array
        Flux. Unit: ph/s/m2/micron. Dimension: big_n.
    psf_wavelength : quantity array
        Point Spread Function per wavelength.

    Returns
    -------
    flux : quantity array
        Flux. UNit: photon/s. Dimension: nw.
    """

    logging.debug("Integrate flux on each bin around the psf...")

    # Set the parameters of the function
    _, all_poles = compute_bandwidth(psf_wavelength)

    # Cumulative count
    cum_sum = cumulative_trapezoid(y=flux, x=wavelength, initial=0)

    # self.wavelength has to quantity: value and units
    # interpolate over psf wavelength
    cum_sum_interp = np.interp(all_poles, wavelength, cum_sum)

    # Compute flux over psf spectral bin
    flux_int = cum_sum_interp[1:] - cum_sum_interp[:-1]

    # Update flux matrix
    flux_int = flux_int  # * flux.unit * wavelength.unit
    flux = np.copy(flux_int)

    return flux


# def multiply_by_transmission(psf, transmission_dict: Mapping[str, Any]) -> None:
#     """The goal of this function is to take into account the flux of the incident star"""
#     for t in transmission_dict.keys():
#         if "M" in t:
#             f = interpolate.interp1d(
#                 transmission_dict[t]["wavelength"],
#                 transmission_dict[t]["reflectivity_eol"],
#             )
#         else:
#             f = interpolate.interp1d(
#                 transmission_dict[t]["wavelength"],
#                 transmission_dict[t]["transmission_eol"],
#             )
#         flux = np.copy(flux) * f(psf.psf_wavelength)
#


def read_psf_from_fits_file(
    filename: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Read psf files depending on simulation and instrument parameters.

    Parameters
    ----------
    filename : str
        Name of the .fits file.

    Returns
    -------
    psf_datacube : ndarray
        3D array, PSF for each wavelength saved as array, one for each wavelength
        waves (1D array) wavelength. Unit: um.
    psf_wavelength : ndarray
        1D array, wavelengths. Unit: um.
    line_pos_psf : ndarray
        1D array, x position of the PSF at each wavelength.
    col_pos_psf : ndarray
        1D array, y position of the PSF at each wavelength.
    """
    # Open fits
    with fits.open(resolve_with_working_directory(filename)) as hdu:
        psf_datacube = hdu[0].data
        table = hdu[1].data

    # Position of the PSF on AIRS window along line
    line_psf_pos = (table["x_centers"]).astype(int)

    # Position of the PSF on AIRS window along col
    col_psf_pos = (table["y_centers"]).astype(int)

    # Wavelength
    psf_wavelength = table["waves"] * u.micron

    logging.debug(
        "PSF Datacube %r %r %r",
        psf_datacube.shape,
        psf_datacube.min(),
        psf_datacube.max(),
    )
    logging.debug(
        "PSF Wavelength %r %r %r",
        psf_wavelength.shape,
        psf_wavelength.min(),
        psf_wavelength.max(),
    )

    return psf_datacube, psf_wavelength, line_psf_pos, col_psf_pos


# TODO: Add units
def project_psfs(
    psf_datacube_3d: np.ndarray,
    line_psf_pos_1d: np.ndarray,
    col_psf_pos,
    flux: np.ndarray,
    row: int,
    col: int,
    expand_factor: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Project each psf on a (n_line_final * self.zoom, n_col_final * self.zoom) pixel image.

    n_line_final, n_col_final = corresponds to window size. It varies with the channel.

    Parameters
    ----------
    psf_datacube_3d : numpy array
        Dimension (nw, n_line, n_col).
    line_psf_pos_1d : numpy array
        Line position of the center of the PSF along AIRS window.
    col_psf_pos : numpy array
        Column position of the center of PSF along AIRS window.
    flux : Quantity
        Unit electron/s dimension big_n.
    row :

    col :

    expand_factor :

    Returns
    -------
    result : Quantity, Quantity
        Dimension ny, nx, spectral image in e-/s. Shape = detector shape.

    """
    nw, n_line, n_col = psf_datacube_3d.shape  # Extract shape of the PSF
    half_size_col, half_size_line = n_col // 2, n_line // 2  # Half size of the PSF

    # photon_incident = np.zeros((detector.geometry.row * expend_factor, detector.geometry.col * expend_factor))
    # photoelectron_generated = np.zeros((detector.geometry.row * expend_factor, detector.geometry.col * expend_factor))
    photon_incident = np.zeros((row * expand_factor, col * expand_factor))
    photoelectron_generated = np.zeros((row * expand_factor, col * expand_factor))

    col_win_middle, line_win_middle = (
        int(col_psf_pos.mean()),
        int(line_psf_pos_1d.mean()),
    )

    for i in np.arange(nw):  # Loop over the wavelength
        # Resize along line dimension
        line1 = (
            line_psf_pos_1d[i]
            - line_win_middle
            + row * expand_factor // 2
            - half_size_line
        )
        line2 = (
            line_psf_pos_1d[i]
            - line_win_middle
            + row * expand_factor // 2
            + half_size_line
        )
        # Resize along col dimension
        col1 = (
            col_psf_pos[i] - col_win_middle + col * expand_factor // 2 - half_size_col
        )
        col2 = (
            col_psf_pos[i] - col_win_middle + col * expand_factor // 2 + half_size_col
        )
        # Derive the amount of photon incident on the detector
        photon_incident[line1:line2, col1:col2] = (
            photon_incident[line1:line2, col1:col2] + psf_datacube_3d[i, :, :] * flux[i]
        )

        # TODO: Here take into account the QE map of the detector, and its dependence with wavelength
        # QE of the detector has to be sampled with the same resolution as the PSF is sampled
        qe = 0.65
        # qe_detector[i]
        photoelectron_generated[line1:line2, col1:col2] = (
            photon_incident[line1:line2, col1:col2].copy() * qe
        )

    # This is the amount of photons incident on the detector
    photon_incident = photon_incident  # * flux.unit

    # This is the amount of photons incident on the detector
    photoelectron_generated = photoelectron_generated * u.electron

    return (rebin_2d(photon_incident, expand_factor)), (
        rebin_2d(photoelectron_generated, expand_factor)
    )


def rebin_2d(
    data: np.ndarray,
    expand_factor: int,
) -> np.ndarray:
    """Rebin as idl.

    Each pixel of the returned image is the sum of zy by zx pixels of the input image.

    Based on:       Rene Gastaud, 13 January 2016
    https://codedump.io/share/P3pB13TPwDI3/1/resize-with-averaging-or-rebin-a-numpy-2d-array
    2017-11-17 : RG and Alan O'Brien  compatibility with python 3 bug452

    Parameters
    ----------
    data : ndarray
        Data with 2 dimensions (image): ny, nx.
    expand_factor : tuple
        Expansion factor is a tuple of 2 integers: zy, zx.

    Returns
    -------
    result : ndarray
        Shrunk in dimension ny/zy, nx/zx.


    Example
    -------
    a = np.arange(48).reshape((6,8))
               rebin2d( a, [2,2])

    """

    # In case asymmetrical zoom is used
    zoom = [expand_factor, expand_factor]

    final_shape = (
        int(data.shape[0] // zoom[0]),
        zoom[0],
        int(data.shape[1] // zoom[1]),
        zoom[1],
    )
    logging.debug("final_shape %r", final_shape)
    result = data.reshape(final_shape).sum(3).sum(1)

    return result


# TODO: Add units
def wavelength_dependence_airs(
    detector: Detector,
    psf_filename: str,
    target_filename: str,
    telescope_diameter_m1: float,
    telescope_diameter_m2: float,
    expand_factor: int,
    time_scale: float = 1.0,
) -> None:
    """Generate the photon over the array according to a specific dispersion pattern (ARIEL-AIRS).

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    psf_filename : string
        The location and the filename where the PSFs are located.
    target_filename : string
        The location and the filename of the target file used in the simulation.
    telescope_diameter_m1 : float
        Diameter of the M1 mirror of the TA in m.
    telescope_diameter_m2 : float
        Diameter of the M2 mirror of the TA in m.
    expand_factor : int
        Expansion factor used.
    time_scale : float
        Time scale in seconds.
    """
    if not isinstance(expand_factor, int):
        raise TypeError("Expecting a 'int' type for 'expand_factor'.")

    if expand_factor <= 0:
        raise ValueError("Expecting a positive value for 'expand_factor'.")

    # Extract information from the PSF
    psf_datacube, psf_wavelength, line_psf_pos, col_psf_pos = read_psf_from_fits_file(
        filename=psf_filename
    )
    # plt.figure()
    # plt.pcolormesh(psf_datacube[10, :, :])
    # plt.title(psf_wavelength[10])

    # Read flux from the fits file
    target_wavelength, target_flux = read_star_flux_from_file(filename=target_filename)

    # convert the flux by multiplying by the area of the detector
    # telescope_diameter_m1, telescope_diameter_m2 = (
    #     1.1,
    #     0.7,
    # )  # in m, TODO to be replaced by Telescope Class ?

    target_conv_flux = convert_flux(
        wavelength=target_wavelength,
        flux=target_flux,
        telescope_diameter_m1=telescope_diameter_m1,
        telescope_diameter_m2=telescope_diameter_m2,
    )
    # Integrate the flux over the PSF spectral bin
    integrated_flux = integrate_flux(
        wavelength=target_wavelength,
        flux=target_conv_flux,
        psf_wavelength=psf_wavelength,
    )  # The flux is now sample similarly to the PSF

    # The Flux can be multiplied here by the optical elements
    # multiply_by_transmission(psf, transmission_dict)
    # #TODO add class to take into account the transmission of the instrument
    # Project the PSF onto the Focal Plane, to get the detector image

    # row, col = 130, 64  # Could be replaced
    # Expend factor used: expand_factor = 18
    _, photo_electron_generated = project_psfs(
        psf_datacube_3d=psf_datacube,
        line_psf_pos_1d=line_psf_pos,
        col_psf_pos=col_psf_pos,
        flux=integrated_flux,
        row=detector.geometry.row,
        col=detector.geometry.col,
        expand_factor=expand_factor,
    )
    # Add the result to the photon array structure
    time_step = 1.0  # ?

    photon_array = photo_electron_generated * (time_step / time_scale)
    # assert photon_array.unit == "electron"

    detector.photon += np.array(photon_array)
