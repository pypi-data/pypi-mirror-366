"""MIDAS upgrade module for the weather data simulator."""

import logging
from importlib import import_module
from typing import Any, cast

import pandas as pd
from midas.scenario.upgrade_module import ModuleParams, UpgradeModule
from mosaik.exceptions import ScenarioError

from pysimmods.base.types import ModelInitVals, ModelParams
from pysimmods.buffer import battery_preset
from pysimmods.consumer import hvac_preset
from pysimmods.generator import (
    biogas_preset,
    chp_preset,
    pv_preset,
    windsys_preset,
)

from .analysis.analysis import analyze

LOG = logging.getLogger(__name__)


class PysimmodsModule(UpgradeModule):
    """Pysimmods upgrade module for MIDAS."""

    def __init__(self, name="der"):
        super().__init__(
            module_name="der",
            default_scope_name="midasmv",
            default_sim_config_name="Pysimmods",
            default_import_str=(
                "pysimmods.mosaik_bridge.pysim_mosaik:PysimmodsSimulator"
            ),
            default_cmd_str=(
                "%(python)s -m pysimmods.mosaik_bridge.pysim_mosaik %(addr)s"
            ),
            log=LOG,
        )

        self.flex_import_str = (
            "pysimmods.mosaik_bridge.flex_mosaik:FlexibilitySimulator"
        )
        self.flex_cmd_str = (
            "%(python)s -m pysimmods.mosaik_bridge.flex_mosaik %(addr)s"
        )
        self.models = {
            "PV": (
                "Photovoltaic",
                "sgen",
                ["bh_w_per_m2", "dh_w_per_m2", "t_air_deg_celsius"],
                [
                    "p_mw",
                    "q_mvar",
                    "t_module_deg_celsius",
                    "p_possible_max_mw",
                ],
            ),
            "HVAC": (
                "HVAC",
                "load",
                ["t_air_deg_celsius"],
                ["p_mw", "q_mvar", "theta_t_deg_celsius"],
            ),
            "CHP": (
                "CHP",
                "sgen",
                ["day_avg_t_air_deg_celsius"],
                ["p_mw", "q_mvar"],
            ),
            "DIESEL": ("DieselGenerator", "sgen", [], ["p_mw", "q_mvar"]),
            "BAT": (
                "Battery",
                "storage",
                [],
                ["p_mw", "q_mvar", "soc_percent"],
            ),
            "Biogas": ("Biogas", "sgen", [], ["p_mw", "q_mvar"]),
            "Wind": (
                "WindTurbine",
                "sgen",
                ["t_air_deg_celsius", "wind_v_m_per_s", "air_pressure_hpa"],
                ["p_mw", "q_mvar", "p_possible_max_mw"],
            ),
        }
        self.sensors = []
        self.actuators = []
        self._models_started = {}

    def check_module_params(self, mp: ModuleParams):
        """Check the module params and provide default values."""

        mp.setdefault("start_date", self.scenario.base.start_date)
        mp.setdefault("cos_phi", self.scenario.base.cos_phi)
        mp.setdefault("q_control", "prioritize_p")
        mp.setdefault("inverter_mode", "inductive")
        mp.setdefault(
            "forecast_horizon_hours", self.scenario.base.forecast_horizon_hours
        )
        mp.setdefault("pv_is_static_t_module", False)
        mp.setdefault("provide_flexibilities", False)
        mp.setdefault(
            "flexibility_horizon_hours",
            self.scenario.base.flexibility_horizon_hours,
        )
        mp.setdefault(
            "flexibility_horizon_start_hours",
            self.scenario.base.flexibility_horizon_start_hours,
        )
        mp.setdefault("flexibility_frequency", 1)
        mp.setdefault("num_schedules", 10)
        mp.setdefault("unit", "mw")
        mp.setdefault("use_decimal_percent", False)
        mp.setdefault("prioritize_setpoint", False)
        mp.setdefault("provide_forecasts", mp["provide_flexibilities"])
        mp.setdefault("enable_schedules", mp["provide_forecasts"])
        mp.setdefault("pv_send_p_possible_max_mw_to_grid", False)
        mp.setdefault("randomize_params", False)
        mp.setdefault("randomize_inits", False)

    def check_sim_params(self, mp: ModuleParams, **kwargs):
        """Check the params for a certain simulator instance."""
        self.sim_params.setdefault("grid_name", self.scope_name)
        self._simp_from_modulep(mp, "start_date")
        self._simp_from_modulep(mp, "cos_phi", dtype="float")
        self._simp_from_modulep(mp, "q_control")
        self._simp_from_modulep(mp, "inverter_mode")
        self._simp_from_modulep(mp, "pv_is_static_t_module", dtype="bool")
        self._simp_from_modulep(
            mp, "pv_send_p_possible_max_mw_to_grid", dtype="bool"
        )
        self._simp_from_modulep(mp, "forecast_horizon_hours", dtype="float")
        self._simp_from_modulep(mp, "provide_flexibilities", dtype="bool")
        self._simp_from_modulep(mp, "flexibility_horizon_hours", dtype="float")
        self._simp_from_modulep(
            mp, "flexibility_horizon_start_hours", dtype="float"
        )
        self._simp_from_modulep(mp, "flexibility_frequency", dtype="float")
        self._simp_from_modulep(mp, "num_schedules", dtype="int")
        self._simp_from_modulep(mp, "unit")
        self._simp_from_modulep(mp, "use_decimal_percent", dtype="bool")
        self._simp_from_modulep(mp, "prioritize_setpoint", dtype="bool")
        self.sim_params.setdefault(
            "provide_forecasts",
            cast("bool", self.sim_params["provide_flexibilities"])
            or cast("bool", mp["provide_forecasts"]),
        )
        self.sim_params.setdefault(
            "enable_schedules",
            cast("bool", self.sim_params["provide_forecasts"])
            or cast("bool", mp["enable_schedules"]),
        )

        if self.scenario.base.no_rng:
            self.sim_params["seed"] = self.scenario.create_seed()
        else:
            self.sim_params.setdefault("seed", self.scenario.create_seed())

        self._simp_from_modulep(mp, "randomize_params", dtype="bool")
        self._simp_from_modulep(mp, "randomize_inits", dtype="bool")
        if (
            self.sim_params["enable_schedules"]
            or self.sim_params["provide_forecasts"]
            or self.sim_params["provide_flexibilities"]
        ):
            if self.sim_params["cmd"] == "python":
                self.sim_params["import_str"] = self.flex_import_str
            elif self.sim_params["cmd"] == "cmd":
                self.sim_params["import_str"] = self.flex_cmd_str

        self.sensors = []
        self.actuators = []
        self._models_started = {}

    def start_models(self):
        """Start all models defined in the mapping of a certain simulator."""

        self._models_started = {}
        mapping_key = "peak_mapping"
        if not self.sim_params.get(mapping_key, {}):
            if self.sim_params.get("mapping", {}):
                self.sim_params[mapping_key] = self.sim_params.pop("mapping")
            else:
                self.sim_params[mapping_key] = {}

        if not self.sim_params[mapping_key]:
            # No mapping configured
            return

        if ":" in self.default_import_str:
            mod, clazz = self.default_import_str.split(":")
        else:
            mod, clazz = self.default_import_str.rsplit(".", 1)
        mod = import_module(mod)

        sim_dummy = getattr(mod, clazz)()
        sim_dummy.init(self.sid, **self.sim_params)

        eid_mapping = self.scenario.create_shared_mapping(
            self, cast("str", self.sim_params["grid_name"]), "eid"
        )
        try:
            pg_mapping = self.scenario.get_powergrid_mappings(
                cast("str", self.sim_params["grid_name"])
            )
        except Exception:
            LOG.exception(
                "Please update midas-mosaik or powergrid mapping will not "
                "work."
            )
            pg_mapping = {}
        model_ctrs = {}

        for model, info in self.models.items():
            for bus, entities in cast(
                "dict", self.sim_params[mapping_key]
            ).items():
                for name, p_peak_mw in entities:
                    if model != name:
                        continue
                    model_ctrs.setdefault(model, 0)
                    model_key = self.scenario.generate_model_key(
                        self, model.lower(), bus, model_ctrs[model]
                    )
                    params: dict[str, Any] = self.generate_model_params(
                        model_key, model, p_peak_mw
                    )
                    sn_mva = params["params"].get("sn_mva", p_peak_mw)
                    self.start_model(model_key, info[0], params)
                    entity = sim_dummy.create(1, info[0], **params)[0]
                    full_id = f"{self.sid}.{entity['eid']}"
                    p_min, p_max, q_min, q_max = get_space(
                        model.lower(), params, p_peak_mw
                    )

                    eid_mapping[full_id] = {
                        "p_mw": p_peak_mw,
                        "bus": bus,
                        "type": info[1],
                        "sn_mva": sn_mva,
                    }
                    bus_mapping = pg_mapping.setdefault(bus, {})
                    module_mapping = bus_mapping.setdefault(
                        self.module_name, {}
                    )
                    model_mapping = module_mapping.setdefault(model, [])
                    model_mapping.append(model_key)
                    if p_min != p_max:
                        self.actuators.append(
                            create_actuator(full_id, "p_set_mw", p_min, p_max)
                        )
                    if q_min != q_max:
                        self.actuators.append(
                            create_actuator(
                                full_id, "q_set_mvar", q_min, q_max
                            )
                        )
                    # self.actuators.append(
                    #     create_actuator(full_id, "set_percent", 0, high)
                    # )
                    for attr in self.models[model][3]:
                        self.sensors.append(create_sensor(full_id, attr))

                    self._models_started[model_key] = {
                        "bus": bus,
                        "type": info[1],
                        "model": info[0],
                        "alias": model,
                        "inputs": info[2],
                        "outputs": info[3],
                        "model_ctr": model_ctrs[model],
                    }
                    model_ctrs[model] += 1

    def connect(self):
        """Connect the models to existing other models."""

        for model_key, info in self._models_started.items():
            # for model, info in self.models.items():
            self._connect_to_weather(model_key, info)
            try:
                self._connect_to_grid(model_key, info)
            except KeyError:
                LOG.warning(
                    "No grid for %s found. Will output only to database "
                    "(if configured).",
                    self.sim_params["sim_name"],
                )

    def _connect_to_weather(self, model_key, info):
        # mapping_key = "peak_mapping"
        wpm_key = "weather_provider_mapping"
        wfm_key = "weather_forecast_mapping"
        model_ctr = info["model_ctr"]

        if not self.sim_params.get(wpm_key, {}):
            self.sim_params[wpm_key] = self.create_default_wpm()
        self.sim_params.setdefault(wfm_key, {})
        weather_key = self.get_weather_model(info["alias"], model_ctr)

        try:
            self.connect_entities(
                cast("str", weather_key), model_key, info["inputs"]
            )
        except KeyError:
            LOG.warning(
                "Weather mapping missing for %s. The simulation"
                " will fail if the model requires weather input",
                info["model"],
            )

        weather_key = self.get_weather_model(info["alias"], model_ctr, True)
        if weather_key is not None:
            fc_attrs: list[str | tuple[str, str]] = [
                f"forecast_{a}" for a in info[2]
            ]
            self.connect_entities(weather_key, model_key, fc_attrs)

        # model_ctrs[model] += 1

    def _connect_to_grid(self, model_key, info):
        # mapping_key = "peak_mapping"
        # model_ctrs = {}
        # model_ctr = info["model_ctr"]
        # for bus, entities in self.sim_params[mapping_key].items():
        #     for name, _ in entities:
        #         if model != name:
        #             continue

        # model_ctrs.setdefault(model, 0)
        # model_key = self.scenario.generate_model_key(
        #     self, model.lower(), info["bus"], model_ctr
        # )
        attrs = info["outputs"][:2]
        if (
            self.sim_params["pv_send_p_possible_max_mw_to_grid"]
            and info["alias"].lower() == "pv"
        ):
            attrs.append(("p_possible_max_mw", "max_p_mw"))
        grid_entity_key = None
        try:
            grid_entity_key = self.get_grid_entity(info["type"], info["bus"])
            self.connect_entities(model_key, grid_entity_key, attrs)
        except ScenarioError as e:
            LOG.warning(
                "Encountered scenario error while connecting %s"
                "to grid entity %s: %s",
                model_key,
                grid_entity_key,
                e,
            )
        except KeyError as e:
            LOG.warning(
                "Entity missing for %s: %s or for grid: %s (%s).",
                info["alias"],
                model_key,
                grid_entity_key,
                e,
            )
        except ValueError as e:
            LOG.warning(
                "Entity missing for %s: %s or for grid: %s (%s).",
                info["alias"],
                model_key,
                grid_entity_key,
                e,
            )
        # model_ctrs[model] += 1

    def connect_to_db(self):
        """Connect the models to db."""
        mapping_key = "peak_mapping"
        db_key = self.scenario.find_first_model("store", "database")[0]

        model_ctrs = dict()
        for model, info in self.models.items():
            for bus, entities in cast(
                "dict", self.sim_params[mapping_key]
            ).items():
                for name, _ in entities:
                    if model != name:
                        continue

                    model_ctrs.setdefault(model, 0)
                    model_key = self.scenario.generate_model_key(
                        self, model.lower(), bus, model_ctrs[model]
                    )

                    fc_attrs = info[3]
                    try:
                        self.connect_entities(
                            model_key, cast("str", db_key), fc_attrs
                        )
                    except ScenarioError:
                        # Only FlexibilitySimulator has target
                        self.connect_entities(
                            model_key, cast("str", db_key), info[3]
                        )

                    model_ctrs[model] += 1

    def connect_to_timesim(self):
        mapping_key = "peak_mapping"
        timesim, _ = self.scenario.find_first_model("timesim")
        model_ctrs = {}

        for model, info in self.models.items():
            for bus, entities in cast(
                "dict", self.sim_params[mapping_key]
            ).items():
                for name, _ in entities:
                    if model != name:
                        continue

                    model_ctrs.setdefault(model, 0)
                    model_key = self.scenario.generate_model_key(
                        self, model.lower(), bus, model_ctrs[model]
                    )
                    self.connect_entities(
                        cast("str", timesim), model_key, ["local_time"]
                    )

                    model_ctrs[model] += 1

    def generate_model_params(
        self, model_key, model, p_peak_mw
    ) -> dict[str, Any]:
        """Load model params and initial configurations."""
        mod_params, mod_inits = get_presets(
            model,
            p_peak_mw,
            q_control=cast("str", self.sim_params["q_control"]),
            cos_phi=cast("float", self.sim_params["cos_phi"]),
            inverter_mode=cast("str", self.sim_params["inverter_mode"]),
            is_static_t_module=cast(
                "bool", self.sim_params["pv_is_static_t_module"]
            ),
            randomize_params=cast("bool", self.sim_params["randomize_params"]),
            randomize_inits=cast("bool", self.sim_params["randomize_inits"]),
            seed=self.scenario.create_seed(),
        )

        self.sim_params.setdefault(model_key, {})
        cast("dict", self.sim_params[model_key]).setdefault(
            "params", mod_params
        )
        cast("dict", self.sim_params[model_key]).setdefault("inits", mod_inits)
        return cast("dict", self.sim_params[model_key])

    def create_default_wpm(self):
        """Create a default weather provider mapping."""
        wprovider = None
        for key, val in self.params["weather_params"].items():
            if isinstance(key, dict):
                try:
                    if len(val["weather_mapping"]["WeatherCurrent"]) > 0:
                        wprovider = key
                        break

                except KeyError:
                    pass

        wpmapping = dict()
        for models in cast("dict", self.sim_params["mapping"]).values():
            for model, _ in models:
                wpmapping.setdefault(model, dict())
                wpmapping[model].setdefault(wprovider, list())
                wpmapping[model][wprovider].append(0)

        return wpmapping

    def get_weather_model(self, model, idx, forecast=False) -> str | None:
        if forecast:
            wmn = "weatherforecast"
            mapping = self.sim_params["weather_forecast_mapping"]
        else:
            wmn = "weathercurrent"
            mapping = self.sim_params["weather_provider_mapping"]
        try:
            model_mapping = cast("dict", mapping)[model]
        except KeyError:
            msg = (
                f"No {wmn} mapping for model {model} defined. This may "
                + "result in an error if the model depends on that inputs."
            )
            LOG.debug(msg)

            return None
        wp_scope = ""
        wp_idx = -1

        if isinstance(model_mapping, dict):
            for model_idx, (name, wpidx) in model_mapping.items():
                if model_idx != idx:
                    continue
                wp_scope = name
                wp_idx = wpidx

        elif isinstance(model_mapping, list):
            wp_scope = model_mapping[0]
            if isinstance(wp_scope, list):
                try:
                    wp_scope, wp_idx = model_mapping[idx]
                except IndexError:
                    wp_scope, wp_idx = model_mapping[-1]
            else:
                wp_idx = model_mapping[1]
        else:
            raise ValueError("Weather provider mapping: Unknown format.")

        models = self.scenario.find_models("weather", wp_scope, wmn)
        for key in models:
            if key.endswith(f"_{wp_idx}"):
                return key

        return None

    def get_grid_entity(self, mtype, bus):
        models = self.scenario.find_grid_entities(
            self.sim_params["grid_name"], mtype, endswith=f"_{bus}"
        )
        if models:
            for key in models:
                # Return first match
                return key

        if mtype == "storage":
            # The storage type may not be present in the grid
            # Attach the unit to load instead
            return self.get_grid_entity("load", bus)

        # self.logger.info(
        #     "Grid entity for %s, %s at bus %d not found",
        #     self.sim_params["grid_name"],
        #     mtype,
        #     bus,
        # )
        raise ValueError(
            f"Grid entity for {self.sim_params['grid_name']}, {mtype} "
            f"at bus {bus} not found!"
        )

    def get_sensors(self):
        for sensor in self.sensors:
            self.scenario.sensors.append(sensor)
            LOG.debug("Created sensor entry %s.", sensor)

    def get_actuators(self):
        for actuator in self.actuators:
            self.scenario.actuators.append(actuator)
            LOG.debug("Created actuator entry %s.", actuator)

    def download(self, data_path: str, tmp_path: str, force: bool):
        # No downloads
        pass

    def analyze(
        self,
        name: str,
        data: pd.DataFrame,
        output_folder: str,
        start: int,
        end: int,
        step_size: int,
        full: bool,
    ):
        analyze(name, data, output_folder, start, end, step_size, full)


def create_default_mapping():
    return {3: [("PV", 6)], 4: [("PV", 2)], 8: [("PV", 2)], 11: [("PV", 3)]}


def get_presets(
    model: str,
    p_peak_mw: float,
    *,
    q_control: str = "prioritize_p",
    cos_phi: float = 0.9,
    inverter_mode: str = "inductive",
    is_static_t_module: bool = False,
    randomize_params: bool = False,
    randomize_inits: bool = False,
    seed: int | None = False,
    **kwargs,
):
    """Return presets for *model* with *p_peak_mw*.

    The presets are taken from the pysimmods package itself.

    """

    if model == "PV":
        params, inits = pv_preset(
            p_peak_kw=p_peak_mw * 1e3,
            q_control=q_control,
            cos_phi=cos_phi,
            inverter_mode=inverter_mode,
            is_static_t_module=is_static_t_module,
        )
        params["sn_mva"] = (
            cast("float", cast("ModelParams", params["inverter"])["sn_kva"])
            * 1e-3
        )

        return params, inits
    elif model == "HVAC":
        return hvac_preset(
            pn_max_kw=p_peak_mw * 1e3,
            randomize_params=randomize_params,
            randomize_inits=randomize_inits,
            seed=seed,
            **kwargs,
        )
    elif model == "CHP":
        return chp_preset(p_kw=p_peak_mw * 1e3, **kwargs)
    elif model == "BAT":
        return battery_preset(
            pn_max_kw=p_peak_mw * 1e3,
            randomize_params=randomize_params,
            randomize_eta_pc=randomize_params,
            randomize_inits=randomize_inits,
            seed=seed,
        )
    elif model == "DIESEL":
        return {
            "sign_convention": "active",
            "p_max_kw": p_peak_mw * 1e3,
            "p_min_kw": 0,
        }, {}
    elif model == "Biogas":
        return biogas_preset(
            pn_max_kw=p_peak_mw * 1e3,
            randomize_params=randomize_params,
            randomize_inits=randomize_inits,
            seed=seed,
        )
    elif model == "Wind":
        params, inits = windsys_preset(
            pn_max_kw=p_peak_mw * 1e3,
            randomize_params=randomize_params,
            seed=seed,
            q_control=q_control,
            inverter_mode=inverter_mode,
            cos_phi=cos_phi,
        )
        params["sn_mva"] = (
            cast("float", cast("ModelParams", params["inverter"])["sn_kva"])
            * 1e-3
        )
        return params, inits
    else:
        raise ValueError(f"Model {model} is unknown.")


def create_actuator(
    full_id: str,
    attr: str,
    vmin: float,
    vmax: float,
    dtype: str = "np.float32",
):
    return {
        "uid": f"{full_id}.{attr}",
        "space": (f"Box(low={vmin}, high={vmax}, shape=(), dtype={dtype})"),
    }


def create_sensor(
    full_id: str,
    attr: str,
    vmin: float = -10000,
    vmax: float = 10000,
    dtype: str = "np.float32",
):
    return {
        "uid": f"{full_id}.{attr}",
        "space": (f"Box(low={vmin}, high={vmax}, shape=(), dtype={dtype})"),
    }


def get_space(model, params, p_peak_mw):
    p_min = q_min = q_max = 0
    p_max = p_peak_mw

    if model.lower() in ["pv"]:
        q_min = -params["params"]["sn_mva"]
        q_max = params["params"]["sn_mva"]

    if model.lower() in ["bat"]:
        p_min = -params["params"]["p_discharge_max_kw"] * 1e-3
        p_max = params["params"]["p_charge_max_kw"] * 1e-3

    return p_min, p_max, q_min, q_max
