#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""

from collections import abc
from collections.abc import Iterator, Sequence
from enum import Enum
from numbers import Number
from typing import Literal

import numpy as np
from numpy.typing import NDArray

from pyxel.evaluator import eval_range


class ParameterType(Enum):
    """TBW."""

    # one-dimensional, can be a dataset coordinate
    Simple = "simple"
    # multi-dimensional or loaded from a file in parallel mode, cannot be a dataset coordinate
    Multi = "multi"


def convert_values(
    values,
    parameter_type: ParameterType,
) -> (
    Literal["_"]
    | Sequence[Literal["_"]]
    | Sequence[Number]
    | Sequence[str]
    | Sequence[tuple[Number, ...]]
):
    """Convert a sequence of input values based on a specified parameter type."""
    if parameter_type is ParameterType.Simple or values == "_":
        return values

    return [  # type: ignore[return-value]
        (
            tuple(convert_values(el, parameter_type=parameter_type))
            if (isinstance(el, Sequence) and not isinstance(el, str))
            else el
        )
        for el in values
    ]


# TODO: Add unit tests. See #336
class ParameterValues:
    """Contains keys and values of parameters in a parametric step."""

    def __init__(
        self,
        key: str,
        values: (
            Literal["_"] | Sequence[Literal["_"]] | Sequence[Number] | Sequence[str]
        ),
        boundaries: tuple[float, float] | Sequence[tuple[float, float]] | None = None,
        enabled: bool = True,
        logarithmic: bool = False,
    ):
        # TODO: maybe use numpy to check multi-dimensional input lists
        # Check YAML input (not real values yet) and define parameter type
        if values == "_":
            self.type: ParameterType = ParameterType.Multi

        elif isinstance(values, str) and "numpy" in values:
            self.type = ParameterType.Simple

        elif isinstance(values, abc.Sequence) and any(
            [
                (
                    el == "_"
                    or (isinstance(el, abc.Sequence) and not isinstance(el, str))
                )
                for el in values
            ]
        ):
            self.type = ParameterType.Multi

        elif isinstance(values, abc.Sequence) and all(
            [isinstance(el, Number | str) for el in values]
        ):
            self.type = ParameterType.Simple

        else:
            raise ValueError("Parameter values cannot be initiated with those values.")

        if "sampling.start_time" in key:
            key = "detector.sampling_properties.start_time"

        # unique identifier to the step. example: 'detector.geometry.row'
        self._key: str = key
        self._values: (
            Literal["_"]
            | Sequence[Literal["_"]]
            | Sequence[Number]
            | Sequence[str]
            | Sequence[tuple[Number, ...]]
        ) = convert_values(values, parameter_type=self.type)

        # short  name identifier: 'row'
        self._short_name = key.split(".")[-1]

        self._enabled: bool = enabled
        self._logarithmic: bool = logarithmic

        if boundaries is None:
            boundaries_array: NDArray[np.float64] | None = None
        else:
            boundaries_array = np.array(boundaries, dtype=np.float64)
            if boundaries_array.ndim == 1:
                if boundaries_array.shape != (2,):
                    raise ValueError(
                        "Expecting only two values for the boundaries. Got:"
                        f" {boundaries}."
                    )
            elif boundaries_array.ndim == 2:
                if boundaries_array.shape != (len(values), 2):
                    raise ValueError(
                        f"Expecting a 2x{len(values)} values for the boundaries. Got:"
                        f" {boundaries}."
                    )
            else:
                raise ValueError(f"Wrong format of boundaries. Got {boundaries}.")

        self._boundaries: NDArray[np.float64] | None = boundaries_array

        self._current: Literal["_"] | Number | tuple[Number, ...] | str | None = None

    def __repr__(self) -> str:
        cls_name: str = self.__class__.__name__

        return (
            f"{cls_name}<key={self.key!r}, values={self.values!r},"
            f" enabled={self.enabled!r}>"
        )

    def __len__(self) -> int:
        try:
            values: Sequence = eval_range(self.values)
        except Exception as exc:
            raise NameError(
                f"Wrong value: {self.values!r} for key: {self.key!r}. Error: {exc}"
            ) from exc

        return len(values)

    # TODO: Is method '__contains__' needed ? If yes then this class will act as a `Collections.abc.Sequence`
    def __iter__(self) -> Iterator[Number]:
        values = eval_range(self.values)
        yield from values

    @property
    def key(self) -> str:
        """TBW."""
        return self._key

    @property
    def short_name(self) -> str:
        """TBW."""
        return self._short_name

    @property
    def values(
        self,
    ) -> (
        Literal["_"]
        | Sequence[Literal["_"]]
        | Sequence[Number]
        | Sequence[str]
        | Sequence[tuple[Number, ...]]
    ):
        """TBW."""
        return self._values

    @property
    def enabled(self) -> bool:
        """TBW."""
        return self._enabled

    @property
    def current(self) -> Literal["_"] | Number | tuple[Number, ...] | str | None:
        """TBW."""
        return self._current

    @current.setter
    def current(self, value: Literal["_"] | str | Number | tuple[Number, ...]) -> None:
        """TBW."""
        self._current = value

    @property
    def logarithmic(self) -> bool:
        """TBW."""
        return self._logarithmic

    @property
    def boundaries(self) -> NDArray[np.float64] | None:
        """TBW."""
        return self._boundaries
