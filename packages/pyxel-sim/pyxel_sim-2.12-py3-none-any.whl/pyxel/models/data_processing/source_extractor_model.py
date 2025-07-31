#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Wrapper to create simple graphs using the source extractor package."""

import warnings
from typing import TYPE_CHECKING, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.patches import Ellipse
from typing_extensions import deprecated

from pyxel.detectors import Detector

if TYPE_CHECKING:
    from photutils.segmentation import SegmentationImage


def show_detector(image_2d: np.ndarray, vmin=0, vmax=100) -> None:
    """Take in the detector object and shows the array values as an image to the user.

    Parameters
    ----------
    image_2d
        2D image array .
    """
    im = plt.imshow(
        image_2d,
        interpolation="nearest",
        cmap="gray",
        vmin=vmin,
        vmax=vmax,
        origin="lower",
    )
    plt.colorbar(im)


def get_background(image_2d: np.ndarray) -> np.ndarray:
    """Get the background of an image using the photutils library.

    Parameters
    ----------
    image_2d
        2d image array.
    """
    try:
        from photutils.background import SExtractorBackground
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Missing optional package 'photutils'.\n"
            "Please install it with 'pip install pyxel-sim[model]'"
            "or 'pip install pyxel-sim[all]' or 'pip install photutils'"
        ) from exc

    background = SExtractorBackground()
    return background.calc_background(image_2d)


def get_background_image_2d(image_2d: np.ndarray) -> np.ndarray:
    """Get the background of an image and converts it to a 2D-array of the same shape of the original input image.

    Parameters
    ----------
    image_2d
        2D image array .
    """
    bkg = get_background(image_2d)
    return np.full_like(image_2d, fill_value=bkg)


def subtract_background(image_2d: np.ndarray):
    """Return a background subtracted numpy array.

    Parameters
    ----------
    image_2d
        2D image array .
    """
    bkg = get_background(image_2d)
    return image_2d - bkg


def extract_roi(
    image_2d: np.ndarray, thresh: int, minarea: int = 5, name: str = "pixel"
) -> Optional["SegmentationImage"]:
    """Return a structured numpy array that gives information on the roi found based on the threshold and minea given.

    Parameters
    ----------
    image_2d : np.ndarray
        2D image array
    thresh : int
        signal level above which signifies a region of interest
    minarea : int
        minimum area of elements required that are above the threshold for the extractor to extract information
    """
    try:
        from photutils.segmentation import SegmentationImage, detect_sources
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Missing optional package 'photutils'.\n"
            "Please install it with 'pip install pyxel-sim[model]'"
            "or 'pip install pyxel-sim[all]' or 'pip install photutils'"
        ) from exc

    # Detect sources above a specified threshold value in an image
    sources: SegmentationImage | None = detect_sources(
        data=image_2d,
        threshold=thresh,
        npixels=minarea,
    )
    return sources


def plot_roi(data: np.ndarray, roi) -> None:
    """Plot the input data on a graph and overlays ellipses over the roi's found by the extract function.

    Parameters
    ----------
    data : np.ndarray
        2D image array
    roi : np.ndarray / xarray.Dataset
        structured numpy array or xarray dataset of extracted data
    """
    _, ax = plt.subplots()
    m, s = np.mean(data), np.std(data)
    im = ax.imshow(
        data,
        interpolation="nearest",
        cmap="gray",
        vmin=m - s,
        vmax=m + s,
        origin="lower",
    )

    # plot an ellipse for each object
    for i in range(len(roi["x"])):
        e = Ellipse(
            xy=(roi["x"][i], roi["y"][i]),
            width=6 * roi["a"][i],
            height=6 * roi["b"][i],
            angle=roi["theta"][i] * 180.0 / np.pi,
        )
        e.set_facecolor("none")
        e.set_edgecolor("red")
        ax.add_artist(e)
    plt.colorbar(im)


def extract_sources_to_xarray(
    data_2d: np.ndarray, thresh: int = 50, minarea: int = 5
) -> xr.Dataset:
    """Detect and extract source information from a 2D array into an xarray.Dataset.

    This function identifies sources in a 2D image array using a threshold-based segmentation
    approach and compiles relevant information about the detected sources into an xarray.Dataset.

    Parameters
    ----------
    data_2d : np.ndarray
        Input 2D image array for source detection.
    thresh : int, optional
        Pixel intensity threshold above which sources are identified, by default 50.
    minarea : int, optional
        Minimum number of contiguous pixels required to form a valid source, by default 5.

    Returns
    -------
    DataSet
        An Dataset containing properties of detected sources:

    Raises
    ------
    ModuleNotFoundError
        If the required `photutils` package is not installed.
    """
    try:
        from photutils.segmentation import (
            SegmentationImage,
            SourceCatalog,
            detect_sources,
        )

    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Missing optional package 'photutils'.\n"
            "Please install it with 'pip install pyxel-sim[model]'"
            "or 'pip install pyxel-sim[all]' or 'pip install photutils'"
        ) from exc

    # Detect sources above a specified threshold value in an image
    segmentation_image: SegmentationImage | None = detect_sources(
        data=data_2d,
        threshold=thresh,
        npixels=minarea,
    )

    if segmentation_image is None:
        ds_sources: xr.Dataset = xr.Dataset()

    else:
        # Analyze the segmentation map
        catalog = SourceCatalog(data=data_2d, segment_img=segmentation_image)

        ds_sources = (
            pd.DataFrame(
                [
                    (
                        source.label,
                        source.bbox.ixmin,
                        source.bbox.ixmax,
                        source.bbox.iymin,
                        source.bbox.iymax,
                        source.xcentroid,
                        source.ycentroid,
                        source.semimajor_sigma.value,  # unit: pix
                        source.semiminor_sigma.value,  # unit: pix
                        source.orientation.value,  # unit: deg
                    )
                    for source in catalog
                ],
                columns=[
                    "label",
                    "xmin",
                    "xmax",
                    "ymin",
                    "ymax",
                    "x",
                    "y",
                    "a",
                    "b",
                    "theta",
                ],
            )
            .set_index("label")
            .to_xarray()
        )
        ds_sources["label"].attrs = {"long_name": "The source label number"}
        ds_sources["xmin"].attrs = {
            "long_name": "The minimum x pixel index within the minimal bounding box containing the source segment"
        }
        ds_sources["xmax"].attrs = {
            "long_name": "The maximum x pixel index within the minimal bounding box containing the source segment"
        }
        ds_sources["ymin"].attrs = {
            "long_name": "The minimum y pixel index within the minimal bounding box containing the source segment"
        }
        ds_sources["ymax"].attrs = {
            "long_name": "The maximum y pixel index within the minimal bounding box containing the source segment"
        }
        ds_sources["x"].attrs = {
            "long_name": "The x coordinate of the centroid within the isophotal source segment"
        }
        ds_sources["y"].attrs = {
            "long_name": "The y coordinate of the centroid within the isophotal source segment"
        }
        ds_sources["a"].attrs = {
            "long_name": "The 1-sigma standard deviation along the semimajor axis of the 2D Gaussian function that "
            "has the same second-order central moments as the source",
            "units": "pix",
        }
        ds_sources["b"].attrs = {
            "long_name": "The 1-sigma standard deviation along the semiminor axis of the 2D Gaussian function that "
            "has the same second-order central moments as the source",
            "units": "pix",
        }
        ds_sources["theta"].attrs = {
            "long_name": "The angle between the x axis and the major axis of the 2D Gaussian function that has "
            "the same second-order moments as the source",
            "units": "deg",
        }

        num_y, num_x = segmentation_image.shape

        ds_sources["segmap"] = xr.DataArray(
            segmentation_image.data,
            dims=["image_y", "image_x"],
            coords={"image_y": range(num_y), "image_x": range(num_x)},
        )

    return ds_sources


def source_extractor(
    detector: Detector,
    array_type: str = "pixel",
    thresh: int = 50,
    minarea: int = 5,
) -> None:
    """Extract the roi data converts it to xarray dataset and saves the information to the final result.

    A warning is generated if the processed data_array is empty.

    Parameters
    ----------
    array_type
    detector : Detector
        Pyxel Detector object.
    thresh : int
        Threshold pixel value above which information from the image array is extracted
    minarea : int
        Minimum area of pixels required that are above the threshold for the extractor to extract information

    Raises
    ------
    ValueError
        If parameter 'array_type' is not 'pixel','signal','image',photon' or 'charge'

    Notes
    -----
    For more information, you can find an example here:
    :external+pyxel_data:doc:`examples/models/data_processing/source_extractor/SEP_exposure`.
    """
    if array_type == "pixel":
        data_2d: np.ndarray = detector.pixel.array
    elif array_type == "signal":
        data_2d = detector.signal.array
    elif array_type == "image":
        data_2d = detector.image.array
    elif array_type == "photon":
        data_2d = detector.photon.array
    elif array_type == "charge":
        data_2d = detector.charge.array
    else:
        raise ValueError(
            "Incorrect array_type. Must be one of 'pixel','signal','image', 'photon' or"
            " 'charge'."
        )

    data_2d = np.asarray(data_2d, dtype=float)
    if np.all(data_2d == 0):
        warnings.warn(f"{array_type} data array is empty", stacklevel=2)

    detector.data["/source_extractor"] = xr.DataTree(
        extract_sources_to_xarray(data_2d, thresh=thresh, minarea=minarea)
    )


@deprecated("Use model 'source_extractor'")
def extract_roi_to_xarray(
    detector: Detector,
    array_type: str = "pixel",
    thresh: int = 50,
    minarea: int = 5,
) -> None:
    """Extract the roi data converts it to xarray dataset and saves the information to the final result.

    A warning is generated if the processed data_array is empty.

    Parameters
    ----------
    array_type
    detector : Detector
        Pyxel Detector object.
    thresh : int
        Threshold pixel value above which information from the image array is extracted
    minarea : int
        Minimum area of pixels required that are above the threshold for the extractor to extract information

    Raises
    ------
    ValueError
        If parameter 'array_type' is not 'pixel','signal','image',photon' or 'charge'

    Notes
    -----
    For more information, you can find an example here:
    :external+pyxel_data:doc:`examples/models/data_processing/source_extractor/SEP_exposure`.
    """
    source_extractor(
        detector=detector, array_type=array_type, thresh=thresh, minarea=minarea
    )
