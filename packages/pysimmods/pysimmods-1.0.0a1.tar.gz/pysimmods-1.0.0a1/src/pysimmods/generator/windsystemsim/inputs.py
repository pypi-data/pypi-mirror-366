"""This module contains the input model for the Wind Turbine System."""

from typing import Optional

from pysimmods.base.inputs import ModelInputs


class WindSystemInputs(ModelInputs):
    def __init__(self):
        super().__init__()

        self.cos_phi_set: Optional[float] = None
        self.inverter_inductive: Optional[bool] = None

        self.t_air_deg_celsius: float = 0.0
        self.wind_v_m_per_s: float = 0.0
        self.air_pressure_hpa: float = 0.0

        # Not used yet
        self.wind_dir_deg: Optional[float] = None
