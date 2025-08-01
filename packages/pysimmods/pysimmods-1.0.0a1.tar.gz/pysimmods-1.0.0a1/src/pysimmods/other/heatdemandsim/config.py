"""This module contains the config information for the heat demand
model.

"""

from typing import cast

from pysimmods.base.config import ModelConfig
from pysimmods.base.types import ModelParams


class HeatDemandConfig(ModelConfig):
    """Captures the configuration variables of the heat demand model."""

    def __init__(self, params: ModelParams):
        super().__init__(params)
        self.const_a: float = cast("float", params.get("A"))
        self.const_b: float = cast("float", params.get("B"))
        self.const_c: float = cast("float", params.get("C"))
        self.const_d: float = cast("float", params.get("D"))
        self.const_v_0: float = cast("float", params.get("V_0"))
        self.const_m_h: float = cast("float", params.get("M_H"))
        self.const_b_h: float = cast("float", params.get("B_H"))
        self.const_m_w: float = cast("float", params.get("M_W"))
        self.const_b_w: float = cast("float", params.get("B_W"))

        self.load_profile: float = cast(
            "list[float]", params.get("load_profile")
        )
        self.consumer_const: float = cast(
            "float", params.get("consumer_constant")
        )
        self.weekday_const: float = cast(
            "list[float]", params.get("weekday_constants")
        )

        self.degree_of_efficiency = 0.93
