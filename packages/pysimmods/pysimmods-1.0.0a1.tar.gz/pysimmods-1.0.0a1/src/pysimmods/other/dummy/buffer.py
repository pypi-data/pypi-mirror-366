from copy import deepcopy
from typing import cast

from pysimmods.base.buffer import Buffer
from pysimmods.base.config import ModelConfig
from pysimmods.base.inputs import ModelInputs
from pysimmods.base.state import ModelState
from pysimmods.base.types import ModelInitVals, ModelParams


class DummyBufferConfig(ModelConfig):
    def __init__(self, params: ModelParams):
        params.setdefault("default_schedule", [10.0] * 24)
        super().__init__(params)

        self.p_max_kw: float = cast("float", params.get("p_max_kw", 500))
        self.p_min_kw: float = cast("float", params.get("p_min_kw", 250))
        self.q_max_kvar: float = cast("float", params.get("q_max_kvar", 100))
        self.q_min_kvar: float = cast("float", params.get("q_min_kvar", 25))
        self.cap_e_khw: float = cast("float", params.get("cap_e_kwh", 5000))

        self.p_charge_max_kw: float = abs(
            cast("float", params.get("p_charge_max_kw", self.p_max_kw))
        )
        self.p_charge_min_kw: float = abs(
            cast("float", params.get("p_charge_min_kw", self.p_min_kw))
        )

        self.p_discharge_max_kw: float = abs(
            cast("float", params.get("p_discharge_max_kw", -self.p_max_kw))
        )

        self.p_discharge_min_kw: float = abs(
            cast("float", params.get("p_discharge_min_kw", -self.p_min_kw))
        )


class DummyBufferState(ModelState):
    def __init__(self, inits: ModelInitVals):
        super().__init__(inits)
        self.soc_kwh: float = cast("float", inits["soc_kwh"])


class DummyBufferInputs(ModelInputs):
    pass


class DummyBuffer(
    Buffer[DummyBufferConfig, DummyBufferState, DummyBufferInputs]
):
    """The dummy buffer model."""

    def __init__(self, params: ModelParams, inits: ModelInitVals):
        self.config = DummyBufferConfig(params)
        self.state = DummyBufferState(inits)
        self.inputs = DummyBufferInputs()

    def step(self, pretend=False) -> DummyBufferState:
        next_state = deepcopy(self.state)

        # Check inputs
        step_size = (
            1 if self.inputs.step_size is None else self.inputs.step_size
        )
        next_state.p_kw = (
            0.0 if self.inputs.p_set_kw is None else self.inputs.p_set_kw
        )
        # Apply constraints
        if next_state.p_kw < 0:
            next_state.p_kw = min(
                -self.config.p_discharge_min_kw,
                max(-self.config.p_discharge_max_kw, next_state.p_kw),
            )
        elif next_state.p_kw > 0:
            next_state.p_kw = min(
                self.config.p_charge_max_kw,
                max(self.config.p_charge_min_kw, next_state.p_kw),
            )

        e_khw = next_state.p_kw * step_size / 3600
        if next_state.soc_kwh + e_khw > self.config.cap_e_khw:
            next_state.p_kw = 0
        elif next_state.soc_kwh + e_khw < 0:
            next_state.p_kw = 0
        else:
            next_state.soc_kwh += e_khw

        if not pretend:
            self.state = next_state

        return next_state
