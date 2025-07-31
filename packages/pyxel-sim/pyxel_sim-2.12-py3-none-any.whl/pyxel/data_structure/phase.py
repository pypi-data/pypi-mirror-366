#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Phase class."""

from typing import TYPE_CHECKING

import numpy as np

from pyxel.data_structure import ArrayBase

if TYPE_CHECKING:
    from pyxel.detectors import Geometry


class Phase(ArrayBase):
    """Phase class.

    Accepted array types: np.float16, np.float32 and np.float64.
    """

    TYPE_LIST = (np.dtype(np.float16), np.dtype(np.float32), np.dtype(np.float64))
    NAME = "Phase"
    UNIT = ""

    def __init__(self, geo: "Geometry"):
        super().__init__(shape=(geo.row, geo.col))
