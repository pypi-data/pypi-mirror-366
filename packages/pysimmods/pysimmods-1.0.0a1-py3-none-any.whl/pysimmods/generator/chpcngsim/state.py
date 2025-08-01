"""This module contains the state model of the chp."""

from typing import cast

from pysimmods.base.state import ModelState
from pysimmods.base.types import ModelInitVals


class CHPCNGState(ModelState):
    """A CHP CNG state information class.

    Parameters
    ----------
    inits: dict
        Contains the initial configuration of this CHP model. See
        attributes section for specific information.

    Attributes
    ----------
    active_s: int
        Time since unit switch to current power level in [s].
    active_s_per_day: int
        Time the unit is active on the current day in [s].
    inactive_s: int
        Time since the unit is switched off in [s].
    inactive_s_per_day: int
        Time the is inactive on the current day in [s].
    restarts: int
        Number of restarts on the current day.
    p_th_kw: float
        Thermal power generated in [kW].
    gas_cons_m3: float
        Gas consumed in the last step in [m^3]
    """

    def __init__(self, inits: ModelInitVals):
        super().__init__(inits)

        self.active_s: int = cast("int", inits["active_s"])
        self.active_s_per_day: int = cast("int", inits["active_s_per_day"])
        self.inactive_s: int = cast("int", inits["inactive_s"])
        self.inactive_s_per_day: int = cast("int", inits["inactive_s_per_day"])

        self.restarts: int = cast("int", inits["restarts"])

        self.p_th_kw: float = 0.0
        self.gas_cons_m3: float = 0.0
