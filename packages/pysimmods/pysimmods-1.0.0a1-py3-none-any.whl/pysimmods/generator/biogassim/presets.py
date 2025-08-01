"""This module contains multiple configuration examples for the
biogas plant.

"""

from pathlib import Path
from typing import cast

import numpy as np
import pandas as pd

from pysimmods.base.types import ModelInitVals, ModelParams
from pysimmods.generator.chpcngsim.presets import (
    chpcng_preset,
    chpcng_preset_by_name,
)

BASE_DATA = (Path(__file__) / ".." / "base_data.csv").resolve()


def biogas_preset(
    pn_max_kw: float,
    randomize_params: bool = False,
    randomize_inits: bool = False,
    seed: int | None = None,
    **kwargs,
) -> tuple[ModelParams, ModelInitVals]:
    """Return the parameter configuration for a biogas model from the
    pysimmods package.

    """
    rng = np.random.default_rng(seed)

    all_params, data = _read_all_params()
    if randomize_params:
        params = {}

        params["gas_fill_min_percent"] = rng.uniform(
            data["gas_fill_min_percent"].min(),
            data["gas_fill_min_percent"].max(),
        )
        params["gas_fill_max_percent"] = rng.uniform(
            data["gas_fill_max_percent"].min(),
            data["gas_fill_max_percent"].max(),
        )
        params["ch4_concentration_percent"] = rng.uniform(
            data["ch4_concentration_percent"].min(),
            data["ch4_concentration_percent"].max(),
        )
        params["num_chps"] = int(rng.integers(1, 6))
        params["has_heat_storage"] = params["num_chps"] == 1

    else:
        closest_name = ""
        closest_distance = 2**32 - 1
        for n, params in all_params.items():
            pn_kw = int(n.split("_")[1].split("k")[0])
            dist = abs(pn_max_kw - pn_kw)
            if dist < closest_distance:
                closest_distance = dist
                closest_name = n

        params = all_params[closest_name]

    if randomize_inits:
        inits: ModelInitVals = {
            "gas_fill_percent": rng.uniform(
                cast("float", params["gas_fill_min_percent"]),
                cast("float", params["gas_fill_max_percent"]),
            )
        }
    else:
        inits: ModelInitVals = {"gas_fill_percent": 50.0}

    if randomize_params:
        chp_powers = _generate_split(rng, pn_max_kw, params["num_chps"])
        max_gas_con = 0.0
        for i, p in enumerate(chp_powers):
            cp, ci = chpcng_preset(
                p, randomize_params, randomize_inits, rng.integers(2**32 - 1)
            )
            cname = f"chp{i}"
            params[cname] = cp
            inits[cname] = ci
            max_gas_con += p / (
                cast("list[float]", cp["eta_stages_percent"])[-1]
                * 0.01
                * 9.94
                * cast("float", params["ch4_concentration_percent"])
                * 0.01
            )
        gas_cap_to_prod_ratio = rng.uniform(
            data["gas_cap_to_prod_ratio"].min(),
            data["gas_cap_to_prod_ratio"].max(),
        )
        gas_prod_to_con_ratio = rng.uniform(0.5, 0.8)
        params["gas_m3_per_day"] = int(
            max_gas_con * gas_prod_to_con_ratio * 24
        )
        params["cap_gas_m3"] = int(
            params["gas_m3_per_day"] * gas_cap_to_prod_ratio
        )
    else:
        max_gas_con = 0.0
        for i in range(3):
            cname = f"chp{i}"
            if cname not in params:
                break
            cp, ci = chpcng_preset_by_name(
                cast("str", params[cname]),
                randomize_inits,
                rng.integers(2**32 - 1),
            )
            params[cname] = cp
            inits[cname] = ci
            max_gas_con += cast("list[float]", cp["pn_stages_kw"])[-1] / (
                cast("list[float]", cp["eta_stages_percent"])[-1]
                * 0.01
                * 9.94
                * cast("float", params["ch4_concentration_percent"])
                * 0.01
            )

    params["sign_convention"] = "active"

    return params, inits


def _read_all_params() -> tuple[dict[str, ModelParams], pd.DataFrame]:
    data = pd.read_csv(BASE_DATA)
    all_params: dict[str, ModelParams] = {}

    for i, row in data.iterrows():
        p_kw = float(cast("str", row["name"]).split("_")[1].split("k")[0])
        data.at[i, "pn_kw"] = p_kw
        params: ModelParams = {
            "gas_m3_per_day": cast("float", row["gas_m3_per_day"]),
            "cap_gas_m3": cast("float", row["cap_gas_m3"]),
            "gas_fill_min_percent": cast("float", row["gas_fill_min_percent"]),
            "gas_fill_max_percent": cast("float", row["gas_fill_max_percent"]),
            "ch4_concentration_percent": cast(
                "float", row["ch4_concentration_percent"]
            ),
        }
        for j in range(3):
            name = row[f"chp{j}"]
            if isinstance(name, str):
                params[f"chp{j}"] = name
                params["num_chps"] = j + 1
            else:
                break
        all_params[cast("str", row["name"])] = params
    data["gas_cap_to_prod_ratio"] = data["cap_gas_m3"] / data["gas_m3_per_day"]
    return all_params, data


def _generate_split(rng: np.random.Generator, total, parts):
    if parts <= 1:
        return [total]

    raw = sorted([float(rng.uniform()) for _ in range(parts)], reverse=True)
    total_weight = sum(raw)
    weights = [w / total_weight for w in raw]

    values = [round(w * total) for w in weights]
    diff = total - sum(values)
    values[-1] += diff
    values.sort(reverse=True)
    return values


# def params_1g_40kw():
#     """Params for a Biogas plant with 40 kw nominal power and
#     one CHP CNG.
#     """
#     return {
#         "gas_m3_per_day": 550,
#         "cap_gas_m3": 250,
#         "gas_fill_min_percent": 2.5,
#         "gas_fill_max_percent": 97.5,
#         "ch4_concentration_percent": 51.9,
#         "num_chps": 1,
#         "chp0": {
#             "pn_stages_kw": [20, 40],
#             "eta_stages_percent": [28.0, 30.0],
#             "eta_th_stages_percent": [31.4, 32.0],
#             "restarts_per_day": 0,
#             "active_min_s": 0,
#             "active_max_s_per_day": 18 * 3_600,
#             "inactive_min_s": 1 * 3_600,
#             "inactive_max_s_per_day": 0,
#         },
#     }


# def inits_1g_40kw():
#     """Init vals for a Biogas plant with 40 kw nominal power and
#     one CHP CNG.
#     """
#     return {
#         "gas_fill_percent": 50.0,
#         "chp0": {
#             "active_s": 0,
#             "active_s_per_day": 0,
#             "inactive_s": 0,
#             "inactive_s_per_day": 0,
#             "restarts": 0,
#             "p_kw": 20,
#         },
#     }


# def params_1g_80kw():
#     """Params for a Biogas plant with 80 kw nominal power and
#     one CHP CNG.
#     """
#     return {
#         "gas_m3_per_day": 750,
#         "cap_gas_m3": 375,
#         "gas_fill_min_percent": 2.5,
#         "gas_fill_max_percent": 97.5,
#         "ch4_concentration_percent": 52.9,
#         "num_chps": 1,
#         "chp0": {
#             "pn_stages_kw": [40, 80],
#             "eta_stages_percent": [37.0, 36.7],
#             "eta_th_stages_percent": [32.4, 32.0],
#             "restarts_per_day": 5,
#             "active_min_s": 0,
#             "active_max_s_per_day": 18 * 3_600,
#             "inactive_min_s": 1 * 3_600,
#             "inactive_max_s_per_day": 0,
#         },
#     }


# def inits_1g_80kw():
#     """Init vals for a Biogas plant with 80 kw nominal power and
#     one CHP CNG.
#     """
#     return {
#         "gas_fill_percent": 50.0,
#         "chp0": {
#             "active_s": 0,
#             "active_s_per_day": 0,
#             "inactive_s": 0,
#             "inactive_s_per_day": 0,
#             "restarts": 0,
#             "p_kw": 40,
#         },
#     }


# def params_1g_320kw():
#     """Params for a Biogas plant with 320 kw nominal power and
#     one CHP CNG.
#     """
#     return {
#         "gas_m3_per_day": 2100,
#         "cap_gas_m3": 2000,
#         "gas_fill_min_percent": 5.0,
#         "gas_fill_max_percent": 95.0,
#         "ch4_concentration_percent": 55.3,
#         "num_chps": 1,
#         "chp0": {
#             "pn_stages_kw": [160, 240, 320],
#             "eta_stages_percent": [36.6, 37.0, 37.5],
#             "eta_th_stages_percent": [31.0, 31.5, 31.9],
#             "restarts_per_day": 0,
#             "active_min_s": 3 * 3_600,
#             "active_max_s_per_day": 0,
#             "inactive_min_s": 1 * 3_600,
#             "inactive_max_s_per_day": 0,
#         },
#     }


# def inits_1g_320kw():
#     """Init vals for a Biogas plant with 320 kw nominal power and
#     one CHP CNG.
#     """
#     return {
#         "gas_fill_percent": 50.0,
#         "chp0": {
#             "active_s": 0,
#             "active_s_per_day": 0,
#             "inactive_s": 0,
#             "inactive_s_per_day": 0,
#             "restarts": 0,
#             "p_kw": 160,
#         },
#     }


# def params_1g_550kw():
#     """Params for a Biogas plant with 550 kw nominal power and
#     one CHP CNG.
#     """
#     return {
#         "gas_m3_per_day": 5450,
#         "cap_gas_m3": 1578,
#         "gas_fill_min_percent": 2.0,
#         "gas_fill_max_percent": 98.0,
#         "ch4_concentration_percent": 55.4,
#         "num_chps": 1,
#         "chp0": {
#             "pn_stages_kw": [275, 330, 440, 550],
#             "eta_stages_percent": [31.6, 31.8, 32.0, 32.2],
#             "eta_th_stages_percent": [41.0, 42.1, 43.2, 44.2],
#             "restarts_per_day": 0,
#             "active_min_s": 3 * 3_600,
#             "active_max_s_per_day": 0,
#             "inactive_min_s": 1 * 3_600,
#             "inactive_max_s_per_day": 0,
#         },
#     }


# def inits_1g_550kw():
#     """Init vals for a Biogas plant with 550 kw nominal power and
#     one CHP CNG.
#     """
#     return {
#         "gas_fill_percent": 50.0,
#         "chp0": {
#             "active_s": 0,
#             "active_s_per_day": 0,
#             "inactive_s": 0,
#             "inactive_s_per_day": 0,
#             "restarts": 0,
#             "p_kw": 275,
#         },
#     }


# def params_1g_373kw():
#     """Params for a Biogas plant with 375 kw nominal power and
#     one CHP CNG.
#     """
#     return {
#         "gas_m3_per_day": 2550,
#         "cap_gas_m3": 2500,
#         "gas_fill_min_percent": 5.0,
#         "gas_fill_max_percent": 95.0,
#         "ch4_concentration_percent": 58.5,
#         "num_chps": 1,
#         "chp0": {
#             "pn_stages_kw": [121, 252, 373],
#             "eta_stages_percent": [33.7, 36.2, 37.9],
#             "eta_th_stages_percent": [45.0, 46.0, 47.8],
#             "restarts_per_day": 6,
#             "active_min_s": 3 * 3_600,
#             "active_max_s_per_day": 0,
#             "inactive_min_s": 1 * 3_600,
#             "inactive_max_s_per_day": 0,
#         },
#     }


# def inits_1g_373kw():
#     """Init vals for a Biogas plant with 373 kw nominal power and
#     one CHP CNG.
#     """
#     return {
#         "gas_fill_percent": 50.0,
#         "chp0": {
#             "active_s": 0,
#             "active_s_per_day": 0,
#             "inactive_s": 0,
#             "inactive_s_per_day": 0,
#             "restarts": 0,
#             "p_kw": 750,
#         },
#     }


# def params_1g_1250kw():
#     """Params for a Biogas plant with 1250 kw nominal power and
#     one CHP CNG.
#     """
#     return {
#         "gas_m3_per_day": 9_750,
#         "cap_gas_m3": 9_250,
#         "gas_fill_min_percent": 2.5,
#         "gas_fill_max_percent": 97.5,
#         "ch4_concentration_percent": 50.0,
#         "num_chps": 1,
#         "chp0": {
#             "pn_stages_kw": [750, 1250],
#             "eta_stages_percent": [37.0, 41.25],
#             "eta_th_stages_percent": [48.0, 44.0],
#             "restarts_per_day": 4,
#             "active_min_s": 0,
#             "active_max_s_per_day": 0,
#             "inactive_min_s": 0,
#             "inactive_max_s_per_day": 0,
#         },
#     }


# def inits_1g_1250kw():
#     """Init vals for a Biogas plant with 1250 kw nominal power and
#     one CHP CNG.
#     """
#     return {
#         "gas_fill_percent": 50.0,
#         "chp0": {
#             "active_s": 0,
#             "active_s_per_day": 0,
#             "inactive_s": 0,
#             "inactive_s_per_day": 0,
#             "restarts": 0,
#             "p_kw": 750,
#         },
#     }


# def params_2g_55kw():
#     """Params for a Biogas plant with 55 kw nominal power and
#     two CHP CNGs.
#     """
#     return {
#         "gas_m3_per_day": 255,
#         "cap_gas_m3": 390,
#         "gas_fill_min_percent": 5.0,
#         "gas_fill_max_percent": 95.0,
#         "ch4_concentration_percent": 50.2,
#         "has_heat_storage": False,
#         "num_chps": 2,
#         "chp0": {
#             "pn_stages_kw": [9.0, 18.0],
#             "eta_stages_percent": [29.3, 28.7],
#             "eta_th_stages_percent": [35.4, 36.1],
#             "restarts_per_day": 0,
#             "active_min_s": 1 * 3_600,
#             "active_max_s_per_day": 0,
#             "inactive_min_s": 0,
#             "inactive_max_s_per_day": 0,
#         },
#         "chp1": {
#             "pn_stages_kw": [18.5, 37.0],
#             "eta_stages_percent": [31.4, 32.5],
#             "eta_th_stages_percent": [36.1, 36.8],
#             "restarts_per_day": 0,
#             "active_min_s": 3 * 3_600,
#             "active_max_s_per_day": 0,
#             "inactive_min_s": 1 * 3_600,
#             "inactive_max_s_per_day": 0,
#         },
#     }


# def inits_2g_55kw():
#     """Init vals for a Biogas plant with 55 kw nominal power and
#     two CHP CNGs.
#     """
#     return {
#         "gas_fill_percent": 50,
#         "chp0": {
#             "active_s": 0,
#             "active_s_per_day": 0,
#             "inactive_s": 0,
#             "inactive_s_per_day": 0,
#             "restarts": 0,
#             "p_kw": 27.5,
#         },
#         "chp1": {
#             "active_s": 0,
#             "active_s_per_day": 0,
#             "inactive_s": 0,
#             "inactive_s_per_day": 0,
#             "restarts": 0,
#             "p_kw": 18.3,
#         },
#     }


# def params_2g_110kw():
#     """Params for a Biogas plant with 110 kw nominal power and
#     two CHP CNGs.
#     """
#     return {
#         "gas_m3_per_day": 950,
#         "cap_gas_m3": 1000,
#         "gas_fill_min_percent": 2.5,
#         "gas_fill_max_percent": 97.5,
#         "ch4_concentration_percent": 56.8,
#         "has_heat_storage": False,
#         "num_chps": 2,
#         "chp0": {
#             "pn_stages_kw": [27.5, 55.0],
#             "eta_stages_percent": [29.7, 31.9],
#             "eta_th_stages_percent": [36.4, 37.0],
#             "restarts_per_day": 6,
#             "active_min_s": 1 * 3_600,
#             "active_max_s_per_day": 0,
#             "inactive_min_s": 0,
#             "inactive_max_s_per_day": 0,
#         },
#         "chp1": {
#             "pn_stages_kw": [18.3, 36.6, 55.0],
#             "eta_stages_percent": [30.8, 32.2, 33.9],
#             "eta_th_stages_percent": [36.1, 36.8, 38.0],
#             "restarts_per_day": 6,
#             "active_min_s": 1 * 3_600,
#             "active_max_s_per_day": 0,
#             "inactive_min_s": 0,
#             "inactive_max_s_per_day": 0,
#         },
#     }


# def inits_2g_110kw():
#     """Init vals for a Biogas plant with 110 kw nominal power and
#     two CHP CNGs.
#     """
#     return {
#         "gas_fill_percent": 50,
#         "chp0": {
#             "active_s": 0,
#             "active_s_per_day": 0,
#             "inactive_s": 0,
#             "inactive_s_per_day": 0,
#             "restarts": 0,
#             "p_kw": 27.5,
#         },
#         "chp1": {
#             "active_s": 0,
#             "active_s_per_day": 0,
#             "inactive_s": 0,
#             "inactive_s_per_day": 0,
#             "restarts": 0,
#             "p_kw": 18.3,
#         },
#     }


# def params_2g_220kw():
#     """Params for a Biogas plant with 220 kw nominal power and
#     two CHP CNGs.
#     """
#     return {
#         "gas_m3_per_day": 2000,
#         "cap_gas_m3": 1150,
#         "gas_fill_min_percent": 2.5,
#         "gas_fill_max_percent": 97.5,
#         "ch4_concentration_percent": 55.7,
#         "has_heat_storage": False,
#         "num_chps": 2,
#         "chp0": {
#             "pn_stages_kw": [55.0, 110.0],
#             "eta_stages_percent": [35.4, 34.7],
#             "eta_th_stages_percent": [31.4, 31.0],
#             "restarts_per_day": 6,
#             "active_min_s": 3 * 3_600,
#             "active_max_s_per_day": 0,
#             "inactive_min_s": 0,
#             "inactive_max_s_per_day": 0,
#         },
#         "chp1": {
#             "pn_stages_kw": [55.0, 110.0],
#             "eta_stages_percent": [35.5, 36.1],
#             "eta_th_stages_percent": [38.0, 42.4],
#             "restarts_per_day": 6,
#             "active_min_s": 3 * 3_600,
#             "active_max_s_per_day": 0,
#             "inactive_min_s": 0,
#             "inactive_max_s_per_day": 0,
#         },
#     }


# def inits_2g_220kw():
#     """Init vals for a Biogas plant with 220 kw nominal power and
#     two CHP CNGs.
#     """
#     return {
#         "gas_fill_percent": 50,
#         "chp0": {
#             "active_s": 0,
#             "active_s_per_day": 0,
#             "inactive_s": 0,
#             "inactive_s_per_day": 0,
#             "restarts": 0,
#             "p_kw": 55.0,
#         },
#         "chp1": {
#             "active_s": 0,
#             "active_s_per_day": 0,
#             "inactive_s": 0,
#             "inactive_s_per_day": 0,
#             "restarts": 0,
#             "p_kw": 55.0,
#         },
#     }


# def params_2g_300kw():
#     """Params for a Biogas plant with 300 kw nominal power and
#     two CHP CNGs.
#     """
#     return {
#         "gas_m3_per_day": 3030,
#         "cap_gas_m3": 1530,
#         "gas_fill_min_percent": 2.0,
#         "gas_fill_max_percent": 98.0,
#         "ch4_concentration_percent": 54.4,
#         "has_heat_storage": False,
#         "num_chps": 2,
#         "chp0": {
#             "pn_stages_kw": [75.0, 150.0],
#             "eta_stages_percent": [31.1, 32.4],
#             "eta_th_stages_percent": [30.8, 31.2],
#             "restarts_per_day": 6,
#             "active_min_s": 3 * 3_600,
#             "active_max_s_per_day": 0,
#             "inactive_min_s": 2 * 3_600,
#             "inactive_max_s_per_day": 0,
#         },
#         "chp1": {
#             "pn_stages_kw": [75.0, 150.0],
#             "eta_stages_percent": [33.0, 33.2],
#             "eta_th_stages_percent": [30.0, 30.5],
#             "restarts_per_day": 6,
#             "active_min_s": 3 * 3_600,
#             "active_max_s_per_day": 0,
#             "inactive_min_s": 2 * 3_600,
#             "inactive_max_s_per_day": 0,
#         },
#     }


# def inits_2g_300kw():
#     """Init vals for a Biogas plant with 300 kw nominal power and
#     two CHP CNGs.
#     """
#     return {
#         "gas_fill_percent": 50,
#         "chp0": {
#             "active_s": 0,
#             "active_s_per_day": 0,
#             "inactive_s": 0,
#             "inactive_s_per_day": 0,
#             "restarts": 0,
#             "p_kw": 75.0,
#         },
#         "chp1": {
#             "active_s": 0,
#             "active_s_per_day": 0,
#             "inactive_s": 0,
#             "inactive_s_per_day": 0,
#             "restarts": 0,
#             "p_kw": 75.0,
#         },
#     }


# def params_2g_320kw():
#     """Params for a Biogas plant with 320 kw nominal power and
#     two CHP CNGs.
#     """
#     return {
#         "gas_m3_per_day": 2050,
#         "cap_gas_m3": 855,
#         "gas_fill_min_percent": 2.0,
#         "gas_fill_max_percent": 98.0,
#         "ch4_concentration_percent": 63.9,
#         "has_heat_storage": False,
#         "num_chps": 2,
#         "chp0": {
#             "pn_stages_kw": [40.0, 80.0, 120.0, 160.0],
#             "eta_stages_percent": [31.1, 32.2, 33.3, 34.4],
#             "eta_th_stages_percent": [30.8, 31.2, 32.3, 32.3],
#             "restarts_per_day": 6,
#             "active_min_s": 3 * 3_600,
#             "active_max_s_per_day": 0,
#             "inactive_min_s": 0,
#             "inactive_max_s_per_day": 0,
#         },
#         "chp1": {
#             "pn_stages_kw": [85.0, 110.0, 135.0, 160.0],
#             "eta_stages_percent": [32.2, 33.0, 33.8, 34.6],
#             "eta_th_stages_percent": [30.0, 30.5, 31.0, 31.5],
#             "restarts_per_day": 6,
#             "active_min_s": 3 * 3_600,
#             "active_max_s_per_day": 0,
#             "inactive_min_s": 0,
#             "inactive_max_s_per_day": 0,
#         },
#     }


# def inits_2g_320kw():
#     """Init vals for a Biogas plant with 320 kw nominal power and
#     two CHP CNGs.
#     """
#     return {
#         "gas_fill_percent": 50,
#         "chp0": {
#             "active_s": 0,
#             "active_s_per_day": 0,
#             "inactive_s": 0,
#             "inactive_s_per_day": 0,
#             "restarts": 0,
#             "p_kw": 80.0,
#         },
#         "chp1": {
#             "active_s": 0,
#             "active_s_per_day": 0,
#             "inactive_s": 0,
#             "inactive_s_per_day": 0,
#             "restarts": 0,
#             "p_kw": 85.0,
#         },
#     }


# def params_2g_2050kw():
#     """Params for a Biogas plant with 2050 kw nominal power and
#     two CHP CNGs.
#     """
#     return {
#         "gas_m3_per_day": 14_500,
#         "cap_gas_m3": 13_000,
#         "gas_fill_min_percent": 5,
#         "gas_fill_max_percent": 95,
#         "ch4_concentration_percent": 50.0,
#         "has_heat_storage": False,
#         "num_chps": 2,
#         "chp0": {
#             "pn_stages_kw": [700, 1150],
#             "eta_stages_percent": [37.0, 44.0],
#             "eta_th_stages_percent": [40.0, 44.0],
#             "restarts_per_day": 4,
#             "active_min_s": 0,
#             "active_max_s_per_day": 16 * 3_600,
#             "inactive_min_s": 2 * 3_600,
#             "inactive_max_s_per_day": 0,
#         },
#         "chp1": {
#             "pn_stages_kw": [600, 900],
#             "eta_stages_percent": [37, 40.0],
#             "eta_th_stages_percent": [42.0, 43.0],
#             "restarts_per_day": 4,
#             "active_min_s": 0,
#             "active_max_s_per_day": 16 * 3_600,
#             "inactive_min_s": 2 * 3_600,
#             "inactive_max_s_per_day": 0,
#         },
#     }


# def inits_2g_2050kw():
#     """Init vals for a Biogas plant with 2050 kw nominal power and
#     two CHP CNGs.
#     """
#     return {
#         "gas_fill_percent": 50,
#         "chp0": {
#             "active_s": 0,
#             "active_s_per_day": 0,
#             "inactive_s": 0,
#             "inactive_s_per_day": 0,
#             "restarts": 0,
#             "p_kw": 700,
#         },
#         "chp1": {
#             "active_s": 0,
#             "active_s_per_day": 0,
#             "inactive_s": 0,
#             "inactive_s_per_day": 0,
#             "restarts": 0,
#             "p_kw": 600,
#         },
#     }


# def params_3g_555kw():
#     """Params for a Biogas plant with 555 kw nominal power and
#     three CHP CNGs.
#     """
#     return {
#         "gas_m3_per_day": 6000,
#         "cap_gas_m3": 2500,
#         "gas_fill_min_percent": 5,
#         "gas_fill_max_percent": 95,
#         "ch4_concentration_percent": 51.6,
#         "has_heat_storage": False,
#         "num_chps": 3,
#         "chp0": {
#             "pn_stages_kw": [125, 250],
#             "eta_stages_percent": [31.2, 34.7],
#             "eta_th_stages_percent": [42.0, 45.9],
#             "restarts_per_day": 0,
#             "active_min_s": 3 * 3_600,
#             "active_max_s_per_day": 18 * 3_600,
#             "inactive_min_s": 1 * 3_600,
#             "inactive_max_s_per_day": 0,
#         },
#         "chp1": {
#             "pn_stages_kw": [125, 250],
#             "eta_stages_percent": [34.3, 36.1],
#             "eta_th_stages_percent": [41.9, 43],
#             "restarts_per_day": 0,
#             "active_min_s": 3 * 3_600,
#             "active_max_s_per_day": 18 * 3_600,
#             "inactive_min_s": 1 * 3_600,
#             "inactive_max_s_per_day": 0,
#         },
#         "chp2": {
#             "pn_stages_kw": [27.5, 55],
#             "eta_stages_percent": [28.6, 30],
#             "eta_th_stages_percent": [35.1, 36.1],
#             "restarts_per_day": 0,
#             "active_min_s": 2 * 3_600,
#             "active_max_s_per_day": 18 * 3_600,
#             "inactive_min_s": 1 * 3_600,
#             "inactive_max_s_per_day": 0,
#         },
#     }


# def inits_3g_555kw():
#     """Init vals for a Biogas plant with 555 kw nominal power and
#     three CHP CNGs.
#     """
#     return {
#         "gas_fill_percent": 50,
#         "chp0": {
#             "active_s": 0,
#             "active_s_per_day": 0,
#             "inactive_s": 0,
#             "inactive_s_per_day": 0,
#             "restarts": 0,
#             "p_kw": 250,
#         },
#         "chp1": {
#             "active_s": 0,
#             "active_s_per_day": 0,
#             "inactive_s": 0,
#             "inactive_s_per_day": 0,
#             "restarts": 0,
#             "p_kw": 125,
#         },
#         "chp2": {
#             "active_s": 0,
#             "active_s_per_day": 0,
#             "inactive_s": 0,
#             "inactive_s_per_day": 0,
#             "restarts": 0,
#             "p_kw": 55,
#         },
#     }


# def params_3g_1500kw():
#     """Params for a Biogas plant with 1500 kw nominal power and
#     three CHP CNGs.
#     """
#     return {
#         "gas_m3_per_day": 16_040,
#         "cap_gas_m3": 25_200,
#         "gas_fill_min_percent": 5,
#         "gas_fill_max_percent": 95,
#         "ch4_concentration_percent": 53.9,
#         "has_heat_storage": False,
#         "num_chps": 3,
#         "chp0": {
#             "pn_stages_kw": [125.0, 250.0, 375.0, 500.0, 625.0, 750.0],
#             "eta_stages_percent": [26.1, 27.0, 27.3, 28.0, 27.7, 27.5],
#             "eta_th_stages_percent": [50.0, 50.2, 50.5, 50.9, 51.0, 52.1],
#             "restarts_per_day": 0,
#             "active_min_s": 3 * 3_600,
#             "active_max_s_per_day": 0,
#             "inactive_min_s": 1 * 3_600,
#             "inactive_max_s_per_day": 0,
#         },
#         "chp1": {
#             "pn_stages_kw": [330.0, 440.0, 550],
#             "eta_stages_percent": [27.9, 28.5, 29.1],
#             "eta_th_stages_percent": [45.9, 47.3, 51.0],
#             "restarts_per_day": 0,
#             "active_min_s": 1 * 3_600,
#             "active_max_s_per_day": 0,
#             "inactive_min_s": 0,
#             "inactive_max_s_per_day": 0,
#         },
#         "chp2": {
#             "pn_stages_kw": [100, 200],
#             "eta_stages_percent": [28.8, 29.9],
#             "eta_th_stages_percent": [29.7, 30.1],
#             "restarts_per_day": 0,
#             "active_min_s": 0,
#             "active_max_s_per_day": 0,
#             "inactive_min_s": 1 * 3_600,
#             "inactive_max_s_per_day": 0,
#         },
#     }


# def inits_3g_1500kw():
#     """Init vals for a Biogas plant with 1500 kw nominal power and
#     three CHP CNGs.
#     """
#     return {
#         "gas_fill_percent": 50,
#         "chp0": {
#             "active_s": 0,
#             "active_s_per_day": 0,
#             "inactive_s": 0,
#             "inactive_s_per_day": 0,
#             "restarts": 0,
#             "p_kw": 125.0,
#         },
#         "chp1": {
#             "active_s": 0,
#             "active_s_per_day": 0,
#             "inactive_s": 0,
#             "inactive_s_per_day": 0,
#             "restarts": 0,
#             "p_kw": 330,
#         },
#         "chp2": {
#             "active_s": 0,
#             "active_s_per_day": 0,
#             "inactive_s": 0,
#             "inactive_s_per_day": 0,
#             "restarts": 0,
#             "p_kw": 100,
#         },
#     }
