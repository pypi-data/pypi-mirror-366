"""This module contains the flexibility model."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import numpy as np
import pandas as pd

from pysimmods.base.model import I
from pysimmods.other.flexibility.flexibilities import Flexibilities
from pysimmods.other.flexibility.forecast_model import ForecastModel
from pysimmods.other.flexibility.schedule import Schedule
from pysimmods.util.date_util import GER

LOG = logging.getLogger(__name__)


class FlexibilityModel(ForecastModel):
    """The flexibility model for all pysimmods."""

    def __init__(
        self,
        model,
        unit="kw",
        prioritize_setpoint: bool = False,
        step_size: Optional[int] = None,
        now_dt: Optional[datetime] = None,
        forecast_horizon_hours: float = 1.0,
        seed: int | None = None,
        store_min_and_max: bool = False,
    ):
        super().__init__(
            model,
            unit,
            prioritize_setpoint,
            step_size,
            now_dt,
            forecast_horizon_hours,
        )

        self._store_min_and_max = store_min_and_max
        self._rng = np.random.default_rng(seed)

    def generate_schedules(
        self, start: str | datetime, flexibility_horizon_hours, num_schedules
    ) -> Flexibilities:
        """Perform sampling and generate a set of schedules for the
        specified time interval.

        Args:
            start (str): Is the start of the planning horizon for which
                the sampling is done. It has to be provided as ISO 8601
                timezone string such as '2020-06-22 12:00:00+0000'

            forecast_horizon_hours (int): The planning horizon is divided into.

        """
        state_backup = self._model.get_state()
        step_size = self._step_size

        now_dt = self._now_dt
        if isinstance(start, str):
            start_dt = datetime.strptime(start, GER).astimezone(timezone.utc)
        else:
            start_dt = start
        end_dt = (
            start_dt
            + timedelta(hours=flexibility_horizon_hours)
            - timedelta(seconds=step_size)
        )
        periods = int(flexibility_horizon_hours * 3_600 / step_size)

        # Fast forward to the planning interval
        while start_dt > now_dt:
            try:
                p_set = self.schedule.get(now_dt, self._psetname)
                if p_set is None or np.isnan(p_set):
                    # Fallback to schedule that was implicitly
                    # created
                    p_set = self.schedule.get(now_dt, self._pname)
                q_set = self.schedule.get(now_dt, self._qsetname)
                if q_set is None or np.isnan(q_set):
                    q_set = self.schedule.get(now_dt, self._qname)
                self._calculate_step(now_dt, p_set, q_set)
                now_dt += timedelta(seconds=step_size)
            except KeyError as err:
                # raise err
                LOG.info("Could not create flexibilities: %s", err)
                return {}

        ff_index = pd.date_range(
            self._now_dt,
            start_dt - timedelta(seconds=step_size),
            freq=f"{step_size}s",
        )
        index = pd.date_range(start_dt, end_dt, periods=periods)

        self.flexibilities = Flexibilities()

        for schedule_id in range(num_schedules):
            self.flexibilities.add_schedule(
                schedule_id, self.sample(index, ff_index)
            )

        self._model.set_state(state_backup)
        return self.flexibilities

    def sample(self, index, ff_index):
        if not ff_index.empty:
            ff_df = pd.DataFrame(
                columns=[
                    self._psetname,
                    self._qsetname,
                    self._pname,
                    self._qname,
                ],
                index=ff_index,
                dtype="float",
            )
            for i, row in ff_df.iterrows():
                p_set = self.schedule.get(i, self._psetname)
                if p_set is None or np.isnan(p_set):
                    p_set = self.schedule.get(i, self._pname)
                q_set = self.schedule.get(I, self._qsetname)
                if q_set is None or np.isnan(q_set):
                    q_set = self.schedule.get(i, self._qname)
                ff_df.at[i, self._psetname] = p_set
                ff_df.at[i, self._qsetname] = q_set
        else:
            ff_df = pd.DataFrame()

        dataframe = pd.DataFrame(
            columns=[self._psetname, self._qsetname, self._pname, self._qname],
            index=index,
            dtype="float",
        )
        dataframe[self._psetname] = self._rng.uniform(
            low=self.get_pn_min_kw(),
            high=self.get_pn_max_kw(),
            size=len(index),
        )
        dataframe[self._qsetname] = self._rng.uniform(
            low=self.get_qn_min_kvar(),
            high=self.get_qn_max_kvar(),
            size=len(index),
        )

        state_backup = self._model.get_state()
        for index, row in dataframe.iterrows():
            try:
                self._calculate_step(
                    index, row[self._psetname], row[self._qsetname]
                )
                dataframe.loc[index, self._pname] = (
                    self._model.get_p_kw() * self._unit_factor
                )
                dataframe.loc[index, self._qname] = (
                    self._model.get_q_kvar() * self._unit_factor
                )

            except KeyError:
                # Forecast is missing
                dataframe.loc[index, self._pname] = np.nan
                dataframe.loc[index, self._qname] = np.nan
                dataframe.loc[index, self._psetname] = np.nan
                dataframe.loc[index, self._qsetname] = np.nan
        self._model.set_state(state_backup)
        if not ff_df.empty:
            dataframe = pd.concat([ff_df, dataframe])
        return Schedule().from_dataframe(dataframe)
