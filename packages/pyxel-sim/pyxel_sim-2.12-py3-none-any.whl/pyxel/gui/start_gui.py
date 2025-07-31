"""Start GUI.

Examples
--------
$ panel serve start_gui.py --dev --show
"""

from pyxel.gui import BasicConfigGUI

cfg = BasicConfigGUI()

cfg.display().servable(title="Pyxel")
