# Copyright (c) 2023 Arthur Kadela and Joonas Viuho, Niels Bohr Institute, University of Copenhagen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Model for replicating the gain register in an EMCCD, including clock-induced-charge (CIC)."""

import numba
import numpy as np

from pyxel.detectors import CCD


def multiplication_register_cic(
    detector: CCD,
    total_gain: int,
    gain_elements: int,
    pcic_rate: float,
    scic_rate: float,
) -> None:
    """Calculate total gain of image with EMCCD multiplication register.

    Parameters
    ----------
    detector : CCD
    total_gain : int
    gain_elements : int
        Amount of single stage gain elements in the EMCCD register.
    pcic_rate : float
        Parallel CIC rate
    scic_rate : float
        Serial CIC rate

    Notes
    -----
    For more information, you can find an example here:
    :external+pyxel_data:doc:`examples/models/multiplication_register/emccd_obs`.
    """

    if total_gain < 0 or gain_elements < 0:
        raise ValueError("Wrong input parameter")

    # TODO: Set number of threads used by numba
    #       See: https://numba.readthedocs.io/en/stable/user/threading-layer.html#api-reference

    detector.pixel.array = multiplication_register_poisson(
        image_cube=detector.pixel.array,
        total_gain=total_gain,
        gain_elements=gain_elements,
        pcic_rate=pcic_rate,
        scic_rate=scic_rate,
    ).astype(float)


@numba.njit
def poisson_register(lam, new_image_cube_pix, gain_elements, scic_rate):
    """Calculate the total gain of a single pixel from EMCCD register elements.

    A single pixel is inputted and iterated through the total number of gain elements
    with the result being the resultant signal from the pixel going through the multiplication process.

    Parameters
    ----------
    lam : float
    new_image_cube_pix : int
    gain_elements : int
    scic_rate : float

    Returns
    -------
    int
    """

    new_image_cube_pix = new_image_cube_pix

    for _ in range(gain_elements):
        # Add possibility for a CIC event at each register stage
        new_image_cube_pix += np.random.poisson(scic_rate)

        # Each electron increase has chance for impact ionization, so one needs
        # to loop over all electrons at each gain stage.
        gain_electrons = 0
        for _ in range(np.floor(new_image_cube_pix)):
            gain_electrons += np.random.poisson(lam)
        new_image_cube_pix += gain_electrons

    return new_image_cube_pix


@numba.njit(parallel=True)
def multiplication_register_poisson(
    image_cube: np.ndarray,
    total_gain: int,
    gain_elements: int,
    pcic_rate: float,
    scic_rate: float,
) -> np.ndarray:
    """Calculate total gain of image from EMCCD register.

    Cycles through each pixel within the image provided.
    Returns a final image with signal added.

    Parameters
    ----------
    image_cube : np.ndarray
    total_gain : int
    gain_elements : int
        Amount of single stage gain elements in the EMCCD register.
    pcic_rate : float
        Parallel CIC rate.
    scic_rate : float
        Serial CIC rate.

    Returns
    -------
    np.ndarray
    """

    new_image_cube = np.zeros_like(image_cube, dtype=np.int32)

    # Generate and add pCIC to the frame
    pcic = np.random.poisson(pcic_rate, image_cube.shape)
    new_image_cube += pcic

    lam = total_gain ** (1 / gain_elements) - 1
    yshape, xshape = image_cube.shape

    for j in numba.prange(yshape):
        for i in numba.prange(xshape):
            new_image_cube[j, i] = poisson_register(
                lam=lam,
                new_image_cube_pix=image_cube[j, i],
                gain_elements=gain_elements,
                scic_rate=scic_rate,
            )

    return new_image_cube
