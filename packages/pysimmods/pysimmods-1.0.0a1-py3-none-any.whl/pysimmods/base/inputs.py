"""This module contains the base class for all model inputs."""

from datetime import datetime

from pysimmods.util.date_util import convert_dt


class ModelInputs:
    """Base class for model inputs.

    All attributes should be resetted after each step in the model
    implementations. Providing None is usually a valid input (though
    not in all cases).

    Attributes
    ----------
    p_set_kw : float
        Target electrical activate power in [kW].
    q_set_kvar : float
        Target electrical reactive power in [kVAr].
    step_size : int
        Step size for the net step in [s].
    now_dt: datetime | str | int
        Current timestamp as datetime object, ISO datestring or unix
        timestamp.

    """

    def __init__(self) -> None:
        self.p_set_kw: float | None = None
        self.q_set_kvar: float | None = None
        self.step_size: int = 1
        self._now_dt: float | None = None

    def reset(self) -> None:
        """To be called at the end of each step."""
        for attr in self.__dict__.keys():
            setattr(self, attr, None)

    @property
    def now_dt(self) -> datetime:
        """The current date and time of the model"""
        return self._now_dt

    @now_dt.setter
    def now_dt(self, now: datetime | str | int) -> None:
        self._now_dt = convert_dt(now)
