"""This module contains the input model for the chp system."""

from pysimmods.base.inputs import ModelInputs


class CHPLPGSystemInputs(ModelInputs):
    """captures the inputs of the chp system"""

    def __init__(self):
        super().__init__()

        self.day_avg_t_air_deg_celsius: float = 0.0
        """Average temperature of the current day in [°C]."""

        self.e_th_demand_set_kwh: float | None = None
