#   Copyright (c) European Space Agency, 2020.
#  #
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.

"""Simple model to convert photon into photo-electrons using QE(-map) inside detector."""

from pathlib import Path
from typing import TYPE_CHECKING, TypeVar

import numpy as np
import xarray as xr

from pyxel.detectors import Detector
from pyxel.inputs.loader import load_dataarray, load_table_v2

if TYPE_CHECKING:
    import pandas as pd

# from pyxel.models.charge_generation.photoelectrons import apply_qe

T = TypeVar("T", xr.DataArray, xr.Dataset)


def interpolate_dataset(
    input_dataset: T,
    input_array: xr.DataArray,
) -> T:
    """Interpolate xr.Dataset to the resolution of xr.DataArray.

    Parameters
    ----------
    input_dataset : xr.Dataset or xr.Dataarray
        Input dataset to interpolate.
    input_array : xr.Dataarray
        Input data on which the input dataset is interpolated to.

    Returns
    -------
    xr.Dataset or xr.DataArray
    """
    interpolated_ds = input_dataset.interp_like(input_array)

    return interpolated_ds


def apply_wavelength_qe(
    photon_array: xr.DataArray,
    qe_array: xr.DataArray,
    # binomial_sampling = False,
    # TODO: add option for binominal_sampling. See pyxel.models.charge_generation.photoelectrons.apply_qe()
) -> xr.DataArray:
    """Apply wavelength dependent QE to photon array to convert to charge array.

    Parameters
    ----------
    photon_array : xr.DataArray
    qe_array : xr.DataArray

    Returns
    -------
    xr.DataArray
    """

    charge_array = photon_array * qe_array

    return charge_array


def integrate_charge(input_array: xr.DataArray) -> xr.DataArray:
    """Convert 3D charge to 2D charge with integration along coordinate wavelength.

    Parameters
    ----------
    input_array: xr.DataArray
        Input 3D charge array with dimensions wavelength, y, x.

    Returns
    -------
    xr.DataArray
    """
    integrated_charge: xr.DataArray = input_array.integrate(coord="wavelength")

    return integrated_charge


def apply_qe_curve(
    detector: Detector,
    filename: str | Path,
    wavelength_col_name: str | int,
    qe_col_name: str | int,
) -> None:
    """Apply wavelength dependent QE with loading a file.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    filename : str or Path
        CSV File path.
    wavelength_col_name : str
        Column name of wavelength in loaded file.
    qe_col_name : str
        Column name of quantum efficiency in loaded file.
    """

    df: pd.DataFrame = load_table_v2(
        filename=filename,
        rename_cols={"wavelength": wavelength_col_name, "QE": qe_col_name},
        header=True,
    )

    qe_curve_ds: xr.Dataset = df.set_index("wavelength").to_xarray()

    # interpolate the qe_curve wavelength data to the resolution of the photon3D data.
    qe_interpolated: xr.Dataset = interpolate_dataset(
        input_dataset=qe_curve_ds,
        input_array=detector.photon.array_3d,
    )

    if not np.all(
        (0 <= qe_interpolated["QE"].values) & (qe_interpolated["QE"].values <= 1)
    ):
        raise ValueError("Quantum efficiency values not between 0 and 1.")

    # apply QE
    foo: xr.DataArray = qe_interpolated["QE"]
    detector_charge: xr.DataArray = apply_wavelength_qe(
        photon_array=detector.photon.array_3d, qe_array=foo
    )

    # integrate charge along coordinate wavelength
    integrated_charge: xr.DataArray = integrate_charge(input_array=detector_charge)

    # get data from xr.DataArray
    new_charge: np.ndarray = np.asarray(integrated_charge)

    detector.charge.add_charge_array(new_charge)


# TODO: refactor with 2d and give option of wavelength to go for 3d
# TODO: unit test to check that file dim and detector are the same
def conversion_with_3d_qe_map(
    detector: Detector,
    filename: str | Path,
    # position: tuple[int, int] = (0, 0),
    # align: Optional[
    #     Literal["center", "top_left", "top_right", "bottom_left", "bottom_right"]
    # ] = None,
    # seed: Optional[int] = None,
) -> None:
    """Generate charge from incident photon via photoelectric effect.

    Model converts photon to charge using custom :term:`QE` map for different wavelengths.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    filename : str or Path
        File path.
    """
    # load 3D QE-map as dataarray from file
    qe_dataarray: xr.DataArray = load_dataarray(filename=filename)

    # interpolate the qe_curve wavelength data to the resolution of the photon3D data.
    qe_interpolated: xr.DataArray = interpolate_dataset(
        input_dataset=qe_dataarray,
        input_array=detector.photon.array_3d,
    )

    # apply QE
    detector_charge: xr.DataArray = apply_wavelength_qe(
        photon_array=detector.photon.array_3d,
        qe_array=qe_interpolated,
    )

    # integrate charge along coordinate wavelength
    integrated_charge: xr.DataArray = integrate_charge(input_array=detector_charge)

    # get data from xr.DataArray
    new_charge: np.ndarray = np.asarray(integrated_charge)

    detector.charge.add_charge_array(new_charge)
