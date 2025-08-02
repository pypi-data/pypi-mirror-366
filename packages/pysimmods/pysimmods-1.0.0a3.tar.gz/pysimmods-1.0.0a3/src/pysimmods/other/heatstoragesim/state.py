from typing import cast

from pysimmods.base.model import ModelState
from pysimmods.base.types import ModelInitVals


class HeatStorageState(ModelState):
    """Captures the state of the heat storage"""

    def __init__(self, inits: ModelInitVals):
        super().__init__(inits)

        self.t_c: float = cast("float", inits["storage_t_c"])
        self.t_chilled: float = 0.0
        self.e_th_in_max_kwh: float = 0.0
        self.e_th_in_min_kwh: float = 0.0
