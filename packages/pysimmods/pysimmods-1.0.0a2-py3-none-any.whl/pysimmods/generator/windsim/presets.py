"""This module contains multiple configuration examples for
wind_turbines with different nominal power.

"""

import csv
import logging
import os
from typing import cast

import numpy as np

from pysimmods.base.types import ModelInitVals, ModelParams

LOG = logging.getLogger(__name__)


def wind_preset(
    pn_max_kw: float,
    wind_profile: str = "hellmann",
    temperature_profile: str = "linear_gradient",
    air_density_profile: str = "barometric",
    power_method: str = "power_curve",
    turbine_type: str | None = None,
    randomize_params: bool = False,
    seed: int | None = None,
    **kwargs,
) -> tuple[ModelParams, ModelInitVals]:
    """Return the parameter configuration for a turbine model"""

    rng = np.random.default_rng(seed)
    data = load_static_data()

    if wind_profile not in ["hellmann", "logarithmic"]:
        wind_profile = "hellmann"

    if temperature_profile not in ["linear_gradient", "no_profile"]:
        temperature_profile = "linear_gradient"

    if air_density_profile not in ["barometric", "ideal_gas", "no_profile"]:
        air_density_profile = "barometric"

    if power_method not in ["power_curve", "power_coefficient"]:
        power_method = "power_curve"

    params: ModelParams = {}
    # Check if a matching model already exists
    if (
        turbine_type is not None
        and turbine_type in data
        and (
            power_method == "power_curve"
            and data[turbine_type]["has_power_curve"]
            or power_method == "power_coefficient"
            and data[turbine_type]["has_power_coefficient"]
        )
    ):
        params = cast("ModelParams", data[turbine_type])

    if not params:
        # No matching model found. Looking for the closest
        # model
        possible_pn = {}
        for ttype, values in data.items():
            possible_pn.setdefault(values["pn_max_kw"], [])
            if power_method == "power_curve" and values["has_power_curve"]:
                possible_pn[values["pn_max_kw"]].append(ttype)
            if (
                power_method == "power_coefficient"
                and values["has_power_coefficient"]
            ):
                possible_pn[values["pn_max_kw"]].append(ttype)

        if pn_max_kw in possible_pn:
            # A model for the given nominal power exists
            if len(possible_pn[pn_max_kw]) == 1:
                params = data[possible_pn[pn_max_kw][0]]
            else:
                if (
                    turbine_type is not None
                    and turbine_type in possible_pn[pn_max_kw]
                ):
                    params = data[turbine_type]
                elif randomize_params:
                    rnd = str(rng.choice(possible_pn[pn_max_kw]))
                    params = cast("ModelParams", data[rnd])
                else:
                    params = data[possible_pn[pn_max_kw][0]]
        else:
            # No model for the given nominal power exists
            # Look for the closest one and scale the power
            # values.
            p_lower = 0
            lower_diff = 0
            p_higher = 0
            higher_diff = 0
            for pn, ttypes in possible_pn.items():
                if not ttypes:
                    continue
                if pn < pn_max_kw:
                    p_lower = pn
                    lower_diff = pn_max_kw - pn
                if pn > pn_max_kw:
                    p_higher = pn
                    higher_diff = pn - pn_max_kw
                    break
            if (
                lower_diff < higher_diff
                and p_lower in possible_pn
                or lower_diff > higher_diff
                and p_higher not in possible_pn
            ):
                params = cast("ModelParams", data[possible_pn[p_lower][0]])

            else:
                params = data[possible_pn[p_higher][0]]
            params["pn_max_kw"] = pn_max_kw

    if power_method == "power_curve":
        params["power_curve_m"] = [
            v * 1000 * pn_max_kw
            for v in cast("list[float]", params["power_curve"])
        ]

    if randomize_params:
        h_min = cast("int", params["height_min_m"])
        h_max = cast("int", params["height_max_m"])
        params["hub_height_m"] = int(rng.integers(h_min, h_max))
    else:
        params["hub_height_m"] = params["height_min_m"]

    params["sign_convention"] = "active"
    params["method"] = power_method
    params["wind_profile"] = wind_profile
    params["temperature_profile"] = temperature_profile
    params["air_density_profile"] = air_density_profile
    return params, {}


def load_static_data():
    data_path = os.path.abspath(
        os.path.join(__file__, "..", "static_data.csv")
    )
    curves_path = os.path.abspath(
        os.path.join(__file__, "..", "static_curves.csv")
    )
    data = {}
    cols = []
    with open(data_path, "r") as csvfile:
        reader = csv.reader(csvfile)
        for idx, row in enumerate(reader):
            if idx == 0:
                cols = row
            else:
                key = row[0]
                data[key] = {}
                for k, v in zip(cols, row):
                    try:
                        v = int(v)
                    except ValueError:
                        try:
                            v = float(v)
                        except ValueError:
                            if v == "false":
                                v = False
                            elif v == "true":
                                v = True
                    data[key][k] = v
    with open(curves_path, "r") as csvfile:
        reader = csv.reader(csvfile)
        for idx, row in enumerate(reader):
            if idx == 0:
                cols = row
            else:
                key = row[0]
                ts_type = row[1]
                ts = []
                for v in row[2:]:
                    ts.append(float(v))
                data[key][ts_type] = ts
    return data
