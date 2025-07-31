#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.


"""TBW."""

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

from typing_extensions import deprecated

if TYPE_CHECKING:
    import pandas as pd

from pyxel.outputs import Outputs, ValidFormat, ValidName

if TYPE_CHECKING:
    import xarray as xr
    from dask.delayed import Delayed

    class SaveToFile(Protocol):
        """TBW."""

        def __call__(self, data: Any, name: str, with_auto_suffix: bool = True) -> Path:
            """TBW."""
            ...


class CalibrationOutputs(Outputs):
    """Collection of methods to save the data buckets from a Detector for a Calibration pipeline.

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
        save_calibration_data: Sequence[Mapping[str, Sequence[str]]] | None = None,
    ):
        super().__init__(
            output_folder=output_folder,
            custom_dir_name=custom_dir_name,
            save_data_to_file=save_data_to_file,
        )

        # Parameter(s) specific for 'Calibration'
        self._save_calibration_data_deprecated: (
            Sequence[Mapping[str, Sequence[str]]] | None
        ) = save_calibration_data

    @deprecated("This method will be removed")
    def _save_processors_deprecated(
        self, processors: "pd.DataFrame"
    ) -> Sequence["Delayed"]:
        """TBW."""
        # Late import to speedup start-up time
        from dask.delayed import Delayed, delayed

        lst: list[Delayed] = []

        if self.save_data_to_file:
            for _, series in processors.iterrows():
                id_island: int = series["island"]
                id_processor: int = series["id_processor"]
                processor: Delayed = series["processor"]

                # TODO: Create folders ?
                prefix = f"island{id_island:02d}_processor{id_processor:02d}"

                output_filenames: Delayed = delayed(self.save_to_file)(
                    processor=processor, prefix=prefix, with_auto_suffix=False
                )
                lst.append(output_filenames)

        return lst

    @deprecated("This method will be removed")
    def _save_calibration_outputs_deprecated(
        self, dataset: "xr.Dataset", logs: "pd.DataFrame"
    ) -> None:
        """Save the calibration outputs such as dataset and logs.

        Parameters
        ----------
        dataset: Dataset
        logs: DataFrame
        """
        save_methods: dict[str, SaveToFile] = {"nc": self.save_to_netcdf}

        if self._save_calibration_data_deprecated is not None:
            dct: Mapping[str, Sequence[str]]
            for dct in self._save_calibration_data_deprecated:
                first_item, *_ = dct.items()
                obj, format_list = first_item

                if obj == "logs":
                    for formal_file in format_list:
                        if formal_file == "csv":
                            filename = self.current_output_folder.joinpath("logs.csv")
                            logs.to_csv(filename)
                        elif formal_file == "xlsx":
                            filename = self.current_output_folder.joinpath("logs.xlsx")
                            logs.to_excel(filename)
                        else:
                            raise NotImplementedError(
                                f"Saving to format {formal_file} not implemented"
                            )

                elif obj == "dataset":
                    if format_list is not None:
                        for out_format in format_list:
                            if out_format not in save_methods:
                                raise ValueError(
                                    "Format " + out_format + " not a valid save method!"
                                )

                            func = save_methods[out_format]
                            func(data=dataset, name=obj)

                else:
                    raise NotImplementedError(f"Object {obj} unknown.")
