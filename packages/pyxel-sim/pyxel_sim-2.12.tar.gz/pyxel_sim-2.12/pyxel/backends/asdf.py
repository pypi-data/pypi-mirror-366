#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Module to read/write ASDF files."""

from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd
    import xarray as xr


def to_asdf(filename: str | Path, dct: Mapping[str, Any]) -> None:
    """Write data to a ASDF file."""
    try:
        import asdf
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Missing optional package 'asdf'.\n"
            "Please install it with 'pip install pyxel-sim[io]' "
            "or 'pip install pyxel-sim[all]'"
        ) from exc

    if dct["version"] != 1:
        raise NotImplementedError

    # Convert a 'DataFrame' into a `dict`
    df: pd.DataFrame = dct["data"]["charge"]["frame"]
    frame_dct: Mapping[str, Sequence[float]] = df.to_dict(orient="list")

    dct["data"]["charge"]["frame"] = frame_dct

    # Convert 'Dataset(s)' into a 'dict(s)'
    data: Mapping[str, xr.Dataset] = dct["data"]["data"]
    dct_data: Mapping[str, Mapping] = {
        key: value.to_dict() for key, value in data.items()
    }

    dct["data"]["data"] = dct_data

    with asdf.AsdfFile(dct) as af:
        af.write_to(filename)


@contextmanager
def from_asdf(filename: str | Path) -> Iterator[Mapping[str, Any]]:
    """Read data from a HDF5 file."""
    import pandas as pd

    try:
        import asdf
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Missing optional package 'asdf'.\n"
            "Please install it with 'pip install pyxel-sim[io]' "
            "or 'pip install pyxel-sim[all]'"
        ) from exc

    dct: dict[str, Any] = {}

    with asdf.open(filename) as af:
        # TODO: Use a JSON schema to validate 'dct'
        if "version" not in af:
            raise ValueError("Missing 'version' !")

        version: int = af["version"]
        if version != 1:
            raise NotImplementedError

        dct["version"] = version

        if "type" not in af:
            raise ValueError("Missing 'type' !")

        dct["type"] = af["type"]

        # Get properties
        dct["properties"] = af["properties"]
        dct["data"] = af["data"]

        # Convert a 'dict' to a 'DataFrame'
        frame_dct: Mapping[str, Sequence[float]] = dct["data"]["charge"]["frame"]
        df = pd.DataFrame(frame_dct)

        dct["data"]["charge"]["frame"] = df

        yield dct
