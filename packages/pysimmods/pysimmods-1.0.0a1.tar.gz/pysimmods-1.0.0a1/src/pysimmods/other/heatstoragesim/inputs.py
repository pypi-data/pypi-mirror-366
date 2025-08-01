from pysimmods.generator.windsystemsim.inputs import ModelInputs


class HeatStorageInputs(ModelInputs):
    """Captures the inputs of the heat storage"""

    def __init__(self):

        self.e_th_prod_kwh: float = 0.0
        self.e_th_demand_kwh: float = 0.0