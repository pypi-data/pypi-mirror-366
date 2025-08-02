"""This module contains an inverter model"""

from copy import copy
from math import sqrt

from pysimmods.base.qgenerator import QGenerator
from pysimmods.base.types import ModelInitVals, ModelParams, QControl
from pysimmods.other.invertersim.config import InverterConfig
from pysimmods.other.invertersim.inputs import InverterInputs
from pysimmods.other.invertersim.state import InverterState


class Inverter(QGenerator[InverterConfig, InverterState, InverterInputs]):
    """Inverter model

    Parameters
    ----------
    params : dict
        A *dict* containing configuration parameters.
    inits : dict, optional
        A *dict* containing initialization parameters.

    Attributes
    ----------
    config : :class:`~.InverterConfig`
        Configuration parameters of the inverter.
    state : :class:`~.InverterState`
        Initialization parameters of the inverter.
    inputs : :class:`~.InverterInputs`
        Input parameters of the inverter.

    """

    def __init__(
        self, params: ModelParams, inits: ModelInitVals | None = None
    ):
        if inits is None:
            inits = {}

        self.config: InverterConfig = InverterConfig(params)
        self.state: InverterState = InverterState(inits)
        self.inputs: InverterInputs = InverterInputs()

    def step(self, pretend=False) -> InverterState:
        """Perform simulation step"""
        self._check_inputs()

        next_state = copy(self.state)
        next_state._inductive = self.inputs._inductive
        self._calculate(next_state)

        if not pretend:
            self.state = next_state

        self.inputs.reset()

        return next_state

    def _check_inputs(self):
        if self.inputs.p_set_kw is None:
            self.inputs.p_set_kw = self.inputs.p_in_kw

        if self.inputs.cos_phi_set is None:
            self.inputs.cos_phi_set = self.config.cos_phi

        if self.inputs._inductive is None:
            self.inputs._inductive = self.config.inverter_mode == "inductive"

    def _calculate(self, next_state: InverterState):
        # Can't output more power than is available
        p_kw = min(abs(self.inputs.p_in_kw), abs(self.inputs.p_set_kw))

        # Check constraints for apparent power
        s_kva = p_kw / self.inputs.cos_phi_set
        s_kva = min(s_kva, self.config.s_max_kva)

        # Use updated apparent power to calculate active power
        p_max_kw = s_kva * self.inputs.cos_phi_set
        p_kw = min(p_kw, p_max_kw)

        # Calculate maximum reactive power
        q_max_kvar = sqrt(self.config.s_max_kva**2 - p_kw**2)

        # Check if reactive power setpoint is provided
        if self.inputs.q_set_kvar is None:
            # No; use "remaining" current apparent power for reactive
            # power, preserving the cos phi
            q_kvar = sqrt(s_kva**2 - p_kw**2)
            q_kvar = min(q_max_kvar, q_kvar)
            if next_state._inductive:
                q_kvar *= -1
        else:
            # Yes; use "remaining" maximum apparent power for reactive
            # power, the cos phi may change
            q_set_sign = 1 if self.inputs.q_set_kvar >= 0 else -1
            q_kvar = min(
                abs(self.inputs.q_set_kvar), abs(self.config.s_max_kva)
            )
            s_kva = sqrt(p_kw**2 + q_kvar**2)

            # Limit active or reactive power according to the q-control
            # mode
            if s_kva > self.config.s_max_kva:
                if self.config.q_control == QControl.PRIORITIZE_P:
                    q_kvar = q_max_kvar
                elif self.config.q_control == QControl.PRIORITIZE_Q:
                    p_kw = sqrt(self.config.s_max_kva**2 - q_kvar**2)

            q_kvar *= q_set_sign

        if s_kva > 0:
            next_state.cos_phi = p_kw / s_kva
        else:
            next_state.cos_phi = self.inputs.cos_phi_set
        next_state.p_kw = p_kw
        next_state.q_kvar = q_kvar

    def set_q_kvar(self, q_kvar: float) -> None:
        self.inputs.q_set_kvar = q_kvar
