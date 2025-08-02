M_AIR_KG_PER_MOL: float = 0.029
ACCELERATION_GRAVITY_M_PER_S2: float = 9.81
GAS_CONSTANT_J_PER_MOL_K: float = 8.314
GAS_CONSTANT_J_PER_KG_K: float = 287.058
T_0_DEGREE_KELVIN: float = 288.15
P_0_HPA: float = 1013.25
P_GRADIENT_HPA_PER_M: float = 1 / 8
AIR_DENSITY_KG_PER_M3: float = 1.225


def barometric(
    pressure_hpa: float,
    t_air_hub_deg_kelvin: float,
    data_height_m: float,
    target_height_m: float,
) -> float:
    """Calculate pressure at altitude h using barometric height equation.

    The barometric height equation to calculate the air density at hub
    height using pressure and temperature at hub height.
    Uses an air density constant of 1.225 [kg/m^3] and the default
    pressure of 1013.25 [hPa].

    Parameters
    ----------
    pressure_hpa: float
        The air pressure that was measured in [hPa].
    t_air_hub_deg_kelvin: float
        The air temperature at altitude in [°K].
    data_height_m: float
        The height in which the data was measured in [m].
    target_height_m: float
        The height for which the pressure should be calculated in [m].

    Returns
    -------
    float
        The air pressure at altitude `target_height_m`.

    """

    return (
        pressure_correction(pressure_hpa, data_height_m, target_height_m)
        * AIR_DENSITY_KG_PER_M3
        * T_0_DEGREE_KELVIN
        / (P_0_HPA * t_air_hub_deg_kelvin)
    )


def ideal_gas(
    pressure_hpa: float,
    t_air_hub_deg_kelvin: float,
    data_height_m: float,
    target_height_m: float,
) -> float:
    """Calculate air pressure using ideal gas method.

    The barometric height equation to calculate the air density at hub
    height using pressure and Temperature at hub height
    gas constant of dry air (287.058 J/(kg*K))

    Returns
    -------
    float
        Air density at `target_height_m` in [hPa].
    """

    return (
        pressure_correction(pressure_hpa, data_height_m, target_height_m)
        / (GAS_CONSTANT_J_PER_KG_K * t_air_hub_deg_kelvin)
        * 100
    )


def pressure_correction(
    pressure_hpa: float, data_height_m: float, target_height_m: float
) -> float:
    """Calculate pressure correction based on a gradient.

    The gradient is assumed to be 1/8 hPa/m.

    Parameters
    ----------
    pressure_hpa: float
        The measured air pressure in [hPa].
    data_height_m: float
        Height in which the data was measured in [m].
    target_height_m: float
        Height for which the pressure should be calculated in [m].

    """
    return (
        pressure_hpa - (target_height_m - data_height_m) * P_GRADIENT_HPA_PER_M
    )
