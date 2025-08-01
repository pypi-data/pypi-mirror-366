"""This module contains different DummyModels, which only implement the
the model interfaces. Their purpose is mainly for testing.

"""

from copy import deepcopy
from typing import cast

from pysimmods.base.config import ModelConfig
from pysimmods.base.inputs import ModelInputs
from pysimmods.base.model import Model
from pysimmods.base.state import ModelState
from pysimmods.base.types import ModelInitVals, ModelParams


class DummyConfig(ModelConfig):
    def __init__(self, params: ModelParams):
        super().__init__(params)

        self.p_max_kw: float = cast("float", params.get("p_max_kw", 500.0))
        self.p_min_kw: float = cast("float", params.get("p_min_kw", 250.0))
        self.q_min_kvar: float = cast(
            "float", params.get("q_min_kvar", -550.0)
        )
        self.q_max_kvar: float = cast("float", params.get("q_max_kvar", 550.0))
        self.default_p_schedule = [375.0] * 24
        self.default_q_schedule = [125.0] * 24


class DummyState(ModelState):
    pass


class DummyInputs(ModelInputs):
    pass


class DummyModel(Model[DummyConfig, DummyState, DummyInputs]):
    """The dummy base model."""

    def __init__(self, params: ModelParams, inits: ModelInitVals):
        self.config = DummyConfig(params)
        self.state = DummyState(inits)
        self.inputs = DummyInputs()

    def step(self, pretend: bool = False) -> DummyState:
        next_state = deepcopy(self.state)

        # Check inputs
        next_state.p_kw = (
            0.0 if self.inputs.p_set_kw is None else self.inputs.p_set_kw
        )
        next_state.q_kvar = (
            0.0 if self.inputs.q_set_kvar is None else self.inputs.q_set_kvar
        )

        # Apply constraints
        next_state.p_kw = min(
            self.config.p_max_kw, max(self.config.p_min_kw, next_state.p_kw)
        )
        next_state.q_kvar = min(
            self.config.q_max_kvar,
            max(self.config.q_min_kvar, next_state.q_kvar),
        )

        if not pretend:
            self.state = next_state
        return next_state

    def get_pn_max_kw(self):
        return self.config.p_max_kw

    def get_pn_min_kw(self):
        return self.config.p_min_kw

    def get_qn_max_kvar(self):
        return self.config.q_max_kvar

    def get_qn_min_kvar(self):
        return self.config.q_min_kvar

    def set_p_kw(self, p_kw: float) -> None:
        self.inputs.p_set_kw = p_kw

    def get_p_kw(self):
        return self.state.p_kw

    def set_q_kvar(self, q_kvar: float) -> None:
        self.inputs.q_set_kvar = q_kvar

    def get_q_kvar(self):
        return self.state.q_kvar
