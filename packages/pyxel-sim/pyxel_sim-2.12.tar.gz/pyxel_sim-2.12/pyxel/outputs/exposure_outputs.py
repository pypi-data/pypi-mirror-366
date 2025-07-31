#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


"""Single outputs."""

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, Union

from typing_extensions import deprecated

from pyxel.outputs import Outputs, ValidFormat, ValidName

if TYPE_CHECKING:
    import xarray as xr

    class SaveToFile(Protocol):
        """TBW."""

        def __call__(self, data: Any, name: str, with_auto_suffix: bool = True) -> Path:
            """TBW."""
            ...


class ExposureOutputs(Outputs):
    """Collection of methods to save the data buckets from a Detector for an Exposure pipeline.

    Parameters
    ----------
    output_folder : str or Path
        Folder where sub-folder(s) that will be created to save data buckets.
    custom_dir_name : str, optional
        Prefix of the sub-folder name that will be created in the 'output_folder' folder.
        The default prefix is `run_`.
    save_data_to_file : Dict
        Dictionary where key is a 'data bucket' name (e.g. 'detector.photon.array') and value
        is the data format (e.g. 'fits').

        Example:
        {'detector.photon.array': 'fits', 'detector.charge.array': 'hdf', 'detector.image.array':'png'}
    """

    def __init__(
        self,
        output_folder: str | Path,
        custom_dir_name: str = "",
        save_data_to_file: (
            Sequence[Mapping[ValidName, Sequence[ValidFormat]]] | None
        ) = None,
        save_exposure_data: Sequence[Mapping[str, Sequence[str]]] | None = None,
    ):
        super().__init__(
            output_folder=output_folder,
            custom_dir_name=custom_dir_name,
            save_data_to_file=save_data_to_file,
        )

        # TODO: This parameter should be removed
        self.save_exposure_data: Sequence[Mapping[str, Sequence[str]]] | None = (
            save_exposure_data
        )

    @deprecated("This method will be removed")
    def save_exposure_outputs(
        self, dataset: Union["xr.Dataset", "xr.DataTree"]
    ) -> None:
        """Save the observation outputs such as the dataset.

        Parameters
        ----------
        dataset: Dataset
        """

        save_methods: dict[str, SaveToFile] = {"nc": self.save_to_netcdf}

        if self.save_exposure_data is None:
            return

        dct: Mapping[str, Sequence[str]]
        for dct in self.save_exposure_data:
            first_item, *_ = dct.items()
            obj, format_list = first_item

            if obj != "dataset":
                raise NotImplementedError(f"Object {obj} unknown.")

            out_format: str
            for out_format in format_list:
                if out_format not in save_methods:
                    raise ValueError(f"Format {out_format} not a valid save method!")

                func = save_methods[out_format]
                func(data=dataset, name=obj)

    def dump(self) -> Mapping[str, Any]:
        return {
            "output_folder": self._output_folder,
            "custom_dir_name": self._custom_dir_name,
            "save_data_to_file": self.save_data_to_file,
        }
