"""This module contains the state model of the chp system."""

from pysimmods.base.state import ModelState
from pysimmods.base.types import ModelInitVals


class CHPLPGSystemState(ModelState):
    """captures the state of the chp system

    The references are updated during each step.
    """

    def __init__(self, init_vals: ModelInitVals):
        super().__init__(init_vals)

        self.p_th_kw = 0.0
        """Current thermal power of the chp in [kW]."""

        self.storage_t_c = 0.0
        """Current temperature of the heat storage in [°C]."""

        self.lubricant_l = 0.0
        """Among of lubricant remaining in [l]."""

        self.e_th_demand_kwh = 0.0
        """Current heat demand of the household in [kW]"""
