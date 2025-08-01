"""This module contains the state model of the Wind Turbine System."""

from pysimmods.base.state import ModelState
from pysimmods.base.types import ModelInitVals


class WindSystemState(ModelState):
    def __init__(self, inits: ModelInitVals):
        super().__init__(inits)

        self.p_possible_max_kw: float = 0
        self.wind_hub_v_m_per_s: float = 0
        self.t_air_hub_deg_kelvin: float = 0
        self.air_density_hub_kg_per_m3: float = 0
        self.cos_phi: float = 0
        self.inverter_inductive: bool = False
