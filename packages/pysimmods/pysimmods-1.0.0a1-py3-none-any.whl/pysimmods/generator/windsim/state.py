"""This module contains the state model for pv."""

from pysimmods.base.state import ModelState
from pysimmods.base.types import ModelInitVals


class WindPowerPlantState(ModelState):
    """State parameters of Wind model.

    See :class:`pysimmods.model.state.ModelState` for additional
    information.

    Parameters
    ----------
    inits : dict
        Contains the initial configuration of this wind plant. See
        attributes section for specific to the wind plant.

    Attributes
    ----------
    wind_hub_v_m_per_s: float
        Calculated wind speed at hub height in [m/s]
    t_air_hub_deg_kelvin: float
        Calculated air temperature at hub height in [°K].
    air_density_hub_kg_per_m3: float
        Calculated air density at hub height in [kg/m^3].

    """

    def __init__(self, inits: ModelInitVals):
        super().__init__(inits)

        self.wind_hub_v_m_per_s: float = 0.0
        self.t_air_hub_deg_kelvin: float = 0.0
        self.air_density_hub_kg_per_m3: float = 0.0
