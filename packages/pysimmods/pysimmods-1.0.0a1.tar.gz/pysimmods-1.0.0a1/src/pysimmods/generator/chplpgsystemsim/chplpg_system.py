"""
This module contains a model of a chp system with a chp and a
household. The household has a heat demand which allows the chp
to run for at least 5000 hours in a year.

"""

import logging
from copy import deepcopy
from typing import cast

from pysimmods.base.generator import Generator
from pysimmods.base.types import ModelInitVals, ModelParams
from pysimmods.generator.chplpgsim.chplpg import CHPLPG
from pysimmods.generator.chplpgsystemsim.config import CHPLPGSystemConfig
from pysimmods.generator.chplpgsystemsim.inputs import CHPLPGSystemInputs
from pysimmods.generator.chplpgsystemsim.state import CHPLPGSystemState
from pysimmods.other import HeatDemand, heatdemand_preset

LOG = logging.getLogger(__name__)


class CHPLPGSystem(
    Generator[CHPLPGSystemConfig, CHPLPGSystemState, CHPLPGSystemInputs]
):
    """CHP system with CHP and household"""

    def __init__(self, params: ModelParams, inits: ModelInitVals):
        # First, create the chp
        chp_params = cast("ModelParams", params["chp"])
        chp_params["sign_convention"] = params.get(
            "sign_convention", "passive"
        )
        self.chp = CHPLPG(chp_params, cast("ModelInitVals", inits["chp"]))

        # Get the thermal capabilities of the chp
        p_th_min_kw = (
            self.chp.config.p_min_kw * self.chp.config.p_2_p_th_percent * 0.01
        )

        # Second, create an appropriate household
        # FIXME: Seeding is non-deterministic here!
        self.heatdemand = HeatDemand(
            *heatdemand_preset(-p_th_min_kw, seed=None)
        )

        self.config = CHPLPGSystemConfig(params)
        self.state = CHPLPGSystemState(inits)
        self.inputs = CHPLPGSystemInputs()

    def step(self, pretend: bool = False) -> CHPLPGSystemState:
        """Perform a simulation step"""
        next_state = deepcopy(self.state)

        err = None
        try:
            # First step the household
            self.heatdemand.inputs.now_dt = self.inputs.now_dt
            self.heatdemand.inputs.step_size = self.inputs.step_size
            self.heatdemand.inputs.day_avg_t_air_deg_celsius = (
                self.inputs.day_avg_t_air_deg_celsius
            )
            self.heatdemand.step()
        except TypeError as te:
            err = te

        # Second step the chp
        p_set_kw = self._check_setpoint()
        self.chp.set_now_dt(self.inputs.now_dt)
        if self.inputs.e_th_demand_set_kwh is not None:
            self.chp.inputs.e_th_demand_set_kwh = (
                self.inputs.e_th_demand_set_kwh * self.config.e_th_demand_sign
            )
        elif err is None:
            self.chp.inputs.e_th_demand_set_kwh = (
                self.heatdemand.state.e_th_kwh
            )
        else:
            msg = (
                "One input is missing for CHP. Must at least provide "
                "one of 'day_avg_t_air_deg_celsius' or "
                "'e_th_demand_kwh'!"
            )
            LOG.error(msg)
            raise ValueError(msg)

        self.chp.set_step_size(self.inputs.step_size)
        self.chp.set_p_kw(p_set_kw * self.config.gsign)
        nstate_chp = self.chp.step(pretend)

        # Update the references
        next_state.p_kw = nstate_chp.p_kw
        next_state.q_kvar = nstate_chp.q_kvar
        next_state.p_th_kw = nstate_chp.p_th_kw
        next_state.storage_t_c = nstate_chp.storage_t_c
        next_state.lubricant_l = nstate_chp.lubricant_l
        if self.inputs.e_th_demand_set_kwh is not None:
            next_state.e_th_demand_kwh = self.inputs.e_th_demand_set_kwh
        else:
            next_state.e_th_demand_kwh = self.heatdemand.state.e_th_kwh

        if not pretend:
            self.state = next_state
        return next_state

    def _check_setpoint(self):
        setpoint = self.inputs.p_set_kw
        if setpoint is not None:
            return abs(setpoint)
        hour = self.inputs.now_dt.hour
        default = self.config.default_schedule[hour]
        setpoint = self.config.p_max_kw * default / 100

        return abs(setpoint)

    def get_state(self):
        """Get state"""
        state_dict = {
            "household": self.heatdemand.get_state(),
            "chp": self.chp.get_state(),
        }
        return state_dict

    def set_state(self, state):
        """Set state"""
        self.heatdemand.set_state(state["household"])
        self.chp.set_state(state["chp"])

        self.state.p_kw = self.chp.state.p_kw
        self.state.q_kvar = self.chp.state.q_kvar
        self.state.p_th_kw = self.chp.state.p_th_kw
        self.state.storage_t_c = self.chp.state.storage_t_c
        self.state.lubricant_l = self.chp.state.lubricant_l
