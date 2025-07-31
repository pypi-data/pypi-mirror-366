#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""

from collections.abc import Iterator, Sequence
from typing import Any

from pyxel.pipelines import ModelFunction, ModelGroup


class DetectionPipeline:
    """Represent a pipeline of detection models organized into different groups."""

    # Define the order of steps in the pipeline.
    MODEL_GROUPS: tuple[str, ...] = (
        "scene_generation",
        "photon_collection",
        "phasing",
        "charge_generation",
        "charge_collection",
        "charge_transfer",
        "charge_measurement",
        "signal_transfer",
        "readout_electronics",
        "data_processing",
    )

    # TODO: develop a ModelGroupList class ? See #333
    def __init__(
        self,  # TODO: Too many instance attributes
        scene_generation: Sequence[ModelFunction] | None = None,
        photon_collection: Sequence[ModelFunction] | None = None,
        phasing: Sequence[ModelFunction] | None = None,
        charge_generation: Sequence[ModelFunction] | None = None,
        charge_collection: Sequence[ModelFunction] | None = None,
        charge_transfer: Sequence[ModelFunction] | None = None,
        charge_measurement: Sequence[ModelFunction] | None = None,
        signal_transfer: Sequence[ModelFunction] | None = None,
        readout_electronics: Sequence[ModelFunction] | None = None,
        data_processing: Sequence[ModelFunction] | None = None,
    ):
        self._scene_generation: ModelGroup | None = (
            ModelGroup(scene_generation, name="scene_generation")
            if scene_generation
            else None
        )

        self._photon_collection: ModelGroup | None = (
            ModelGroup(photon_collection, name="photon_collection")
            if photon_collection
            else None
        )

        self._phasing: ModelGroup | None = (
            ModelGroup(phasing, name="phasing") if phasing else None
        )  # MKID-array

        self._charge_generation: ModelGroup | None = (
            ModelGroup(charge_generation, name="charge_generation")
            if charge_generation
            else None
        )

        self._charge_collection: ModelGroup | None = (
            ModelGroup(charge_collection, name="charge_collection")
            if charge_collection
            else None
        )

        self._charge_measurement: ModelGroup | None = (
            ModelGroup(charge_measurement, name="charge_measurement")
            if charge_measurement
            else None
        )

        self._readout_electronics: ModelGroup | None = (
            ModelGroup(readout_electronics, name="readout_electronics")
            if readout_electronics
            else None
        )

        self._charge_transfer: ModelGroup | None = (
            ModelGroup(charge_transfer, name="charge_transfer")
            if charge_transfer
            else None
        )  # CCD

        self._signal_transfer: ModelGroup | None = (
            ModelGroup(signal_transfer, name="signal_transfer")
            if signal_transfer
            else None
        )  # CMOS

        self._data_processing: ModelGroup | None = (
            ModelGroup(data_processing, name="data_processing")
            if data_processing
            else None
        )

    def __repr__(self) -> str:
        cls_name: str = self.__class__.__name__

        return f"{cls_name}<{len(list(self))} model(s)>"

    def __iter__(self) -> Iterator[ModelFunction]:
        for model in self.MODEL_GROUPS:
            models_grp: ModelGroup | None = getattr(self, model)
            if models_grp:
                yield from models_grp

    @property
    def scene_generation(self) -> ModelGroup | None:
        """Get group 'scene generation'."""
        return self._scene_generation

    @property
    def photon_collection(self) -> ModelGroup | None:
        """Get group 'photon collection'."""
        return self._photon_collection

    @property
    def phasing(self) -> ModelGroup | None:
        """Get group 'phasing'."""
        return self._phasing

    @property
    def charge_generation(self) -> ModelGroup | None:
        """Get group 'charge generation'."""
        return self._charge_generation

    @property
    def charge_collection(self) -> ModelGroup | None:
        """Get group 'charge collection'."""
        return self._charge_collection

    @property
    def charge_transfer(self) -> ModelGroup | None:
        """Get group 'charge transfer'."""
        return self._charge_transfer

    @property
    def charge_measurement(self) -> ModelGroup | None:
        """Get group 'charge measurement'."""
        return self._charge_measurement

    @property
    def signal_transfer(self) -> ModelGroup | None:
        """Get group 'signal transfer'."""
        return self._signal_transfer

    @property
    def readout_electronics(self) -> ModelGroup | None:
        """Get group 'readout electronics'."""
        return self._readout_electronics

    @property
    def data_processing(self) -> ModelGroup | None:
        """Get group 'data processing'."""
        return self._data_processing

    @property
    def model_group_names(self) -> tuple[str, ...]:
        """Get all model groups."""
        return self.MODEL_GROUPS

    # TODO: Is this method used ?
    def get_model(self, name: str) -> ModelFunction:
        """Return a ``ModelFunction`` object for the specified model name.

        Parameters
        ----------
        name: str
            Name of the model.

        Returns
        -------
        ModelFunction

        Raises
        ------
        AttributeError
            If model with the specified name is not found.
        """
        group_name: str
        for group_name in self.model_group_names:
            model_group: ModelGroup = getattr(self, group_name)
            if model_group:
                model: ModelFunction
                for model in model_group.models:
                    if name == model.name:
                        return model
        raise AttributeError("Model has not been found.")

    def describe(self) -> Iterator[str]:
        for model_group_name in self.MODEL_GROUPS:
            models_grp: ModelGroup | None = getattr(self, model_group_name)
            if not models_grp:
                continue

            yield f"PYXEL / Group: {models_grp._name}"

            model: ModelFunction
            for model in models_grp:
                yield f"PYXEL /  func: {model.func.__module__}.{model.func.__name__}"
                yield f"PYXEL /  name: {model.name}"
                yield "PYXEL /  arguments:"

                for key, value in model.arguments.items():
                    yield f"PYXEL /    {key}: {value}"

    def dump(self) -> dict[str, list[dict[str, str | bool | dict[str, Any] | None]]]:
        dct: dict[str, list[dict[str, str | bool | dict[str, Any] | None]]] = {}

        if models_group := self._scene_generation:
            dct["scene_generation"] = [model.dump() for model in models_group.models]

        if models_group := self._photon_collection:
            dct["photon_collection"] = [model.dump() for model in models_group.models]

        if models_group := self._phasing:
            dct["phasing"] = [model.dump() for model in models_group.models]

        if models_group := self._charge_generation:
            dct["charge_generation"] = [model.dump() for model in models_group.models]

        if models_group := self._charge_collection:
            dct["charge_collection"] = [model.dump() for model in models_group.models]

        if models_group := self._charge_transfer:
            dct["charge_transfer"] = [model.dump() for model in models_group.models]

        if models_group := self._charge_measurement:
            dct["charge_measurement"] = [model.dump() for model in models_group.models]

        if models_group := self._signal_transfer:
            dct["signal_transfer"] = [model.dump() for model in models_group.models]

        if models_group := self._readout_electronics:
            dct["readout_electronics"] = [model.dump() for model in models_group.models]

        if models_group := self._data_processing:
            dct["data_processing"] = [model.dump() for model in models_group.models]

        return dct
