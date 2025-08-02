from copy import deepcopy
from typing import cast

from pysimmods.base.config import ModelConfig
from pysimmods.base.inputs import ModelInputs
from pysimmods.base.qgenerator import QGenerator
from pysimmods.base.state import ModelState
from pysimmods.base.types import ModelInitVals, ModelParams, QControl


class DummyQGeneratorConfig(ModelConfig):
    def __init__(self, params: ModelParams):
        super().__init__(params)

        self.p_max_kw: float = cast("float", params.get("p_max_kw", 500))
        self.p_min_kw: float = cast("float", params.get("p_min_kw", 250))
        self.q_min_kvar: float = cast("float", params.get("q_min_kvar", -550))
        self.q_max_kvar: float = cast("float", params.get("q_max_kvar", 550))
        self.default_p_schedule = [375.0] * 24
        self.default_q_schedule = [125.0] * 24
        self.s_max_kva: float = cast(
            "float", params.get("s_max_kva", self.p_max_kw * 1.2)
        )
        self.q_control: QControl = cast(
            "QControl", params.get("q_control", QControl.PRIORITIZE_P)
        )
        self.cos_phi: float = cast("float", params.get("cos_phi", 0.9))


class DummyQGeneratorState(ModelState):
    pass


class DummyQGeneratorInputs(ModelInputs):
    def __init__(self):
        super().__init__()

        self.cos_phi: float | None = None


class DummyQGenerator(
    QGenerator[
        DummyQGeneratorConfig, DummyQGeneratorState, DummyQGeneratorInputs
    ]
):
    """The dummy Q generator model."""

    def __init__(self, params: ModelParams, inits: ModelInitVals):
        self.config = DummyQGeneratorConfig(params)
        self.state = DummyQGeneratorState(inits)
        self.inputs = DummyQGeneratorInputs()

    def step(self, pretend: bool = False) -> DummyQGeneratorState:
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
            self.config.s_max_kva,
            max(-self.config.s_max_kva, next_state.q_kvar),
        )

        if not pretend:
            self.state = next_state
        return next_state
