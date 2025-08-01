"""This module contains the heat storage model that is used by the
CHP LPG.
"""

import math
from copy import deepcopy

from pysimmods.base.buffer import Buffer
from pysimmods.base.types import ModelInitVals, ModelParams
from pysimmods.other.heatstoragesim.config import HeatStorageConfig
from pysimmods.other.heatstoragesim.inputs import HeatStorageInputs
from pysimmods.other.heatstoragesim.state import HeatStorageState

C_WATER = 4.18
"""Specific heat capacity of water in [kJ/(kg*K)]"""


class HeatStorage(
    Buffer[HeatStorageConfig, HeatStorageState, HeatStorageInputs]
):
    """Model of a heat storage.

    Parameters
    ----------
    params : dict
        A *dict* containing values for all attributes. The keys all
        have the prefix "storage_".
    inits : dict
        A *dict* containing state variables for the storage. The keys
        all have the prefix "storage_".

    Attributes
    ----------
    cap_l : float
        Capacity of the buffer storage in [l].
    consumption_kwh_per_day : float
        Average loss of energy in [kWh/day].
    t_min_c : float
        Minimal water temperature of the buffer storage in [°C].
    t_max_c : float
        Maximal water temperature of the buffer storage in [°C].
    t_c : float
        Current water temperature of the buffer storage in [°C].
    env_t_c : float, optional
        Current temperature of the environment in [°C]. The storage
        is assumed to be placed indoor and, therefore, defaults to
        19.0 °C.

    """

    def __init__(self, params: ModelParams, inits: ModelInitVals):
        self.config = HeatStorageConfig(params)
        self.state = HeatStorageState(inits)
        self.inputs = HeatStorageInputs()
        # self.cap_l = params["storage_cap_l"]
        # self.consumption_kwh_per_day = params[
        #     "storage_consumption_kwh_per_day"
        # ]
        # self.t_min_c = params["storage_t_min_c"]
        # self.t_max_c = params["storage_t_max_c"]
        # self.env_t_c = params.get("storage_env_t_c", 19.0)

        # State
        # self.t_c = inits["storage_t_c"]
        # self._t_chilled = None

    def step(self, pretend: bool = False) -> HeatStorageState:
        next_state = deepcopy(self.state)

        next_state.e_th_in_max_kwh = self.get_absorbable_energy()
        next_state.e_th_in_min_kwh = self.get_available_energy()

        e_th_delta_kj = (
            self.inputs.e_th_prod_kwh + self.inputs.e_th_demand_kwh
        ) * 3_600

        next_state.t_chilled = self._calculate_chilled_t()
        t_new = (
            e_th_delta_kj / (C_WATER * self.config.cap_l)
            + next_state.t_chilled
        )

        next_state.t_c = max(t_new, self.config.env_t_c)

        if not pretend:
            self.state = next_state
        return next_state

    def _calculate_chilled_t(self):
        """Calculate the chilled temperature.

        This function requires that the :attr:`.env_t_c` is set.

        Returns
        -------
        float
            The chilled temperature

        """

        chill = (
            self.config.consumption_kwh_per_day
            * 3_600_00
            / (C_WATER * 1_000 * self.config.cap_l * 24)
        )
        t_next = self.state.t_c - chill

        # Prevent math domain/division by zero errors
        dif_t_next_env = max(t_next - self.config.env_t_c, 1e-3)
        dif_t_init_env = max(self.state.t_c - self.config.env_t_c, 1e-3)
        div_t = max(dif_t_next_env / dif_t_init_env, 1e-3)

        chill_coef = math.log(div_t) / t_next
        t_chilled = (self.state.t_c - self.config.env_t_c) * math.pow(
            math.e, chill_coef
        ) + self.config.env_t_c

        return t_chilled

    def get_absorbable_energy(self) -> float:
        """Return the amount of energy the storage can absorb."""
        e_th_in_max_kwh = (
            C_WATER
            * self.config.cap_l
            * (self.config.t_max_c - self.state.t_c)
            / 3_600
        )

        return e_th_in_max_kwh

    def get_available_energy(self) -> float:
        """Return the amount of energy the storage has absorbed."""

        e_th_in_min_kwh = (
            C_WATER
            * self.config.cap_l
            * max(0, self.state.t_c - self.config.t_min_c)
            / 3_600
        )

        return e_th_in_min_kwh

    def absorb_energy(self, e_th_prod, e_th_demand):
        # 1 kWh = 3600 kJ
        # One and only one of prod and demand has to be negative
        e_th_delta_kj = (e_th_prod + e_th_demand) * 3_600

        t_chilled = self._calculate_chilled_t()
        t_new = e_th_delta_kj / (C_WATER * self.config.cap_l) + t_chilled

        self.state.t_c = max(t_new, self.config.env_t_c)
