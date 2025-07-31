#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Utility functions."""

# flake8: noqa
from .memory import get_size, memory_usage_details
from .examples import download_examples
from .timing import time_pipeline
from .add_model import create_model, create_model_to_console
from .randomize import set_random_seed
from .fileutil import is_path_relative, resolve_with_working_directory, complete_path
from .image import fit_into_array, load_cropped_and_aligned_image
from .caching import get_cache
from .misc import (
    round_convert_to_int,
    convert_to_int,
    LogFilter,
    convert_unit,
    get_dtype,
)
from .errors import get_uninitialized_error
from .metadata import get_schema, get_metadata, clean_text
