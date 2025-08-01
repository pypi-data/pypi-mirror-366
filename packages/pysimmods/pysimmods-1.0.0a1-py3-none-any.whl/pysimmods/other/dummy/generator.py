from copy import deepcopy
from typing import cast

from pysimmods.base.config import ModelConfig
from pysimmods.base.generator import Generator
from pysimmods.base.inputs import ModelInputs
from pysimmods.base.state import ModelState
from pysimmods.base.types import ModelInitVals, ModelParams


class DummyGeneratorConfig(ModelConfig):
    def __init__(self, params: ModelParams):
        super().__init__(params)

        self.p_max_kw: float = cast("float", params.get("p_max_kw", 500))
        self.p_min_kw: float = cast("float", params.get("p_min_kw", 250))
        self.default_p_schedule = [(self.p_max_kw + self.p_min_kw) / 2] * 24


class DummyGeneratorState(ModelState):
    pass


class DummyGeneratorInputs(ModelInputs):
    pass


class DummyGenerator(
    Generator[DummyGeneratorConfig, DummyGeneratorState, DummyGeneratorInputs]
):
    """The dummy generator model."""

    def __init__(self, params: ModelParams, inits: ModelInitVals):
        self.config = DummyGeneratorConfig(params)
        self.state = DummyGeneratorState(inits)
        self.inputs = DummyGeneratorInputs()

    def step(self, pretend: bool = False) -> DummyGeneratorState:
        next_state = deepcopy(self.state)

        # Check inputs
        next_state.p_kw = (
            0.0 if self.inputs.p_set_kw is None else self.inputs.p_set_kw
        )
        next_state.q_kvar = (
            0.0 if self.inputs.q_set_kvar is None else self.inputs.q_set_kvar
        )

        # Apply constraints
        if next_state.p_kw > 0:
            next_state.p_kw = min(
                self.config.p_max_kw,
                max(self.config.p_min_kw, next_state.p_kw),
            )

        next_state.q_kvar = min(
            self.config.q_max_kvar,
            max(self.config.q_min_kvar, next_state.q_kvar),
        )

        if not pretend:
            self.state = next_state
        return next_state
