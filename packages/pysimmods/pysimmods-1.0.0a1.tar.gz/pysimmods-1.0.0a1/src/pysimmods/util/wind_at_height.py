import numpy as np


def logarithmic_profile(
    wind_v_m_per_s: float,
    wind_height_m: float,
    hub_height_m: float,
    roughness_length_m: float = 0.15,
    obstacle_height_m: float = 0.0,
) -> float:
    """Calculate wind speed at altitude using logarithm.

    Parameters
    ----------
    wind_v_m_per_s: float
        The measured wind speed in [m/s].
    wind_height_m: float
        The height on which the wind speed was measured in [m].
    hub_height_m: float
        The height for which the wind speed should be calculated in [m].
    roughness_length_m: float
        Length of roughness in [m].
    obstacle_height_m: float
        Height of obstacles that affect wind speed in [m].

    Parameters
    ----------
    float
        Wind speed at altitude `hub_height_m`.

    """
    return (
        wind_v_m_per_s
        * np.log((hub_height_m - 0.7 * obstacle_height_m) / roughness_length_m)
        / np.log(
            (wind_height_m - 0.7 * obstacle_height_m) / roughness_length_m
        )
    )


def hellmann(
    wind_v_m_per_s: float,
    wind_height_m: float,
    hub_height_m: float,
    hellman_exponent: float = 1 / 7,
) -> float:
    """Calculate wind speed at altitude using hellmann formula

    Parameters
    ----------
    wind_v_m_per_s: float
        The measured wind speed in [m/s].
    wind_height_m: float
        The height on which the wind speed was measured in [m].
    hub_height_m: float
        The height for which the wind speed should be calculated in [m].
    hellmann_exponent: float
        The hellmann exponent for this calculation, defaults to 1/7.

    Returns
    -------
    float
        Wind speed at altitude `hub_height_m`.
    """
    return wind_v_m_per_s * (hub_height_m / wind_height_m) ** hellman_exponent
