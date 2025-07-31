#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "apischema",
#     "typing-extensions",
# ]
# ///

"""Sub-package for metadata.

Usage
-----
$ uv run metadata.py
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TypeAlias

from typing_extensions import Self

DetectorType: TypeAlias = Literal["all", "CCD", "CMOS", "APD", "MKID"]


@dataclass
class MetadataModel:
    """Store metadata information for a single model."""

    name: str
    full_name: str
    detector: DetectorType | list[DetectorType] = "all"
    status: Literal["draft", "validated", None] = None
    authors: list[str] | None = None
    description: str | None = None
    notes: str | list[str] | None = None
    warnings: str | None = None
    config: str | list[str] | None = None
    notebooks: list[str] | None = None


@dataclass
class GroupInfo:
    """Store metadata for a Model Group."""

    name: Literal[
        "scene_generation",
        "photon_collection",
        "charge_generation",
        "charge_collection",
        "phasing",
        "charge_transfer",
        "charge_measurement",
        "readout_electronics",
        "data_processing",
    ]
    description: str


@dataclass
class MetadataGroup:
    """Store metadata information for all models from a Model Group."""

    group: GroupInfo
    models: list[MetadataModel]

    @classmethod
    def from_yaml(cls, filename: str | Path) -> Self:
        """Create a new MetadataGroup from a YAML file."""
        # TODO: Use JSON Schema to check if filename is valid
        # TODO: Use YAML to read the content
        raise NotImplementedError


def create_json_schema_file():
    """Create 'metadata.schema.json' file."""
    import json
    import logging

    from apischema.json_schema import (  # pip install apischema
        JsonSchemaVersion,
        deserialization_schema,
    )

    logging.info("Create JSON Schema")
    dct = deserialization_schema(
        MetadataGroup,
        version=JsonSchemaVersion.DRAFT_2020_12,
        all_refs=True,
    )

    logging.info("Save JSON Schema")
    with Path("metadata.schema.json").open("w") as fh:
        json.dump(obj=dct, fp=fh, indent=2, sort_keys=True)


if __name__ == "__main__":
    create_json_schema_file()
