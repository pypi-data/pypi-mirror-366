from enum import Enum
from typing import Generic

from typing_extensions import override

from pysimmods.base.generator import Generator
from pysimmods.base.model import C, I, S


class QGenerator(Generator[C, S, I], Generic[C, S, I]):
    """A generator subtype model with reactive power support."""

    @override
    def set_q_kvar(self, q_kvar: float | None) -> None:
        """Set target value for reactive power in kVAr.

        Can be set to None to fall back to the default schedule.
        """
        if q_kvar is None:
            self.inputs.q_set_kvar = None
        else:
            self.inputs.q_set_kvar = q_kvar * self.config.gsign

    @override
    def get_q_kvar(self) -> float:
        """Return current reactive power in kVAr of the model.

        Respects the current sign convention.
        """
        return self.state.q_kvar * self.config.gsign

    def get_qn_max_kvar(self) -> float:
        """Return the nominal maximum reactive power output in kVAr."""
        return self.config.s_max_kva
