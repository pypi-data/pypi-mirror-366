"""This module contains a :class:`mosaik_api.Simulator` for the
flexiblity model, which is a wrapper for all models of the
pysimmods package.

"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Union, cast

import mosaik_api_v3
import numpy as np
import pandas as pd
from midas.util.logging import set_and_init_logger
from mosaik_api_v3.types import (
    CreateResult,
    InputData,
    Meta,
    ModelName,
    OutputData,
    OutputRequest,
    SimId,
    Time,
)
from typing_extensions import override

from pysimmods.base.model import Model
from pysimmods.mosaik_bridge import LOG
from pysimmods.mosaik_bridge.meta import MODELS
from pysimmods.mosaik_bridge.pysim_mosaik import PysimmodsSimulator
from pysimmods.other.flexibility.flexibility_model import FlexibilityModel
from pysimmods.other.flexibility.forecast_model import ForecastModel
from pysimmods.other.flexibility.schedule_model import ScheduleModel
from pysimmods.util.date_util import GER


class FlexibilitySimulator(PysimmodsSimulator):
    """The generic flexiblity mosaik simulator for all pysimmods."""

    def __init__(self):
        super().__init__()

        self.models: dict[str, Model] = {}
        self.num_models: dict[ModelName, int] = {}

        self.sid: SimId = ""
        self.step_size: int = 0
        self.now_dt: datetime = datetime(1970, 1, 1)

        self.unit: str = "kw"
        self.use_decimal_percent: bool = False
        self.prioritize_setpoint: bool = False
        self.provide_forecasts: bool = False
        self.provide_flexibilities: bool = False
        self.forecast_horizon_hours: float = 0.25
        self.planning_horizon_hours: float = 1.0
        self.flexibility_horizon_hours: float = 2.0
        self.num_schedules: int = 10
        self.rng: np.random.Generator = np.random.default_rng()

    @override
    def init(
        self,
        sid: SimId,
        time_resolution: float = 1.0,
        start_date: str = "2010-01-01 00:00:00+0100",
        step_size: int = 900,
        unit: str = "kw",
        use_decimal_percent: bool = False,
        prioritize_setpoint: bool = False,
        provide_forecasts: bool = False,
        forecast_horizon_hours: float = 0.25,
        provide_flexibilities: bool = False,
        planning_horizon_hours: float = 1.0,
        flexibility_horizon_hours: float = 2.0,
        num_schedules: int = 10,
        seed: int | None = None,
        **sim_params: Dict[str, Any],
    ) -> Meta:
        """Called exactly ones after the simulator has been started.

        Parameters
        ----------
        sid : str
            Simulator ID for this simulator.
        start_date : str
            The start date as UTC ISO 8601 date string.
        step_size : int, optional
            Step size for this simulator. Defaults to 900.
        unit: str

        use_decimal_percent

        prioritize_setpoint

        provide_forecasts

        forecast_horizon_hours

        provide_flexibilities

        planning_horizon_hours

        flexibility_horizon_hours

        num_schedules

        seed

        key_value_logs

        Returns
        -------
        dict
            The meta dict (set by *mosaik_api.Simulator*).

        """
        self.sid = sid
        self.step_size = step_size
        self.now_dt = datetime.strptime(start_date, GER).astimezone(
            timezone.utc
        )

        self.unit = unit
        self.use_decimal_percent = use_decimal_percent

        self.prioritize_setpoint = prioritize_setpoint
        self.provide_forecasts = provide_forecasts
        self.forecast_horizon_hours = forecast_horizon_hours

        self.provide_flexibilities = provide_flexibilities
        self.planning_horizon_hours = planning_horizon_hours
        self.flexibility_horizon_hours = flexibility_horizon_hours
        self.num_schedules = num_schedules
        self.rng = np.random.default_rng(seed)

        self._update_meta()

        return self.meta

    @override
    def create(
        self,
        num: int,
        model: ModelName,
        *,
        params: Dict[str, Any],
        inits: Dict[str, Any],
        **model_params,  # for compatibility
    ) -> list[CreateResult]:
        """Initialize the simulation model instance (entity).

        Parameters
        ----------
        num : int
            The number of models to create.
        model : str
            The name of the models to create. Must be present inside
            the simulator's meta.
        params: Dict[str, Any]
            The parameters dictionary for the model to create.
        inits: Dict[str, Any]
            The initial state dictionary for the model to create.

        Returns
        -------
        List[Dict[str, str]]
            A list with information on the created entity.

        """
        entities: list[CreateResult] = []
        params.setdefault("use_decimal_percent", self.use_decimal_percent)
        self.num_models.setdefault(model, 0)

        for _ in range(num):
            eid = f"{model}-{self.num_models[model]}"

            if self.provide_flexibilities:
                self.models[eid] = FlexibilityModel(
                    MODELS[model](params, inits),
                    unit=self.unit,
                    prioritize_setpoint=self.prioritize_setpoint,
                    forecast_horizon_hours=self.forecast_horizon_hours,
                    seed=self.rng.integers(2**32 - 1),
                )

            elif self.provide_forecasts:
                self.models[eid] = ForecastModel(
                    MODELS[model](params, inits),
                    unit=self.unit,
                    prioritize_setpoint=self.prioritize_setpoint,
                    forecast_horizon_hours=self.forecast_horizon_hours,
                )

            else:
                self.models[eid] = ScheduleModel(
                    MODELS[model](params, inits),
                    unit=self.unit,
                    prioritize_setpoint=self.prioritize_setpoint,
                )

            self.num_models[model] += 1
            entities.append({"eid": eid, "type": model})
        return entities

    @override
    def step(
        self, time: Time, inputs: InputData, max_advance: Time = 0
    ) -> Time | None:
        """Perform a simulation step.

        Parameters
        ----------
        time : int
            The current simulation step (by convention in seconds since
            simulation start.
        inputs : dict
            A *dict* containing inputs for entities of this simulator.

        Returns
        -------
        int
            The next step this simulator wants to be stepped.

        """

        self._set_default_inputs()

        for eid, attrs in inputs.items():
            for attr, src_ids in attrs.items():
                if "forecast" in attr:
                    self._set_attr_forecast(eid, src_ids)
                elif attr == "schedule":
                    self._set_attr_schedule(eid, src_ids)
                elif attr == "local_time":
                    self._set_attr_local_time(eid, src_ids)
                else:
                    attr_sum = self._aggregate_attr(src_ids)
                    self._set_remaining_attrs(eid, attr, attr_sum)

        for model in self.models.values():
            model.step()

        self.now_dt += timedelta(seconds=self.step_size)
        self._generate_flexibilities()

        return time + self.step_size

    @override
    def get_data(self, outputs: OutputRequest) -> OutputData:
        """Returns the requested outputs (if feasible)"""

        data: Dict[str, Dict[str, Any]] = {}
        for eid, attrs in outputs.items():
            data[eid] = {}

            log_msg: dict[str, str | float | int | None] = {
                "id": f"{self.sid}_{eid}",
                "name": eid,
                "type": eid.split("-")[0],
            }

            for attr in attrs:
                if attr == "flexibilities":
                    value = self._get_attr_flexibilities(eid)
                    log_msg[attr] = json.loads(value)

                elif attr == "schedule":
                    value = self._get_attr_schedule(eid)
                    log_msg[attr] = json.loads(value)

                else:
                    value = self._get_remaining_attrs(eid, attr)
                    log_msg[attr] = value

                data.setdefault(eid, dict())[attr] = value

            LOG.debug(json.dumps(log_msg))

        return data

    def _update_meta(self):
        for model in self.meta["models"].keys():
            self.meta["models"][model]["attrs"].extend(
                ["flexibilities", "schedule", "target"]
            )

        self.meta["models"]["Photovoltaic"]["attrs"].extend(
            [
                "forecast_t_air_deg_celsius",
                "forecast_bh_w_per_m2",
                "forecast_dh_w_per_m2",
            ]
        )
        self.meta["models"]["CHP"]["attrs"].extend(
            ["forecast_day_avg_t_air_deg_celsius"]
        )
        self.meta["models"]["HVAC"]["attrs"].extend(
            ["forecast_t_air_deg_celsius"]
        )

    def _set_attr_forecast(self, eid: str, src_ids: Dict[str, Any]):
        for forecast in src_ids.values():
            if not isinstance(forecast, pd.DataFrame):
                forecast = pd.read_json(forecast).tz_localize("UTC")
            cast("ForecastModel", self.models[eid]).update_forecasts(forecast)

    def _set_attr_schedule(self, eid: str, src_ids: Dict[str, Any]):
        for schedule in src_ids.values():
            if schedule is not None:
                schedule = deserialize_schedule(schedule)

                if not schedule.empty:
                    cast("ScheduleModel", self.models[eid]).update_schedule(
                        schedule
                    )

    def _get_attr_schedule(self, eid: str) -> str:
        value = cast("ScheduleModel", self.models[eid]).schedule.to_json(
            self.now_dt,
            self.now_dt
            + timedelta(hours=self.forecast_horizon_hours)
            - timedelta(seconds=self.step_size),
        )

        return value

    def _get_attr_flexibilities(self, eid: str) -> str:
        dict_of_json = cast(
            "FlexibilityModel", self.models[eid]
        ).flexibilities.to_json()
        # value = json.dumps(dict_of_json)
        return dict_of_json

    def _generate_flexibilities(self):
        if self.provide_flexibilities:
            for model in self.models.values():
                cast("FlexibilityModel", model).generate_schedules(
                    (
                        self.now_dt
                        + timedelta(hours=self.planning_horizon_hours)
                    ).strftime(GER),
                    self.flexibility_horizon_hours,
                    self.num_schedules,
                )


def deserialize_schedule(
    schedule: Union[pd.DataFrame, Dict[str, Any], str],
) -> pd.DataFrame:
    """Convert the schedule provided by mosaik to DataFrame"""

    if isinstance(schedule, pd.DataFrame):
        return schedule

    if isinstance(schedule, dict):
        # The schedule might be nested into the schedule because of an
        # ICT simulator
        return deserialize_schedule(list(schedule.values())[0])

    if isinstance(schedule, str):
        return pd.read_json(schedule).tz_localize("UTC")

    raise ValueError(
        f"Unsupported schedule format {type(schedule)}: {schedule}"
    )


if __name__ == "__main__":
    set_and_init_logger(
        0, "pysimmods-logfile", "pysimmods-flex.log", replace=True
    )
    LOG.info("Starting mosaik simulation...")
    mosaik_api_v3.start_simulation(FlexibilitySimulator())
