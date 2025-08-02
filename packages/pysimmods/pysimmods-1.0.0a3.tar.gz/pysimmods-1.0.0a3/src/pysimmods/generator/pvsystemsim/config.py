"""This module contains the config model of the PV plant system."""

from typing import cast

from pysimmods.base.config import ModelConfig
from pysimmods.base.types import ModelParams
from pysimmods.generator.pvsim.config import PVConfig
from pysimmods.other.invertersim.config import InverterConfig


class PVSystemConfig(ModelConfig):
    """Config parameters of the PV plant System.

    Consists of a :class:`~.PVConfig` and an :class:`~.InverterConfig`
    object.

    """

    def __init__(self, params: ModelParams):
        super().__init__(params)
        pv_params = cast("ModelParams", params["pv"])
        inv_params = cast("ModelParams", params["inverter"])
        pv_params["sign_convention"] = self.sign_convention
        inv_params["sign_convention"] = self.sign_convention

        self.pv = PVConfig(pv_params)
        self.inverter = InverterConfig(inv_params)
        self.default_p_schedule = None
        self.default_q_schedule = None

        self.p_max_kw = self.pv.p_max_kw
        self.p_min_kw = self.pv.p_min_kw
        self.s_max_kva = self.inverter.s_max_kva

    @property
    def q_control(self):
        return self.inverter.q_control

    @property
    def cos_phi(self):
        return self.inverter.cos_phi
