"""This module contains the config model for the chp system."""

from pysimmods.base.config import ModelConfig
from pysimmods.base.types import ModelParams
from pysimmods.generator.chplpgsim.config import CHPLPGConfig
from pysimmods.other.heatdemandsim.config import HeatDemandConfig


class CHPLPGSystemConfig(ModelConfig):
    """captures the configs for the chp system's components"""

    def __init__(self, params: ModelParams):
        super().__init__(params)

        self.house = HeatDemandConfig(params.get("household", {}))
        self.chp = CHPLPGConfig(params["chp"])
        self.p_max_kw = self.chp.p_max_kw
        self.p_min_kw = self.chp.p_min_kw
        self.q_min_kvar = self.chp.q_min_kvar
        self.q_min_kvar = self.chp.q_max_kvar
        self.e_th_demand_sign = 1.0
        if params.get("flip_e_th_demand_sign", False):
            self.e_th_demand_sign = -1.0
        self.default_schedule = self.chp.default_schedule
