def linear_gradient(
    t_air_deg_kelvin: float,
    temperature_height_m: float,
    hub_height_m: float,
    gradient: float = 0.0065,
) -> float:
    """Calculate temperature at altitude h using linear gradient.
    
    Parameters
    ----------
    t_air_deg_kelvin: float
        Measured air temperature in [°K]
    temperature_height_m: float
        Height on which temperature was measured in [m].
    hub_height_m: float
        Height for which temperature should be calculated in [m].
    gradient: float
        The gradient used for the calculation.
    
    Returns
    -------
    float
        The temperature at altitude `hub_height_m` in [°K].
    
    """
    return t_air_deg_kelvin - gradient * (hub_height_m - temperature_height_m)
