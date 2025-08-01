"""This module contains the state model for the PV system."""

from typing import cast

from pysimmods.base.state import ModelState
from pysimmods.base.types import ModelInitVals


class PVSystemState(ModelState):
    """State variables of PV plant system model.

    Parameters
    ----------
    inits : dict
        A *dict* containing initialization parameters.

    Attributes
    ----------
    t_module_deg_celsius : float
        See :attr:`~.PVState.t_module_deg_celsius`
    p_kw : float
        See :attr:`~.ModelState.p_kw`
    q_kvar : float
        See :attr:`~.ModelState.q_kvar`
    p_possible_max_kw: float
        Power output of the PV module before inverter gets active.
    inverter_inductive: int
        1 if inverter mode was inductive, else 0
    """

    def __init__(self, inits: ModelInitVals):
        super().__init__(inits)

        self.t_module_deg_celsius: float = cast(
            "float", cast("ModelInitVals", inits["pv"])["t_module_deg_celsius"]
        )
        self.p_possible_max_kw: float = 0.0
        self.cos_phi: float = 0.0
        self.inverter_inductive: int = 0
