#   Copyright (c) European Space Agency, 2020.
#  #
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.

"""Convert scene to photon with simple collection model."""

import astropy.units as u
import numpy as np
import xarray as xr
from astropy import wcs
from astropy.coordinates import SkyCoord
from astropy.units import Quantity

from pyxel.data_structure import Scene, SceneCoordinates
from pyxel.detectors import Detector, WavelengthHandling


def extract_wavelength(
    scene: Scene,
    wavelengths: xr.DataArray,
) -> xr.Dataset:
    """Extract xarray Dataset of Scene for selected wavelength band.

    Parameters
    ----------
    scene : Scene
        Pyxel scene object.
    wavelengths : WavelengthHandling
        Selected wavelength band. Unit: nm.

    Returns
    -------
    selected_data : xr.Dataset

    Examples
    --------
    >>> scene = Scene(...)
    >>> extract_wavelength(scene=scene, wavelength_band=[500, 900])
    <xarray.Dataset>
    Dimensions:     (ref: 345, wavelength: 201)
    Coordinates:
      * ref         (ref) int64 0 1 2 3 4 5 6 7 ... 337 338 339 340 341 342 343 344
      * wavelength  (wavelength) float64 500.0 502.0 504.0 ... 896.0 898.0 900.0
    Data variables:
        x           (ref) float64 2.057e+05 2.058e+05 ... 2.031e+05 2.03e+05
        y           (ref) float64 8.575e+04 8.58e+04 ... 8.795e+04 8.807e+04
        weight      (ref) float64 11.49 14.13 15.22 14.56 ... 15.21 11.51 8.727
        flux        (ref, wavelength) float64 0.2331 0.231 0.2269 ... 2.213 2.212
    """

    # retrieve scene data, convert it to xarray and interpolate it
    interpolated_wavelengths = scene.to_xarray().interp(wavelength=wavelengths)

    # get dataset with x, y, weight and flux of scene for selected wavelength band.
    # selected_data: xr.Dataset = data.sel(
    #     wavelength=interpolated_wavelengths["wavelength"]
    # )

    return interpolated_wavelengths


def integrate_flux(
    flux: xr.DataArray,
) -> xr.DataArray:
    """Integrate flux in photon/(s nm cm2) along the wavelength band in nm and return integrated flux in photon/(s cm2).

    Parameters
    ----------
    flux : xr.DataArray
        Flux. Unit: photon/(s nm cm2).

    Returns
    -------
    integrated_flux : xr.DataArray
        Flux integrated alaong wavelangth band. Unit: photon/(s cm2).

    Examples
    --------
    >>> flux
    <xarray.DataArray 'flux' (ref: 345, wavelength: 201)>
    array([[0.23309256, 0.23099403, 0.22690838, ..., 0.74632666, 0.74254087,
            0.74107508],
           [0.02540123, 0.02539306, 0.02532492, ..., 0.02315146, 0.02275346,
            0.02240911],
           [0.00848251, 0.00849082, 0.00835927, ..., 0.01687145, 0.01677347,
            0.01674323],
           ...,
           [0.0086873 , 0.00874152, 0.0088429 , ..., 0.01047889, 0.01037253,
            0.01032473],
           [0.28250153, 0.27994777, 0.27599212, ..., 0.30550521, 0.30414266,
            0.30421148],
           [3.82353376, 3.86376387, 3.88179622, ..., 2.22050587, 2.21307412,
            2.21216093]])
    Coordinates:
      * ref         (ref) int64 0 1 2 3 4 5 6 7 ... 337 338 339 340 341 342 343 344
      * wavelength  (wavelength) float64 500.0 502.0 504.0 ... 896.0 898.0 900.0
    Attributes:
        units:    ph / (cm2 nm s)
    >>> integrate_flux(flux=flux)
    <xarray.DataArray 'flux' (ref: 345)>
    array([2.13684421e+02, 1.01716326e+01, 5.69110647e+00, 1.17371054e+01,
           2.55767948e+01, 6.91026764e+00, 3.79706245e+00, 1.04048130e+01,
           ...
           6.00547211e+00, 6.19314865e+00, 9.97548328e+00, 5.88036380e+00,
           1.10089431e+01, 1.40244956e+01, 4.23104795e+00, 1.28482189e+02,
           1.18302668e+03])
    Coordinates:
      * ref      (ref) int64 0 1 2 3 4 5 6 7 8 ... 337 338 339 340 341 342 343 344
    Attributes:
        units:    ph / (cm2 s)
    """
    # integrate flux along coordinate wavelength
    integrated_flux = flux.integrate(coord="wavelength")
    integrated_flux.attrs["units"] = str(u.Unit(flux.units) * u.nm)

    return integrated_flux


def convert_flux(
    flux: Quantity,
    t_exp: Quantity,
    aperture: Quantity,
) -> Quantity:
    """Convert flux in ph/(s cm2) to ph OR in ph/(s nm cm2) to ph/nm.

    Parameters
    ----------
    flux : Quantity
        Flux. Unit: ph/(s cm2).
    t_exp : Quantity
        Exposure time. Unit: s.
    aperture : Quantity
        Collecting area of the telescope. Unit: m.

    Returns
    -------
    Quantity
        Converted flux in ph OR ph/nm.

    Examples
    --------
    >>> flux
     <Quantity [0.037690712, 0.041374086, 0.03988154, …,
     0.79658112, 0.80078535, 0.83254124] ph/s cm2>
    >>> convert_flux(flux=flux, t_exp=6000 * u.s, aperture=0.1267 * u.m)
    <Quantity  [1362360.7, 1284980.7, 1188073.3, …,
    1357639.3, 1371451.7, 1434596.3] ph>
    """
    # TODO: check aperture factor 1e2 correct?!
    # TODO: add unit test.
    col_area = np.pi * (aperture * 1e2 / 2) ** 2
    flux_converted = flux * t_exp * col_area

    return flux_converted


def project_objects_to_detector(
    scene_data: xr.Dataset,
    pixel_scale: Quantity,
    rows: int,
    cols: int,
) -> xr.Dataset:
    """
    Project objects onto detector. Converting scene from arcsec to detector coordinates.

    Parameters
    ----------
    scene_data : xr.Dataset
        Scene dataset with wavelength and flux information to project onto detector.
    pixel_scale : Quantity
        Pixel sclae of instrument. Unit: arcsec/pixel.
    rows : int
        Rows of detector.
    cols : int
        Columns of detector.

    Returns
    -------
     projected : Dataset
        Projected objects in detector coordinates.

    Examples
    --------
    >>> scene_data
    <xarray.Dataset>
    Dimensions:            (ref: 345, wavelength: 201)
    Coordinates:
      * ref                (ref) int64 0 1 2 3 4 5 6 ... 338 339 340 341 342 343 344
      * wavelength         (wavelength) float64 500.0 502.0 504.0 ... 898.0 900.0
    Data variables:
        x                  (ref) float64 2.057e+05 2.058e+05 ... 2.031e+05 2.03e+05
        y                  (ref) float64 8.575e+04 8.58e+04 ... 8.795e+04 8.807e+04
        weight             (ref) float64 11.49 14.13 15.22 ... 15.21 11.51 8.727
        flux               (ref, wavelength) float64 0.2331 0.231 ... 2.213 2.212
        converted_flux     (ref) float64 1.616e+08 7.695e+06 ... 9.719e+07 8.949e+08
        detector_coords_x  (ref) float64 1.307e+03 1.252e+03 ... 2.748e+03 2.809e+03
        detector_coords_y  (ref) float64 1.454e+03 1.487e+03 ... 2.79e+03 2.859e+03
    >>> project_objects_to_detector(
    ...     selected_data=selected_data,
    ...     pixel_scale=Quantity(1.65, unit="arcsec / pix"),
    ...     rows=4096,
    ...     cols=4132,
    ... )
    array([[0., 0., 0., ..., 0., 0., 0.],
           [0., 0., 0., ..., 0., 0., 0.],
           [0., 0., 0., ..., 0., 0., 0.],
           ...,
           [0., 0., 0., ..., 0., 0., 0.],
           [0., 0., 0., ..., 0., 0., 0.],
           [0., 0., 0., ..., 0., 0., 0.]])
    """
    # we project the stars in the FOV:
    stars_coords = SkyCoord(
        Quantity(scene_data["x"].values, unit="arcsec"),
        Quantity(scene_data["y"].values, unit="arcsec"),
        frame="icrs",
    )

    # coordinates of telescope pointing
    # Extract parameters from 'scene'
    scene_coord: SceneCoordinates = SceneCoordinates.from_dataset(scene_data)
    telescope_ra: Quantity = scene_coord.right_ascension
    telescope_dec: Quantity = scene_coord.declination
    # fov = scene_coord.fov

    # telescope_ra: Quantity = (scene_data["x"].values * u.arcsec).mean()
    # telescope_dec: Quantity = (scene_data["y"].values * u.arcsec).mean()
    coords_detector = SkyCoord(ra=telescope_ra, dec=telescope_dec, unit="degree")

    # using World Coordinate System (WCS) to convert to pixel
    # more info: https://heasarc.gsfc.nasa.gov/docs/fcg/standard_dict.html
    w = wcs.WCS(naxis=2)

    # define cdelt: coordinate increment along axis
    cdelt = (np.array([-1.0, 1.0]) * pixel_scale).to("deg / pix")
    w.wcs.cdelt = cdelt

    # define crpix: coordinate system reference pixel
    crpix = Quantity(np.array([rows / 2, cols / 2]), unit="pix")
    w.wcs.crpix = crpix

    # define crval: coordinate system value at reference pixel
    w.wcs.crval = [coords_detector.ra.deg, coords_detector.dec.deg]

    # define crota: coordinate system rotation angle
    w.wcs.crota = [0, -0]

    # define ctype: name of the coordinate axis
    w.wcs.ctype = ["RA---TAN", "DEC--TAN"]

    """
    # Other possible method to convert to pixel usingscopesim:
    # https://github.com/AstarVienna/ScopeSim/blob/dev_master/scopesim/optics/image_plane_utils.py#L698
    # gives different result.
    # da = cdelt[0]
    # db = cdelt[1]
    # x0 = crpix[0]
    # y0 = crpix[1]
    # a0 = selected_data["x"].values * u.arcsec
    # b0 = selected_data["y"].values * u.arcsec
    # a = float(telescope_ra) * u.deg
    # b = float(telescope_dec) * u.deg
    # convert stars coordinate to detector coordinates
    # detector_coords_x = x0 + 1. / da * (a - a0)
    # detector_coords_y = y0 + 1. / db * (b - b0)
    """

    detector_coords_x = np.round(
        w.world_to_pixel_values(stars_coords.ra, stars_coords.dec)[0]
    )
    detector_coords_y = np.round(
        w.world_to_pixel_values(stars_coords.ra, stars_coords.dec)[1]
    )
    scene_data["detector_coords_x"] = xr.DataArray(
        detector_coords_x, dims="ref", attrs={"units": "pixel"}
    )
    scene_data["detector_coords_y"] = xr.DataArray(
        detector_coords_y, dims="ref", attrs={"units": "pixel"}
    )

    # make sure that only stars inside the detector
    selected_data_query = (
        scene_data.copy(deep=True)
        .query(ref="detector_coords_x > 0")
        .query(ref=f"detector_coords_x < {cols}")
        .query(ref=f"detector_coords_y < {rows}")
        .query(ref="detector_coords_y > 0")
    )

    if selected_data_query.sizes["ref"] == 0:
        raise ValueError(
            "No objects projected in the detector. "
            "To resolve this issue you can use function 'pyxel.display_scene'"
        )

    # convert to int
    selected_data_query["detector_coords_x"] = selected_data_query[
        "detector_coords_x"
    ].astype(int)
    selected_data_query["detector_coords_y"] = selected_data_query[
        "detector_coords_y"
    ].astype(int)

    return selected_data_query


def aggregate_monochromatic(data: xr.Dataset, rows: int, cols: int) -> np.ndarray:
    """Aggregate a 3D data array containing fluxes into a 2D array.

    Parameters
    ----------
    data : xr.DataArray
    rows : int
        The number of rows in the detector.
    cols : int
        The number of columns in the detector.

    Returns
    -------
    2D array
    """
    # get empty array in shape of the detector
    projection_2d: np.ndarray = np.zeros([rows, cols])

    # fill in projection of objects in detector coordinates
    for x, group_x in data.groupby("detector_coords_x"):
        for y, group_y in group_x.groupby("detector_coords_y"):
            projection_2d[int(y), int(x)] += group_y["converted_flux"].values.sum()

    return projection_2d


def aggregate_multiwavelength(data: xr.Dataset, rows: int, cols: int) -> xr.DataArray:
    """Aggregate a 3D ``DataArray`` containing fluxes into a 3D ``DataArray``.

    Parameters
    ----------
    data : xr.DataArray
    rows : int
        The number of rows in the detector.
    cols : int
        The number of columns in the detector.

    Returns
    -------
    3D array
    """
    # get empty array in shape of the 3D datacube of the detector
    projection = np.zeros([data.wavelength.size, rows, cols])

    # fill in projection of objects in detector coordinates
    for x, group_x in data.groupby("detector_coords_x"):
        for y, group_y in group_x.groupby("detector_coords_y"):
            projection[:, int(y), int(x)] += np.array(
                group_y["converted_flux"].sum(dim="ref")
            )

    projection_3d: xr.DataArray = xr.DataArray(
        projection,
        dims=["wavelength", "y", "x"],
        coords={"wavelength": data.wavelength},
        attrs={"units": data.converted_flux.units},
    )

    return projection_3d


# TODO: Add unit tests
def _extract_wavelength(
    resolution: int | None,
    filter_band: tuple[float, float] | None,
    default_wavelength_handling: float | WavelengthHandling | None,
) -> xr.DataArray:
    """Extract wavelength."""
    if filter_band is not None:
        first_band, last_band = filter_band
        if not (0 < first_band < last_band):
            raise ValueError(
                f"'filter_band' must be increasing and strictly positive. Got: {filter_band!r}"
            )

        if resolution is not None:
            if resolution <= 0.0:
                raise ValueError(f"Expected 'resolution' > 0. Got: {resolution!r}")

            step_size = resolution

        else:
            if not isinstance(default_wavelength_handling, WavelengthHandling):
                raise ValueError(
                    "No 'resolution' provided for model 'simple_collection'. Please provide 'resolution'` "
                    "parameters in the detector environment wavelength or as input into this model directly."
                )

            step_size = default_wavelength_handling.resolution

    else:
        if resolution is not None:
            if resolution <= 0.0:
                raise ValueError(f"Expected 'resolution' > 0. Got: {resolution!r}")

            if not isinstance(default_wavelength_handling, WavelengthHandling):
                raise ValueError(
                    "No 'filter_band' provided for model 'simple_collection'. Please provide 'resolution'` "
                    "parameters in the detector environment wavelength or as input into this model directly."
                )

            first_band = default_wavelength_handling.cut_on
            last_band = default_wavelength_handling.cut_off
            step_size = resolution

        else:
            if not isinstance(default_wavelength_handling, WavelengthHandling):
                raise ValueError(
                    "'filter_band' and 'resolution' have both to be provided either as model arguments or in the "
                    "detector environment. Please provide them in the detector in the detector wavelength or "
                    "as input into this model directly"
                )

            first_band = default_wavelength_handling.cut_on
            last_band = default_wavelength_handling.cut_off
            step_size = default_wavelength_handling.resolution

    wavelengths: xr.DataArray = WavelengthHandling(
        cut_on=first_band,
        cut_off=last_band,
        resolution=step_size,
    ).get_wavelengths()

    return wavelengths


def simple_collection(
    detector: Detector,
    aperture: float,
    filter_band: tuple[float, float] | None = None,
    resolution: int | None = None,
    pixel_scale: float | None = None,
    integrate_wavelength: bool = True,
):
    """Convert scene in ph/(cm2 nm s) to photon in ph/nm s or ph s.

    Parameters
    ----------
    detector : Detector
        Pyxel detector object.
    aperture : float
        Collecting area of the telescope. Unit: m.
    filter_band : Union[tuple[float, float], None]
        Wavelength range of selected filter band, default is None. Unit: nm.
    resolution : Optional[int]
        Resolution of provided wavelength range in filter band. Unit: nm.
    pixel_scale : float, optional
        Pixel scale of detector, default is None. Unit: arcsec/pixel.
    integrate_wavelength : bool
        If true, integrates along the wavelength else multiwavelength, default is True.
    """
    if aperture <= 0.0:
        raise ValueError(f"Expected 'aperture' > 0. Got: {aperture!r}")

    if detector.scene == Scene():
        raise ValueError(
            "Missing 'scene' in 'detector'. "
            "To resolve this issue, you must use a model that generate a 'Scene' "
            "from the 'Photon Collection' group.\nConsider using the 'load_star_map' "
            "model."
        )

    if detector.photon.ndim != 0:
        raise ValueError(
            "Photons are already defined in 'detector.photon'. "
            "To resolve this issue, you must have no photons before running this model."
        )

    if pixel_scale is None:
        if detector.geometry._pixel_scale is None:
            raise ValueError(
                "Pixel scale is not defined. It must be either provided in the detector geometry "
                "or as model argument."
            )
        pixel_scale_arcsec: Quantity = Quantity(
            detector.geometry.pixel_scale, unit="arcsec/pixel"
        )
    else:
        if pixel_scale <= 0.0:
            raise ValueError(f"Expected 'pixel_scale' > 0. Got: {pixel_scale!r}")

        pixel_scale_arcsec = Quantity(pixel_scale, unit="arcsec/pixel")

    wavelengths: xr.DataArray = _extract_wavelength(
        resolution=resolution,
        filter_band=filter_band,
        default_wavelength_handling=detector.environment._wavelength,
    )

    # get dataset for given wavelength and scene object.
    scene_data: xr.Dataset = extract_wavelength(
        scene=detector.scene,
        wavelengths=wavelengths,
    )

    # get time in s
    time = Quantity(detector.time_step, unit="s")
    # get aperture in m
    aperture = Quantity(aperture, unit="m")

    if integrate_wavelength:
        # integrate flux
        integrated_flux: xr.DataArray = integrate_flux(flux=scene_data["flux"])
        # get flux in ph/s/cm^2
        flux = Quantity(integrated_flux, unit=integrated_flux.units)

        # get flux converted to ph
        converted_flux_2d: Quantity = convert_flux(
            flux=flux, t_exp=time, aperture=aperture
        )

        # load converted flux to selected dataset
        scene_data["converted_flux"] = xr.DataArray(
            converted_flux_2d, dims="ref", attrs={"units": str(converted_flux_2d.unit)}
        )

        photon_projected = project_objects_to_detector(
            scene_data=scene_data,
            pixel_scale=pixel_scale_arcsec,
            rows=detector.geometry.row,
            cols=detector.geometry.col,
        )

        photon_projection_2d: np.ndarray = aggregate_monochromatic(
            data=photon_projected,
            rows=detector.geometry.row,
            cols=detector.geometry.col,
        )

        detector.photon.array_2d = photon_projection_2d

    else:
        # get flux in ph/(s nm cm^2)
        flux_with_weight: xr.DataArray = scene_data["flux"] * scene_data["weight"]

        flux = Quantity(flux_with_weight, unit=scene_data["flux"].units)

        # get flux converted to ph/nm
        converted_flux_3d: Quantity = convert_flux(
            flux=flux,
            t_exp=time,
            aperture=aperture,
        )

        # load converted flux to scene_data dataset
        scene_data["converted_flux"] = xr.DataArray(
            converted_flux_3d,
            dims=["ref", "wavelength"],
            attrs={"units": str(converted_flux_3d.unit)},
        )
        # min_x, max_x = scene_data["x"].min().item(), scene_data["x"].max().item()
        # min_y, max_y = scene_data["y"].min().item(), scene_data["y"].max().item()
        # print(f"Scene x range: {min_x} to {max_x}")
        # print(f"Scene y range: {min_y} to {max_y}")
        # print("Scene attributes:", scene_data.attrs)

        photon_projected = project_objects_to_detector(
            scene_data=scene_data,
            pixel_scale=pixel_scale_arcsec,
            rows=detector.geometry.row,
            cols=detector.geometry.col,
        )

        photon_projection_3d: xr.DataArray = aggregate_multiwavelength(
            data=photon_projected,
            rows=detector.geometry.row,
            cols=detector.geometry.col,
        )

        detector.photon.array_3d = photon_projection_3d
