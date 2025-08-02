"""This module contains the state information of the heat demand model."""

from pysimmods.base.state import ModelState
from pysimmods.base.types import ModelInitVals


class HeatDemandState(ModelState):
    """Captures the state of the heat demand model"""

    def __init__(self, inits: ModelInitVals):
        super().__init__(inits)

        self.t_last_3_deg_celsius = inits.get("t_last_3_deg_celsius", 10.3)
        self.t_last_2_deg_celsius = inits.get("t_last_2_deg_celsius", 10.3)
        self.t_last_1_deg_celsius = inits.get("t_last_1_deg_celsius", 10.3)

        self.e_th_kwh: float = 0.0
