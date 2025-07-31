#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel Scene class to track multi-wavelength photon."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING

from typing_extensions import Self

if TYPE_CHECKING:
    import xarray as xr
    from astropy.units import Quantity
    from scopesim import Source


@dataclass
class SceneCoordinates:
    """Represent the coordinates from one scene.

    Parameters
    ----------
    right_ascension : Quantity
        The right ascension of the scene in degree.
    declination : Quantity
        The declination of the scene in degree.
    fov : Quantity
        The field of view of the scene in degree.
    """

    right_ascension: "Quantity"
    declination: "Quantity"
    fov: "Quantity"

    @classmethod
    def from_dataset(cls, ds: "xr.Dataset") -> Self:
        """Create a `SceneCoordinates` object from an xarray Dataset.

        Parameters
        ----------
        ds : xr.Dataset
            The dataset containing the scene coordinates in its attributes.

        Returns
        -------
        SceneCoordinates
            A new `SceneCoordinates` object.

        Examples
        --------
        >>> ds = xr.Dataset(...)
        >>> ds
        <xarray.Dataset>
        Dimensions:     (ref: 345, wavelength: 343)
        Coordinates:
          * ref         (ref) int64 0 1 2 3 4 5 6 7 ... 337 338 339 340 341 342 343 344
          * wavelength  (wavelength) float64 336.0 338.0 340.0 ... 1.018e+03 1.02e+03
        Data variables:
            x           (ref) float64 1.334e+03 1.434e+03 ... -1.271e+03 -1.381e+03
            y           (ref) float64 -1.009e+03 -956.1 -797.1 ... 1.195e+03 1.309e+03
            weight      (ref) float64 11.49 14.13 15.22 14.56 ... 15.21 11.51 8.727
            flux        (ref, wavelength) float64 0.003769 0.004137 ... 0.1813 0.1896
        Attributes:
            right_ascension:   56.75 deg
            declination:       24.1167 deg
            fov_radius:        0.5 deg

        >>> SceneCoordinates.from_dataset(ds)
        SceneCoordinates(right_ascension=<Quantity 56.75 deg>, declination=<Quantity 24.1167 deg>, fov=<Quantity 0.5 deg>)
        """
        # Late import to speedup start-up time
        from astropy.units import Quantity

        right_ascension_key = "right_ascension"
        declination_key = "declination"
        fov_radius_key = "fov_radius"

        if right_ascension_key not in ds.attrs:
            raise KeyError(f"Missing key {right_ascension_key!r} in the attributes.")

        if declination_key not in ds.attrs:
            raise KeyError(f"Missing key {declination_key!r} in the attributes.")

        if fov_radius_key not in ds.attrs:
            raise KeyError(f"Missing key {fov_radius_key!r} in the attributes.")

        # Extract parameters from 'scene'
        right_ascension = Quantity(ds.attrs[right_ascension_key], unit="deg")
        declination = Quantity(ds.attrs[declination_key], unit="deg")
        fov = Quantity(ds.attrs[fov_radius_key], unit="deg")

        return cls(right_ascension=right_ascension, declination=declination, fov=fov)


class Scene:
    """Scene class defining and storing information of all multi-wavelength photons (unit: ph / (cm2 nm s)).

    Multi-wavelength photon information are store in form of xarray Datasets
    within a hierarchical structure.

    Examples
    --------
    Create an empty Scene

    >>> from pyxel.detectors import CCD, CCDGeometry, Characteristics, Environment
    >>> detector = CCD(
    ...     geometry=CCDGeometry(row=5, col=5),
    ...     characteristics=Characteristics(),
    ...     environment=Environment(),
    ... )
    >>> detector.scene
    Scene<no source>

    Add a source

    >>> import xarray as xr
    >>> source = xr.Dataset(...)
    >>> source
    <xarray.Dataset>
    Dimensions:     (ref: 345, wavelength: 343)
    Coordinates:
      * ref         (ref) int64 0 1 2 3 4 5 6 7 ... 337 338 339 340 341 342 343 344
      * wavelength  (wavelength) float64 336.0 338.0 340.0 ... 1.018e+03 1.02e+03
    Data variables:
        x           (ref) float64 2.057e+05 2.058e+05 ... 2.031e+05 2.03e+05
        y           (ref) float64 8.575e+04 8.58e+04 ... 8.795e+04 8.807e+04
        weight      (ref) float64 11.49 14.13 15.22 14.56 ... 15.21 11.51 8.727
        flux        (ref, wavelength) float64 0.03769 0.04137 ... 1.813 1.896
    Attributes:
        right_ascension:  56.75 deg
        declination:      24.1167 deg
        fov_radius:       0.5 deg

    >>> detector.scene.add_source(source)
    >>> detector.scene
    Scene<1 source(s)>

    Get the pointing coordinates of the first source
    >>> detector.scene.get_pointing_coordinates()
    or
    >>> detector.scene.get_pointing_coordinates(source_idx=0)
    SceneCoordinates(right_ascension=<Quantity 56.75 deg>, declination=<Quantity 24.1167 deg>, fov=<Quantity 0.5 deg>)
    """

    def __init__(self):
        # Late import to speedup start-up time
        import xarray as xr

        self._source: xr.DataTree = xr.DataTree(name="scene")

    def __repr__(self) -> str:
        cls_name: str = self.__class__.__name__

        if "list" not in self._source:
            return f"{cls_name}<no source>"

        # Get number of nodes at 'list' level
        num_sources: int = len(self._source["list"])
        return f"{cls_name}<{num_sources} source(s)>"

    def __eq__(self, other) -> bool:
        return type(self) is type(other) and self.data.identical(other.data)

    def add_source(self, source: "xr.Dataset") -> None:
        """Add a source to the current scene.

        Parameters
        ----------
        source : Dataset

        Raises
        ------
        TypeError
            If 'source' is not a ``Dataset`` object.
        ValueError
            If 'source' has not the expected format.

        Examples
        --------
        >>> from pyxel.detectors import CCD
        >>> detector = CCD(...)

        >>> source
        <xarray.Dataset>
        Dimensions:     (ref: 345, wavelength: 343)
        Coordinates:
          * ref         (ref) int64 0 1 2 3 4 5 6 7 ... 337 338 339 340 341 342 343 344
          * wavelength  (wavelength) float64 336.0 338.0 340.0 ... 1.018e+03 1.02e+03
        Data variables:
            x           (ref) float64 1.334e+03 1.434e+03 ... -1.271e+03 -1.381e+03
            y           (ref) float64 -1.009e+03 -956.1 -797.1 ... 1.195e+03 1.309e+03
            weight      (ref) float64 11.49 14.13 15.22 14.56 ... 15.21 11.51 8.727
            flux        (ref, wavelength) float64 0.003769 0.004137 ... 0.1813 0.1896
        Attributes:
            right_ascension:  56.75 deg
            declination:      24.1167 deg
            fov_radius:       0.5 deg

        >>> detector.scene.add_source(source)
        >>> detector.scene.data
        DataTree('scene', parent=None)
        └── DataTree('list')
            └── DataTree('0')
                    Dimensions:     (ref: 4, wavelength: 4)
                    Coordinates:
                      * ref         (ref) int64 0 1 2 3
                      * wavelength  (wavelength) float64 336.0 338.0 1.018e+03 1.02e+03
                    Data variables:
                        x           (ref) float64 64.97 11.44 -55.75 -20.66
                        y           (ref) float64 89.62 -129.3 -48.16 87.87
                        weight      (ref) float64 14.73 12.34 14.63 14.27
                        flux        (ref, wavelength) float64 0.003769 0.004137 ... 0.1813 0.1896
                    Attributes:
                        right_ascension:  56.75 deg
                        declination:      24.1167 deg
                        fov_radius:       0.5 deg
        """
        # Late import to speedup start-up time
        import xarray as xr

        if not isinstance(source, xr.Dataset):
            raise TypeError("Expecting a Dataset object for source")

        if set(source.coords) != {"ref", "wavelength"}:
            raise ValueError(
                "Wrong format for source. Expecting coordinates 'ref' and 'wavelength'."
            )

        if set(source.data_vars) != {
            "x",
            "y",
            "weight",
            "flux",
        }:
            raise ValueError(
                "Wrong format for source. Expecting a Dataset with variables 'x', 'y',"
                " 'weight' and 'flux'."
            )

        if "list" not in self.data:
            key: int = 0
        else:
            key = len(self.data["/list"])

        self.data[f"/list/{key}"] = xr.DataTree(source)

    def get_pointing_coordinates(self, source_idx: int = 0) -> SceneCoordinates:
        """Get the `SceneCoordinates` from a source in the scene."""
        if source_idx != 0:
            raise NotImplementedError

        sub_scene: "xr.Dataset" = self.data[f"/list/{source_idx}"].to_dataset()
        return SceneCoordinates.from_dataset(sub_scene)

    @property
    def data(self) -> "xr.DataTree":
        """Get a multi-wavelength object."""
        return self._source

    def empty(self):
        """Create a new empty source."""
        # Late import to speedup start-up time
        import xarray as xr

        self._source = xr.DataTree(name="scene")

    def from_scopesim(self, source: "Source") -> None:
        """Convert a ScopeSim `Source` object into a `Scene` object.

        Parameters
        ----------
        source : scopesim.Source
            Object to convert to a `Scene` object.

        Raises
        ------
        RuntimeError
            If package 'scopesim' is not installed.
        TypeError
            If input parameter 'source' is not a ScopeSim `Source` object.

        Notes
        -----
        More information about ScopeSim `Source` objects at
        this link: https://scopesim.readthedocs.io/en/latest/reference/scopesim.source.source.html
        """
        try:
            from scopesim import Source
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "Package 'scopesim' is not installed ! "
                "Please run command 'pip install scopesim' from the command line."
            ) from exc

        if not isinstance(source, Source):
            raise TypeError("Expecting a ScopeSim `Source` object for 'source'.")

        raise NotImplementedError

    def to_scopesim(self) -> "Source":
        """Convert this `Scene` object into a ScopeSim `Source` object.

        Returns
        -------
        Source
            A ScopeSim `Source` object.

        Notes
        -----
        More information about ScopeSim `Source` objects at
        this link: https://scopesim.readthedocs.io/en/latest/reference/scopesim.source.source.html
        """
        raise NotImplementedError

    def to_dict(self) -> Mapping:
        """Convert an instance of `Scene` to a `dict`."""
        result: Mapping = {
            key: value.to_dict() for key, value in self.data.to_dict().items()
        }

        return result

    @classmethod
    def from_dict(cls, dct: Mapping) -> "Scene":
        """Create a new instance of a `Scene` object from a `dict`."""
        # Late import to speedup start-up time
        import xarray as xr

        data: Mapping[str, xr.Dataset] = {
            key: xr.Dataset.from_dict(value) for key, value in dct.items()
        }

        scene = cls()
        scene._source = xr.DataTree.from_dict(data, name="scene")

        return scene

    def to_xarray(self) -> "xr.Dataset":
        """Convert current scene to a xarray Dataset.

        Returns
        -------
        xr.Dataset

        Examples
        --------
        >>> ds = scene.to_xarray()
        >>> ds
        <xarray.Dataset>
        Dimensions:     (ref: 345, wavelength: 343)
        Coordinates:
          * ref         (ref) int64 0 1 2 3 4 5 6 7 ... 337 338 339 340 341 342 343 344
          * wavelength  (wavelength) float64 336.0 338.0 340.0 ... 1.018e+03 1.02e+03
        Data variables:
            x           (ref) float64 2.057e+05 2.058e+05 ... 2.031e+05 2.03e+05
            y           (ref) float64 8.575e+04 8.58e+04 ... 8.795e+04 8.807e+04
            weight      (ref) float64 11.49 14.13 15.22 14.56 ... 15.21 11.51 8.727
            flux        (ref, wavelength) float64 0.03769 0.04137 ... 1.813 1.896
        Attributes:
            right_ascension:  56.75 deg
            declination:      24.1167 deg
            fov_radius:       0.5 deg
        >>> ds["wavelength"]
        <xarray.DataArray 'wavelength' (wavelength: 343)>
        array([ 336.,  338.,  340., ..., 1016., 1018., 1020.])
        Coordinates:
          * wavelength  (wavelength) float64 336.0 338.0 340.0 ... 1.018e+03 1.02e+03
        Attributes:
            units:    nm
        >>> ds["flux"]
        <xarray.DataArray 'flux' (ref: 345, wavelength: 343)>
        array([[3.76907117e-02, 4.13740861e-02, ..., 3.98815404e-02, 7.96581117e-01],
               [1.15190254e-02, 1.02210366e-02, ..., 2.00486326e-02, 2.05518196e-02],
               ...,
               [1.01187592e-01, 9.57637374e-02, ..., 2.71410354e-01, 2.85997559e-01],
               [1.80093381e+00, 1.69864354e+00, ..., 1.81295134e+00, 1.89642359e+00]])
        Coordinates:
          * ref         (ref) int64 0 1 2 3 4 5 6 7 ... 337 338 339 340 341 342 343 344
          * wavelength  (wavelength) float64 336.0 338.0 340.0 ... 1.018e+03 1.02e+03
        Attributes:
            units:    ph / (cm2 nm s)
        """
        # Late import to speedup start-up time
        import xarray as xr

        if "list" not in self.data:
            return xr.Dataset()

        scene_dt = self.data["/list"]
        assert isinstance(scene_dt, xr.DataTree)  # TODO: Improve this

        last_ref: int = 0
        lst: list[xr.Dataset] = []

        partial_scene: xr.DataArray | xr.DataTree
        for partial_scene in scene_dt.values():
            ds: xr.Dataset = partial_scene.to_dataset()

            num_ref: int = len(ds["ref"])
            lst.append(ds.assign_coords(ref=range(last_ref, last_ref + num_ref)))

            last_ref += num_ref

        scene: xr.Dataset = xr.concat(lst, dim="ref")

        return scene
