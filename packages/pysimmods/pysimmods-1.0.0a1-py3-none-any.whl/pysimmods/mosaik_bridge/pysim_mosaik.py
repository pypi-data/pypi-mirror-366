"""This module contains a :class:`mosaik_api.Simulator` for all models
of the pysimmods package.

"""

import json
import logging
import warnings
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import mosaik_api_v3
import numpy as np
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
from pysimmods.mosaik_bridge.meta import META, MODELS
from pysimmods.util.date_util import GER

VLOG = logging.getLogger("pysimmods.mosaik_bridge.verbose")


class PysimmodsSimulator(mosaik_api_v3.Simulator):
    """The Pysimmods simulator."""

    def __init__(self):
        super().__init__(META)
        self.sid: str = ""
        self.step_size: int = 0
        self.now_dt: datetime = datetime(1977, 1, 1)
        self.key_value_logs: bool

        self.models: dict[str, Model] = {}
        self.num_models: dict[str, int] = {}

    @override
    def init(
        self,
        sid: SimId,
        time_resolution: float = 1.0,
        start_date: str = "2010-01-01 00:00:00+0100",
        step_size: int = 900,
        **sim_params,  # for compatibility
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
        key_value_logs: bool, optional
            If set to True, a different, json-based logging format will
            be used. Default is False.
        time_resolution: float, optional
            Something new from mosaik 3.

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

        return self.meta

    @override
    def create(
        self,
        num: int,
        model: ModelName,
        *,
        params: dict[str, Any],
        inits: dict[str, Any],
        **model_params,  # for compatibility
    ) -> list[CreateResult]:
        """Initialize the simulation model instance (entity).

        Parameters
        ----------
        num: int
            The number of models to create.
        model: str
            The name of the models to create. Must be present inside
            the simulator's meta.
        params: Dict[str, Any]
            The dictionary with parameters for the model to be created.
            Must be provided but can be empty.
        inits: Dict[str, Any]
            The dictionary with initial values for the state of the
            model to be created. Must be provided but can be empty.

        Returns
        -------
        list
            A list with information on the created entity.

        """
        entities = []
        self.num_models.setdefault(model, 0)

        for _ in range(num):
            eid = f"{model}-{self.num_models[model]}"
            self.models[eid] = MODELS[model](params, inits)
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
        max_advance: int,
            Required for mosaik>=3 but not explicitly supported yet.

        Returns
        -------
        int
            The next step this simulator wants to be stepped.

        """
        self._set_default_inputs()

        # Set inputs from other simulators
        for eid, attrs in inputs.items():
            for attr, src_ids in attrs.items():
                self._log_input(eid, attr, src_ids)

                # Use time information from time generator
                if attr == "local_time":
                    self._set_attr_local_time(eid, src_ids)
                    continue

                attr_sum = self._aggregate_attr(src_ids)
                self._set_remaining_attrs(eid, attr, attr_sum)

        # Step the models
        for model in self.models.values():
            model.step()

        # Update time for the next step
        self.now_dt += timedelta(seconds=self.step_size)

        return time + self.step_size

    @override
    def get_data(self, outputs: OutputRequest) -> OutputData:
        """Return the requested output (if feasible).

        Parameters
        ----------
        outputs : dict
            A *dict* containing requested outputs of each entity.

        Returns
        -------
        dict
            A *dict* containing the values of the requested outputs.

        """

        data = {}
        for eid, attrs in outputs.items():
            for attr in attrs:
                value = self._get_remaining_attrs(eid, attr)
                data.setdefault(eid, dict())[attr] = value

                self._log_output(eid, attr, value)

        return data

    def _set_default_inputs(self):
        VLOG.debug(
            "Setting step size %d and current time %s to all models.",
            self.step_size,
            self.now_dt,
        )
        for _, model in self.models.items():
            model.set_step_size(self.step_size)
            model.set_now_dt(self.now_dt)

    def _log_input(self, eid: str, attr: str, src_ids: Dict[str, Any]):
        for src_id, val in src_ids.items():
            if isinstance(val, np.ndarray):
                val = val.tolist()
            elif isinstance(val, np.integer):
                val = int(val)
            elif isinstance(val, np.floating):
                val = float(val)

            LOG.debug(
                json.dumps(
                    {
                        "id": f"{self.sid}_{eid}",
                        "name": eid,
                        "model": eid.split("-")[0],
                        "type": "input",
                        "attribute": attr,
                        "source": src_id,
                        "value": val,
                    }
                )
            )

    def _log_output(self, eid: str, attr: str, value: Any):
        LOG.debug(
            json.dumps(
                {
                    "id": f"{self.sid}_{eid}",
                    "name": eid,
                    "model": eid.split("-")[0],
                    "type": "output",
                    "attribute": attr,
                    "value": value,
                }
            )
        )

    def _set_attr_local_time(self, eid: str, src_ids: Dict[str, Any]) -> bool:
        for val in src_ids.values():
            self.models[eid].set_now_dt(val)
            self.now_dt = datetime.strptime(val, GER).astimezone(timezone.utc)
            return True

        return False

    def _aggregate_attr(self, src_ids: Dict[str, Any]) -> float:
        """Aggregate inputs from different sources.

        If more inputs for one source exists, the average is calculated.

        """
        attr_sum = 0
        for val in src_ids.values():
            if val is None:
                continue
            if isinstance(val, (list, np.ndarray)):
                # This should only happen if palaestrAI is used
                val = val[0]
            attr_sum += val
        attr_sum /= len(src_ids)

        return float(attr_sum)

    def _set_remaining_attrs(self, eid: str, attr: str, attr_sum: float):
        # Apply corrections
        if attr in ("p_set_mw", "p_th_set_mw", "q_set_mvar"):
            attr = attr.replace("m", "k")
            attr_sum *= 1e3

        # Set the inputs
        if attr == "set_percent":
            warnings.warn(
                "Using set_percent is deprecated and will be ignored. Use "
                "p_set_kw or p_set_mw instead",
                UserWarning,
            )

        elif attr == "p_set_kw":
            self.models[eid].set_p_kw(attr_sum)
        elif attr == "q_set_kvar":
            self.models[eid].set_q_kvar(attr_sum)
        else:
            setattr(self.models[eid].inputs, attr, attr_sum)

    def _get_remaining_attrs(self, eid: str, attr: str) -> float:
        # Apply correction of the attr if necessary
        if attr in ("p_mw", "p_th_mw", "q_mvar"):
            true_attr = attr.replace("m", "k")
        elif attr == "p_possible_max_mw":
            true_attr = "p_possible_max_kw"
        else:
            true_attr = attr

        if true_attr == "p_kw":
            value = self.models[eid].get_p_kw()
        elif true_attr == "q_kvar":
            value = self.models[eid].get_q_kvar()
        else:
            value = getattr(self.models[eid].state, true_attr)

        # Apply correction of the value if necessary
        if attr in ("p_mw", "p_th_mw", "q_mvar", "p_possible_max_mw"):
            value *= 1e-3

        return value


if __name__ == "__main__":
    set_and_init_logger(
        0, "pysimmods-logfile", "pysimmods-mosaik.log", replace=True
    )
    LOG.info("Starting mosaik simulation...")
    mosaik_api_v3.start_simulation(PysimmodsSimulator())
