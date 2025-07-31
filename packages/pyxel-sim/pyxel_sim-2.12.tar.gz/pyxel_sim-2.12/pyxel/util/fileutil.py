#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""File utility functions to simplify path logic."""

from pathlib import Path, PurePath

from typing_extensions import overload


def is_path_relative(filename: str | Path) -> bool:
    """Check if the filename is a relative or absolute path.

    Examples
    --------
    >>> from pathlib import Path
    >>> is_path_relative("file.fits")
    True
    >>> is_path_relative(Path("/file.fits"))
    False
    >>> is_path_relative("https://server/file.fits")
    False
    """
    if isinstance(filename, PurePath):
        return not filename.is_absolute()

    return (
        ":" not in filename
        and not filename.startswith("\\")
        and not filename.startswith("/")
    )


@overload
def complete_path(filename: str, working_dir: str | Path | None) -> str: ...


@overload
def complete_path(filename: Path, working_dir: str | Path | None) -> Path: ...


def complete_path(filename: str | Path, working_dir: str | Path | None) -> str | Path:
    """Prefix the filename with the working directory.

    The returned type will be the same as the `filename` type.

    Parameters
    ----------
    filename : str or Path
        The filename or path that needs to be completed. This can be a string or a Path object.
    working_dir :str or Path. Optional
        The working directory to prefix to the filename if it is relative. This can be a string, a Path object, or None.
        If None, the function will return the filename unchanged.

    Returns
    -------
    str or Path
        The completed path.

    Examples
    --------
    >>> from pathlib import Path
    >>> complete_path(filename="file.fits", working_directory=None)
    'file.fits'
    >>> complete_path(filename=Path("file.fits"), working_directory="/folder")
    Path('/folder/file.fits')
    >>> complete_path(filename="/my_folder/file.fits", working_dir="/folder")
    '/my_folder/file.fits'
    >>> complete_path(filename="https://server/file.fits", working_dir="/folder")
    'https://server/file.fits'
    """
    if not working_dir or not is_path_relative(filename):
        return filename

    if isinstance(filename, Path):
        return Path(working_dir).joinpath(filename)

    return str(working_dir) + "/" + filename


@overload
def resolve_with_working_directory(
    filename: str,
) -> str: ...


@overload
def resolve_with_working_directory(filename: Path) -> Path: ...


def resolve_with_working_directory(filename: str | Path) -> str | Path:
    """Make the given path absolute using the global working directory.

    This function uses a global working directory specified in the global options to
    make the given filename absolute.

    Parameters
    ----------
    filename : str or Path
       The filename or path that needs to be resolved to an absolute path.

    Returns
    -------
    str or Path
       The absolute path of the given filename. The return type will match the type of the input `filename`.


    Examples
    --------
    >>> resolve_with_working_directory("file.fits")
    'file.fits'

    >>> from pyxel import set_options
    >>> set_options(working_directory="my_folder")
    >>> resolve_with_working_directory(Path("file.fits"))
    Path('my_folder/file.fits')
    """
    from pyxel.options import global_options

    return complete_path(
        filename,
        working_dir=global_options.working_directory,
    )
