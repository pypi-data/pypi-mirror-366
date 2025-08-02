"""
This module contains a household class that simulates thermal power demand
for the chp.

"""

import math
from copy import deepcopy
from datetime import timedelta

from pysimmods.base.consumer import Consumer
from pysimmods.base.types import ModelInitVals, ModelParams
from pysimmods.other.heatdemandsim.config import HeatDemandConfig
from pysimmods.other.heatdemandsim.inputs import HeatDemandInputs
from pysimmods.other.heatdemandsim.state import HeatDemandState


class HeatDemand(
    Consumer[HeatDemandConfig, HeatDemandState, HeatDemandInputs]
):
    """A simple model for thermal power demand."""

    def __init__(self, params: ModelParams, inits: ModelInitVals):
        self.config = HeatDemandConfig(params)
        self.state = HeatDemandState(inits)
        self.inputs = HeatDemandInputs()

    def step(self, pretend: bool = False) -> HeatDemandState:
        """Perform a simulation step"""

        next_state = deepcopy(self.state)

        # calculate allocation temperature for the current day
        # (weighted mean temperature of the current and the last
        # three days)
        t_alloc = (
            1.0 * self.inputs.day_avg_t_air_deg_celsius
            + 0.5 * self.state.t_last_1_deg_celsius
            + 0.25 * self.state.t_last_2_deg_celsius
            + 0.125 * self.state.t_last_3_deg_celsius
        ) / (1 + 0.5 + 0.25 + 0.125)

        if t_alloc >= self.config.const_v_0:
            t_alloc = self.config.const_v_0 * 0.99

        # profile function 'SigLinDe': calculate daily consumption
        # depending on the allocation temperature. Has both a sigmoid
        # and a linear part
        tmp = self._daily_consumption_pow(t_alloc)
        sigmoid = self.config.const_a / (1.0 + tmp) + self.config.const_d
        linear = max(
            self.config.const_m_h * t_alloc + self.config.const_b_h,
            self.config.const_m_w * t_alloc + self.config.const_b_w,
        )

        daily_cons = (
            self.config.consumer_const
            * (sigmoid + linear)
            * self.config.weekday_const[self.inputs.now_dt.weekday()]
        )

        next_state.e_th_kwh = float(
            daily_cons
            * self.config.degree_of_efficiency
            * self.config.load_profile[self.inputs.now_dt.hour]
            * self.inputs.step_size
            / 3_600
        )

        next_dt = self.inputs.now_dt + timedelta(seconds=self.inputs.step_size)
        if next_dt.day > self.inputs.now_dt.day:
            # we reached a new day
            next_state.t_last_3_deg_celsius = next_state.t_last_2_deg_celsius
            next_state.t_last_2_deg_celsius = next_state.t_last_1_deg_celsius
            next_state.t_last_1_deg_celsius = (
                self.inputs.day_avg_t_air_deg_celsius
            )

        if not pretend:
            self.state = next_state
        return next_state

    def _daily_consumption_pow(self, t_alloc):
        return math.pow(
            self.config.const_b / (t_alloc - self.config.const_v_0),
            self.config.const_c,
        )

    @property
    def e_th_kwh(self):
        """Returns the current thermal power demand"""
        return self.state.e_th_kwh

    def get_state(self) -> dict:
        """Return the current state of the model.

        Returns
        -------
        dict
            The current state of the model in form of a dictionary
            containing entries for all state variables. Returned dict
            can be assigned to the *inits* argument when creating a new
            model instance.

        """

        try:
            return {
                attr: getattr(self.state, attr)
                for attr in self.state.__slots__
            }
        except AttributeError:
            return deepcopy(self.state.__dict__)

    def set_state(self, state: dict) -> None:
        """Set the current state of the model.

        Parameters
        ----------
        state : dict
            A *dict* containing entries for all state variables.

        """
        for attr, value in state.items():
            setattr(self.state, attr, value)
