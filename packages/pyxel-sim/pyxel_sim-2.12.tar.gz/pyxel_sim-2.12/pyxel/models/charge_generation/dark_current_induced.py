# Copyright (c) 2023, Florian MORIOUSEF, Vincent GOIFFON, Alexandre LE ROCH, Aubin ANTONSANTI, ISAE-SUPAERO
#
# vincent.goiffon@isae-supaero.fr
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


"""Model to generate charge due to dark current induced by radiation.

The Dark Current Model description can be found in:
A. Le Roch et al., "Radiation-Induced Leakage Current and Electric Field Enhancement in CMOS Image Sensor Sense Node
Floating Diffusions,"
in IEEE Transactions on Nuclear Science, vol. 66, no. 3, pp. 616-624, March 2019, doi: 10.1109/TNS.2019.2892645.
Jean-Marc Belloir, Vincent Goiffon, Cédric Virmontois, Mélanie Raine, Philippe Paillet, Olivier Duhamel,
Marc Gaillardin, Romain Molina, Pierre Magnan, and Olivier Gilard, "Pixel pitch and particle energy influence on the
dark current distribution of neutron irradiated CMOS image sensors," Opt. Express 24, 4299-4315 (2016)

"""

import warnings

import numpy as np
from astropy import constants as const

from pyxel.detectors import CCD, CMOS
from pyxel.util import set_random_seed

warnings.filterwarnings("once", category=RuntimeWarning, append=True)


def damage_factors(
    annealing_time: float,
    eact_dc: float,
    temperature: float,
    kdark_srour: float,
    gamma_dark: float,
    depletion_volume: float,
    displacement_dose: float,
) -> tuple[float, float]:
    """Calculaye damage factors and return as list [nu_dark, mu_dark].

    Parameters
    ----------
    annealing_time : float
        Annealing time. Unit: s
    eact_dc : float
        Activation energy parameter. Unit: eV
    temperature : float
        Temperature parameter. Unit K
    kdark_srour : float
        Damage factor K. Unit e-/cm3/sec per MeV/g
    gamma_dark : float
        Gamma dark parameter. Unit 1/µm3/(TeV/g)
    depletion_volume : float
        Depletion volume parameter. Unit µm3
    displacement_dose : float
        Displacement dose parameter. Unit TeV/g

    Returns
    -------
    float
        nu_dark. Unit: e-/s
    float
        mu_dark: Mean number of interactions per pixel. Unit: no units
    """

    k = const.k_B.value
    q = const.e.value

    # Linear fit of Srour & Lo annealing factor (TNS 2000) in the 10^4 - 5.10^6 s range
    annealing_factor = (-0.3965 * np.log10(annealing_time) + 3.5948) / 1.3024
    operating_temperature_correction = np.exp(
        (-eact_dc * q / k / temperature) - (-eact_dc * q / k / 300)
    )
    kdark = (
        kdark_srour * annealing_factor * operating_temperature_correction / 1e4**3 * 1e6
    )
    nu_dark = kdark / gamma_dark
    mu_dark = (
        gamma_dark * depletion_volume * displacement_dose
    )  # mean number of interactions per pixel

    return nu_dark, mu_dark


def damage_factors_silicon(
    annealing_time: float,
    temperature: float,
    depletion_volume: float,
    displacement_dose: float,
) -> tuple[float, float]:
    """Return damage factors (for silicon device) calculation list [nu_dark, mu_dark].

    based on:
    Source: J. R. Srour and D. H. Lo, "Universal damage factor for radiation-induced dark current in silicon devices,"
    in IEEE Transactions     xon Nuclear Science, vol. 47, no. 6, pp. 2451-2459, Dec. 2000, doi: 10.1109/23.903792.

    Parameters
    ----------
    annealing_time : float
        Annealing time. Unit: weeks
    temperature :
        Temperature parameter. Unit: K
    depletion_volume :
        Depletion volume parameter. Unit: µm3
    displacement_dose :
        Displacement dose parameter. Unit: TeV/g

    Returns
    -------
    float
        nu_dark. Unit: e-/s
    float
        mu_dark: Mean number of interactions per pixel. Unit: no units
    """

    eact_dc = 0.63  # eV
    kdark_srour = 1.9e5  # e-/cm3/sec per MeV/g
    gamma_dark = 0.097179425484859 / 4100  # 1/µm3/(TeV/g)
    annealing_time = annealing_time * 7 * 24 * 3600  # convert week --> sec

    return damage_factors(
        annealing_time=annealing_time,
        eact_dc=eact_dc,
        temperature=temperature,
        kdark_srour=kdark_srour,
        gamma_dark=gamma_dark,
        depletion_volume=depletion_volume,
        displacement_dose=displacement_dose,
    )


def compute_radiation_induced_dark_current(
    number_of_rows: int,
    number_of_columns: int,
    mu_dark: float,
    nu_dark: float,
    integration_time: float,
    shot_noise: bool,
) -> np.ndarray:
    """Return Dark Signal Frame.

    Parameters
    ----------
    number_of_rows : int
        Number of rows. Unit: pixel
    number_of_columns : int
        Number of columns. Unit: pixel
    mu_dark : float
        Mean number of interactions per pixel. Unit: no unit
    nu_dark : float
        Parameter nu_dark. Unit: e-/s
    integration_time : float
        Integration time. Unit: s
    shot_noise : bool
        Shot noise: true for shotnoise

    Returns
    -------
    np.ndarray
        DarkCurrentFrame. Unit: e-
    """

    # Define the Dark Current Frame
    dark_current_frame = np.zeros((number_of_rows, number_of_columns))  # e-

    # Assign a number of interactions for each pixel of the frame
    interactions_array = np.random.poisson(
        mu_dark,
        size=(number_of_rows, number_of_columns),
    )

    for i in range(1, np.max(interactions_array)):
        # Index of pixels with i events
        temp = np.array(np.where(interactions_array == i))
        temp = np.swapaxes(temp, 0, 1)

        temp_darkcurrent = np.random.exponential(
            scale=nu_dark, size=(i, len(temp))
        )  # e-/s

        if i > 1:
            # if one pixel has more than 1 interaction, sum darkcurrent contributions
            temp_darkcurrent = np.sum(temp_darkcurrent, axis=0)
        else:
            temp_darkcurrent = np.reshape(
                temp_darkcurrent, (np.shape(temp_darkcurrent)[1])
            )

        for pixels in range(len(temp)):
            row = temp[pixels][0]
            column = temp[pixels][1]

            # assign dark current value to corresponding pixel, e-/s
            dark_current_frame[row, column] = temp_darkcurrent[pixels]

    dark_signal_frame = np.round(dark_current_frame * integration_time)  # e-

    if shot_noise:
        dark_signal_frame = np.random.poisson(dark_signal_frame).astype(float)

    if np.isinf(dark_signal_frame).any():
        warnings.warn(
            "Unphysical high value for dark current from fixed pattern noise"
            " distribution will result in inf values. Enable a FWC model to ensure a"
            " physical limit.",
            RuntimeWarning,
            stacklevel=2,
        )

    return dark_signal_frame


def radiation_induced_dark_current(
    detector: CCD | CMOS,
    depletion_volume: float,
    annealing_time: float,
    displacement_dose: float,
    shot_noise: bool,
    seed: int | None = None,
) -> None:
    """Model to add dark current induced by radiation to the detector charge.

    The radiation induced dark current model description can be found in :cite:p:`RadiationLeRoch2019`
    and :cite:p:`Belloir:16`.

    Parameters
    ----------
    detector : Detector
        Pyxel detector object.
    depletion_volume : float
        Depletion volume parameter. Unit: µm3.
    annealing_time : float
        Annealing time. Unit: weeks
    displacement_dose : float
        Displacement dose parameter. Unit: TeV/g
    shot_noise : bool
        True to enable shot noise.
    seed : int, optional

    Notes
    -----
    For more information, you can find an example here:
    :external+pyxel_data:doc:`examples/models/dark_current_induced/dark_current_induced`.
    """
    geo = detector.geometry
    temperature = detector.environment.temperature
    nu_dark, mu_dark = damage_factors_silicon(
        annealing_time=annealing_time,
        temperature=temperature,
        depletion_volume=depletion_volume,
        displacement_dose=displacement_dose,
    )

    integration_time = detector.time_step
    number_of_rows, number_of_columns = geo.shape

    with set_random_seed(seed):
        dark_signal_frame = compute_radiation_induced_dark_current(
            number_of_rows=number_of_rows,
            number_of_columns=number_of_columns,
            mu_dark=mu_dark,
            nu_dark=nu_dark,
            integration_time=integration_time,
            shot_noise=shot_noise,
        )
    detector.charge.add_charge_array(dark_signal_frame)
