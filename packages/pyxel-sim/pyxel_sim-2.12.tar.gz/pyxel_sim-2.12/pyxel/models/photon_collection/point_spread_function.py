#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


"""Model for loading PSF from file."""

from pathlib import Path

import numpy as np
import xarray as xr
from astropy import units as u
from astropy.convolution import convolve_fft

from pyxel.detectors import Detector
from pyxel.inputs import load_image
from pyxel.inputs.loader import load_image_v2, load_table_v2

# from astropy.units import Quantity


def apply_psf(
    array: np.ndarray, psf: np.ndarray, normalize_kernel: bool = True
) -> np.ndarray:
    """Convolve the input array with the point spread function kernel.

    Parameters
    ----------
    array : ndarray
        Input array.
    psf : ndarray
        Convolution kernel.
    normalize_kernel : bool
        Normalize kernel.

    Returns
    -------
    ndarray
    """

    mean = np.mean(array)

    array_2d = convolve_fft(
        array,
        kernel=psf,
        boundary="fill",
        fill_value=mean,
        normalize_kernel=normalize_kernel,
    )

    return array_2d


def load_psf(
    detector: Detector, filename: str | Path, normalize_kernel: bool = True
) -> None:
    """Load a point spread function from file and convolve the photon array with the PSF.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    filename : Path or str
        Input filename of the point spread function.
    normalize_kernel : bool
        Normalize kernel.

    Notes
    -----
    For more information, you can find an example here:
    :external+pyxel_data:doc:`examples/models/scene_generation/tutorial_example_scene_generation`.
    """
    psf = load_image(filename)

    detector.photon.array = apply_psf(
        array=detector.photon.array, psf=psf, normalize_kernel=normalize_kernel
    )


def load_wavelength_psf(
    detector: Detector,
    filename: str | Path,
    wavelength_col: str,
    y_col: str,
    x_col: str,
    wavelength_table_name: str,
    normalize_kernel: bool = True,
):
    """Read psf files depending on simulation and instrument parameters.

    Parameters
    ----------
    detector : Detector
            Pyxel Detector object.
    filename : Path or str
        Input filename of the point spread function.
    wavelength_col : str
        Dimension name in the file that contains the wavelength information.
    y_col : str
        Dimension name in the file that contains the y information.
    x_col : str
        Dimension name in the file that contains the x information.
    wavelength_table_name : str
        Column name in the file that contains the wavelength information.
    normalize_kernel : bool
            Normalize kernel.
    """
    # load fits image
    data = load_image_v2(
        filename=filename,
        data_path=0,  # TODO: remove magical value
        rename_dims={"wavelength": wavelength_col, "y": y_col, "x": x_col},
    )

    # load wavelength information from table
    table = load_table_v2(
        filename=filename,
        data_path=1,  # TODO: remove magical value
        rename_cols={"wavelength": wavelength_table_name},
    )

    # save table information into DataArray.
    wavelength_da = xr.DataArray(
        table.wavelength,
        dims=["wavelength"],
        coords={"wavelength": table.wavelength},
        attrs={"units": u.nm.to_string("unicode")},
    )
    # save image information into DataArray with wavelength info from table.
    da = xr.DataArray(
        np.asarray(data, dtype=float),
        dims=["wavelength", "y", "x"],
        coords={"wavelength": wavelength_da},
    )

    # interpolate array along wavelength dimension
    interpolated_array: xr.DataArray = da.interp_like(detector.photon.array_3d)

    # drop nan values.
    kernel: xr.DataArray = interpolated_array.dropna(dim="wavelength", how="any")

    integrated: xr.DataArray = kernel.integrate(coord="wavelength")

    mean: xr.DataArray = integrated.mean(dim=["y", "x"])

    # TODO check that kernel size is not to large and kernel has 3 dimensions.
    # if kernel.shape > (200, 50, 50):
    #     raise ValueError("Input PSF used as kernel to convolute with input photon arrat needs to be smaller than "
    #                      "(200, 50, 50). Please reduce the size of the PSF input file, e.g. "
    #                      "with skimage.transform.resize(image, (200, 10, 10)).")

    # convolve the input 3d photon array with the psf kernel
    array_3d: np.ndarray = convolve_fft(
        detector.photon.array_3d.to_numpy(),
        kernel=kernel.to_numpy(),
        boundary="fill",
        fill_value=float(mean),
        normalize_kernel=normalize_kernel,
    )

    # save psf into a DataArray
    psf = xr.DataArray(
        array_3d,
        dims=["wavelength", "y", "x"],
        coords={"wavelength": interpolated_array.wavelength},
    )

    # integrated = psf.integrate(coord="wavelength")

    detector.photon.array_3d = psf
