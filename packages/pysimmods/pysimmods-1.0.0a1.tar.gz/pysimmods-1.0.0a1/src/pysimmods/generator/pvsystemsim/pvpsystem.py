"""This module contains a model of a pv system with pv modules and an
inverter"""

from copy import deepcopy
from typing import cast

from pysimmods.base.qgenerator import QGenerator
from pysimmods.base.types import ModelInitVals, ModelParams
from pysimmods.generator.pvsim.pvp import PhotovoltaicPowerPlant
from pysimmods.generator.pvsystemsim.config import PVSystemConfig
from pysimmods.generator.pvsystemsim.inputs import PVSystemInputs
from pysimmods.generator.pvsystemsim.state import PVSystemState
from pysimmods.other import Inverter


class PVPlantSystem(QGenerator[PVSystemConfig, PVSystemState, PVSystemInputs]):
    """Pv system with pv modules and inverter"""

    def __init__(self, params: ModelParams, inits: ModelInitVals):
        self.config = PVSystemConfig(params)
        self.inputs = PVSystemInputs()
        self.state = PVSystemState(inits)
        self.pv = PhotovoltaicPowerPlant(
            cast("ModelParams", params["pv"]),
            cast("ModelInitVals", inits["pv"]),
        )
        self.inverter = Inverter(
            cast("ModelParams", params["inverter"]),
            cast("ModelInitVals", inits.get("inverter", {})),
        )

    def step(self, pretend: bool = False) -> PVSystemState:
        """Perform simulation step"""

        next_state = deepcopy(self.state)

        # Step the pv plant
        self.pv.inputs.bh_w_per_m2 = self.inputs.bh_w_per_m2
        self.pv.inputs.dh_w_per_m2 = self.inputs.dh_w_per_m2
        self.pv.inputs.s_module_w_per_m2 = self.inputs.s_module_w_per_m2
        self.pv.inputs.t_air_deg_celsius = self.inputs.t_air_deg_celsius
        self.pv.inputs.step_size = self.inputs.step_size
        self.pv.inputs.now_dt = self.inputs.now_dt

        pv_state = self.pv.step(pretend)

        # Step the inverter
        self.inverter.inputs.p_in_kw = pv_state.p_kw
        self.inverter.inputs.p_set_kw = self.inputs.p_set_kw
        self.inverter.inputs.q_set_kvar = self.inputs.q_set_kvar
        self.inverter.inputs.cos_phi_set = self.inputs.cos_phi_set
        self.inverter.inputs.inductive = self.inputs.inverter_inductive

        inv_state = self.inverter.step(pretend)

        # Update state
        next_state.t_module_deg_celsius = pv_state.t_module_deg_celsius
        next_state.p_kw = inv_state.p_kw
        next_state.p_possible_max_kw = pv_state.p_kw
        next_state.q_kvar = inv_state.q_kvar
        next_state.cos_phi = inv_state.cos_phi
        next_state.inverter_inductive = inv_state.inductive

        if not pretend:
            self.state = next_state

        return next_state

    def get_state(self):
        """Get state"""
        state_dict = {
            "pv": self.pv.get_state(),
            "inverter": self.inverter.get_state(),
        }
        return state_dict

    def set_state(self, state):
        """Set state"""
        self.pv.set_state(state["pv"])
        self.inverter.set_state(state["inverter"])

        self.state.t_module_deg_celsius = self.pv.state.t_module_deg_celsius
        self.state.p_kw = self.inverter.state.p_kw
        self.state.q_kvar = self.inverter.state.q_kvar

    # def set_q_kvar(self, q_kvar: float) -> None:
    #     self.inputs.q_set_kvar = q_kvar
