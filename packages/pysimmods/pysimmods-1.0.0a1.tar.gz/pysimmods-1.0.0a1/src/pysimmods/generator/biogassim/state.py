"""This module contains the state model of the Biogas plant."""

from pysimmods.base.state import ModelState
from pysimmods.base.types import ModelInitVals


class BiogasState(ModelState):
    """State parameters of the biogas plant model.

    This class captures the state of the biogas model. States normally
    change during the step-method of this model.

    Parameters
    ----------
    inits: dict
        A dictionary containing initialization parameters for the
        biogas model. The :attr:`gas_fill_percent` is the only
        model-specific key that ist required.

    Attributes
    ----------
    gas_fill_percent: float
        Current level of the gas storage in [%].
    gas_prod_m3: float
        Amount of gas produced in current step in [m^3].
    gas_cons_m3: float
        Amount of gas consumed in the current step in [m^3].
    p_th_kw: float
        Thermal power output in [kW].
    gas_critical: bool, optional
        Is true, when storage boundaries are exceeded.
    burn_gas: bool, optional
        Is true, when the upper storage boundary is exceeded.
        Resets to False, when gas_fill_percent gets below 60 %.
    pool_gas: bool, optional
        Is true, when the lower storage boundary is exceeded.
        Resets to False, when gas_fill_percent gets above 40 %.

    """

    def __init__(self, inits: ModelInitVals):
        super().__init__(inits)
        self.gas_fill_percent: float = inits["gas_fill_percent"]
        self.gas_prod_m3: float = inits.get("gas_prod_m3", 0.0)
        self.gas_cons_m3: float = inits.get("gas_cons_m3", 0.0)
        self.p_th_kw: float = inits.get("p_th_kw", 0.0)
        self.gas_critical: bool = inits.get("gas_critical", False)
        self.burn_gas: bool = inits.get("burn_gas", False)
        self.pool_gas: bool = inits.get("pool_gas", False)
