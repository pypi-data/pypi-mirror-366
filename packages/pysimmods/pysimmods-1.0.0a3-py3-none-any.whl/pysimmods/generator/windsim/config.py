"""This module contains the config model for the Wind plant."""

from typing import cast

import numpy as np

from pysimmods.base.config import ModelConfig
from pysimmods.base.types import ModelParams


class WindPowerPlantConfig(ModelConfig):
    """Config parameters of Wind plant model.

    Parameters
    ----------

    params : dict
        Contains the configuration of the turbine. See attribute
        section for more information about the parameters, attributes
        marked with *(Input)* can or must be provided.

    Attributes
    ----------

    pn_max_kw : float
        Nominal power of the wind turbine in [kW].
    turbine_type: str
        Model type of this turbine. Has no practical impact.
    hub_height_m: float
        Height of the wind turbine in [m].
    rotor_diameter_m: float
        Diameter of the rotor of the turbine in [m].
    roughness_length_m: float
        Length of roughness in [m].
    obstacle_height_m: float
        Height of obstacles that affect wind speed in [m].
    wind_height_m: float
        Height in which wind speed was measured in [m].
    temperature_height_m: float
        Height in which temperature was measured in [m].
    pressure_height_m: float
        Height in which air pressure was measured in [m].
    method: str
        The method used to calculate wind power. Can be either
        `power_curve` or `power_coefficient`.
    temperature_profile: str
        Method to extrapolate the temperature at hub height. Can be
        either `linear_gradient` or `no_profile` to directly use the
        provided temperature values without extrapolation.
    wind_profile: str
        Method to calculate wind speed at hub height. Can be either
        `hellmann` or `logarithmic`.
    air_density_profile: str
        Method to calculate air density at hub height. Can be either
        `barometric`, `ideal_gas`, or `no_profile`.
    power_curve_w: np.ndarray
        Contains the power values used for power curve calculation
        in [w].
    power_coefficient: np.ndarray
        Contains the values used for power coefficient calculation.
    wind_speeds_m_per_s: np.ndarray
        Contains the wind speed levels for either `power_curve` or
        `power_coefficient`, depending on which `method` is used.

    """

    def __init__(self, params: ModelParams):
        super().__init__(params)

        self.p_max_kw: float = cast("float", params.get("pn_max_kw", 2000.0))
        self.p_min_kw: float = 0
        self.turbine_type: str = cast(
            "str", params.get("turbine_type", "E-82/2000")
        )
        self.hub_height_m: float = cast(
            "float", params.get("hub_height_m", 78)
        )
        self.rotor_diameter_m: float = cast(
            "float", params.get("rotor_diameter_m", 82)
        )
        self.roughness_length_m: float = cast(
            "float", params.get("roughness_length_m", 0.15)
        )
        self.obstacle_height_m: float = cast(
            "float", params.get("obstacle_height_m", 0)
        )

        self.wind_height_m: float = cast(
            "float", params.get("wind_height_m", 10)
        )
        self.temperature_height_m: float = cast(
            "float", params.get("temperature_height_m", 10)
        )
        self.pressure_height_m: float = cast(
            "float", params.get("pressure_height_m", 10)
        )

        self.method: str = cast("str", params.get("method", "power_curve"))

        self.temperature_profile: str = cast(
            "str", params.get("temperature_profile", "linear_gradient")
        )
        if self.temperature_profile != "linear_gradient":
            self.temperature_profile = "no_profile"

        self.wind_profile: str = cast(
            "str", params.get("wind_profile", "hellmann")
        )

        self.air_density_profile: str = cast(
            "str", params.get("air_density_profile", "barometric")
        )
        self.power_curve_w: np.ndarray = np.array(
            cast(
                "list[float]",
                params.get("power_curve_m", [0, 26, 180, 1500, 3000, 3000]),
            )
        )

        self.power_coefficient: np.ndarray = np.array(
            cast(
                "list[float]",
                params.get(
                    "power_coefficient",
                    [0.301, 0.36, 0.39, 0.409, 0.421, 0.429],
                ),
            )
        )

        self.wind_speeds_m_per_s = np.array(params.get("wind_speeds", []))
        if self.wind_speeds_m_per_s.size == 0:
            if self.method == "power_curve":
                num_vals = len(self.power_curve_w)
            else:
                num_vals = len(self.power_coefficient)

            self.wind_speeds_m_per_s = np.linspace(0.0, 25.0, num_vals)
