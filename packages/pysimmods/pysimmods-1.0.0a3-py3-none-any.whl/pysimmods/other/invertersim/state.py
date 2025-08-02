"""This module contains the state model of the inverter."""

from typing import cast

from pysimmods.base.state import ModelState
from pysimmods.base.types import ModelInitVals


class InverterState(ModelState):
    """Inverter state

    Parameters
    ----------
    inits : dict
        A *dict* containing initialization parameters of the inverter.

    Attributes
    ----------
    cos_phi : float
        The cosinus of the phase angle used in the last step.
    inductive: int
        Indicates whether the inverter used inductive (True) or
        capacitive (False) mode in the last step.
    """

    def __init__(self, inits: ModelInitVals):
        super().__init__(inits)

        self.cos_phi: float = cast("float", inits.get("cos_phi", 0.9))
        self._inductive: bool = False

    @property
    def inductive(self) -> int:
        if self._inductive:
            return 1
        else:
            return 0
