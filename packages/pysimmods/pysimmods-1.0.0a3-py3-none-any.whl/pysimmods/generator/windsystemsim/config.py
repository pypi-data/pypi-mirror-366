"""This module contains the config of the Wind Turbine System."""

from typing import cast

from pysimmods.base.config import ModelConfig
from pysimmods.base.types import ModelParams
from pysimmods.generator.windsim.config import WindPowerPlantConfig
from pysimmods.other.invertersim.config import InverterConfig


class WindSystemConfig(ModelConfig):
    def __init__(self, params: ModelParams):
        super().__init__(params)
        cast("ModelParams", params["wind"])["sign_convention"] = (
            self.sign_convention
        )
        cast("ModelParams", params["inverter"])["sign_convention"] = (
            self.sign_convention
        )

        # Those are duplicate to the original configs
        self._turbine: WindPowerPlantConfig = WindPowerPlantConfig(
            cast("ModelParams", params["wind"])
        )
        self._inverter: InverterConfig = InverterConfig(
            cast("ModelParams", params["inverter"])
        )

        self.s_max_kva = self._inverter.s_max_kva
        self.q_control = self._inverter.q_control
        self.cos_phi = self._inverter.cos_phi
        self.p_max_kw = self._turbine.p_max_kw
        self.p_min_kw = self._turbine.p_min_kw

        self.default_p_schedule = None
        self.default_q_schedule = None
