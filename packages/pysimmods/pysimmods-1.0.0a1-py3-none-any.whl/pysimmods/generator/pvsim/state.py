"""This module contains the state model for pv."""

from typing import cast

from pysimmods.base.state import ModelState
from pysimmods.base.types import ModelInitVals


class PVState(ModelState):
    """State parameters of pv model.

    See :class:`pysimmods.model.state.ModelState` for additional
    information.

    Parameters
    ----------
    inits : dict
        Contains the initial configuration of this PV plant. See
        attributes section for specific to the PV plant.

    Attributes
    ----------
    t_module_deg_celsius : float
        Temperature of the module in [°C].

    """

    def __init__(self, inits: ModelInitVals):
        super().__init__(inits)
        self.t_module_deg_celsius: float = cast(
            "float", inits["t_module_deg_celsius"]
        )
