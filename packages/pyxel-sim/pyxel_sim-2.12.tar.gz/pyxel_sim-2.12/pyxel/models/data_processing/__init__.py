#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Subpackage with all models related to the 'DataProcessing' model group."""

# flake8: noqa
from .statistics import statistics
from .remove_cosmic_rays import remove_cosmic_rays
from .source_extractor_model import extract_roi_to_xarray, source_extractor, plot_roi
from .mean_variance import mean_variance
from .linear_regression import linear_regression
from .snr import signal_to_noise_ratio
