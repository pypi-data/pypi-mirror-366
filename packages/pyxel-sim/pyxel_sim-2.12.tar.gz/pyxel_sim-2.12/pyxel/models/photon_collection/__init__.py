#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Photon generation models are used to add to and manipulate data in Photon array
inside the Detector object."""

# flake8: noqa
from .illumination import illumination
from .load_image import load_image
from .shot_noise import shot_noise
from .stripe_pattern import stripe_pattern
from .poppy import optical_psf
from .point_spread_function import load_psf, load_wavelength_psf
from .ariel_airs import wavelength_dependence_airs
from .simple_collection import simple_collection
from .usaf_illumination import usaf_illumination
