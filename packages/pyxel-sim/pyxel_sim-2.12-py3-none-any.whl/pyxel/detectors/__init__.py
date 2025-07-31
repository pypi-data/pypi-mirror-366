#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""The detector attribute and data structure subpackage."""

# flake8: noqa
# Warning: Import order matters
from .channels import Channels, Matrix, ReadoutPosition
from .readout_properties import ReadoutProperties
from .environment import Environment, WavelengthHandling
from .detector import Detector
from .geometry import Geometry
from .characteristics import Characteristics
from .ccd import CCDGeometry, CCD
from .mkid import MKID, MKIDGeometry
from .apd import APD, APDCharacteristics, APDGeometry
from .cmos import CMOSGeometry, CMOS
from .optics import Optics
