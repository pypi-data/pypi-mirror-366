#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""General purposes models or routines for all Group Models."""

from pathlib import Path

from pyxel.detectors import Detector


def load_detector(detector: Detector, filename: str | Path) -> None:
    """Load a new detector from a file.

    Raises
    ------
    TypeError
        If the loaded detector has not the same type of the current detector.
    """
    new_detector = Detector.load(filename)

    # Check type of 'new_detector'
    if type(detector) is not type(new_detector):
        raise TypeError(
            f"Wrong detector type from 'filename':'{filename}'. Got type:"
            f" '{type(detector).__name__}', expected '{type(new_detector).__name__}'"
        )

    detector = new_detector


def save_detector(detector: Detector, filename: str | Path) -> None:
    """Save the current detector into a file."""
    detector.save(filename)
