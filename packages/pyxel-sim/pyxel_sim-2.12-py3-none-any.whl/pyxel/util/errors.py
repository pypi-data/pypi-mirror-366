#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Functions to generate error messages."""


def get_uninitialized_error(name: str, parent_name: str) -> str:
    return (
        f"Missing required parameter '{name}' in '{parent_name}'.\n"
        f"This parameter must be defined in your detector 'detector.{parent_name}.{name}'.\n\n"
        f"To fix this issue, you can either:\n"
        f"  - Set the parameter directly in your Python code (see following example):\n"
        f"      >>> config = pyxel.load_config(...)\n"
        f"      >>> config.detector.{parent_name}.{name} = ...\n\n"
        f"  - Or define it directly in your YAML configuration file (see following example):\n"
        f"      detector:\n"
        f"        {parent_name}:\n"
        f"          {name}:..."
    )
