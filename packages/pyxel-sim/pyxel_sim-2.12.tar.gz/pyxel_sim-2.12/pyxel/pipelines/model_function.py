#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""

import inspect
import sys
import warnings
from collections.abc import Callable, Mapping, MutableMapping, Sequence
from typing import TYPE_CHECKING, Any

from pyxel.evaluator import evaluate_reference

if TYPE_CHECKING:
    import numpy as np

    from pyxel.calibration import FittingCallable
    from pyxel.detectors import Detector


class Arguments(MutableMapping):
    """Arguments class for usage in ModelFunction.

    Class Arguments is initialized from a dictionary of model function arguments.
    It resembles the behaviour of the passed dictionary with additional methods __setattr__ and __getattr__,
    which enable to get and set the model parameters through attribute interface.
    Dictionary of arguments is saved in private attribute _arguments.

    Examples
    --------
    >>> from pyxel.pipelines.model_function import Arguments
    >>> arguments = Arguments({"one": 1, "two": 2})
    >>> arguments
    Arguments({'one': 1, 'two': 2})

    Access arguments
    >>> arguments["one"]
    1
    or
    >>> arguments.one
    1

    Changing parameters
    >>> arguments["one"] = 10
    >>> arguments["two"] = 20
    >>> arguments
    Arguments({'one': 10, 'two': 20})

    Non existing arguments
    >>> arguments["three"] = 3
    KeyError: 'No argument named three !'
    >>> arguments.three = 3
    AttributeError: 'No argument named three !'
    """

    def __init__(self, input_arguments: Mapping[str, Any]):
        self._arguments: dict[str, Any] = {
            key: (
                value
                if (
                    isinstance(value, str)
                    or not isinstance(value, Sequence)
                    or isinstance(value, Mapping)
                )
                else list(value)
            )
            for key, value in input_arguments.items()
        }

    def __setitem__(self, key, value):
        if key not in self._arguments:
            raise KeyError(f"No argument named {key} !")

        self._arguments[key] = value

    def __getitem__(self, key):
        if key not in self._arguments:
            raise KeyError(f"No argument named {key} !")

        return self._arguments[key]

    def __delitem__(self, key):
        del self._arguments[key]

    def __iter__(self):
        return iter(self._arguments)

    def __len__(self):
        return len(self._arguments)

    def __getattr__(self, key):
        # Use non-modified __getattr__ in this case.
        if key == "_arguments":
            return object.__getattribute__(self, "_arguments")

        if key not in self._arguments:
            raise AttributeError(f"'{self!r}' object has no argument {key!r} !")

        return self._arguments[key]

    def __setattr__(self, key, value):
        # Use non-modified __setattr__ in this case.
        if key == "_arguments":
            super().__setattr__(key, value)
            return

        if key not in self._arguments:
            raise AttributeError(f"'{self!r}' object has no argument {key!r} !")

        self._arguments[key] = value

    def __dir__(self):
        return dir(type(self)) + list(self)

    def __repr__(self):
        return f"Arguments({self._arguments})"

    # def __deepcopy__(self, memo) -> "Arguments":
    #     """TBW."""
    #     return Arguments(deepcopy(self._arguments))


# TODO: Improve this class. See issue #132.
class ModelFunction:
    """Create a wrapper function around a Model function.

    Parameters
    ----------
    func : str
        Full name of the model to use with this ModelFunction.
    name : str
        A unique name for this ModelFunction.
    arguments : dict (optional). Default: None
        Parameters that will be passed to 'func'.
    enabled : bool. Default: True
        A flag indicating whether this ModelFunction is enabled or disabled.

    Examples
    --------
    >>> model_func = ModelFunction(
    ...     func="pyxel.models.photon_collection.illumination",
    ...     name="illumination",
    ...     arguments={"level": 1, "option": "foo"},
    ... )

    Access basic parameters

    >>> model_func.name
    'illumination'
    >>> model_func.enabled
    True
    >>> model_func.arguments
    Arguments({'level': 1, 'option': 'foo'})

    Access the arguments with a ``dict`` interface

    >>> list(model_func.arguments)
    ['level', 'option']
    >>> model_func.arguments["level"]
    1
    >>> model_func.arguments["level"] = 2
    TypeError: 'Arguments' object does not support item assignment

    Access the arguments with an attribute interface

    >>> model_func.arguments.level
    1

    Execute this ModelFunction
    >>> from pyxel.detectors import CCD
    >>> detector = CCD(...)
    >>> model_func(detector=detector)
    >>> detector  # Modified detector
    """

    def __init__(
        self,
        func: str,
        name: str,
        arguments: dict | None = None,
        enabled: bool = True,
    ):
        # TODO: Remove this !
        if inspect.isclass(func):
            raise AttributeError("Cannot pass a class to ModelFunction.")

        self._func_name: str = func
        self._func: Callable | None = None

        self._name: str = name
        self.enabled: bool = enabled

        if arguments is None:
            arguments = {}

        self._arguments = Arguments(arguments)

        # self.group = None               # TODO

    def __repr__(self) -> str:
        cls_name: str = self.__class__.__name__

        return (
            f"{cls_name}(name={self.name!r}, func={self._func_name}, "
            f"arguments={self.arguments!r}, enabled={self.enabled!r})"
        )

    @property
    def name(self) -> str:
        """Name for this ModelFunction."""
        return self._name

    @property
    def arguments(self) -> Arguments:
        """TBW."""
        return self._arguments

    @property
    def func(self) -> Callable:
        """TBW."""
        if self._func is None:
            try:
                self._func = evaluate_reference(self._func_name)
            except Exception as exc:
                if sys.version_info >= (3, 11):
                    exc.add_note(f"Cannot retrieve function from {self._func_name!r}")

                raise

        if hasattr(self._func, "__deprecated__"):
            # This will be visible by the user
            msg = self._func.__deprecated__
            warnings.warn(msg, FutureWarning, stacklevel=2)

        return self._func

    def __call__(self, detector: "Detector") -> None:
        """TBW."""
        # TODO: Implement this a context manager
        detector.current_running_model_name = self.name
        self.func(detector, **self.arguments)

    def dump(self) -> dict[str, str | bool | dict[str, Any] | None]:
        if self._arguments:
            return {
                "func": self._func_name,
                "name": self._name,
                "enabled": self.enabled,
                "arguments": dict(self._arguments),
            }
        else:
            return {
                "func": self._func_name,
                "name": self._name,
                "enabled": self.enabled,
            }


class FitnessFunction:
    """Fitness function for model fitting."""

    def __init__(self, func: str, arguments: Mapping[str, Any] | None = None):
        self._func: FittingCallable = evaluate_reference(func)
        self._arguments: Mapping[str, Any] | None = arguments

    def __call__(
        self,
        simulated: "np.ndarray",
        target: "np.ndarray",
        weighting: "np.ndarray",
    ) -> float:
        """Compute fitness."""
        if self._arguments is None:
            result: float = self._func(
                simulated=simulated,
                target=target,
                weighting=weighting,
            )
        else:
            result = self._func(
                simulated=simulated,
                target=target,
                weighting=weighting,
                **self._arguments,
            )
        return result
