from typing import Generic

from pysimmods.base.model import C, I, Model, S


class Buffer(Model[C, S, I], Generic[C, S, I]):
    """A buffer subtype model.

    This class provides all required functions for a buffer so that
    derived models only need to provide the step-function. However,
    those functions can be overwritten if needed.

    """

    def get_pn_charge_max_kw(self) -> float:
        """Return nominal maximum charging rate in kW.

        Respects the sign convention with charging rate as positive
        values.
        """
        if hasattr(self.config, "p_charge_max_kw"):
            return getattr(self.config, "p_charge_max_kw") * self.config.lsign
        else:
            return self.config.p_max_kw * self.config.lsign

    def get_pn_charge_min_kw(self) -> float:
        """Return nominal minimum charging rate in kW.

        Respects the sign convention with charging rate as positive
        values.
        """
        if hasattr(self.config, "p_charge_min_kw"):
            return getattr(self.config, "p_charge_min_kw") * self.config.lsign
        else:
            return self.config.p_min_kw * self.config.lsign

    def get_pn_discharge_max_kw(self) -> float:
        """Return nominal maximum discharging rate in kW.

        Respects the sign convention with discharging rate as negative
        values.
        """
        if hasattr(self.config, "p_discharge_max_kw"):
            return (
                getattr(self.config, "p_discharge_max_kw") * self.config.gsign
            )
        else:
            return self.config.p_max_kw * self.config.gsign

    def get_pn_discharge_min_kw(self) -> float:
        """Return nominal minimum charging rate in kW.

        Respects the sign convention with discharging rate as negative
        values.
        """

        if hasattr(self.config, "p_discharge_min_kw"):
            return (
                getattr(self.config, "p_discharge_min_kw") * self.config.gsign
            )
        else:
            return self.config.p_min_kw * self.config.gsign

    def get_pn_min_kw(self) -> float:
        """Minimum power of battery in kW.

        The minimum power is the maximum discharging power in passive
        sign convention.

        """
        if self.config.psc:
            return self.get_pn_discharge_max_kw()
        else:
            return self.get_pn_charge_max_kw()

    def get_pn_max_kw(self) -> float:
        """Maximum power of battery in kW.

        The maximum power is the maximum charging power in passive sign
        convention.

        """
        if self.config.psc:
            return self.get_pn_charge_max_kw()
        else:
            return self.get_pn_discharge_max_kw()

    def set_p_kw(self, p_kw: float) -> None:
        """Set the target active power value.

        With passive sign convention, positive values indicate charging
        and *p_kw* needs to be between pn_charge_min_kw and
        pn_charge_max_kw. Negative values indicate discharging and
        *p_kw* needs to be between pn_discharge_min_kw and
        pn_discharge_max_kw.

        If *p_kw* is lower than the respective min value, it will be set
        to zero. If it is higher than the respective max value, it will
        be set to the max value.

        """
        if self.config.psc and p_kw < 0 or self.config.asc and p_kw > 0:
            # Discharging
            if p_kw < 0:
                p_max = self.get_pn_discharge_min_kw()
                p_min = self.get_pn_discharge_max_kw()
            else:
                p_min = self.get_pn_discharge_min_kw()
                p_max = self.get_pn_discharge_max_kw()
        elif self.config.psc and p_kw > 0 or self.config.asc and p_kw < 0:
            # Charging
            if p_kw < 0:
                p_max = self.get_pn_charge_min_kw()
                p_min = self.get_pn_charge_max_kw()
            else:
                p_min = self.get_pn_charge_min_kw()
                p_max = self.get_pn_charge_max_kw()
        else:
            self.inputs.p_set_kw = 0
            return

        if abs(p_kw) < abs(p_min) and abs(p_kw) < abs(p_max):
            self.inputs.p_set_kw = 0
        else:
            self.inputs.p_set_kw = max(p_min, min(p_max, p_kw))

    def set_q_kvar(self, q_kvar) -> None:
        """Set the target reactive power value.

        Currently, there is no further functionality behind this,
        because there is no buffer model that makes use of reactive
        power.

        """
        self.inputs.q_set_kvar = q_kvar

    def get_p_kw(self) -> float:
        """Return the current active power in kW of this model.

        Respects the current sign convention.
        """
        return self.state.p_kw * self.config.lsign
