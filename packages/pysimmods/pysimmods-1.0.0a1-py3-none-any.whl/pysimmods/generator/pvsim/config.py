"""This module contains the config model for the PV plant."""

from typing import cast

from pysimmods.base.config import ModelConfig
from pysimmods.base.types import ModelParams


class PVConfig(ModelConfig):
    """Config parameters of PV plant model.

    Parameters
    ----------
    params : dict
        Contains the configuration of the PV plant. See attribute
        section for more information about the parameters, attributes
        marked with *(Input)* can or must be provided.

    Attributes
    ----------
    a_m2 : float
        (Input) The size of the surface of the PV plant in [m²].
    lat_deg : float, optional
        (Input) The geographical latitude of the plant position in [°].
        Default is the latitude of Oldenburg.
    lon_deg : float, optional
        (Input) The geographical longitude of the plant position in
        [°]. Default is the longitude of Oldenburg.
    orient_deg : float, optional
        (Input) The orientation of the plant in [°]. 0° means
        north and 90° means east. Default is 180° (south).
    tilt_deg : float, optional
        (Input) The tilt of the plant in [°]. Default is 30°.
    eta_percent : float, optional
        (Input) The efficiency of the PV plant at reference conditions
        (25°C module temperature, 1000 Watt/m² radiation power)
        including inverter losses, in [%]. Default is 25%.
    beta_percent_per_kelvin : float, optional
        (Input) The efficiency losses caused by module temperature
        exceeding the reference temperature of 25°C, in [%/K]. Default
        is 0.29.
    k_m_w_per_m2 : float, optional
        (Input) The half-saturation constant to the Michaelis-Menten
        saturation curve which is used to model the irradiance
        dependency of the PV plant efficiency in [W/m²]. Default is 50.
    alpha_w_per_m2_kelvin : float, optional
        (Input) The heat transmission coefficient between the PV plant
        and the air in [W/(m²K)]. Heat exchange is assumed to take only
        place on the top side of the PV plant. Default is 11.
    rho_kg_per_m2 : float, optional
        (Input) The mass per unit area of the PV plant in [kg/m²].
        Default is 15.
    reflex_percent : float, optional
        (Input) The reflexiveness of the surface area of the PV plant
        in [%]. Reflexiveness is assumed to be independent from angle
        of incidence. Default is 5.
    c_j_per_kw_kelvin : float, optional
        (Input) The specific heat capacity of the PV plant in [J/kg K].
        Default is 900.
    is_static_t_module : bool, optional
        If set to true the module temperature is kept constant
        during simulation at the temperature the initial temperature
        (see :class:`~.PVState`). Default is False.
    has_external_irradiance_model : bool, optional
        If set to True, an external irradiance model is assumed and
        instead for :attr:`~.PVInputs.bh_w_per_m2` and
        :attr:`~.PVInputs.dh_w_per_m2` input for
        :attr:`~.PVInputs.s_module_w_per_m2` has to be provided,
        default is False.
    p_peak_kw : float
        Peak power of the PV plant in [kW], measured under standard
        testing conditions (module temperature 25°C, irradiance 1000 W)

    """

    def __init__(self, params: ModelParams):
        super().__init__(params)
        self.a_m2: float = cast("float", params["a_m2"])

        self.lat_deg: float = cast("float", params.get("lat_deg", 53.143890))
        self.lon_deg: float = cast("float", params.get("lon_deg", 8.213889))
        self.orient_deg: float = cast("float", params.get("orient_deg", 180))
        self.tilt_deg: float = cast("float", params.get("tilt_deg", 30))
        self.eta_percent: float = cast("float", params.get("eta_percent", 25))
        self.beta_percent_per_kelvin: float = cast(
            "float", params.get("beta_percent_per_kelvin", 0.29)
        )
        self.k_m_w_per_m2: float = cast(
            "float", params.get("k_m_w_per_m2", 50)
        )
        self.alpha_w_per_m2_kelvin: float = cast(
            "float", params.get("alpha_w_per_m2_kelvin", 11)
        )
        self.rho_kg_per_m2: float = cast(
            "float", params.get("rho_kg_per_m2", 15)
        )
        self.reflex_percent: float = cast(
            "float", params.get("reflex_percent", 5)
        )
        self.c_j_per_kg_kelvin: float = cast(
            "float", params.get("c_j_per_kg_kelvin", 900)
        )
        self.is_static_t_module: bool = cast(
            "bool", params.get("is_static_t_module", False)
        )
        self.has_external_irradiance_model: bool = cast(
            "bool", params.get("has_external_irradiance_model", False)
        )

        self.p_max_kw: float = self.eta_percent / 100 * self.a_m2
        self.p_min_kw: float = 0
        self.max_step_size: int = 300
        self.default_p_schedule = None
        self.default_q_schedule = None
