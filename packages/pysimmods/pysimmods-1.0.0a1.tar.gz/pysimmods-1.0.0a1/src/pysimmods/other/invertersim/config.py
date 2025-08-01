"""This module contains the config model for the inverter."""

from typing import cast

from pysimmods.base.config import ModelConfig
from pysimmods.base.types import ModelInitVals, ModelParams, QControl


class InverterConfig(ModelConfig):
    """Inverter config

    Parameter
    ---------
    params : dict
        Contains configuration parameters of the inverter. See
        *attributes* section for more information.

    Attributes
    ----------
    sn_kva : float
        Nominal apparent power of the inverter in [kVA].
    q_control : str, optional
        Set the mode for the inverter. Can be either `prioritize_p` or
        `prioritize_q`, with the first being the default value.
        See :class:`~.Inverter` for more information
        about the different modes.
    cos_phi : float, optional
        Cosinus of the phase angle for *q_control* modes with constant
        *cos_phi*. Default is 0.9.
    inverter_mode : str, optional
        Specifies whether the inverter is *'capacitive'* or
        *'inductive'*. Default is *'capacitive'*.

    """

    def __init__(self, params: ModelParams):
        super().__init__(params)

        self.s_max_kva: float = cast("float", params["sn_kva"])
        self.q_control = QControl[
            params.get("q_control", "prioritize_p").upper()
        ]
        self.cos_phi: float = cast("float", params.get("cos_phi", 0.95))
        self.inverter_mode: str = cast(
            "str", params.get("inverter_mode", "capacitive")
        )
