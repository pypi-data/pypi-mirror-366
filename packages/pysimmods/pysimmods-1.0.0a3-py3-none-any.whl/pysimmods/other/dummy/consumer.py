from copy import deepcopy
from typing import cast

from pysimmods.base.config import ModelConfig
from pysimmods.base.consumer import Consumer
from pysimmods.base.inputs import ModelInputs
from pysimmods.base.state import ModelState
from pysimmods.base.types import ModelInitVals, ModelParams


class DummyConsumerConfig(ModelConfig):
    def __init__(self, params: ModelParams):
        super().__init__(params)

        self.p_max_kw: float = cast("float", params.get("p_max_kw", 500))
        self.p_min_kw: float = cast("float", params.get("p_min_kw", 250))
        self.q_max_kvar: float = cast("float", params.get("q_max_kvar", 100))
        self.q_min_kvar: float = cast("float", params.get("q_min_kvar", 25))

        self.default_p_schedule = [10.0] * 24
        self.default_q_schedule = [-4.0] * 24


class DummyConsumerState(ModelState):
    pass


class DummyConsumerInputs(ModelInputs):
    pass


class DummyConsumer(
    Consumer[DummyConsumerConfig, DummyConsumerState, DummyConsumerInputs]
):
    """The dummy consumer model."""

    def __init__(self, params: ModelParams, inits: ModelInitVals):
        self.config = DummyConsumerConfig(params)
        self.state = DummyConsumerState(inits)
        self.inputs = DummyConsumerInputs()

    def step(self, pretend=False) -> DummyConsumerState:
        next_state = deepcopy(self.state)

        next_state.p_kw = (
            0.0 if self.inputs.p_set_kw is None else self.inputs.p_set_kw
        )
        if next_state.p_kw > 0:
            next_state.p_kw = min(
                self.config.p_max_kw,
                max(self.config.p_min_kw, next_state.p_kw),
            )
        if not pretend:
            self.state = next_state
        return next_state
