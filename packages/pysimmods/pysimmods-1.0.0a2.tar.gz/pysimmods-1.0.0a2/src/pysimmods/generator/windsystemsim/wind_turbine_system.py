"""This module contains a model of a wind turbine and an inverter"""

from copy import deepcopy
from typing import cast

from pysimmods.base.qgenerator import QGenerator
from pysimmods.base.types import ModelInitVals, ModelParams
from pysimmods.generator.windsim.wind import WindPowerPlant
from pysimmods.generator.windsystemsim.config import WindSystemConfig
from pysimmods.generator.windsystemsim.inputs import WindSystemInputs
from pysimmods.generator.windsystemsim.state import WindSystemState
from pysimmods.other.invertersim.inverter import Inverter


class WindPowerPlantSystem(
    QGenerator[WindSystemConfig, WindSystemState, WindSystemInputs]
):
    def __init__(self, params: ModelParams, inits: ModelInitVals):
        self.config = WindSystemConfig(params)
        self.inputs = WindSystemInputs()
        self.state = WindSystemState(inits)

        self.wind = WindPowerPlant(
            cast("ModelParams", params["wind"]),
            cast("ModelInitVals", inits.get("wind", {})),
        )
        self.inverter = Inverter(
            cast("ModelParams", params["inverter"]),
            cast("ModelInitVals", inits.get("inverter", {})),
        )

    def step(self, pretend: bool = False) -> WindSystemState:
        """Perform simulation step."""
        next_state = deepcopy(self.state)

        # Step the wind turbine
        # self.wind.inputs.step_size = self.inputs.step_size
        # self.wind.inputs.now_dt = self.inputs.now_dt
        self.wind.inputs.wind_v_m_per_s = self.inputs.wind_v_m_per_s
        self.wind.inputs.t_air_deg_celsius = self.inputs.t_air_deg_celsius
        self.wind.inputs.air_pressure_hpa = self.inputs.air_pressure_hpa
        wind_state = self.wind.step(pretend)

        # Step the inverter
        self.inverter.inputs.p_in_kw = wind_state.p_kw
        self.inverter.inputs.p_set_kw = self.inputs.p_set_kw
        self.inverter.inputs.q_set_kvar = self.inputs.q_set_kvar
        self.inverter.inputs.cos_phi_set = self.inputs.cos_phi_set
        self.inverter.inputs.inductive = self.inputs.inverter_inductive
        inv_state = self.inverter.step(pretend)

        # Update state
        next_state.p_kw = inv_state.p_kw
        next_state.p_possible_max_kw = wind_state.p_kw
        next_state.q_kvar = inv_state.q_kvar
        next_state.cos_phi = inv_state.cos_phi
        next_state.inverter_inductive = inv_state._inductive
        next_state.wind_hub_v_m_per_s = wind_state.wind_hub_v_m_per_s
        next_state.t_air_hub_deg_kelvin = wind_state.t_air_hub_deg_kelvin
        next_state.air_density_hub_kg_per_m3 = (
            wind_state.air_density_hub_kg_per_m3
        )

        if not pretend:
            self.state = next_state

        return next_state

    def get_state(self):
        state_dict = {
            "wind": self.wind.get_state(),
            "inverter": self.inverter.get_state(),
        }
        return state_dict

    def set_state(self, state):
        self.wind.set_state(state["wind"])
        self.inverter.set_state(state["inverter"])

        self.state.p_kw = self.inverter.state.p_kw
        self.state.p_possible_max_kw = self.wind.state.p_kw
        self.state.q_kvar = self.inverter.state.q_kvar
        self.state.cos_phi = self.inverter.state.cos_phi
        self.state.inverter_inductive = self.inverter.state._inductive
        self.state.wind_hub_v_m_per_s = self.wind.state.wind_hub_v_m_per_s
        self.state.t_air_hub_deg_kelvin = self.wind.state.t_air_hub_deg_kelvin
        self.state.air_density_hub_kg_per_m3 = (
            self.wind.state.air_density_hub_kg_per_m3
        )

    # def set_q_kvar(self, q_kvar: float):
    #     self.inputs.q_set_kvar = q_kvar
