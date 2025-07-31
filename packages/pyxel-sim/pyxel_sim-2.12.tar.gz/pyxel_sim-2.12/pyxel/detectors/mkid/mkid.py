#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

""":term:`MKID`-array detector modeling class."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from pyxel.data_structure import Phase, _get_array_if_initialized
from pyxel.detectors import Detector
from pyxel.util import memory_usage_details

if TYPE_CHECKING:
    import pandas as pd

    from pyxel.detectors import Characteristics, Environment, MKIDGeometry


class MKID(Detector):
    """:term:`MKID`-based detector class containing all detector attributes and data."""

    def __init__(
        self,
        geometry: "MKIDGeometry",
        environment: "Environment",
        characteristics: "Characteristics",
    ):
        self._geometry: MKIDGeometry = geometry
        self._characteristics: Characteristics = characteristics

        super().__init__(environment=environment)

        self._phase: Phase | None = None
        self._initialize()

    def __eq__(self, other) -> bool:
        return (
            type(self) is type(other)
            and self.geometry == other.geometry
            and self.environment == other.environment
            and self.characteristics == other.characteristics
            and self._phase == other._phase
            and super().__eq__(other)
        )

    def _initialize(self) -> None:
        """TBW."""
        super()._initialize()
        self._phase = Phase(geo=self.geometry)

    def empty(self, reset: bool = True) -> None:
        """Empty the data in the detector.

        Returns
        -------
        None
        """
        super().empty(reset)

        if reset and self._phase and self._phase._array is not None:
            self.phase.array *= 0

    @property
    def geometry(self) -> "MKIDGeometry":
        return self._geometry

    @property
    def characteristics(self) -> "Characteristics":
        return self._characteristics

    @property
    def phase(self) -> Phase:
        """TBW."""
        if not self._phase:
            raise RuntimeError("'phase' not initialized.")

        return self._phase

    def memory_usage(
        self, print_result: bool = True, human_readable: bool = True
    ) -> dict:
        """TBW.

        Returns
        -------
        dict
            Dictionary of attribute memory usage
        """
        attributes = [
            "_photon",
            "_charge",
            "_pixel",
            "_signal",
            "_image",
            "_phase",
            "material",
            "environment",
            "_geometry",
            "_characteristics",
        ]

        return memory_usage_details(
            self, attributes, print_result=print_result, human_readable=human_readable
        )

    # TODO: Refactor this
    def to_dict(self) -> Mapping:
        """Convert an instance of `MKID` to a `dict`."""
        dct = {
            "version": 1,
            "type": "MKID",
            "properties": {
                "geometry": self.geometry.to_dict(),
                "environment": self.environment.to_dict(),
                "characteristics": self.characteristics.to_dict(),
            },
            "data": {
                "photon": self.photon.to_dict(),
                "pixel": _get_array_if_initialized(self._pixel),
                "signal": _get_array_if_initialized(self._signal),
                "image": _get_array_if_initialized(self._image),
                "phase": _get_array_if_initialized(self._phase),
                "data": (
                    None
                    if self._data is None
                    else {
                        key.replace("/", "#"): value
                        for key, value in self._data.to_dict().items()
                    }
                ),
                "charge": (
                    None
                    if self._charge is None
                    else {
                        "array": self._charge.array.copy(),
                        "frame": self._charge.frame.copy(),
                    }
                ),
                "scene": (
                    None
                    if self._scene is None
                    else {
                        key.replace("/", "#"): value
                        for key, value in self._scene.to_dict().items()
                    }
                ),
            },
        }

        return dct

    # TODO: Refactor this
    @classmethod
    def from_dict(cls, dct: Mapping) -> "MKID":
        """Create a new instance of `MKID` from a `dict`."""
        # TODO: This is a simplistic implementation. Improve this.
        import numpy as np
        import xarray as xr

        from pyxel.data_structure import Photon, Scene
        from pyxel.detectors import Characteristics, Environment, MKIDGeometry

        if dct["type"] != "MKID":
            raise ValueError

        if dct["version"] != 1:
            raise ValueError

        properties = dct["properties"]
        geometry = MKIDGeometry.from_dict(properties["geometry"])
        environment = Environment.from_dict(properties["environment"])
        characteristics = Characteristics.from_dict(properties["characteristics"])

        detector = cls(
            geometry=geometry,
            environment=environment,
            characteristics=characteristics,
        )

        data: Mapping[str, Any] = dct["data"]

        detector.photon = Photon.from_dict(
            geometry=geometry, data=data.get("photon", dict())
        )
        detector.pixel.update(data.get("pixel"))
        detector.signal.update(data.get("signal"))
        detector.image.update(data.get("image"))

        if "data" in data:
            detector._data = xr.DataTree.from_dict(
                {
                    key.replace("#", "/"): xr.Dataset.from_dict(value)
                    for key, value in data["data"].items()
                }
            )
        if "scene" in data and (scene_dct := data["scene"]) is not None:
            detector.scene = Scene.from_dict(
                {key.replace("#", "/"): value for key, value in scene_dct.items()}
            )
        if "charge" in data and data["charge"] is not None:
            charge_dct = data["charge"]
            detector.charge._array = np.asarray(charge_dct["array"])

            new_frame: pd.DataFrame = charge_dct["frame"]
            previous_frame: pd.DataFrame = detector.charge._frame
            detector.charge._frame = new_frame[previous_frame.columns]

        return detector
