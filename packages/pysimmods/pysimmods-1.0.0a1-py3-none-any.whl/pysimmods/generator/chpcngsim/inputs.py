"""This module contains the input model for the chp."""

from pysimmods.base.inputs import ModelInputs


class CHPCNGInputs(ModelInputs):
    """A CHP CNG input class.

    Attributes
    ----------
    gas_in_m3: float
        Available gas (e.g., from a gas storage) in [m^3].
    gas_critical: bool
        If set to True, this unit will reduce generation.
    heat_critical: bool
        If set to True, this unit will increase generation. Has lower
        priority than gas_critical
    """

    def __init__(self):
        super().__init__()

        self.gas_in_m3: float = 0.0
        self.gas_critical = False
        self.heat_critical = False

    def reset(self):
        """To be called at the end of each step."""
        # for attr in self.__dict__.keys():
        #     setattr(self, attr, None)
        self.gas_in_m3 = 0.0
        self.gas_critical = False
        self.heat_critical = False
