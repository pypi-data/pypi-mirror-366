"""This module contains the input model for the HVAC model."""

from pysimmods.base.inputs import ModelInputs


class HVACInputs(ModelInputs):
    """Input variables of the HVAC model.

    See :class:`.ModelInputs` for additional information.

    Attributes
    ----------
    t_air_deg_celsius : float
        Temperature of the environment in [°C].

    """

    def __init__(self):
        super().__init__()

        self.t_air_deg_celsius: float | None = None
