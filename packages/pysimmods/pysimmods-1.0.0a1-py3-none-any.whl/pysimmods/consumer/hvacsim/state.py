"""This module contains the state model for HVAC."""

from pysimmods.base.state import ModelState
from pysimmods.base.types import ModelInitVals


class HVACState(ModelState):
    """State parameters of the HVAC model.

    See :class:`.ModelState` for additional information.

    Parameters
    ----------
    inits : dict
        Contains the initial configuration of this HVAC model. See
        the attributes section for specific information of the HVAC
        model.

    Attributes
    ----------
    mass_kg : float
        Mass of the content in [kg].
    c_j_per_kg_k : float
        Mean specific heat capacity of refer cargo in [Jkg^-K^-1].
    theta_t_deg_celsius : float
        Time dependent temperature of the model in [°C].
    cooling : bool
        If set to True, the model is cooling, i.e., consuming power.


    """

    def __init__(self, inits: ModelInitVals):
        super().__init__(inits)

        self.mass_kg: float = inits.get("mass_kg", 500)
        self.c_j_per_kg_k: float = inits.get("c_j_per_kg_k", 2390)
        self.theta_t_deg_celsius: float = inits.get("theta_t_deg_celsius", 21)
        self.cooling: bool = inits.get("cooling", True)
        if isinstance(self.cooling, str):
            self.cooling = self.cooling.lower() not in ("0", "f", "false")
