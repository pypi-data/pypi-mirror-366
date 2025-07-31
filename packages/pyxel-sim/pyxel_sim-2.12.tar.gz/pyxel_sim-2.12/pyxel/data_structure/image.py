#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel Image class."""

from typing import TYPE_CHECKING

import numpy as np
from typing_extensions import override

from pyxel.data_structure import ArrayBase

if TYPE_CHECKING:
    from pyxel.detectors import Geometry


class Image(ArrayBase):
    """Image class defining and storing information of detector image (unit: adu).

    Accepted array types: ``np.uint16``, ``np.uint32``, ``np.uint64``
    """

    TYPE_LIST = (
        np.dtype(np.uint8),
        np.dtype(np.uint16),
        np.dtype(np.uint32),
        np.dtype(np.uint64),
    )
    NAME = "Image"
    UNIT = "adu"

    def __init__(self, geo: "Geometry"):
        super().__init__(shape=(geo.row, geo.col))

    @override
    def _get_uninitialized_error_message(self) -> str:
        """Get an explicit error message for an uninitialized 'array'.

        This method is used in the property 'array' in the ``Array`` parent class.
        """
        example_model = "simple_amplifier"
        example_yaml_content = """
- name: simple_amplifier
  func: pyxel.models.readout_electronics.simple_amplifier
  enabled: true
"""
        cls_name: str = self.__class__.__name__
        obj_name = "images"
        group_name = "Readout Electronics"

        return (
            f"The '.array' attribute cannot be retrieved because the '{cls_name}'"
            " container is not initialized.\nTo resolve this issue, initialize"
            f" '.array' using a model that generates {obj_name} from the "
            f"'{group_name}' group.\n"
            f"Consider using the '{example_model}' model from"
            f" the '{group_name}' group.\n\n"
            "Example code snippet to add to your YAML configuration file "
            f"to initialize the '{cls_name}' container:\n{example_yaml_content}"
        )
