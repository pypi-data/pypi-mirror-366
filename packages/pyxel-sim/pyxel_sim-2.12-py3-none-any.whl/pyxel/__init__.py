#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel detector simulation framework."""

# flake8: noqa
from . import _version

__version__: str = _version.get_versions()["version"]

from .options import SetOptions as set_options
from .options import options_wrapper
from .show_versions import show_versions
from .inputs import load_image, load_table, load_datacube, load_header
from .configuration import (
    load,
    loads,
    copy_config_file,
    Configuration,
    build_configuration,
    launch_basic_gui,
)
from .run import (
    calibration_mode,
    exposure_mode,
    observation_mode,
    run,
    run_mode,
    run_mode_dataset,
)
from .notebook import (
    display_detector,
    display_scene,
    display_persist,
    display_html,
    display_calibration_inputs,
    display_simulated,
    display_evolution,
    display_dataset,
    champion_heatmap,
    optimal_parameters,
)
