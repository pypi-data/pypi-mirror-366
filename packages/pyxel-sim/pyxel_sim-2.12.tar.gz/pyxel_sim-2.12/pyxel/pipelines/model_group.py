#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""

import logging
import sys
from collections.abc import Iterator, Mapping, Sequence
from copy import deepcopy
from typing import TYPE_CHECKING, Optional

from pyxel.pipelines import ModelFunction

if TYPE_CHECKING:
    from pyxel.detectors import Detector
    from pyxel.exposure.exposure import TqdmProgressBar


# TODO: These methods could also be as a `abc.Sequence` with magical methods:
#       __getitem__, __iter__, __len__, __contains__, ...
class ModelGroup:
    """Manage a collection of model functions.

    Parameters
    ----------
    models : Sequence of ``ModelFunction``
        Sequence of model functions belonging to the group.
    name : str
        Name of this group.
    """

    def __init__(self, models: Sequence[ModelFunction], name: str):
        self._log = logging.getLogger(__name__)
        self._name = name
        self.models: Sequence[ModelFunction] = models

    def __repr__(self):
        cls_name: str = self.__class__.__name__

        all_models: list[str] = [model.name for model in self.models if model.name]

        return f"{cls_name}<name={self._name!r}, models={all_models!r}>"

    def __deepcopy__(self, memo: dict) -> "ModelGroup":
        copied_models = deepcopy(self.models)
        return ModelGroup(models=copied_models, name=self._name)

    def __iter__(self) -> Iterator[ModelFunction]:
        for model in self.models:
            if model.enabled:
                yield model

    def __len__(self) -> int:
        num_elements = 0
        for _ in self:
            num_elements += 1

        return num_elements

    def __getstate__(self) -> Mapping:
        return {"models": tuple(self.models), "name": self._name}

    def __setstate__(self, state: Mapping) -> None:
        self.models = list(state["models"])
        self._name = state["name"]

    def __getattr__(self, item: str) -> ModelFunction:
        for model in self.models:
            if model.name == item:
                return model
        else:
            raise AttributeError(f"Cannot find model {item!r}.")

    def __dir__(self):
        return dir(type(self)) + [model.name for model in self.models]

    def run(
        self,
        detector: "Detector",
        debug: bool,
        progress_bar: Optional["TqdmProgressBar"] = None,
    ):
        """Execute each enabled model in this group.

        Parameters
        ----------
        detector : Detector
        debug : bool
        """
        model: ModelFunction
        for model in self:
            self._log.info("Model: %r", model.name)
            try:
                model(detector)
            except Exception as exc:
                if sys.version_info >= (3, 11):
                    note = (
                        f"This error is raised in group '{self._name}' at "
                        f"model '{model.name}' ({model._func_name})."
                    )
                    exc.add_note(note)

                raise

            # TODO: Refactor
            if debug:
                import numpy as np
                import xarray as xr

                # Get current absolute time
                absolute_time = xr.DataArray(
                    [detector.absolute_time],
                    dims="time",
                    attrs={"units": "s"},
                )

                # Get current Dataset
                ds: xr.Dataset = detector.to_xarray().assign_coords(time=absolute_time)

                # TODO: Fix this dirty hack
                if detector._intermediate is None:
                    new_datatree: xr.DataTree = xr.DataTree()
                    new_datatree.name = "intermediate"
                    new_datatree.attrs = {
                        "long_name": (
                            "Store all intermediate results modified along a pipeline"
                        )
                    }
                    detector._intermediate = new_datatree

                # TODO: Refactor
                pipeline_key: str = f"time_idx_{detector.pipeline_count}"
                if pipeline_key not in detector.intermediate:
                    datatree_single_time: xr.DataTree = xr.DataTree()
                    datatree_single_time.attrs = {
                        "long_name": "Pipeline for one unique time",
                        "pipeline_count": detector.pipeline_count,
                        "time": f"{detector.absolute_time} s",
                    }

                    detector.intermediate[pipeline_key] = datatree_single_time

                # TODO: Refactor
                model_group_key: str = self._name
                if model_group_key not in detector.intermediate[pipeline_key]:
                    datatree_group: xr.DataTree = xr.DataTree()

                    # TODO: Refactor this ?
                    # Convert a model group's name to a better string representation
                    # Example: 'photon_collection' becomes 'Photon Collection'
                    group_name: str = " ".join(
                        map(str.capitalize, self._name.split("_"))
                    )
                    datatree_group.attrs = {"long_name": f"Model group: {group_name}"}
                    detector.intermediate[f"{pipeline_key}/{model_group_key}"] = (
                        datatree_group
                    )

                # TODO: Refactor
                model_key: str = model.name
                if (
                    model_key
                    not in detector.intermediate[f"{pipeline_key}/{model_group_key}"]
                ):
                    datatree_model: xr.DataTree = xr.DataTree()
                    datatree_model.attrs = {
                        "long_name": f"Model name: {model.name!r}",
                        "function_name": f"Model function: {model.func.__name__!r}",
                    }

                    detector.intermediate[
                        f"{pipeline_key}/{model_group_key}/{model_key}"
                    ] = datatree_model

                # TODO: Refactor. Is 'last' needed ?
                last_key: str = "last"
                if last_key not in detector.intermediate:
                    last_full_ds: xr.Dataset = xr.zeros_like(ds)
                else:
                    last_full_ds = detector.intermediate[last_key]  # type: ignore

                for name, data_array in ds.data_vars.items():
                    if name in last_full_ds:
                        previous_data_array = last_full_ds[name]

                        if not np.allclose(data_array, previous_data_array):
                            detector.intermediate[
                                f"{pipeline_key}/{model_group_key}/{model_key}/{name}"
                            ] = data_array
                    else:
                        detector.intermediate[
                            f"{pipeline_key}/{model_group_key}/{model_key}/{name}"
                        ] = data_array

                detector.intermediate[last_key] = xr.DataTree(ds.copy(deep=True))

            if progress_bar is not None:
                progress_bar.update(1)
