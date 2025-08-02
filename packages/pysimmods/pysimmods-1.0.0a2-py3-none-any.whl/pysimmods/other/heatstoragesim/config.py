from typing import cast

from pysimmods.base.config import ModelConfig
from pysimmods.base.types import ModelParams


class HeatStorageConfig(ModelConfig):
    """Captures the configuration parameters of the heat storage."""

    def __init__(self, params: ModelParams):
        super().__init__(params)

        self.cap_l: float = cast("float", params["storage_cap_l"])
        self.consumption_kwh_per_day: float = cast(
            "float", params["storage_consumption_kwh_per_day"]
        )
        self.t_min_c: float = cast("float", params["storage_t_min_c"])
        self.t_max_c: float = cast("float", params["storage_t_max_c"])
        self.env_t_c: float = cast(
            "float", params.get("storage_env_t_c", 19.0)
        )
