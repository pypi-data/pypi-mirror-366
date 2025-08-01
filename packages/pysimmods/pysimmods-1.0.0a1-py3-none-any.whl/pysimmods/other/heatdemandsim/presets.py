"""Contains the preset function for thermal household profiles

:constant CHP_AVERAGE_RUNTIME:
    source: 'IHK Projekte Hannover, Blockheizkraftwerke,
    Seite 5 IHK Projekte Durschnittliche Betriebsstunden
    eines BHKWs'
:constant CHP_MIN_TH_CONS_COEF:
    source: 'IHK Projekte Hannover, Blockheizkraftwerke,
    Seite 5 Prozentzahl für die untere minimale thermische
    Leistung des Jahresverbrauchs eines Householdtypes'
:constant CHP_MAX_TH_CONS_COEF:
    source: 'IHK Projekte Hannover, Blockheizkraftwerke,
    Seite 5 Prozentzahl für die obere maximale thermische
    Leistung des Jahresverbrauchs eines Householdtypes'
:constant DEGREE_OF_EFFIENCY:
    source: 'Niedertemperatur- und Brennwertkessel.
    Wissenswertes über moderne Zentralheizungsanlagen.
    Hessisches Ministerium für Umwelt, Energie,
    Landwirtschaft und Verbraucherschutz. 2011'

"""

from types import FunctionType
from typing import Any, cast

import numpy as np

from pysimmods.base.types import ModelInitVals, ModelParams
from pysimmods.other.heatdemandsim.util import hprofiles

CHP_AVERAGE_RUNTIME = 5_000.0
CHP_MIN_TH_CONS_COEF = 1.0
CHP_MAX_TH_CONS_COEF = 1.5
# DEGREE_OF_EFFIENCY = 0.93


def heatdemand_preset(
    pn_th_kw: float, seed: int | None = None, **kwargs: dict[str, Any]
) -> tuple[ModelParams, ModelInitVals]:
    rng = np.random.default_rng(seed)

    profile = find_demand_profile(rng, pn_th_kw)

    # Adapt the consumer constant of the household, so that power
    # and consumption better fit to each other
    profile["consumer_constant"] = pn_th_kw * 24 * 2 / 3
    inits: ModelInitVals = {
        "t_last_3_deg_celsius": 0.0,
        "t_last_2_deg_celsius": 0.0,
        "t_last_1_deg_celsius": 0.0,
    }
    return profile, inits


def demand_profiles() -> dict[str, ModelParams]:
    """Load heat demand profiles into global store."""

    profiles = {}
    for name, func in hprofiles.__dict__.items():
        if "__" not in name and isinstance(func, FunctionType):
            profiles[name] = func()

    return profiles


def find_demand_profile(
    rng: np.random.Generator, chp_p_th_kw: float
) -> ModelParams:
    """Find heat demand profile based on thermal power supply."""
    min_consumption = {}
    max_consumption = {}
    profiles = demand_profiles()
    for key, val in profiles.items():
        # average annual consumption per average operating
        # hours of the chp
        consumption = (
            cast("float", val["consumer_constant"]) * 365 / CHP_AVERAGE_RUNTIME
        )
        # calculate lower power boundary
        min_consumption[key] = consumption * CHP_MIN_TH_CONS_COEF
        # calculate upper power boundary
        max_consumption[key] = consumption * CHP_MAX_TH_CONS_COEF

    possible_profiles = []
    distances = {}

    # Look for fitting households
    for key, val in profiles.items():
        if abs(chp_p_th_kw >= min_consumption[key]) and abs(
            chp_p_th_kw <= max_consumption[key]
        ):
            # Profile fits optimally
            possible_profiles.append(key)
            distances[key] = 0.0
        else:
            # Profile does not fit, calculate difference
            lower = abs(abs(chp_p_th_kw) - min_consumption[key])
            upper = abs(abs(chp_p_th_kw) - max_consumption[key])
            distances[key] = lower if lower < upper else upper

    if len(possible_profiles) == 1:
        # Exactly one matching profile
        demand_profile = profiles[possible_profiles[0]].copy()
    elif len(possible_profiles) > 1:
        # More than one matching profile, select randomly
        demand_profile = profiles[rng.choice(possible_profiles)].copy()
    else:
        # No matching profile, select the nearest one

        min_type = "one_family"
        min_val = float("Inf")

        for key, val in distances.items():
            if val < min_val:
                min_val = val
                min_type = key

        demand_profile = profiles[min_type].copy()
    return demand_profile
