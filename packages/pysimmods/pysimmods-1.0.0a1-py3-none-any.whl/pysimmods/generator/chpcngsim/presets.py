"""This module provides configurations for CHP CNGs.

The CHP Compressed Natural Gas are used by the Biogas model.
The configurations are derived from ... (TODO).

"""

from pathlib import Path
from typing import Any, cast

import numpy as np
import pandas as pd

from pysimmods.base.types import ModelInitVals, ModelParams

BASE_DATA = (Path(__file__) / ".." / "base_data.csv").resolve()


def chpcng_preset(
    pn_max_kw: float,
    randomize_params: bool = False,
    randomize_inits: bool = False,
    seed: int | None = None,
    **kwargs: dict[str, Any],
) -> tuple[ModelParams, ModelInitVals]:
    rng = np.random.default_rng(seed)
    all_params = _read_all_params()

    if randomize_params:
        # "Magic values" derived from base_data.csv
        active_max = max(0, int(rng.integers(18) - 12))
        if active_max > 0:
            active_max = (active_max + 12) * 3600
        params: ModelParams = {
            "restarts_per_day": max(0, int(rng.integers(-6, 6))),
            "active_min_s": max(0, int(rng.integers(-3, 3))) * 3600,
            "active_max_s_per_day": active_max,
            "inactive_min_s": max(0, int(rng.integers(-2, 2))) * 3600,
            "inactive_max_s_per_day": 0,
        }
        n_stages = int(rng.integers(2, 7))
        min_ratio = float(rng.uniform(0.3, 0.6))
        pn_min_kw = pn_max_kw * min_ratio
        step_size = (pn_max_kw - pn_min_kw) / (n_stages - 1)
        eta_min = float(rng.uniform(25.0, 40.0))
        eta_max = float(rng.uniform(eta_min, max(eta_min + 2, 45.0)))
        eta_step_size = (eta_max - eta_min) / (n_stages - 1)
        eta_th_min = float(rng.uniform(28.0, 50.0))
        eta_th_max = float(rng.uniform(eta_th_min, max(eta_th_min + 2, 55.0)))
        eta_th_step_size = (eta_th_max - eta_th_min) / (n_stages - 1)

        pn_stages: list[float] = []
        eta_stages: list[float] = []
        eta_th_stages: list[float] = []
        for i in range(n_stages):
            pn_stages.append(pn_min_kw + i * step_size)
            eta_stages.append(
                eta_min + i * eta_step_size * rng.uniform(0.5, 2.5)
            )
            eta_th_stages.append(
                eta_th_min + i * eta_th_step_size * rng.uniform(0.5, 2.5)
            )
        params["pn_stages_kw"] = pn_stages
        params["eta_stages_percent"] = eta_stages
        params["eta_th_stages_percent"] = eta_th_stages

    else:
        closest_name = ""
        closest_distance = 2**32 - 1
        for n, params in all_params.items():
            dist = abs(
                pn_max_kw - cast("list[float]", params["pn_stages_kw"])[-1]
            )

            if dist < closest_distance:
                closest_distance = dist
                closest_name = n
        params = all_params[closest_name]

    return params, _build_inits(
        params, randomize_inits, int(rng.integers(2**32 - 1))
    )


def chpcng_preset_by_name(
    name: str, randomize_inits: bool = False, seed: int | None = None, **kwargs
) -> tuple[ModelParams, ModelInitVals]:
    params = _read_all_params()[name]

    return params, _build_inits(params, randomize_inits, seed)


def _read_all_params() -> dict[str, ModelParams]:
    data = pd.read_csv(BASE_DATA)

    all_params = {}

    for _, row in data.iterrows():
        params = {
            "restarts_per_day": cast("int", row["restarts_per_day"]),
            "active_min_s": cast("int", row["active_min_s"]),
            "active_max_s_per_day": cast("int", row["active_max_s_per_day"]),
            "inactive_min_s": cast("int", row["inactive_min_s"]),
            "inactive_max_s_per_day": cast(
                "int", row["inactive_max_s_per_day"]
            ),
            "pn_stages_kw": [],
            "eta_stages_percent": [],
            "eta_th_stages_percent": [],
        }
        for j in range(6):
            pn_kw = cast("float", row[f"pn_{j:02d}"])
            if pd.isnull(pn_kw):
                break
            params["pn_stages_kw"].append(pn_kw)
            params["eta_stages_percent"].append(
                cast("float", row[f"eta_{j:02d}"])
            )
            params["eta_th_stages_percent"].append(
                cast("float", row[f"eta_th_{j:02d}"])
            )
        all_params[row["name"]] = params

    return all_params


def _build_inits(
    params: ModelParams, randomize_inits: bool = False, seed: int | None = None
) -> ModelInitVals:
    rng = np.random.default_rng(seed)
    if randomize_inits:
        inits: ModelInitVals = {
            "active_s": max(
                0, int(rng.integers(-1, cast("int", params["active_min_s"])))
            ),
            "active_s_per_day": max(
                0,
                int(
                    rng.integers(
                        -1, cast("int", params["active_max_s_per_day"])
                    )
                ),
            ),
            "inactive_s": max(
                0, int(rng.integers(-1, cast("int", params["inactive_min_s"])))
            ),
            "inactive_s_per_day": 0,
            "restarts": max(
                0,
                int(rng.integers(-1, cast("int", params["restarts_per_day"]))),
            ),
            "p_kw": float(
                rng.choice(cast("list[float]", params["pn_stages_kw"]))
            ),
        }
    else:
        inits: ModelInitVals = {
            "active_s": 0,
            "active_s_per_day": 0,
            "inactive_s": 0,
            "inactive_s_per_day": 0,
            "restarts": 0,
            "p_kw": cast("list[float]", params["pn_stages_kw"])[0],
        }

    return inits
