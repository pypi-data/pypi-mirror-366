"""This module contains the input model for PV plant."""

from typing import Optional

from pysimmods.base.inputs import ModelInputs

CELSIUS_TO_KELVIN: float = 273.15
KELVIN_TO_CELSIUS: float = -1 * CELSIUS_TO_KELVIN
HPA_TO_PA: float = 100.0
PA_TO_HPA: float = 1 / HPA_TO_PA


class WindPowerPlantInputs(ModelInputs):
    """Input variables of Wind plant model.

    See :class:`pysimmods.model.inputs.ModelInputs` for additional
    information. This class has no inputs itself. Instead, each
    of the values is to be provided before each step.

    Attributes
    ----------
    t_air_deg_celsius:
        Air temperature in [°C].
    t_air_deg_kelvin:
        Air temperature in [°K].
    wind_v_m_per_s:
        Wind speed in [m/s].
    wind_dir_deg:
        Wind direction in degrees (currently not used).
    air_pressure_hpa:
        Air pressure in [hPa]
    pressure_pa:
        Air pressure in [Pa].

    """

    def __init__(self):
        super().__init__()

        self.t_air_deg_celsius: float = 0.0
        self.wind_v_m_per_s: float = 0.0
        self.wind_dir_deg: Optional[float] = None
        self.air_pressure_hpa: float = 0.0

    @property
    def pressure_pa(self):
        return self.air_pressure_hpa * HPA_TO_PA

    @pressure_pa.setter
    def pressure_pa(self, value):
        if value < 50000:
            raise ValueError("pressure value error")
        self.air_pressure_hpa = value * PA_TO_HPA

    @property
    def t_air_deg_kelvin(self):
        return self.t_air_deg_celsius + CELSIUS_TO_KELVIN

    @t_air_deg_kelvin.setter
    def t_air_deg_kelvin(self, value):
        if value < 0:
            raise ValueError("temperature value error")
        self.t_air_deg_celsius = value + KELVIN_TO_CELSIUS
