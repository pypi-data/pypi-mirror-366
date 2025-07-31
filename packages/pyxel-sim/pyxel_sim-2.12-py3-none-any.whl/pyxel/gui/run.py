#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Sub-package for routines to be used for a GUI."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import xarray as xr
    from panel.widgets import Tqdm

    from pyxel import Configuration
    from pyxel.outputs import ExposureOutputs


def run_mode_gui(
    config: "Configuration",
    *,
    tqdm_widget: "Tqdm",
    override_dct: Mapping[str, Any] | None = None,
) -> "xr.Dataset":
    # Late import
    from pyxel.exposure import Exposure, run_pipeline
    from pyxel.observation import Observation
    from pyxel.pipelines import Processor
    from pyxel.run import apply_overrides

    # Initialize the Processor object with the detector and pipeline.
    if isinstance(config.running_mode, Observation):
        processor = Processor(
            detector=config.detector,
            pipeline=config.pipeline,
            observation_mode=config.running_mode,  # TODO: See #836
        )
    else:
        processor = Processor(detector=config.detector, pipeline=config.pipeline)

    # Apply any overrides provided in the 'override_dct' to adjust processor settings.
    if override_dct is not None:
        apply_overrides(
            overrides=override_dct,
            processor=processor,
            mode=config.running_mode,
        )

    mode = config.running_mode
    match mode:
        case Exposure():
            # Create an output folder (if needed)
            outputs: ExposureOutputs | None = mode.outputs
            if outputs:
                outputs.create_output_folder()

            data_tree = run_pipeline(
                processor=processor,
                readout=mode.readout,
                outputs=outputs,
                pipeline_seed=mode.pipeline_seed,
                debug=False,
                with_inherited_coords=True,
                progress_bar=tqdm_widget([]),
            )
            data_tree.attrs["running mode"] = "Exposure"

        case _:
            raise NotImplementedError

    ds = data_tree["/bucket"].to_dataset()

    return ds
