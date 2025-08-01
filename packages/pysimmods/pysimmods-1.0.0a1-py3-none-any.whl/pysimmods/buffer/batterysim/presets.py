"""Presets for the battery model."""

from typing import Any

import numpy as np

from pysimmods.base.types import ModelInitVals, ModelParams


def battery_preset(
    pn_max_kw: float,
    cap_kwh: float | None = None,
    soc_percent: float = 50.0,
    soc_min_percent: float = 15.0,
    pn_to_cap_ratio: float = 5.0,
    randomize_params: bool = False,
    randomize_inits: bool = False,
    randomize_eta_pc: bool = False,
    seed: int | None = None,
    **kwargs: dict[str, Any],
) -> tuple[ModelParams, ModelInitVals]:
    rng = np.random.default_rng(seed)
    if randomize_params:
        pn_to_cap_ratio = rng.uniform(1.0, 10.0)
        p_charge_max_kw = pn_max_kw * rng.uniform(0.5, 1.0)
        p_discharge_max_kw = pn_max_kw * rng.uniform(0.5, 1.0)
        soc_min_percent = rng.uniform(0.0, 25.0)
    else:
        p_charge_max_kw = pn_max_kw
        p_discharge_max_kw = pn_max_kw

    eta_pc = [-2.109566, 0.403556, 97.110770]

    if randomize_eta_pc:
        eta_pc = [pc * rng.uniform(0.9, 1.1) for pc in eta_pc]

    if cap_kwh is None:
        cap_kwh = pn_max_kw * pn_to_cap_ratio

    params: ModelParams = {
        "cap_kwh": cap_kwh,
        "soc_min_percent": soc_min_percent,
        "p_charge_max_kw": p_charge_max_kw,
        "p_discharge_max_kw": p_discharge_max_kw,
        "eta_pc": eta_pc,
    }

    if randomize_inits:
        soc_percent = rng.uniform(soc_min_percent, 100.0)

    inits: ModelInitVals = {"soc_percent": soc_percent}

    return params, inits
