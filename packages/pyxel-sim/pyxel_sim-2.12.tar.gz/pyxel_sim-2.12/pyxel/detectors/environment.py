#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
from typing_extensions import Self

from pyxel.util import get_size, get_uninitialized_error

if TYPE_CHECKING:
    import xarray as xr


@dataclass
class WavelengthHandling:
    """Information about multi-wavelength."""

    cut_on: float
    cut_off: float
    resolution: int

    def __post_init__(self):
        if self.cut_on <= 0:
            raise ValueError(f"'cut_on' must be > 0. {self.cut_on=}")

        if self.cut_on > self.cut_off:
            raise ValueError(
                "'cut_off' must be bigger than 'cut_on'. "
                f"{self.cut_on=}, {self.cut_off=}"
            )

        if self.resolution <= 0:
            raise ValueError(f"'resolution' must be > 0. {self.resolution=}")

    def to_dict(self) -> dict[str, float | int]:
        return {
            "cut_on": self.cut_on,
            "cut_off": self.cut_off,
            "resolution": self.resolution,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            cut_on=data["cut_on"],
            cut_off=data["cut_off"],
            resolution=data["resolution"],
        )

    def get_wavelengths(self) -> "xr.DataArray":
        # Late import to speedup start-up time
        import xarray as xr

        return xr.DataArray(
            np.arange(self.cut_on, self.cut_off, self.resolution),
            dims="wavelength",
            attrs={"units": "nm"},
        )


class Environment:
    """Environmental attributes of the detector.

    Parameters
    ----------
    temperature : float, optional
        Temperature of the detector. Unit: K
    wavelength : float, WavelengthHandling, optional
        Information about multi-wavelength. Unit: nm
    """

    def __init__(
        self,
        temperature: float | None = None,
        wavelength: float | WavelengthHandling | None = None,
    ):
        if isinstance(temperature, int | float) and not (0.0 < temperature <= 1000.0):
            raise ValueError("'temperature' must be between 0.0 and 1000.0.")

        if isinstance(wavelength, int | float) and not (wavelength > 0.0):
            raise ValueError("'wavelength' must be strictly positive.")

        self._temperature: float | None = (
            float(temperature) if temperature is not None else None
        )

        self._wavelength: float | WavelengthHandling | None = (
            float(wavelength) if isinstance(wavelength, int | float) else wavelength
        )

        self._numbytes = 0

    def __repr__(self) -> str:
        cls_name: str = self.__class__.__name__
        return f"{cls_name}(temperature={self._temperature!r}, wavelength={self._wavelength!r})"

    def __eq__(self, other) -> bool:
        return (
            type(self) is type(other)
            and self._temperature == other._temperature
            and self._wavelength == other._wavelength
        )

    @property
    def temperature(self) -> float:
        """Get Temperature of the detector."""
        if self._temperature is None:
            raise ValueError(
                get_uninitialized_error(
                    name="temperature",
                    parent_name="environment",
                )
            )

        return self._temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        """Set Temperature of the detector."""
        if not (0.0 < value <= 1000.0):
            raise ValueError("'temperature' must be between 0.0 and 1000.0.")

        self._temperature = value

    @property
    def wavelength(self) -> float | WavelengthHandling:
        """Get wavelength of the detector."""
        if self._wavelength is None:
            raise ValueError(
                get_uninitialized_error(
                    name="wavelength",
                    parent_name="environment",
                )
            )
        return self._wavelength

    @wavelength.setter
    def wavelength(self, value: int | float | WavelengthHandling) -> None:
        """Set wavelength of the detector."""
        if isinstance(value, int | float):
            if value <= 0.0:
                raise ValueError("'wavelength' must be strictly positive.")
        elif not isinstance(value, WavelengthHandling):
            raise TypeError("A WavelengthHandling object or a float must be provided.")

        self._wavelength = value

    @property
    def numbytes(self) -> int:
        """Recursively calculates object size in bytes using Pympler library.

        Returns
        -------
        int
            Size of the object in bytes.
        """
        self._numbytes = get_size(self)
        return self._numbytes

    def to_dict(self) -> Mapping:
        """Get the attributes of this instance as a `dict`."""
        if self._wavelength is None:
            wavelength_dict: dict[str, int | float | dict] = {}
        elif isinstance(self._wavelength, int | float):
            wavelength_dict = {"wavelength": self._wavelength}
        else:
            wavelength_dict = {"wavelength": self._wavelength.to_dict()}

        return {"temperature": self._temperature} | wavelength_dict

    @classmethod
    def from_dict(cls, dct: Mapping) -> Self:
        """Create a new instance of `Geometry` from a `dict`."""

        value = dct.get("wavelength")

        if value is None:
            wavelength: float | WavelengthHandling | None = None
        elif isinstance(value, int | float):
            wavelength = float(value)
        elif isinstance(value, dict):
            wavelength = WavelengthHandling.from_dict(value)
        else:
            raise NotImplementedError

        return cls(temperature=dct.get("temperature"), wavelength=wavelength)

    def dump(self) -> dict[str, float | dict[str, float | int] | None]:
        return {
            "temperature": self._temperature,
            "wavelength": (
                self._wavelength.to_dict()
                if isinstance(self._wavelength, WavelengthHandling)
                else self._wavelength
            ),
        }
