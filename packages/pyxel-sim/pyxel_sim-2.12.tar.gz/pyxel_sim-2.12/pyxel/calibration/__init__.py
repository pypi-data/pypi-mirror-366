#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""

# flake8: noqa
from .algorithm import AlgorithmType, Algorithm
from .user_defined import DaskBFE, DaskIsland
from .protocols import IslandProtocol, ProblemSingleObjective, FittingCallable
from .util import (
    CalibrationResult,
    CalibrationMode,
    Island,
    check_ranges,
    list_to_slice,
    read_data,
    read_datacubes,
    create_processor_data_array,
    list_to_3d_slice,
    FitRange2D,
    FitRange3D,
    to_fit_range,
    check_fit_ranges,
)
from .archipelago import MyArchipelago
from .archipelago_datatree import ArchipelagoDataTree
from .calibration import Calibration, CalibrationMode
from .fitness import sum_of_abs_residuals, sum_of_squared_residuals, reduced_chi_squared
