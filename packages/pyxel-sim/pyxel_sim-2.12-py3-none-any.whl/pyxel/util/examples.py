#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel examples downloader."""

import shutil
from pathlib import Path


def download_examples(foldername: str = "pyxel-examples", force: bool = False) -> None:
    """Download and save examples from Pyxel Data Gitlab repository in the working directory.

    Parameters
    ----------
    foldername: str
    force: bool
    """
    # Late import to speedup start-up time
    from zipfile import ZipFile

    import requests
    from tqdm import tqdm

    folder: Path = Path(foldername).resolve()

    if folder.is_dir():
        if force:
            shutil.rmtree(folder)
        else:
            raise OSError(
                f"Folder '{folder}' already exists. Either delete it, "
                "use a different name, or use the '--force' argument."
            )

    url = "https://gitlab.com/esa/pyxel-data/-/archive/master/pyxel-data-master.zip"
    response = requests.get(url, stream=True)

    examples_filename = Path("examples_tmp.zip")

    total = int(response.headers.get("content-length", 0))
    with (
        examples_filename.open("wb") as tmp,
        tqdm(
            desc="Downloading examples",
            total=total,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar,
    ):
        for data in response.iter_content(chunk_size=1024):
            size = tmp.write(data)
            bar.update(size)

    with ZipFile(examples_filename, "r") as zipobj:
        zipobj.extractall(folder)

    pyxel_data_folder: Path = folder.joinpath("pyxel-data-master")

    filename: Path
    for filename in pyxel_data_folder.glob("*"):
        relative_filename: Path = filename.relative_to(pyxel_data_folder)
        shutil.move(src=filename, dst=folder.joinpath(relative_filename))

    pyxel_data_folder.rmdir()
    examples_filename.unlink()

    print(f"Done in folder '{folder}'.")
