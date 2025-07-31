#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel Photon class to generate and track photon."""

import warnings
from collections.abc import Hashable, Mapping
from typing import TYPE_CHECKING, Any, Union

import numpy as np
from typing_extensions import Self

from pyxel.util import convert_unit, get_size

if TYPE_CHECKING:
    import xarray as xr
    from matplotlib.pyplot import AxesImage

    from pyxel.detectors import Geometry


class Photon:
    """Photon class designed to handle the storage of monochromatic (unit: ph or multi-wavelength photons (unit ph/nm).

    Monochromatic photons are stored in a 2D Numpy array and
    multi-wavelength photons are stored in a 3D Xarray DataArray.

    Accepted array types: ``np.float16``, ``np.float32``, ``np.float64``

    Examples
    --------
    Create an empty Photon container

    >>> import numpy as np
    >>> from pyxel.detectors import CCD, CCDGeometry, Characteristics, Environment
    >>> detector = CCD(
    ...     geometry=CCDGeometry(row=5, col=5),
    ...     characteristics=Characteristics(),
    ...     environment=Environment(),
    ... )
    >>> detector.photon
    Photon<UNINITIALIZED, shape=(5, 5)>
    >>> detector.ndim
    0
    >>> detector.shape
    ()

    Use monochromatic photons

    >>> detector.photon.empty()
    >>> detector.photon.array = np.zeros(shape=(5, 5), dtype=float)
    >>> detector.photon
    Photon<shape=(5, 5), dtype=float64>

    >>> detector.photon.array = detector.photon.array + np.ones(shape=(5, 5))
    >>> detector.photon += np.ones(shape=(5, 5))

    >>> detector.photon.array
    array([[2., ...., 2.],
           ...,
           [2., ..., 2.]])
    >>> detector.photon.to_xarray()
    <xarray.DataArray 'photon' (y: 5, x: 5)>
    array([[2., ...., 2.],
           ...,
           [2., ..., 2.]])
    Coordinates:
      * y        (y) int64 0 1 2 3 4
      * x        (x) int64 0 1 2 3 4
    Attributes:
        units:      Ph
        long_name:  Photon

    Use multi-wavelength photons

    >>> detector.photon.empty()
    >>> new_photon_3d = xr.DataArray(
    ...     np.ones(shape=(4, 5, 5), dtype=float),
    ...     dims=["wavelength", "y", "x"],
    ...     coords={"wavelength": [400.0, 420.0, 440.0, 460.0]},
    ... )

    >>> detector.photon.array_3d = detector.photon.array_3d + new_photon_3d
    >>> detector.photon += new_photon_3d

    >>> detector.photon.array_3d
    <xarray.DataArray 'photon' (wavelength: 4, y: 5, x: 5)>
    array([[[2., ...., 2.],
            ...,
            [2., ..., 2.]]])
    Coordinates:
      * wavelength  (wavelength) float 400.0 ... 460.0
    """

    TYPE_LIST = (
        np.dtype(np.float16),
        np.dtype(np.float32),
        np.dtype(np.float64),
    )

    def __init__(self, geo: "Geometry"):
        self._array: np.ndarray | "xr.DataArray" | None = None

        self._num_rows: int = geo.row
        self._num_cols: int = geo.col

    def __repr__(self) -> str:
        # Late import to speedup start-up time
        import xarray as xr

        cls_name = self.__class__.__name__

        if self._array is None:
            return (
                f"{cls_name}<UNINITIALIZED, shape={(self._num_rows, self._num_cols)}>"
            )

        elif isinstance(self._array, np.ndarray):
            return f"{cls_name}<shape={self.shape}, dtype={self.dtype}>"

        elif isinstance(self._array, xr.DataArray):
            dct = self._array.sizes
            result = ", ".join([f"{key}: {value}" for key, value in dct.items()])
            return f"{cls_name}<{result:s}>"

        else:
            raise NotImplementedError

    def __eq__(self, other) -> bool:
        # Late import to speedup start-up time
        import xarray as xr

        if type(self) is not type(other):
            return False

        if self._array is other._array is None:
            return True

        if isinstance(self._array, np.ndarray):
            return np.array_equal(self._array, other._array)

        if isinstance(self._array, xr.DataArray):
            return self._array.equals(other._array)

        return False

    def __array__(self, dtype: np.dtype | None = None) -> np.ndarray:
        if self._array is None:
            raise ValueError("Not initialized")

        return np.asarray(self.array, dtype=dtype)

    def __iadd__(self, other: Union[np.ndarray, "xr.DataArray"]) -> Self:
        # Late import to speedup start-up time
        import xarray as xr

        if isinstance(other, np.ndarray) and isinstance(self._array, xr.DataArray):
            raise TypeError("data must be a 3D DataArray")

        if isinstance(other, xr.DataArray) and isinstance(self._array, np.ndarray):
            raise TypeError("data must be a 2D Numpy array")

        if self._array is not None:
            self._array += other
        else:
            self._array = other
        return self

    def __add__(self, other: Union[np.ndarray, "xr.DataArray"]) -> Self:
        # Late import to speedup start-up time
        import xarray as xr

        if isinstance(other, np.ndarray) and isinstance(self._array, xr.DataArray):
            raise TypeError("Must be a 3D DataArray")

        if isinstance(other, xr.DataArray) and isinstance(self._array, np.ndarray):
            raise TypeError("Must be a 2D numpy array")

        if self._array is not None:
            self._array += other
        else:
            self._array = other
        return self

    def _get_uninitialized_2d_error_message(self) -> str:
        """Get an explicit error message for an uninitialized 'array'.

        This method is used in the property 'array' in the ``Array`` parent class.
        """
        example_model = "illumination"
        example_yaml_content = """
- name: illumination
  func: pyxel.models.photon_collection.illumination
  enabled: true
  arguments:
      level: 500
      object_center: [250,250]
      object_size: [15,15]
      option: "elliptic"
"""
        cls_name: str = self.__class__.__name__
        obj_name = "photons"
        group_name = "Photon Collection"

        return (
            f"The '.array' attribute cannot be retrieved because the '{cls_name}'"
            " container is not initialized.\nTo resolve this issue, initialize"
            f" '.array' using a model that generate {obj_name} from the "
            f"'{group_name}' group.\n"
            f"Consider using the '{example_model}' model from"
            f" the '{group_name}' group.\n\n"
            "Example code snippet to add to your YAML configuration file "
            f"to initialize the '{cls_name}' container:\n{example_yaml_content}"
        )

    def _get_uninitialized_3d_error_message(self) -> str:
        """Get an explicit error message for an uninitialized 'array'.

        This method is used in the property 'array' in the ``Array`` parent class.
        """
        example_models = "'load_star_map' and 'simple_aperture'"
        example_yaml_content = """

pipeline:

  scene_generation:
    - name: load_star_map
      func: pyxel.models.scene_generation.load_star_map
      enabled: true
      arguments:
        right_ascension: 56.75 # deg
        declination: 24.1167 # deg
        fov_radius: 0.5 # deg

  photon_collection:
    - name: aperture
      func: pyxel.models.photon_collection.simple_aperture
      enabled: true
      arguments:
       aperture: 126.70e-3
       wavelength_band: [500, 900]
"""
        cls_name: str = self.__class__.__name__
        obj_name = "photons"
        groups_names = "'Scene Generation' and 'Photon Collection'"

        return (
            f"The '.array_3d' attribute cannot be retrieved because the '{cls_name}'"
            " container is not initialized.\nTo resolve this issue, initialize"
            f" '.array_3d' using a model that generate {obj_name} from the "
            f"{groups_names} groups.\n"
            f"Consider using the {example_models} models from"
            f" the {groups_names} groups.\n\n"
            "Example code snippet to add to your YAML configuration file "
            f"to initialize the '{cls_name}' container:\n{example_yaml_content}"
        )

    @property
    def shape(self) -> tuple[int, ...]:
        """Return the shape of the Photon container."""
        if self._array is None:
            return ()

        return self._array.shape

    @property
    def ndim(self) -> int:
        return len(self.shape)

    @property
    def dtype(self) -> np.dtype:
        if self._array is None:
            raise ValueError("Not initialized")

        return self._array.dtype

    @property
    def array(self) -> np.ndarray:
        """Two-dimensional numpy array storing monochromatic photon.

        Only accepts an array with the right type and shape.

        Raises
        ------
        ValueError
            Raised if 'array' is not initialized.

        Examples
        --------
        >>> from pyxel.detectors import CCD, CCDGeometry
        >>> detector = CCD(geometry=CCDGeometry(row=2, col=3))

        >>> import numpy as np
        >>> detector.photon.array = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])

        >>> detector.photon.array
        array([[1., 2., 3.],
              [4., 5., 6.]])
        """
        # Late import to speedup start-up time
        import xarray as xr

        if self._array is None:
            msg: str = self._get_uninitialized_2d_error_message()
            raise ValueError(msg)

        if isinstance(self._array, xr.DataArray):
            raise TypeError("Cannot get a 2D array. A 3D array is already defined !")

        return self._array

    @array.setter
    def array(self, value: np.ndarray) -> None:
        cls_name: str = self.__class__.__name__

        if not isinstance(value, np.ndarray):
            raise TypeError(f"{cls_name} array must be a 2D Numpy array")

        if value.dtype not in self.TYPE_LIST:
            raise ValueError(
                f"{cls_name} array 'dtype' must be one of these values: "
                f"{', '.join(map(str, self.TYPE_LIST))}. Got {value.dtype!r}"
            )

        if value.ndim != 2:
            raise ValueError(
                f"{cls_name} array must have 2 dimensions. Got: {value.ndim}"
            )

        if value.shape != (self._num_rows, self._num_cols):
            raise ValueError(
                f"{cls_name} array must have this shape: {(self._num_rows, self._num_cols)!r}. "
                f"Got: {(self._num_rows, self._num_cols)!r}"
            )

        if isinstance(self._array, np.ndarray) and not isinstance(value, np.ndarray):
            raise TypeError(f"{cls_name} expects a 2D numpy array")

        if np.any(value < 0):
            value = np.clip(value, a_min=0.0, a_max=None)
            warnings.warn(
                "Trying to set negative values in the Photon array! Negative values"
                " clipped to 0.",
                stacklevel=4,
            )

        self._array = value.copy()

    @property
    def array_2d(self) -> np.ndarray:
        """Two-dimensional numpy array storing the data.

        Only accepts an array with the right type and shape.

        Raises
        ------
        ValueError
            Raised if 'array' is not initialized.
        """
        return self.array

    @array_2d.setter
    def array_2d(self, value: np.ndarray) -> None:
        self.array = value

    @property
    def array_3d(self) -> "xr.DataArray":
        """Three-dimensional numpy array storing the data.

        Only accepts an array with the right type and shape.

        Raises
        ------
        ValueError
            Raised if 'array' is not initialized.
        """
        if self._array is None:
            msg: str = self._get_uninitialized_3d_error_message()
            raise ValueError(msg)

        if isinstance(self._array, np.ndarray):
            raise TypeError("Cannot get a 3D array. A 2D array is already defined !")

        return self._array

    @array_3d.setter
    def array_3d(self, value: "xr.DataArray") -> None:
        # Late import to speedup start-up time
        import xarray as xr

        cls_name: str = self.__class__.__name__

        if not isinstance(value, xr.DataArray):
            raise TypeError(f"{cls_name} array must be a 3D DataArray")

        if value.dtype not in self.TYPE_LIST:
            raise ValueError(
                f"{cls_name} array 'dtype' must be one of these values: "
                f"{', '.join(map(str, self.TYPE_LIST))}. Got {value.dtype!r}"
            )

        if value.ndim != 3:
            raise ValueError(
                f"{cls_name} data array must have 3 dimensions. Got: {value.ndim}"
            )

        expected_dims = ("wavelength", "y", "x")
        if value.dims != expected_dims:
            raise ValueError(
                f"{cls_name} data array must have these dimensions: {expected_dims!r}. "
                f"Got: {value.dims!r}"
            )

        shape_3d: Mapping[Hashable, int] = value.sizes
        if (shape_3d["y"], shape_3d["x"]) != (self._num_rows, self._num_cols):
            raise ValueError(
                f"{cls_name} data array must have this shape: {(self._num_rows, self._num_cols)!r}."
                f" Got: {self.shape!r}"
            )

        if "wavelength" not in value.coords:
            raise ValueError(
                f"{cls_name} data array must have coordinates for dimension 'wavelength'."
            )

        if isinstance(self._array, xr.DataArray) and not isinstance(
            value, xr.DataArray
        ):
            raise TypeError(f"{cls_name} expects a 3D Data Array")

        if np.any(value < 0):
            value = value.clip(min=0.0)
            warnings.warn(
                "Trying to set negative values in the Photon array! Negative values"
                " clipped to 0.",
                stacklevel=4,
            )

        self._array = value.copy()

    @property
    def numbytes(self) -> int:
        """Recursively calculates object size in bytes using `Pympler` library.

        Returns
        -------
        int
            Size of the object in bytes.
        """
        if self._array is None:
            return 0

        return get_size(self._array)

    def to_dict(self) -> dict:
        # Late import to speedup start-up time
        import xarray as xr

        dct: dict = {}
        if self._array is None:
            # Do nothing
            pass

        elif isinstance(self._array, np.ndarray):
            dct["array_2d"] = self._array.copy()

        elif isinstance(self._array, xr.DataArray):
            dct["array_3d"] = {
                key.replace("/", "#"): value
                for key, value in self._array.to_dict().items()
            }

        else:
            raise NotImplementedError

        return dct

    @classmethod
    def from_dict(cls, geometry: "Geometry", data: Mapping[str, Any]) -> Self:
        # Late import to speedup start-up time
        import xarray as xr

        obj = cls(geo=geometry)

        if "array_2d" in data:
            obj.array = np.array(data["array_2d"])

        elif "array_3d" in data:
            dct_array_3d = data.get("array_3d", dict())
            new_dct = {
                key.replace("#", "/"): value for key, value in dct_array_3d.items()
            }

            obj.array_3d = xr.DataArray.from_dict(new_dct)

        return obj

    def to_xarray(self, dtype: np.typing.DTypeLike | None = None) -> "xr.DataArray":
        # Late import to speedup start-up time
        import xarray as xr

        if self._array is None:
            return xr.DataArray()

        if isinstance(self._array, np.ndarray):
            num_rows, num_cols = self.shape

            rows = xr.DataArray(
                range(num_rows),
                dims="y",
                attrs={"units": convert_unit("pixel"), "long_name": "Row"},
            )
            cols = xr.DataArray(
                range(num_cols),
                dims="x",
                attrs={"units": convert_unit("pixel"), "long_name": "Column"},
            )

            return xr.DataArray(
                np.array(self.array, dtype=dtype),
                name="photon",
                dims=["y", "x"],
                coords={"y": rows, "x": cols},
                attrs={"units": convert_unit("Ph"), "long_name": "Photon"},
            )

        else:
            data_3d: xr.DataArray = self._array.astype(dtype=dtype)
            data_3d.name = "photon"
            data_3d.coords["y"] = xr.DataArray(
                range(self._num_rows),
                dims="y",
                attrs={"units": "pix", "long_name": "Row"},
            )
            data_3d.coords["x"] = xr.DataArray(
                range(self._num_cols),
                dims="x",
                attrs={"units": "pix", "long_name": "Column"},
            )
            data_3d.coords["wavelength"].attrs = {
                "units": "nm",
                "long_name": "Wavelength",
            }
            data_3d.attrs = {"units": convert_unit("Ph/nm"), "long_name": "Photon"}

            return data_3d

    def plot(self, robust: bool = True) -> "AxesImage":
        """Plot the array using Matplotlib.

        Parameters
        ----------
        robust : bool, optional
            If True, the colormap is computed with 2nd and 98th percentile
            instead of the extreme values.

        Examples
        --------
        >>> detector.photon.plot()

        .. image:: _static/photon_plot.png
        """
        arr: "xr.DataArray" = self.to_xarray()

        return arr.plot.imshow(robust=robust)

    def empty(self) -> None:
        """Empty the data container."""
        self._array = None
