from enum import IntEnum

class LogpMethod(IntEnum):
    """
    - CONSENSUS - Consensus model built on the Chemaxon and Klopman et al. models and the PhysProp database
    - CHEMAXON - Chemaxon's own logP model, which is based on the VG method
    """
    CONSENSUS = 0
    CHEMAXON = 1