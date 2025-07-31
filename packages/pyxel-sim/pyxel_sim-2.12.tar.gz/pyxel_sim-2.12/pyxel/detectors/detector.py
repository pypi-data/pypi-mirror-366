#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Detector class."""

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

from pyxel import __version__, backends
from pyxel.data_structure import (
    Charge,
    Image,
    Persistence,
    Photon,
    Pixel,
    Scene,
    Signal,
    SimplePersistence,
)
from pyxel.detectors import Environment, ReadoutProperties
from pyxel.util import get_size, memory_usage_details, resolve_with_working_directory

if TYPE_CHECKING:
    import xarray as xr
    from astropy.io import fits

__all__ = ["Detector"]


# TODO: Add methods to save/load a `Detector` instance to the filesystem. See #329
class Detector:
    """Base class for simulating a generic detector (e.g., CCD, CMOS).

    This class is responsible for handling the various stages of a detector's data acquisition process,
    including scene initialization, photon detection, charge distribution, pixel-level processing,
    signal generation, and final image creation.

    It is designed to be extended by more specific detector types.

    Notes
    -----
    - This class is not intended to be directly used.
    - This is the base class for the other detectors such as CCD, CMOS...

    Attributes
    ----------
    geometry : Any
        Geometrical attributes of the detector, defined in subclasses.
    characteristics : Any
        Characteristic attributes of the detector, defined in subclasses.
    environment : Environment
        Environmental attributes affecting the detector (e.g., temperature).
    scene : Scene
        The current scene being observed by the detector.
    photon : Photon
        Information about detected photons (in photons or photons/nm).
    charge : Charge
        Information about charge distribution (in electrons).
    pixel : Pixel
        Information about charge packets within a pixel (in electrons).
    signal : Signal
        Information about the detector signal (in Volts).
    image : Image
        Information about the detector image (in Analog-to-Digital Units, ADU).
    data : DataTree
        Structured data representing the results of the detector’s processing.
    intermediate : DataTree
        Data used for intermediate calculations during processing.
    output_dir : Optional[Path]
        Directory for output files related to the detector's operations.
    """

    def __init__(self, environment: Environment | None = None):
        self._environment: Environment = environment or Environment()

        self._scene: Scene | None = None
        self._photon: Photon | None = None
        self._charge: Charge | None = None
        self._pixel: Pixel | None = None
        self._signal: Signal | None = None
        self._image: Image | None = None
        self._data: xr.DataTree | None = None

        self._intermediate: xr.DataTree | None = None

        # This will be the memory of the detector where trapped charges will be saved
        self._memory: dict = {}
        self._persistence: Persistence | SimplePersistence | None = None

        self._output_dir: Path | None = None  # TODO: See #330

        self._readout_properties: "ReadoutProperties" | None = None

        self._numbytes = get_size(self)

        # TODO: This variable is used to store the name of the current model executed
        #       A better interface to access this information must be provided
        self.current_running_model_name: str = ""

        self.header: "fits.Header" | None = None

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, Detector)
            and self._scene == other._scene
            and self._photon == other._photon
            and self._charge == other._charge
            and self._pixel == other._pixel
            and self._signal == other._signal
            and self._image == other._image
            and (
                (self._data is other._data is None)
                or (
                    self._data is not None
                    and other._data is not None
                    and self._data.equals(other._data)
                )
            )
        )

    @property
    def geometry(self):
        """Geometrical attributes of the detector (e.g. num of rows, columns...).

        Raises
        ------
        NotImplementedError
            If called directly on the base class.
        """
        raise NotImplementedError

    @property
    def characteristics(self):
        """Characteristics attributes of the detector (e.g. quantum efficiency...).

        Raises
        ------
        NotImplementedError
            If called directly on the base class.
        """
        raise NotImplementedError

    @property
    def environment(self) -> Environment:
        """Environmental attributes affecting the detector (e.g. temperature...)."""
        return self._environment

    @property
    def photon(self) -> Photon:
        """Get the information of detected photon (in ph or ph/nm)."""
        if not self._photon:
            raise RuntimeError("Photon array is not initialized ! ")
        return self._photon

    @photon.setter
    def photon(self, obj: Photon) -> None:
        """Set the photon information for the detector."""
        self.photon._array = obj._array

    @property
    def scene(self) -> Scene:
        """Get the current scene being observed by the detector.

        Returns
        -------
        Scene
            The scene object. Unit: ph / (cm2 nm s)
        """
        if not self._scene:
            raise RuntimeError("Scene object is not initialized ! ")
        return self._scene

    @scene.setter
    def scene(self, obj: Scene) -> None:
        """Set a new scene being observed by the detector."""
        if not isinstance(obj, Scene):
            raise TypeError(f"Expected a 'Scene' object. Got: {obj!r}")

        self._scene = obj

    # TODO: Why no setter for charge, pixel, signal and image?
    @property
    def charge(self) -> Charge:
        """Get the charge information of charge distribution (in electron)."""

        if not self._charge:
            raise RuntimeError("'charge' not initialized.")

        return self._charge

    @property
    def pixel(self) -> Pixel:
        """Get the pixel information of charge packets within pixel (in electron)."""

        if not self._pixel:
            raise RuntimeError("'pixel' not initialized.")

        return self._pixel

    @pixel.setter
    def pixel(self, obj: Pixel) -> None:
        """Set the pixel information for the detector."""
        self.pixel.array = obj.array

    @property
    def signal(self) -> Signal:
        """Get the signal information from the detector (in Volt)."""
        if not self._signal:
            raise RuntimeError("'signal' not initialized.")

        return self._signal

    @signal.setter
    def signal(self, obj: Pixel) -> None:
        """Set the signal information for the detector."""
        self.signal.array = obj.array

    @property
    def image(self) -> Image:
        """Get the image information from the detector (in adu)."""
        if not self._image:
            raise RuntimeError("'image' not initialized.")

        return self._image

    @image.setter
    def image(self, obj: Pixel) -> None:
        """Set the image information for the detector."""
        self.image.array = obj.array

    @property
    def data(self) -> "xr.DataTree":
        """Get the structured ata from the detector's processing."""
        if self._data is None:
            raise RuntimeError("'data' not initialized.")

        return self._data

    @property
    def intermediate(self) -> "xr.DataTree":
        """Get the intermediate data used during processing."""
        if self._intermediate is None:
            raise RuntimeError("'intermediate' not initialized.")

        return self._intermediate

    def to_xarray(self) -> "xr.Dataset":
        """Create a new ``Dataset`` from all data containers.

        Examples
        --------
        >>> detector.to_xarray()
        <xarray.Dataset>
        Dimensions:  (y: 100, x: 100)
        Coordinates:
          * y        (y) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
          * x        (x) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
        Data variables:
            photon   (y, x) float64 0.0 0.0 0.0 0.0 0.0 0.0 ... 0.0 0.0 0.0 0.0 0.0 0.0
            pixel    (y, x) float64 0.0 0.0 0.0 0.0 0.0 0.0 ... 0.0 0.0 0.0 0.0 0.0 0.0
            signal   (y, x) float64 0.0 0.0 0.0 0.0 0.0 0.0 ... 0.0 0.0 0.0 0.0 0.0 0.0
            image    (y, x) uint64 0 0 0 0 0 0 0 0 0 0 0 0 0 ... 0 0 0 0 0 0 0 0 0 0 0 0
        Attributes:
            detector:       CCD
            pyxel version:  1.5
        """
        import xarray as xr

        # ds["scene"] = self.scene.to_xarray()

        ds = xr.Dataset()
        for name in ("photon", "charge", "pixel", "signal", "image"):
            container: Photon | Charge | Pixel | Signal | Image = getattr(self, name)
            data_array: xr.DataArray = container.to_xarray()

            # TODO: Special case, this will be fixed in issue #692
            if name == "charge" and bool((data_array == 0).all()):
                # No charges
                continue

            if data_array.ndim != 0:
                ds[name] = data_array
        #
        # array:xr.DataArray = self.photon.to_xarray()
        # if array.ndim != 0:
        #     ds['photon'] = array
        #
        # ds["photon"] = self.photon.to_xarray()
        # ds["charge"] = self.charge.to_xarray()
        # ds["pixel"] = self.pixel.to_xarray()
        # ds["signal"] = self.signal.to_xarray()
        # ds["image"] = self.image.to_xarray()

        ds.attrs.update({"detector": type(self).__name__, "pyxel version": __version__})

        return ds

    def _initialize(self) -> None:
        """Initialize data buckets."""

        import xarray as xr

        #
        # if self.characteristics._charge_to_volt_conversion is None or isinstance(
        #     self.characteristics._charge_to_volt_conversion, float
        # ):
        #     value_1d: float | None = self.characteristics._charge_to_volt_conversion
        #     self.characteristics._channels_gain = value_1d
        #
        # elif isinstance(self.characteristics._charge_to_volt_conversion, dict):
        #     # TODO: sanity check
        #     # TODO: Extract channels from 'self.geometry.channels'
        #     value_2d: np.ndarray = np.zeros(shape=self.geometry.shape, dtype=float)
        #     for (
        #         channel,
        #         gain,
        #     ) in self.characteristics._charge_to_volt_conversion.items():
        #         slice_y, slice_x = self.geometry.get_channel_coord(channel)
        #         value_2d[slice_y, slice_x] = gain
        #     self.characteristics._channels_gain = value_2d
        #
        # else:
        #     raise ValueError

        self._scene = Scene()
        self._photon = Photon(geo=self.geometry)
        self._charge = Charge(geo=self.geometry)

        self._pixel = Pixel(geo=self.geometry)

        self._signal = Signal(geo=self.geometry)
        self._image = Image(geo=self.geometry)

        self._data = xr.DataTree()

    # TODO: refactor to split up to empty and reset.
    def empty(self, reset: bool = True) -> None:
        """Empty the data in the detector."""
        self.scene = Scene()

        self.photon.empty()
        self.charge.empty()

        if reset:
            self.pixel.empty()

        self.signal.empty()
        self.image.empty()

    def set_readout(
        self,
        times: Sequence[float] | np.ndarray,
        start_time: float = 0.0,
        non_destructive: bool = False,
    ) -> None:
        """Set readout sampling properties.

        Parameters
        ----------
        times : Sequence[Number]
            A sequence of numeric values representing the sampling times for the readout simulation.
        start_time : float, optional. Default: 0.0
            A float representing the starting time of the readout simulation.
            The readout time(s) should be greater that this ``start_time``.
        non_destructive : bool, optional. Default: False
            A boolean flag indicating whether the readout simulation is non-destructive.
            If set to ``True``, the readout process will not modify the underlying data.

        Examples
        --------
        >>> detector.set_readout(times=[1, 2, 4, 7, 10], start_time=0.0)
        """
        self._readout_properties = ReadoutProperties(
            times=times,
            start_time=start_time,
            non_destructive=non_destructive,
        )

    @property
    def readout_properties(self) -> ReadoutProperties:
        """Return current readout sampling properties."""
        if self._readout_properties is None:
            raise ValueError("No readout defined.")

        return self._readout_properties

    @property
    def time(self) -> float:
        """Get the current time within the readout simulation.

        Returns
        -------
        float
            The current time during the readout process.
        """
        return self.readout_properties.time

    @time.setter
    def time(self, value: float) -> None:
        """Set the current time within the readout simulation.

        Parameters
        ----------
        value : float
            The new current time to set in the simulation.
        """
        self.readout_properties.time = value

    @property
    def start_time(self) -> float:
        """TBW."""
        return self.readout_properties.start_time

    @start_time.setter
    def start_time(self, value: float) -> None:
        """Get the start time for the readout simulation."""
        self.readout_properties.start_time = value

    @property
    def absolute_time(self) -> float:
        """Get the absolute time relative to the simulation start."""
        return self.readout_properties.absolute_time

    @property
    def time_step(self) -> float:
        """Get the step size used for advancing in the simulation."""
        return self.readout_properties.time_step

    @time_step.setter
    def time_step(self, value: float) -> None:
        """Set the time step size for advancing the simulation."""
        self.readout_properties.time_step = value

    @property
    def times_linear(self) -> bool:
        """Check if the time intervals between readout samples are uniform."""
        return self.readout_properties.times_linear

    @property
    def num_steps(self) -> int:
        """Return the total number of readout steps."""
        return self.readout_properties.num_steps

    @property
    def pipeline_count(self) -> int:
        """Get the current readout pipeline count."""
        return self.readout_properties.pipeline_count

    @pipeline_count.setter
    def pipeline_count(self, value: int) -> None:
        """Set the pipeline count for the readout process."""
        self.readout_properties.pipeline_count = value

    @property
    def is_first_readout(self) -> bool:
        """Check if this is the first readout time."""
        return self.readout_properties.is_first_readout

    @property
    def is_last_readout(self) -> bool:
        """Check if this is the last readout time."""
        return bool(self.pipeline_count == (self.num_steps - 1))

    @property
    def read_out(self) -> bool:
        """Get the status of the readout process."""
        return self.readout_properties.read_out

    @read_out.setter
    def read_out(self, value: bool) -> None:
        """Set the readout status."""
        self.readout_properties.read_out = value

    @property
    def is_dynamic(self) -> bool:
        """Return if detector is dynamic (time dependent) or not.

        By default it is not dynamic.
        """
        return self._readout_properties is not None

    @property
    def non_destructive_readout(self) -> bool:
        """Return if detector readout mode is destructive or integrating.

        By default it is destructive (non-integrating).
        """
        return self.readout_properties.non_destructive

    def has_persistence(self) -> bool:
        """TBW."""
        return self._persistence is not None

    @property
    def persistence(self) -> Persistence | SimplePersistence:
        """TBW."""
        if self._persistence is None:
            raise RuntimeError("'persistence' not initialized.")

        return self._persistence

    @persistence.setter
    def persistence(self, value: Persistence | SimplePersistence) -> None:
        """TBW."""
        if not isinstance(value, Persistence | SimplePersistence):
            raise TypeError(
                "Expecting Persistence or SimplePersistence type to set detector"
                " persistence."
            )
        self._persistence = value

    @property
    def numbytes(self) -> int:
        """Recursively calculates object size in bytes using Pympler library.

        Returns
        -------
        int
            Size of the object in bytes.
        """
        self._numbytes = get_size(self)
        return self._numbytes

    def memory_usage(
        self, print_result: bool = True, human_readable: bool = True
    ) -> dict:
        """Calculate and return the memory usage of each component of the detector.

        This method computes the memory usafe of the internal data structures
        (e.g. scene, photon, charge, pixel, etc.) to provide insights into the
        memory consumption of this Detector object.

        Parameters
        ----------
        print_result : bool, default: True
            Boolean flag indicating whether to print the
            memory usage details
        human_readable : bool, default: True
            Boolean flag indicating whether to print
            memory usage details in human-readable format

        Returns
        -------
        dict
            Dictionary of attribute memory usage
        """
        attributes = [
            "_scene",
            "_photon",
            "_charge",
            "_pixel",
            "_signal",
            "_image",
            "material",
            "environment",
            "_geometry",
            "_characteristics",
        ]

        return memory_usage_details(
            self, attributes, print_result=print_result, human_readable=human_readable
        )

    @classmethod
    def load(cls, filename: str | Path) -> "Detector":
        """Load a detector object from a filename.

        This is a general-purpose load method that can handle different file formats (e.g., HDF5, ASDF)
        based on the file extension.

        It restores the internal state of the detector from the file.

        Parameters
        ----------
        filename : str or Path

        Returns
        -------
        Detector
            A new ``Detector`` object.

        Raises
        ------
        FileNotFoundError
            If ``filename`` is not found.
        ValueError
            If the extension of filename is not recognized.

        Examples
        --------
        >>> detector = Detector()
        >>> detector.load("detector.h5")  # Loads from HDF5 format
        """
        full_filename = Path(resolve_with_working_directory(filename)).resolve()
        if not full_filename.exists():
            raise FileNotFoundError(f"Filename '{filename}' does not exist !")

        extension: str = full_filename.suffix

        if extension in (".h5", ".hdf5", ".hdf"):
            return cls.from_hdf5(filename)
        elif extension == ".asdf":
            return cls.from_asdf(filename)
        else:
            raise ValueError(f"Unknown extension {extension!r}.")

    def save(self, filename: str | Path) -> None:
        """Save a detector object into a filename.

        This is a general-purpose save method that can use different formats (e.g., HDF5, ASDF)
        to serialize the detector's current state to disk.

        The format is inferred from the file extension.

        Parameters
        ----------
        filename : str or Path

        Raises
        ------
        ValueError
            If the extension of filename is not recognized.

        Examples
        --------
        >>> detector = ...
        >>> detector.save("detector.h5")  # Save in HDF5 format
        >>> detector.save("detector.asdf")  # Save in ASDF format
        """
        full_filename = Path(resolve_with_working_directory(filename)).resolve()
        extension: str = full_filename.suffix

        if extension in (".h5", ".hdf5", ".hdf"):
            return self.to_hdf5(filename)
        elif extension == ".asdf":
            return self.to_asdf(filename)
        else:
            raise ValueError(f"Unknown extension {extension!r}.")

    # TODO: Move this to another place. See #241
    def to_hdf5(self, filename: str | Path) -> None:
        """Write the detector content to a :term:`HDF5` file.

        The HDF5 file has the following structure:

        .. code-block:: bash

            filename.h5  (4 objects, 3 attributes)
            │   ├── pyxel-version  1.0.0+161.g659eec86
            │   ├── type  CCD
            │   └── version  1
            ├── geometry  (5 objects)
            │   ├── col  (), int64
            │   ├── pixel_horz_size  (), float64
            │   ├── pixel_vert_size  (), float64
            │   ├── row  (), int64
            │   └── total_thickness  (), float64
            ├── environment  (1 object)
            │   └── temperature  (), float64
            ├── characteristics  (4 objects)
            │   ├── charge_to_volt_conversion  (), float64
            │   ├── full_well_capacity  (), int64
            │   ├── pre_amplification  (), float64
            │   └── quantum_efficiency  (), float64
            └── data  (5 objects)
                ├── charge  (2 objects, 2 attributes)
                │   ├── name  Charge
                │   ├── unit  electron
                │   ├── array  (100, 120), float64
                │   └── frame  (13 objects, 1 attribute)
                │       ├── type  DataFrame
                │       ├── charge  (0,), float64
                │       ├── energy  (0,), float64
                │       ├── init_energy  (0,), float64
                │       ├── init_pos_hor  (0,), float64
                │       ├── init_pos_ver  (0,), float64
                │       ├── init_pos_z  (0,), float64
                │       ├── number  (0,), float64
                │       ├── position_hor  (0,), float64
                │       ├── position_ver  (0,), float64
                │       ├── position_z  (0,), float64
                │       ├── velocity_hor  (0,), float64
                │       ├── velocity_ver  (0,), float64
                │       └── velocity_z  (0,), float64
                ├── image  (100, 120), uint64
                │   └── name  Image
                ├── photon  (100, 120), float64
                ├── pixel  (100, 120), float64
                └── signal  (100, 120), float64

        Parameters
        ----------
        filename : str or Path

        Notes
        -----
        You can find more information in the 'how-to' guide section.

        Examples
        --------
        >>> from pyxel.detectors import CCD
        >>> detector = CCD(...)

        >>> detector.to_hdf5("ccd.h5")
        """
        dct: Mapping = self.to_dict()
        backends.to_hdf5(filename=filename, dct=dct)

    @classmethod
    def from_hdf5(cls, filename: str | Path) -> "Detector":
        """Load a detector object from a :term:`HDF5` file.

        Parameters
        ----------
        filename : str or Path

        Examples
        --------
        >>> detector = Detector.from_hdf5("ccd.h5")
        >>> detector
        CCD(...)
        """
        dct: Mapping[str, Any]
        with backends.from_hdf5(filename) as dct:
            obj: Detector = cls.from_dict(dct)
            return obj

    def to_asdf(self, filename: str | Path) -> None:
        """Write the detector content to a :term:`ASDF` file.

        The ASDF file has the following structure:

        .. code-block:: bash

             root (AsdfObject)
             ├─version (int): 1
             ├─type (str): CCD
             ├─properties (dict)
             │ ├─geometry (dict)
             │ │ ├─row (int): 4
             │ │ ├─col (int): 5
             │ │ ├─total_thickness (NoneType): None
             │ │ ├─pixel_vert_size (NoneType): None
             │ │ └─pixel_horz_size (NoneType): None
             │ ├─environment (dict)
             │ │ └─temperature (NoneType): None
             │ └─characteristics (dict)
             │   ├─quantum_efficiency (NoneType): None
             │   ├─charge_to_volt_conversion (NoneType): None
             │   └─4 not shown
             └─data (dict)
               ├─photon (ndarray): shape=(4, 5), dtype=float64
               ├─scene (NoneType): None
               ├─pixel (ndarray): shape=(4, 5), dtype=float64
               ├─signal (ndarray): shape=(4, 5), dtype=float64
               ├─image (ndarray): shape=(4, 5), dtype=uint64
               └─charge (dict) ...

        Parameters
        ----------
        filename : str or Path

        Notes
        -----
        You can find more information in the 'how-to' guide section.

        Examples
        --------
        >>> from pyxel.detectors import CCD
        >>> detector = CCD(...)

        >>> detector.to_asdf("ccd.asdf")

        >>> import asdf
        >>> af = asdf.open("ccd_asdf")
        >>> af["type"]
        'CCD'
        >>> af.info()
        """
        dct: Mapping = self.to_dict()
        backends.to_asdf(filename=filename, dct=dct)

    @classmethod
    def from_asdf(cls, filename: str | Path) -> "Detector":
        """Load a detector object from a :term:`ASDF` file.

        Parameters
        ----------
        filename : str or Path

        Examples
        --------
        >>> detector = Detector.from_asdf("ccd.asdf")
        >>> detector
        CCD(...)
        """
        with backends.from_asdf(filename) as dct:
            detector: Detector = cls.from_dict(dct)

        return detector

    def to_dict(self) -> Mapping:
        """Convert a `Detector` to a `dict`."""
        raise NotImplementedError

    # TODO: Replace `-> 'Detector'` by `Union[CCD, CMOS, MKID]`
    @classmethod
    def from_dict(cls, dct: Mapping) -> "Detector":
        """Create a new instance of a `Detector` from a `dict`."""
        # TODO: This is a simplistic implementation. Improve this.
        if dct["type"] == "CCD":
            from pyxel.detectors import CCD  # Imported here to avoid circular import

            return CCD.from_dict(dct)

        elif dct["type"] == "CMOS":
            from pyxel.detectors import CMOS

            return CMOS.from_dict(dct)

        elif dct["type"] == "MKID":
            from pyxel.detectors import MKID

            return MKID.from_dict(dct)

        elif dct["type"] == "APD":
            from pyxel.detectors import APD

            return APD.from_dict(dct)

        else:
            raise NotImplementedError(f"Unknown type: {dct['type']!r}")
