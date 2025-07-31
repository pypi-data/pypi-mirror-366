#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Sub-package to retrieve information from JSON Schema and metadata from models."""

import json
import re
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path

from typing_extensions import Self


@cache
def get_schema() -> Mapping:
    """Retrieve the Pyxel JSON Schema.

    This function reads and parses file 'pyxel/static/pyxel_schema.json' into a dictionary.

    Returns
    -------
    dict
        Pyxel JSON Schema
    """
    # Late import
    from pyxel import static

    # Locate the 'pyxel_schema.json' file
    folder = Path(static.__path__[0])
    pyxel_schema_filename = folder / "pyxel_schema.json"

    # Read and parse the JSON schema
    schema = json.loads(pyxel_schema_filename.read_text())

    return schema


def clean_text(data: str) -> str:
    """Remove 'reStructuredText' Sphinx-style references from the input text.

    Parameters
    ----------
    data : str
        Text containing potential reStructuredText term references.

    Returns
    -------
    str
        Cleaned text

    Examples
    --------
    >>> clean_text("Geometrical attributes of a :term:`CCD` detector.")
    'Geometrical attributes of a CCD detector.'
    """
    # Define patterns and their replacement
    patterns: Sequence[tuple[str, str]] = [
        (r":term:`([^`]+)`", r"\1"),
        (r":ref:`([^`]+)`", r"'\1'"),
    ]

    for pattern, replacement in patterns:
        data = re.sub(pattern=pattern, repl=replacement, string=data)

    return data


@dataclass(frozen=True)
class MetadataModel:
    """Metadata for a single model."""

    name: str
    full_name: str = field(repr=False)
    detector: str = field(repr=False)
    status: str | None = field(repr=False)
    description: str = field(repr=False)

    @classmethod
    def from_metadata(cls, dct: Mapping) -> Self:
        """Build a MetadataModel instance from a dictionary."""
        return cls(
            name=dct["name"],
            full_name=dct["full_name"],
            detector=dct["detector"],
            status=dct.get("status"),
            description=clean_text(dct["description"]),
        )


class MetadataGroup(Mapping[str, MetadataModel]):
    """Metadata from a group of models."""

    def __init__(
        self,
        name: str,
        description: str,
        models: Sequence[MetadataModel],
    ):
        self._name = name
        self._description = description
        self._models = {model.name: model for model in models}

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f"{cls_name}<name={self._name!r}, {len(self)} models>"

    def __getitem__(self, key: str) -> MetadataModel:
        if key not in self._models:
            raise KeyError(f"Model {key!r} not found in group {self.name!r}")

        return self._models[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._models)

    def __len__(self) -> int:
        return len(self._models)

    @property
    def name(self) -> str:
        """Return the group name."""
        return self._name

    @property
    def description(self) -> str:
        """Return the group description."""
        return self._description

    @classmethod
    def from_metadata(cls, dct: Mapping) -> Self:
        """Build a MetadataGroup instance from a dictionary."""
        return cls(
            name=dct["group"]["name"],
            description=clean_text(dct["group"]["description"]),
            models=[MetadataModel.from_metadata(dct) for dct in dct["models"]],
        )


class Metadata(Mapping[str, MetadataGroup]):
    """Metadata for all groups."""

    def __init__(self, groups: Sequence[MetadataGroup]):
        self._groups = {group.name: group for group in groups}

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f"{cls_name}<{len(self)} groups>"

    def __getitem__(self, key: str) -> MetadataGroup:
        if key not in self._groups:
            raise KeyError(f"Group {key!r} not found")

        return self._groups[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._groups)

    def __len__(self) -> int:
        return len(self._groups)

    @classmethod
    def from_metadata(cls, dct: Sequence[Mapping]) -> Self:
        """Build a Metadata instance from a dictionary."""
        return cls(
            groups=[
                MetadataGroup.from_metadata(metadata_group) for metadata_group in dct
            ]
        )


@cache
def get_metadata() -> Metadata:
    """Load and build metadata for all models.

    Examples
    --------
    >>> from pyxel.util import get_metadata
    >>> metadata = get_metadata()
    >>> metadata
    Metadata<9 groups>
    >>> list(metadata)
    ['scene_generation', 'photon_collection', ...]

    >>> metadata["photon_collection"]
    MetadataGroup<name='photon_collection', 10 models>
    >>> list(metadata["photon_collection"])
    ['simple_collection', 'load_image', ...]

    >>> metadata["photon_collection"]["simple_collection"]
    MetadataModel(name='simple_collection')
    >>> metadata["photon_collection"]["simple_collection"].full_name
    'Simple collection'
    >>> metadata["photon_collection"]["simple_collection"].description
    """
    # Late import
    from yaml import safe_load

    import pyxel.models

    folder = Path(pyxel.models.__path__[0])

    lst: Sequence[Mapping] = [
        safe_load(filename.read_text()) for filename in folder.glob("**/metadata.yaml")
    ]

    return Metadata.from_metadata(lst)
