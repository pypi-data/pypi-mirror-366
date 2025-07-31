#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Avalanche gain model."""

from pyxel.detectors import APD


def apd_gain(detector: APD) -> None:
    """Apply APD gain.

    Parameters
    ----------
    detector : APD
        Pyxel APD detector object.

    Notes
    -----
    For more information, you can find an example here:
    :external+pyxel_data:doc:`use_cases/APD/saphira`.
    """

    if not isinstance(detector, APD):
        raise TypeError("Expecting a 'APD' detector object.")

    if detector.charge.frame_empty():
        array_copy = detector.charge.array.copy()
        detector.charge.empty()
        array_copy *= detector.characteristics.avalanche_gain
        detector.charge.add_charge_array(array=array_copy)

    else:
        frame_copy = detector.charge.frame.copy()
        detector.charge.empty()
        frame_copy.number *= detector.characteristics.avalanche_gain
        detector.charge.add_charge_dataframe(new_charges=frame_copy)
