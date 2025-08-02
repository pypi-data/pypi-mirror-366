"""This module contains the python port of a CHP model developed in the
student's project group POWDER.
"""

from copy import copy

from pysimmods.base.generator import Generator
from pysimmods.base.types import ModelInitVals, ModelParams
from pysimmods.generator.chplpgsim.config import CHPLPGConfig
from pysimmods.generator.chplpgsim.inputs import CHPLPGInputs
from pysimmods.generator.chplpgsim.state import CHPLPGState
from pysimmods.other.heatstoragesim.heatstorage import HeatStorage


class CHPLPG(Generator[CHPLPGConfig, CHPLPGState, CHPLPGInputs]):
    """A Combined Heat and Power unit model.

    The CHP is fueled with Liquefied Petroleum Gas (LPG).

    Attributes
    ----------
    config : CHPLPGConfig
    state : CHPLPGState
    inputs : CHPLPGInputs

    """

    def __init__(self, params: ModelParams, inits: ModelInitVals):
        self.config = CHPLPGConfig(params)
        self.state = CHPLPGState(inits)
        self.inputs: CHPLPGInputs = CHPLPGInputs()

        self._storage = HeatStorage(params, inits)

    def step(self, pretend: bool = False) -> CHPLPGState:
        """Perform a simulation step."""
        next_state = copy(self.state)
        next_state.p_kw = self._get_setpoint()

        self._check_inputs()

        # Operating state constraint is checked first to prevent
        # invalid user inputs. However, this has least priority and
        # changes due to other constraints are possible.
        self._check_operating_state(next_state)

        self._check_performance_limit(next_state)
        self._check_lubricant(next_state)
        self._check_storage_temperature(next_state)

        # Change operating state
        if next_state.p_kw != 0:
            next_state.is_active = True
            next_state.active_s += self.inputs.step_size
            next_state.inactive_s = 0
        else:
            next_state.is_active = False
            next_state.active_s = 0
            next_state.inactive_s += self.inputs.step_size
            # Auto refill of lubricant
            next_state.lubricant_l = self.config.lubricant_max_l

        next_state.q_kvar = 0

        if not pretend:
            self.state = next_state
        return next_state

    def _check_inputs(self):
        if self.inputs.e_th_demand_set_kwh is None:
            self.inputs.e_th_demand_set_kwh = 0

    def _get_setpoint(self):
        setpoint = self.inputs.p_set_kw

        if setpoint is not None:
            return abs(setpoint)

        hour = self.inputs.now_dt.hour
        default = self.config.default_schedule[hour]
        setpoint = self.config.p_max_kw * default / 100

        return abs(setpoint)

    def _check_operating_state(self, next_state):
        """Check if operating state constraints are satisfied.

        If the inut is not allowed to switch on, it will stay off.
        On the other hand, if the unit is not allowed to switch off,
        the minimal power is used as set value.

        """

        if next_state.p_kw > 0:
            if (
                not self.state.is_active
                and self.state.inactive_s < self.config.inactive_min_s
            ):
                next_state.p_kw = 0
        else:
            if (
                self.state.is_active
                and self.state.active_s < self.config.active_min_s
            ):
                next_state.p_kw = self.config.p_min_kw

    def _check_performance_limit(self, next_state):
        """Check if minimal performance is reached.

        If this is not the case, the set value is adapted to minimal
        power.

        """
        if next_state.p_kw > 0:
            next_state.p_kw = max(
                min(next_state.p_kw, self.config.p_max_kw),
                self.config.p_min_kw,
            )

    def _check_lubricant(self, next_state):
        """Check if lubricant constraint is satisfied.

        If no lubricant is available, the unit will switch off.

        """
        if next_state.p_kw > 0:
            lubricant_delta_l = (
                self.config.lubricant_ml_per_h
                * (self.inputs.step_size / 3_600)
                / 1_000
            )
            if self.state.lubricant_l < lubricant_delta_l:
                # not enough lubricant, switch off
                next_state.p_kw = 0
            else:
                next_state.lubricant_l -= lubricant_delta_l

    def _check_storage_temperature(self, next_state):
        """Check if the storage temperature is not too high

        Also calculates the new storage temperature and if the
        temperature is too high, a lower set value for power is
        calculated.

        """
        # Thermal energy production
        e_th_prod_kwh = (
            next_state.p_kw
            * self.config.p_2_p_th_percent
            / 100
            * self.inputs.step_size
            / 3_600
        )
        self._storage.inputs.e_th_prod_kwh = 0
        self._storage.inputs.e_th_demand_kwh = 0
        sstate = self._storage.step(pretend=True)

        # Get maximal energy the storage can absorb
        e_th_in_max_kwh = sstate.e_th_in_max_kwh

        if e_th_prod_kwh > e_th_in_max_kwh:
            next_state.p_kw = (
                e_th_in_max_kwh
                * (100 / self.config.p_2_p_th_percent)
                * (3_600 / self.inputs.step_size)
            )
            e_th_prod_kwh = e_th_in_max_kwh

        # Get available storage energy
        e_th_in_min_kwh = sstate.e_th_in_min_kwh
        demand_after_prod = min(
            0, self.inputs.e_th_demand_set_kwh + e_th_prod_kwh
        )

        if abs(demand_after_prod) > e_th_in_min_kwh:
            next_state.p_kw = max(
                self.config.p_min_kw,
                next_state.p_kw + (self.config.p_min_kw * 0.25),
            )
            return self._check_storage_temperature(next_state)

        self._storage.inputs.e_th_prod_kwh = e_th_prod_kwh
        self._storage.inputs.e_th_demand_kwh = self.inputs.e_th_demand_set_kwh
        sstate = self._storage.step(pretend=False)

        next_state.storage_t_c = self._storage.state.t_c
        next_state.p_th_kw = (
            next_state.p_kw * self.config.p_2_p_th_percent / 100
        )

    def set_state(self, state):
        """Set the state."""
        super().set_state(state)
        self._storage.state.t_c = self.state.storage_t_c
