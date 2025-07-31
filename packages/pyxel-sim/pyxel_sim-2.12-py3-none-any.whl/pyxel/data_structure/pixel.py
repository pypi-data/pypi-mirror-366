#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel Pixel class."""

from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import ArrayLike
from typing_extensions import override

from pyxel.data_structure import ArrayBase

if TYPE_CHECKING:
    from pyxel.detectors import Geometry


class Pixel(ArrayBase):
    """Pixel class defining and storing information of charge packets within pixel (unit: e⁻).

    Accepted array types: ``np.int32``, ``np.int64``, ``np.uint32``, ``np.uint64``,
    ``np.float16``, ``np.float32``, ``np.float64``.
    """

    TYPE_LIST = (
        np.dtype(np.float16),
        np.dtype(np.float32),
        np.dtype(np.float64),
    )
    NAME = "Pixel"
    UNIT = "e⁻"

    def __init__(self, geo: "Geometry"):
        super().__init__(shape=(geo.row, geo.col))

    @override
    def empty(self):
        """Empty the array by setting the array to zero array in detector shape."""
        self._array = np.zeros(shape=self._shape, dtype=float)
        # TODO: Rename this method to '_update' ?

    @override
    def update(self, data: ArrayLike | None) -> None:
        """Update 'array' attribute.

        This method updates 'array' attribute of this object with new data.
        If the data is None, then the object is empty.

        Parameters
        ----------
        data : array_like, Optional

        Examples
        --------
        >>> from pyxel.data_structure import Photon
        >>> obj = Photon(...)
        >>> obj.update([[1, 2], [3, 4]])
        >>> obj.array
        array([[1, 2], [3, 4]])

        >>> obj.update(None)  # Equivalent to obj.empty()
        """
        if data is not None:
            self.array = np.asarray(data)
        else:
            self._array = None

    @override
    def _get_uninitialized_error_message(self) -> str:
        """Get an explicit error message for an uninitialized 'array'.

        This method is used in the property 'array' in the ``Array`` parent class.
        """
        example_model = "simple_collection"
        example_yaml_content = """
- name: simple_collection
  func: pyxel.models.charge_collection.simple_collection
  enabled: true
"""
        cls_name: str = self.__class__.__name__
        obj_name = "pixels"
        group_name = "Charge Collection"

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
