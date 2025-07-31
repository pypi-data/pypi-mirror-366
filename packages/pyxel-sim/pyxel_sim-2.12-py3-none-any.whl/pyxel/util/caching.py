#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Function(s) to get a global caching mechanism."""

import tempfile
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from diskcache import Cache


_global_cache: Optional["Cache"] = None


def get_cache(folder: str | None = None) -> "Cache":
    """Retrieve a unique global cache instance.

    Examples
    --------
    >>> from pyxel.util import get_cache

    Check that 'get_cache()' always return the same object

    >>> cache1 = get_cache()
    >>> cache2 = get_cache()
    >>> cache1 is cache2
    True

    Clean the cache
    >>> cache = get_cache()
    >>> cache.clear()
    """
    # Late import to speedup start-up time
    from diskcache import Cache

    global _global_cache

    if _global_cache is None:
        if folder is None:
            folder = tempfile.gettempdir()

        _global_cache = Cache(directory=folder)

    return _global_cache
