from typing import Generic

from pysimmods.base.model import C, I, Model, S


class Consumer(Model[C, S, I], Generic[C, S, I]):
    """A consumer subtype model.

    A consumer returns positive power values in the
    consumer reference arrow system (passive sign convention).

    """

    def set_p_kw(self, p_kw: float | None) -> None:
        """Set the target value for active power in kW.

        Since the model internally ignores the sign convention,
        the value is converted to a positive value.

        If None is provided, the model will fallback to the default
        schedule.
        """
        if p_kw is not None:
            self.inputs.p_set_kw = abs(p_kw)
        else:
            self.inputs.p_set_kw = None

    def get_p_kw(self) -> float:
        """Return the current active power in kW of the model.

        Respects the current sign convention.
        """
        return self.state.p_kw * self.config.lsign
