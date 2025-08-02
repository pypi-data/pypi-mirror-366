"""This module provides configurations for the HVAC model.

The base formula is derived from the practical training energy
informatics at the University of Oldenburg. There is a frigde model
with 80 Watts and an air conditioning with 2 Kilowatts. To use one of
those, you can do it like this::

    params, inits = hvac_preset(0.08)  # for the fridge
    params, inits = hvac_preset(2)  # for the air conditioning

Additional, configurations for "TK-Anlagen" were derived from
https://www.tis-gdv.de/tis/tagungen/svt/svt10/weilhart/inhalt-htm/
The modeling of those should be considered as "educated guess" rather
than an acurate modeling. Those are available with different nominal
power values::

    hvac_preset(60)
    hvac_preset(100)
    hvac_preset(232)
    hvac_preset(415)
    hvac_preset(1743)
    hvac_preset(2075)
    hvac_preset(2325)
    hvac_preset(3139)
    hvac_preset(4456)

Choosing any of those will give a solid configuration but it is also
possible to choose any value between; the preset function will
determine the closest configuration to the provided nominal power.
Selecting a value that is located in the middle of two of those values
can lead to a model that has either not enough power or too much power,
resulting in a behavior that is further away from reality.

To overcome this, it is possible create configurations procedurally, by
setting either `randomize_params=True` and/or `randomize_inits=True`.
This will aim to create a configuration that is, even under worst case
conditions, able to provide the necessary power. However there is no
guarantee that cooling house with such a configuration could exist in
reality.

As an example how the calculations for the configuration is done, we
will go through the 60 kW model. All of the following calculations use
rounded values. According to the link above, the facility has an
energetic value of approx. 205 kWh/(m^3*a) and a storage volume of
800 m^3. This results in a total of 164000 kWh/a and 450 kWh/Day.

Now we're assuming that those energy is based on a workload of 33 %,
which means this cooling house could consume up to 1350 kWh/Day and,
consequently, 56.6 kWh/h. This is rounded up to 60 kW. However, since
the nominal power is the provided value, we need to reverse those
calculations to find a suitable configuration for a given power value.

The initialization parameters are derived from the air conditioning
configuration, which assumes 500 kg of oak furniture with a specific
heat capacity of 2390 J/(kg*K). This goes into the equation as
500 kg * 2390 J/(kg*K) = 1195000 J/K.

However, the cooling house does not store oak, but food. Non-frozen
food, e.g., apples, have a specific heat capacity of 3890 J(kg*K).
To get a similar cooling-power relationship, we calculate a
reference mass of 1195000 J/K / 3890 J/(kg*K) = 311 kg, and, sub-
sequently apply the relation of the cooling volume, which is 50 m^3
for the air conditioning and 800 m^3 for the cooling house, i.e.:
311 kg * 800 m^3 / 50 m^3 = 4966 kg of food content (apples, yay ^.^).

The larger cooling houses are determined similar, just assuming
different volumes and energetic values.

"""

from pathlib import Path
from typing import Any, cast

import numpy as np
import pandas as pd

from pysimmods.base.types import ModelInitVals, ModelParams

BASE_DATA = (Path(__file__) / ".." / "base_data.csv").resolve()

PARAM_KEYS = (
    ["eta_percent"]
    + ["length_m", "width_m", "height_m", "isolation_m"]
    + ["lambda_w_per_m_k", "t_min_deg_celsius", "t_max_deg_celsius"]
)
INIT_KEYS = ["c_j_per_kg_k", "theta_t_deg_celsius", "mass_kg"]


def hvac_preset(
    pn_max_kw: float,
    randomize_params: bool = False,
    randomize_inits: bool = False,
    workload: float = 33,
    seed: int | None = None,
    **kwargs,
) -> tuple[ModelParams, ModelInitVals]:
    rng = np.random.default_rng(seed)
    data = pd.read_csv(BASE_DATA)

    data = _compute_dynamic_values(data)

    e_kwh_day = pn_max_kw * 24
    e_kwh_day_workload = e_kwh_day * workload / 100
    e_kwh_year = e_kwh_day_workload * 365

    closest_row = data.iloc[
        (data["energy_kwh_a"] - e_kwh_year).abs().idxmin()
    ].to_dict()

    if randomize_params:
        workload = int(rng.integers(25, 75))
        e_kwh_day_workload = e_kwh_day * workload / 100
        e_kwh_year = e_kwh_day_workload * 365

        energetic_value = float(rng.integers(30, 250))
        volume_m3 = e_kwh_year / energetic_value
        length_m, width_m, height_m = _sample_dimensions(volume_m3, rng)

        params: ModelParams = {
            "p_max_kw": pn_max_kw,
            "length_m": float(length_m),
            "width_m": float(width_m),
            "height_m": float(height_m),
            "isolation_m": float(rng.uniform(0.15, 0.25)),
            "lambda_w_per_m_k": float(rng.uniform(0.1, 0.2)),
            "eta_percent": (1 - (energetic_value / 250)) * 100,
            "t_min_deg_celsius": float(rng.uniform(-40.0, -27.0)),
            "t_max_deg_celsius": float(rng.uniform(-20.0, 17.5)),
        }
    else:
        params: ModelParams = {k: closest_row[k] for k in PARAM_KEYS}
        params["p_max_kw"] = pn_max_kw

    if randomize_inits:
        c_j_per_kg_k = float(rng.uniform(2000, 4000))
        cooling_ref = 2390 * float(rng.uniform(5, 15))
        inits = {
            "c_j_per_kg_k": c_j_per_kg_k,
            "theta_t_deg_celsius": float(
                rng.uniform(
                    cast("float", params["t_min_deg_celsius"]),
                    cast("float", params["t_max_deg_celsius"]),
                )
            ),
            "mass_kg": cooling_ref
            / c_j_per_kg_k
            * cast("float", params["length_m"])
            * cast("float", params["width_m"])
            * cast("float", params["height_m"]),
            "cooling": bool(rng.choice([True, False])),
        }
    else:
        inits = {k: closest_row[k] for k in INIT_KEYS}
        inits["cooling"] = True

    if randomize_params or randomize_inits:
        check_configuration(params, inits)

    return params, inits


def _compute_dynamic_values(data: pd.DataFrame) -> pd.DataFrame:
    data["surface_m2"] = data.eval(
        "2*(length_m*width_m + length_m*height_m + width_m*height_m)"
    )
    data["volume_m3"] = data.eval("length_m * width_m * height_m")
    data["energy_kwh_a"] = data.eval("volume_m3 * energetic_value")
    cooling_ref = 2390 * 500 / 50  # from the 2 kW device
    data["mass_kg"] = cooling_ref / data["c_j_per_kg_k"] * data["volume_m3"]
    data.at[0, "mass_kg"] = 5.0  # The fridge has a different load
    return data


def _sample_dimensions(
    volume_m3: float, rng: np.random.Generator
) -> tuple[float, float, float]:
    # Sample height first, constraint by cube root upper bound
    h_max = volume_m3 ** (1 / 3)
    height_m = rng.uniform(h_max * 0.4, h_max * 0.95)

    # Given height, max width is (volume / height) ** 0.5
    w_max = (volume_m3 / height_m) ** 0.5
    width_m = rng.uniform(height_m, w_max)

    # Given height and width, length is determined
    length_m = volume_m3 / (width_m * height_m)

    return round(length_m, 2), round(width_m, 2), round(height_m, 2)


def check_configuration(params: dict[str, Any], inits: dict[str, Any]):
    alpha = (
        params["lambda_w_per_m_k"]
        * params["length_m"]
        * params["width_m"]
        * params["height_m"]
        / params["isolation_m"]
    )
    eta = params["eta_percent"] / 100
    p = params["p_max_kw"] * 1000
    C = inits["c_j_per_kg_k"]
    m = inits["mass_kg"]

    # calculate temperature change under worst case conditions
    t_diff = 40 - (-22)
    delta_t = ((alpha * t_diff) - eta * p) / (C * m)

    if delta_t > -0.0001:
        # current configuration is not powerful enough to cool
        # down the warehouse
        cool_factor = (alpha * t_diff - (-0.0001) * C * m) / (eta * p)
        params["cool_factor"] = round(cool_factor / 5, 2)
