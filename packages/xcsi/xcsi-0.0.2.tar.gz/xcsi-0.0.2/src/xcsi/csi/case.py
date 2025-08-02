class Case:
    """
    Class to handle case definitions in CSI models.
    """

    def __init__(self, name, csi, model):
        self.csi = csi
        self.model = model

    def apply_loads(self, case: str = None):
        """
        Apply loads to the model for a specific case.
        """
        return self.csi.apply_loads(self.model, case)

    "LOAD CASE DEFINITIONS"
    "CASE - STATIC 2 - NONLINEAR LOAD APPLICATION"