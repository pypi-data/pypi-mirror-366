"""This module contains the input information of the heat demand
model.
"""

from pysimmods.base.model import ModelInputs


class HeatDemandInputs(ModelInputs):
    """Captures the inputs of the heat demand model"""

    def __init__(self):
        super().__init__()

        self.day_avg_t_air_deg_celsius: float = 0.0
