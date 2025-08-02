__version__ = "1.0.0a2"

import sys

from . import mosaik_bridge

# Create a fake module alias so `pysimmods.mosaik` still works
sys.modules["pysimmods.mosaik"] = mosaik_bridge
