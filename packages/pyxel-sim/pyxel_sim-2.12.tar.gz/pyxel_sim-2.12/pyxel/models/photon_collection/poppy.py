#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Poppy model."""

import logging
import textwrap
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Final, get_args

import numpy as np
import xarray as xr
from astropy.convolution import convolve_fft
from astropy.io import fits
from astropy.units import Quantity

from pyxel.detectors import Detector, WavelengthHandling
from pyxel.util import convert_unit

if TYPE_CHECKING:
    import poppy as op

GENERIC_ERROR_MESSAGE: Final[str] = (
    "To resolve this issue, you can use for example this input in the YAML configuration:\n"
    "arguments:\n"
    "  optical_system:\n"
    "    - item: CircularAperture\n"
    "      radius: 1.0     # radius in meter"
)


@dataclass
class CircularAperture:
    """Parameters for an ideal circular pupil aperture.

    Parameters
    ----------
    radius : Quantity
        Radius of the pupil, in meters.
    """

    radius: Quantity


@dataclass
class DeprecatedThinLens:
    """Parameters for an idealized thin lens.

    Parameters
    ----------
    nwaves : float
        The number of waves of defocus, peak to valley.
    radius : float
        Pupil radius, in meters, over which the Zernike defocus term should be computed
        such that rho = 1 at r = `radius`.
    """

    nwaves: float
    radius: float


@dataclass
class ThinLens:
    """Parameters for an idealized thin lens.

    Parameters
    ----------
    nwaves : float
        The number of waves of defocus, peak to valley.
    radius : Quantity
        Pupil radius, in meters, over which the Zernike defocus term should be computed
        such that rho = 1 at r = `radius`.
    reference_wavelength : Quantity
        Wavelength, in nm, at which that number of waves of defocus is specified.
    """

    nwaves: float
    radius: Quantity
    reference_wavelength: Quantity | None = None
    # center wavelength if not provided takes the middle


@dataclass
class SquareAperture:
    """Parameters for an ideal square pupil aperture.

    Parameters
    ----------
    size : Quantity
        side length of the square, in meters.
    """

    size: Quantity


@dataclass
class RectangleAperture:
    """Parameters for an ideal rectangular pupil aperture.

    Parameters
    ----------
    width : Quantity
        width of the rectangle, in meters.
    height : Quantity
        height of the rectangle, in meters.
    """

    width: Quantity
    height: Quantity


@dataclass
class HexagonAperture:
    """Parameters for an ideal hexagonal pupil aperture.

    Parameters
    ----------
    side : Quantity
        side length (and/or radius) of hexagon, in meters.
    """

    side: Quantity


@dataclass
class MultiHexagonalAperture:
    """Parameters for an hexagonaly segmented aperture.

    Parameters
    ----------
    side : Quantity
        side length (and/or radius) of hexagon, in meters.
    rings : integer
        The number of rings of hexagons to include, not counting the central segment
        (i.e. 2 for a JWST-like aperture, 3 for a Keck-like aperture, and so on)
    gap : Quantity
        Gap between adjacent segments, in meters.
    """

    side: Quantity
    rings: int
    gap: Quantity


@dataclass
class SecondaryObscuration:
    """Parameters to define the central obscuration of an on-axis telescope.

    The parameters include secondary mirror and supports.

    Parameters
    ----------
    secondary_radius : Quantity
        Radius of the circular secondary obscuration, in meters.
    n_supports : int
        Number of secondary mirror supports ("spiders"). These will be
        spaced equally around a circle.
    support_width : Quantity
        Width of each support, in meters.
    """

    secondary_radius: Quantity
    n_supports: int
    support_width: Quantity


@dataclass
class ZernikeWFE:
    """Parameters to define an optical element in terms of its Zernike components.

    Parameters
    ----------
    radius : Quantity
        Pupil radius, in meters, over which the Zernike terms should be
        computed such that rho = 1 at r = `radius`.
    coefficients : iterable of floats
        Specifies the coefficients for the Zernike terms, ordered
        according to the convention of Noll et al. JOSA 1976. The
        coefficient is in meters of optical path difference (not waves).
    aperture_stop : float
    """

    radius: Quantity
    coefficients: Sequence[float]
    aperture_stop: float


@dataclass
class SineWaveWFE:
    """Parameters to define a single sine wave ripple across the optic.

    Parameters
    ----------
    spatialfreq : Quantity
    amplitude : Quantity
    rotation : float
    """

    spatialfreq: Quantity
    amplitude: Quantity
    rotation: float


# Define a type alias
OpticalParameter = (
    CircularAperture
    | ThinLens
    | SquareAperture
    | RectangleAperture
    | HexagonAperture
    | MultiHexagonalAperture
    | SecondaryObscuration
    | ZernikeWFE
    | SineWaveWFE
)


def _create_optical_parameter(
    dct: Mapping, default_wavelength: Quantity | tuple[Quantity, Quantity]
) -> OpticalParameter:
    """Create an``OpticalParameter`` based on a dictionary.

    Parameters
    ----------
    dct : dict
        Dictionary to convert.
    default_wavelength : Union[Quantity, tuple[Quantity,Quantity]]
        Wavelength in nanometer.

    Returns
    -------
    OpticalParameter
        New parameters.
    """
    if "item" not in dct:
        raise KeyError(
            f"Missing keyword 'item'. Got: {dct!r}.\n{GENERIC_ERROR_MESSAGE}"
        )

    if dct["item"] == "CircularAperture":
        if "radius" not in dct:
            raise KeyError(
                "Missing parameter 'radius' for the optical element 'CircularAperture'."
            )

        return CircularAperture(radius=Quantity(dct["radius"], unit="m"))

    elif dct["item"] == "ThinLens":
        if "reference_wavelength" in dct:
            reference_wavelength = Quantity(dct["reference_wavelength"], unit="nm")

        elif isinstance(default_wavelength, Quantity):
            reference_wavelength = default_wavelength
        else:
            cut_on, cut_off = default_wavelength
            reference_wavelength = (cut_on + cut_off) / 2

        if "nwaves" not in dct or "radius" not in dct:
            raise KeyError(
                "Missing one of these parameters: 'nwaves', 'radius' "
                "for the optical element 'ThinLens'."
            )

        return ThinLens(
            nwaves=float(dct["nwaves"]),
            radius=Quantity(dct["radius"], unit="m"),
            reference_wavelength=reference_wavelength,
        )

    elif dct["item"] == "SquareAperture":
        if "size" not in dct:
            raise KeyError(
                "Missing parameter 'size' for the optical element 'SquareAperture'."
            )

        return SquareAperture(size=Quantity(dct["size"], unit="m"))

    elif dct["item"] == "RectangularAperture":
        if "width" not in dct or "height" not in dct:
            raise KeyError(
                "Missing one of these parameters: 'width', 'height' "
                "for the optical element 'RectangularAperture'."
            )

        return RectangleAperture(
            width=Quantity(dct["width"], unit="m"),
            height=Quantity(dct["height"], unit="m"),
        )

    elif dct["item"] == "HexagonAperture":
        if "side" not in dct:
            raise KeyError(
                "Missing parameter 'side' for the optical element 'HexagonAperture'."
            )

        return HexagonAperture(side=Quantity(dct["side"], unit="m"))

    elif dct["item"] == "MultiHexagonalAperture":
        if "side" not in dct or "rings" not in dct or "gap" not in dct:
            raise KeyError(
                "Missing one of these parameters: 'side', 'rings', 'gap' "
                "for the optical element 'MultiHexagonalAperture'."
            )

        return MultiHexagonalAperture(
            side=Quantity(dct["side"], unit="m"),
            rings=int(dct["rings"]),
            gap=Quantity(dct["gap"], unit="m"),
        )

    elif dct["item"] == "SecondaryObscuration":
        if (
            "secondary_radius" not in dct
            or "n_supports" not in dct
            or "support_width" not in dct
        ):
            raise KeyError(
                "Missing one of these parameters: 'secondary_radius', 'n_supports', 'support_width' "
                "for the optical element 'SecondaryObscuration'."
            )

        return SecondaryObscuration(
            secondary_radius=Quantity(dct["secondary_radius"], unit="m"),
            n_supports=int(dct["n_supports"]),
            support_width=Quantity(dct["support_width"], unit="m"),
        )  # cm

    elif dct["item"] == "ZernikeWFE":
        if (
            "radius" not in dct
            or "coefficients" not in dct
            or "aperture_stop" not in dct
        ):
            raise KeyError(
                "Missing one of these parameters: 'radius', 'coefficients', 'aperture_stop' "
                "for the optical element 'ZernikeWFE'."
            )

        if (
            not isinstance(dct["coefficients"], Sequence)
            or len(dct["coefficients"]) == 0
        ):
            raise ValueError(
                "Expecting a list of numbers for parameter 'coefficients'"
                "for the optical element 'ZernikeWFE'."
            )

        return ZernikeWFE(
            radius=Quantity(dct["radius"], unit="m"),
            coefficients=dct["coefficients"],  # list of floats
            aperture_stop=float(dct["aperture_stop"]),
        )  # bool

    elif dct["item"] == "SineWaveWFE":
        if "spatialfreq" not in dct or "amplitude" not in dct or "rotation" not in dct:
            raise KeyError(
                "Missing one of these parameters: 'spatialfreq', 'amplitude', 'rotation' "
                "for the optical element 'SineWaveWFE'."
            )

        return SineWaveWFE(
            spatialfreq=Quantity(dct["spatialfreq"], unit="1/m"),
            amplitude=Quantity(dct["amplitude"], unit="um"),
            rotation=float(dct["rotation"]),
        )
    else:
        valid_optical_elements: Sequence[str] = [
            repr(cls.__name__) for cls in get_args(OpticalParameter)
        ]
        msg = f"Unknown 'optical_element', expected values: {', '.join(valid_optical_elements)}. Got: {dct!r}"
        msg_lst: list[str] = textwrap.wrap(msg, drop_whitespace=False)
        raise KeyError("\n".join(msg_lst))


def create_optical_item(
    dct: Mapping,
    default_wavelength: Quantity | tuple[Quantity, Quantity],
) -> "op.OpticalElement":
    """Create a poppy ``OpticalElement``.

    Parameters
    ----------
    dct : dict
        Dictionary to convert.
    default_wavelength : Union[Quantity, tuple[Quantity,Quantity]]
        Wavelength in nanometer.

    Returns
    -------
    ``OpticalElement``
        A poppy ``OpticalElement``.
    """
    try:
        import poppy as op
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Missing optional package 'poppy'.\n"
            "Please install it with 'pip install pyxel-sim[model]'"
            "or 'pip install pyxel-sim[all]' or 'pip install poppy'"
        ) from exc

    param: OpticalParameter = _create_optical_parameter(
        dct=dct,
        default_wavelength=default_wavelength,
    )

    if isinstance(param, CircularAperture):
        return op.CircularAperture(radius=param.radius)

    elif isinstance(param, ThinLens):
        return op.ThinLens(
            nwaves=param.nwaves,
            reference_wavelength=param.reference_wavelength,
            radius=param.radius,
        )

    elif isinstance(param, SquareAperture):
        return op.SquareAperture(size=param.size)

    elif isinstance(param, RectangleAperture):
        return op.RectangleAperture(width=param.width, height=param.height)

    elif isinstance(param, HexagonAperture):
        return op.HexagonAperture(side=param.side)

    elif isinstance(param, MultiHexagonalAperture):
        return op.MultiHexagonAperture(
            side=param.side,
            rings=param.rings,
            gap=param.gap,
        )

    elif isinstance(param, SecondaryObscuration):
        return op.SecondaryObscuration(
            secondary_radius=param.secondary_radius,
            n_supports=param.n_supports,
            support_width=param.support_width,
        )

    elif isinstance(param, ZernikeWFE):
        return op.ZernikeWFE(
            radius=param.radius,
            coefficients=param.coefficients,
            aperture_stop=param.aperture_stop,
        )

    elif isinstance(param, SineWaveWFE):
        return op.SineWaveWFE(
            spatialfreq=param.spatialfreq,
            amplitude=param.amplitude,
            rotation=param.rotation,
        )
    else:
        raise NotImplementedError(f"{param=}")


def calc_psf(
    wavelengths: Sequence[float],
    fov_arcsec: float,
    pixel_scale: Quantity,
    optical_elements: Sequence["op.OpticalElement"],
    apply_jitter: bool = False,
    jitter_sigma: float = 0.007,
) -> tuple[fits.PrimaryHDU, fits.PrimaryHDU]:
    """Calculate the point spread function for the given optical system.

    Parameters
    ----------
    wavelengths : sequence of float
        Wavelengths of incoming light in meters.
    fov_arcsec : float, optional
        Field Of View on detector plane in arcsec.
    pixel_scale : float
        Pixel scale on detector plane (arcsec/pixel).
        Defines sampling resolution of :term:`PSF`.
    optical_elements : list of OpticalElement
        List of optical elements to apply.
    apply_jitter : bool
        Defines whether jitter should be applied. Default = False.
    jitter_sigma : float
        Jitter sigma value in arcsec per axis, default is 0.007.

    Returns
    -------
    Tuple of two :term:`FITS`
        Tuple of psf and intermediate wavefronts.
    """
    try:
        import poppy as op
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Missing optional package 'poppy'.\n"
            "Please install it with 'pip install pyxel-sim[model]'"
            "or 'pip install pyxel-sim[all]' or 'pip install poppy'"
        ) from exc

    class PyxelInstrument(op.instrument.Instrument):
        """Instrument class for Pyxel using poppy.instrument."""

        def __init__(
            self,
            pixel_scale: Quantity,
            optical_elements: Sequence["op.OpticalElement"],
            fov_arcsec: float = 2,
            name="PyxelInstrument",
        ):
            super().__init__(name=name)
            self._pixel_scale: Quantity = pixel_scale.to("arcsec/pix")
            self._optical_elements = optical_elements
            self._fov_arcsec = fov_arcsec

        def get_optical_system(
            self,
            fft_oversample=2,
            detector_oversample=None,
            fov_arcsec=None,
            fov_pixels=None,
            options=None,
        ):
            """Return an OpticalSystem instance corresponding to the instrument as currently configured.

            Parameters
            ----------
            fft_oversample : int
                Oversampling factor for intermediate plane calculations. Default is 2
            detector_oversample : int, optional
                By default the detector oversampling is equal to the intermediate calculation oversampling.
                If you wish to use a different value for the detector, set this parameter.
                Note that if you just want images at detector pixel resolution you will achieve higher fidelity
                by still using some oversampling (i.e. *not* setting `oversample_detector=1`) and instead rebinning
                down the oversampled data.
            fov_pixels : float
                Field of view in pixels. Overrides fov_arcsec if both set.
            fov_arcsec : float
                Field of view, in arcseconds. Default is 2
            options : dict
                Other arbitrary options for optical system creation

            Returns
            -------
            osys : poppy.OpticalSystem
                an optical system instance representing the desired configuration.
            """
            osys = op.OpticalSystem(npix=1000)  # default: 1024

            element: op.OpticalElement
            for element in self._optical_elements:
                osys.add_pupil(element)

            analysis_fov = self._pixel_scale * Quantity(10, unit="pix")
            osys.add_detector(
                pixelscale=self._pixel_scale,
                fov_arcsec=analysis_fov,
            )

            return osys

    output_fits: Sequence[fits.hdu.image.PrimaryHDU]
    wavefronts: Sequence[op.Wavefront]

    # Create Instrument
    instrument = PyxelInstrument(
        optical_elements=optical_elements,
        pixel_scale=pixel_scale,
        fov_arcsec=fov_arcsec,
    )

    instrument.pixelscale = pixel_scale

    if apply_jitter:
        instrument.options["jitter"] = "gaussian"
        instrument.options["jitter_sigma"] = (
            jitter_sigma  # in arcsec per axis, default 0.007
        )

    output_fits, wavefronts = instrument.calc_datacube(
        wavelengths=wavelengths,
        fov_arcsec=fov_arcsec,
        oversample=1,
    )

    return output_fits, wavefronts


def apply_convolution(data: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Convolve an array in 2D or 3D.

    Parameters
    ----------
    data : ndarray
        2D or 3D Array to be convolved with kernel_2d.
    kernel : ndarray
        The convolution kernel.

    Returns
    -------
    ndarray
        A convolved array.
    """

    if kernel.ndim == 2:
        mean = np.mean(data)
    elif kernel.ndim == 3:
        integrated = kernel.sum(axis=0)
        mean = integrated.mean()
    else:
        raise NotImplementedError

    *_, num_rows, num_cols = kernel.shape

    assert num_rows == num_cols
    # resize kernel, if kernel size too big.
    if num_rows > 11:
        import skimage.transform as sk

        if kernel.ndim == 2:
            new_shape: tuple[int, ...] = (11, 11)
        elif kernel.ndim == 3:
            num_wavelengths, _, _ = kernel.shape
            new_shape = num_wavelengths, 11, 11

        resized_kernel = sk.resize(kernel, output_shape=new_shape, anti_aliasing=False)
        kernel = resized_kernel / resized_kernel.sum()

    array = convolve_fft(
        data,
        kernel=kernel,
        boundary="fill",
        fill_value=mean,
    )

    return array


# ruff: noqa: C901
def optical_psf(
    detector: Detector,
    fov_arcsec: float,
    optical_system: Sequence[Mapping[str, Any]],
    wavelength: float | tuple[float, float] | None = None,
    pixel_scale: float | None = None,
    apply_jitter: bool = False,
    jitter_sigma: float = 0.007,
    extract_psf: bool = False,
) -> None:
    """Model function for poppy optics model: convolve photon array with psf.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    fov_arcsec : float
        Field Of View on detector plane in arcsec.
    optical_system : list of dict
        List of optical elements before detector with their specific arguments.
    wavelength : Union[float, tuple[float, float], None]
        Wavelength of incoming light in meters, default is None.
    pixel_scale : float, Optional, default: None
        Pixel scale of detector in arcsec/pix.
    apply_jitter : bool, default: False
        Defines whether jitter should be applied, default is False.
    jitter_sigma : float
        Jitter sigma value in arcsec per axis, default is 0.007.
    extract_psf : bool, default: False
        Copy the computed PSF into the data
        bucket ``detector.data['/photon_collection/optical_psf/[name of the model]/psf']``

    Notes
    -----
    For more information, you can find examples here:

    * :external+pyxel_data:doc:`examples/models/scene_generation/tutorial_example_scene_generation`
    * :external+pyxel_data:doc:`tutorial/01_first_simulation`
    """
    logging.getLogger("poppy").setLevel(
        logging.WARNING
    )  # TODO: Fix this. See issue #81

    if fov_arcsec <= 0.0:
        raise ValueError(
            f"Expecting strictly positive value for 'fov_arcsec'. Got {fov_arcsec!r} "
        )

    if not optical_system:
        raise ValueError(
            "Parameter 'optical_system' does not contain any optical element(s)."
            f"\n{GENERIC_ERROR_MESSAGE}"
        )

    # get pixel scale either from detector geometry or from model input
    if pixel_scale is None:
        if detector.geometry._pixel_scale is None:
            raise ValueError(
                "Pixel scale is not defined. It must be either provided in the detector geometry "
                "or as model argument."
            )
        pixel_scale_with_unit: Quantity = Quantity(
            detector.geometry.pixel_scale,
            unit="arcsec/pix",
        )
    else:
        if pixel_scale <= 0:
            raise ValueError(
                f"Parameter 'pixelscale' must be strictly positive. Got: {pixel_scale}"
            )

        pixel_scale_with_unit = Quantity(pixel_scale, unit="arcsec/pix")

    # get wavelength information either from detector environment or from model input
    if wavelength is None:
        # take wavelength input from detector.environment
        if isinstance(detector.environment._wavelength, float):
            selected_wavelength: Quantity | tuple[Quantity, Quantity] = Quantity(
                detector.environment.wavelength, unit="nm"
            )

        elif isinstance(detector.environment._wavelength, WavelengthHandling):
            selected_wavelength = (
                Quantity(detector.environment._wavelength.cut_on, unit="nm"),
                Quantity(detector.environment._wavelength.cut_off, unit="nm"),
            )
        else:
            raise ValueError(
                "Wavelength is not defined. It must be either provided in the detector geometry "
                "or as model argument."
            )
    else:
        if isinstance(wavelength, int | float):
            if wavelength <= 0:
                raise ValueError(
                    "Parameter 'wavelength' must be strictly positive. "
                    f"Got: {wavelength}"
                )

            selected_wavelength = Quantity(wavelength, unit="nm")

        elif isinstance(wavelength, Sequence) and len(wavelength) == 2:
            cut_on, cut_off = wavelength

            selected_wavelength = (
                Quantity(cut_on, unit="nm"),
                Quantity(cut_off, unit="nm"),
            )

            if not (0 < cut_on < cut_off):
                raise ValueError(
                    "'wavelength' must be increasing and strictly positive. "
                    f"Got: {selected_wavelength!r}"
                )

    # Create 'OpticalElement' from an input 'dict'
    optical_elements: Sequence["op.OpticalElement"] = [
        create_optical_item(dct, default_wavelength=selected_wavelength)
        for dct in optical_system
    ]

    # Depending on Type calculate for 2D or 3D photon
    if isinstance(selected_wavelength, Quantity):
        if detector.photon.ndim != 2:
            raise ValueError(
                f"A 'detector.photon' 2D is expected. Got an '{detector.photon.ndim=}' "
            )

        # 2D
        # Processing
        # Get a Point Spread Function
        psf_hdu: fits.PrimaryHDU
        psf_hdu, _ = calc_psf(
            wavelengths=[selected_wavelength.to("m").value],
            fov_arcsec=fov_arcsec,
            pixel_scale=pixel_scale_with_unit,
            optical_elements=optical_elements,
            apply_jitter=apply_jitter,
            jitter_sigma=jitter_sigma,
        )

        psf_3d: np.ndarray = psf_hdu.data
        psf_2d: np.ndarray = psf_3d[0, :, :]

        if extract_psf and detector.is_first_readout:
            optical_elements_attrs: dict[str, str | int] = {
                "num_optical_elements": len(optical_elements)
            }
            for idx, element in enumerate(optical_elements):
                optical_elements_attrs[f"element_{idx}"] = str(element)

            model_name: str = detector.current_running_model_name
            general_attrs = {
                "model": model_name,
                "wavelength": str(selected_wavelength),
                "fov": str(Quantity(fov_arcsec, unit="arcsec")),
                "pixel_scale": str(pixel_scale_with_unit),
                "apply_jitter": apply_jitter,
                "jitter_sigma": jitter_sigma,
            }

            psf_info = xr.DataArray(
                psf_2d,
                dims=["y", "x"],
                coords={
                    "wavelength": xr.DataArray(
                        selected_wavelength.value,
                        attrs={"unit": selected_wavelength.unit},
                    )
                },
                attrs=general_attrs | optical_elements_attrs,
            )

            detector.data[f"/photon_collection/optical_psf/{model_name}/psf"] = psf_info

        # Convolution
        new_array_2d: np.ndarray = apply_convolution(
            data=detector.photon.array,
            kernel=psf_2d,
        )

        detector.photon.array = new_array_2d
    else:
        if detector.photon.ndim != 3:
            raise ValueError(
                f"A 'detector.photon' 3D is expected. Got an '{detector.photon.ndim=}' "
            )

        # 3D
        min_wavelength, max_wavelength = selected_wavelength

        # Get current wavelengths (in nm)
        start_wavelength = Quantity(min_wavelength, unit="m")
        end_wavelength = Quantity(max_wavelength, unit="m")
        wavelengths_nm: Quantity = Quantity(
            detector.photon.array_3d["wavelength"], unit="nm"
        )

        tolerance = Quantity(1e-7, unit="m")
        selected_wavelengths_nm: Quantity = wavelengths_nm[
            np.logical_and(
                wavelengths_nm >= (start_wavelength - tolerance),
                wavelengths_nm <= (end_wavelength + tolerance),
            )
        ]
        if selected_wavelengths_nm.size == 0:
            raise ValueError(
                f"The provided wavelength range ({min_wavelength:unicode}, {max_wavelength:unicode}) has "
                f"no overlap with the wavelengths from 'detector.photon.array_3d' "
                f"({wavelengths_nm[0]:unicode}, {wavelengths_nm[-1]:unicode})."
            )

        # Processing
        # Get a Point Spread Function
        psf_hdu_3d: fits.PrimaryHDU
        psf_hdu_3d, _ = calc_psf(
            wavelengths=selected_wavelengths_nm.to("m").value,
            fov_arcsec=fov_arcsec,
            pixel_scale=pixel_scale_with_unit,
            optical_elements=optical_elements,
            apply_jitter=apply_jitter,
            jitter_sigma=jitter_sigma,
        )

        # Convolution
        psf_3d = psf_hdu_3d.data

        if extract_psf and detector.is_first_readout:
            optical_elements_attrs = {"num_optical_elements": len(optical_elements)}
            for idx, element in enumerate(optical_elements):
                optical_elements_attrs[f"element_{idx}"] = str(element)

            start_wavelength, end_wavelength = selected_wavelength

            model_name = detector.current_running_model_name
            general_attrs = {
                "model": model_name,
                "wavelengths": f"From {start_wavelength} to {end_wavelength}",
                "fov": str(Quantity(fov_arcsec, unit="arcsec")),
                "pixel_scale": str(pixel_scale_with_unit),
                "apply_jitter": apply_jitter,
                "jitter_sigma": jitter_sigma,
            }

            psf_info = xr.DataArray(
                psf_3d,
                dims=["wavelength", "y", "x"],
                coords={
                    "wavelength": xr.DataArray(
                        selected_wavelengths_nm.value,
                        dims="wavelength",
                        attrs={"unit": selected_wavelengths_nm.unit},
                    )
                },
                attrs=general_attrs | optical_elements_attrs,
            )

            detector.data[f"/photon_collection/optical_psf/{model_name}/psf"] = psf_info

        new_array_3d: np.ndarray = apply_convolution(
            data=detector.photon.array_3d.to_numpy(),
            kernel=psf_3d,
        )

        data_selected_wavelength = xr.DataArray(
            selected_wavelengths_nm.value,
            dims=["wavelength"],
            attrs={"wavelength": convert_unit(selected_wavelengths_nm.unit)},
        )

        array_3d = xr.DataArray(
            new_array_3d,
            dims=["wavelength", "y", "x"],
            coords={"wavelength": data_selected_wavelength},
        )
        detector.photon.array_3d = array_3d
