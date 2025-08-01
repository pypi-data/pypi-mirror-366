"""This module contains the config model for the chp."""

from typing import cast

from pysimmods.base.config import ModelConfig
from pysimmods.base.types import ModelParams


class CHPCNGConfig(ModelConfig):
    """A CHP CNG configuration parameter class.

    Parameters
    ----------
    params: dict
        Contains the configuration for the CHP CNG. See attribute
        section for more information about the parameters.
        Attributes marked with *(Input)* can be provided with this
        dict, others are calculated from those.

    Attributes
    ----------
    pn_stages_kw: list[float]
        (Input) Possible eletrical power stages in [kW]. Power level 0
        (unit off) should not be included.
    p_max_kw: float
        The maximum power output of this unit in [kW].
    p_min_kw: float
        The minimum power output of this unit in [kW], while it is
        operating (exluding 0).
    eta_stages_percent: list[float]
        (Input) The electrical efficiency at each power stage in [%]
    eta_th_stages_percent: list[float]
        (Input) The thermal efficiency at each power stage in [%]
    restarts_per_day: int
        (Input) Allowed number of restarts per day.
    active_min_s: int
        (Input) Minimum active time of this unit before it is allowed
        to shut down again in [s].
    active_max_s_per_day: int
        (Input) Maximum cumulated active time per day in [s]. Unit will
        shut down after that time.
    inactive_min_s: int
        (Input) Minimum inactive time until this unit is allowed to
        start again in [s].
    inactive_max_s_per_day: int
        (Input) Maximum cumulated inactive time per day in [s]. Unit
        will try to stay on when this time is reached.
    e_ch4_kwh: float
        Energy of methane gas in [kWh]. Constant value.
    ch4_concentration_percent: float
        (Input) Concentration of methane gas in [%].
    """

    def __init__(self, params: ModelParams) -> None:
        super().__init__(params)

        self.pn_stages_kw: list[float] = cast(
            "list[float]", params["pn_stages_kw"]
        )
        self.pn_stages_kw = [abs(stage) for stage in self.pn_stages_kw]
        self.p_max_kw: float = max(self.pn_stages_kw)
        self.p_min_kw: float = min(self.pn_stages_kw)

        self.eta_stages_percent: list[float] = cast(
            "list[float]", params["eta_stages_percent"]
        )
        self.eta_th_stages_percent: list[float] = cast(
            "list[float]", params["eta_th_stages_percent"]
        )

        self.restarts_per_day: int = cast("int", params["restarts_per_day"])
        self.active_min_s: int = cast("int", params["active_min_s"])
        self.active_max_s_per_day: int = cast(
            "int", params["active_max_s_per_day"]
        )
        self.inactive_min_s: int = cast("int", params["inactive_min_s"])
        self.inactive_max_s_per_day: int = cast(
            "int", params["inactive_max_s_per_day"]
        )

        self.e_ch4_kwh = 9.94
        self.ch4_concentration_percent: float = cast(
            "float", params.get("ch4_concentration_percent", 50.302)
        )

        self.default_schedule: list[float] = [50.0] * 24
