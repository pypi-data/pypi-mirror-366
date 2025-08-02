"""This module contains the base config used by each model."""

from pysimmods.base.types import ModelParams


class ModelConfig:
    """The base config for all models.

    Parameters
    ----------
    params: dict
        A *dict* containing configuration parameters. See *Attributes*
        for detailed information

    Attributes
    ----------
    sign_convention: str
        Should be defined in *params* and can have the values
        *'passive'* or *'active'*. Passive sign convention aka load
        reference arrow system is normally used and leads to positive
        consumption and negative generation power flows.
    psc: bool
        Will be automatically set to *True* if passive sign convention
        is used.
    asc: bool
        Will be automatically set to *True* if active sign convention is
        used.
    gsign: int
        The generator sign depending on the sign convention. Will be
        set to *-1* if passive sign convention is used and to *1*
        otherwise.
    lsign: int
        The load sign depending on the sign convention. Will be set to
        *1* is passive sign convention is used and to *-1* otherwise.
    use_decimal_percent: bool
        If *True* decimal percentage [0, 1.0] is used, otherwise normal
        percentage [0, 100] ist used.
    default_p_schedule: List[float]
        A *list* containing a default schedule for active power for
        each hour of the day (i.e., len(default_schedule) == 24). This
        is used if no other *p* input is provided.
    default_q_schedule: List[float]
        A *list* containing a default schedule for reactive power for
        each hour of the day (i.e., len(default_schedule) == 24). This
        is used if no other *q* input is provided.
    p_min_kw: float
        The minimum nominal active power output of the model.
    p_max_kw: float
        The maximum nominal active power output of the model.
    q_min_kvar: float
        The minimum nominal reactive power output of the model.
    q_max_kvar: float
        The maximum nominal reactive power output of the model.
    s_min_kva: float
        The minimal nominal apparent power output of the model.
    s_max_kva: float
        The maximal nominal apparent power output of the model.

    """

    def __init__(self, params: ModelParams) -> None:
        self.sign_convention = params.get("sign_convention", "passive")
        if self.sign_convention not in ["active", "passive"]:
            msg = (
                f"Invalid sign convention {self.sign_convention}. "
                "Allowed values are 'active' and 'passive'"
            )
            raise ValueError(msg)

        self.psc = self.sign_convention == "passive"
        self.asc = self.sign_convention == "active"

        if self.sign_convention == "active":
            self.gsign = 1
            self.lsign = -1
        else:
            self.gsign = -1
            self.lsign = 1

        self.use_decimal_percent = params.get("use_decimal_percent", False)
        self.default_p_schedule = params.get("default_p_schedule", [0.0] * 24)
        self.default_q_schedule = params.get("default_q_schedule", [0.0] * 24)

        self.p_min_kw: float = 0.0
        self.p_max_kw: float = 0.0
        self.q_min_kvar: float = 0.0
        self.q_max_kvar: float = 0.0
        self.s_min_kva: float = 0.0
        self.s_max_kva: float = 0.0
