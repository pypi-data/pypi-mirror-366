import ctypes

from .logp_method import LogpMethod
from .._util import _customresize, _PRECISION
from .._isolate_handler import _isolate_handler, _cxn, _Opaque
from ..molecule import _CMolecule, Molecule
from .._exception_util import _CExceptionData, _checkException

class _CLogPResult(ctypes.Structure):
    """:meta private:"""
    _fields_ = [("logp", ctypes.c_double),
                ("length", ctypes.c_int),
                ("indices", ctypes.c_int * _CMolecule.MAX_ATOM_OR_BOND_COUNT),
                ("logp_by_atoms", ctypes.c_double * _CMolecule.MAX_ATOM_OR_BOND_COUNT),
                ("exception_data", ctypes.POINTER(_CExceptionData))
                ]


class LogPResult:
    """LogPResult

    Attributes
    ----------
    logp: `float`
        The calculated logp value
    logp_by_atoms: `dict`
        The logp values by atom indexes
    """
    def __init__(self, result: _CLogPResult):
        _checkException(result)
        self.logp = round(result.logp, _PRECISION)
        if result.length != 0:
            c_logp_by_atoms = _customresize(result.logp_by_atoms, result.length)
            c_indices = _customresize(result.indices, result.length)
            self.logp_by_atoms = {c_indices[i]:round(c_logp_by_atoms[i], _PRECISION) for i in range(result.length)}
        else:
            self.logp_by_atoms = None


def logp_by_atoms(mol: Molecule, method: LogpMethod = LogpMethod.CONSENSUS, anion: float = 0.1, kation: float = 0.1, consider_tautomerization: bool = False, ph: float = -1) -> LogPResult:
    """logP by atoms calculation.

    The logp function calculates the logarithm of the octanol/water partition coefficient (logP), which is used in QSAR analysis and rational drug design as a measure of molecular lipophylicity/hydrophobicity.

    Link: https://docs.chemaxon.com/display/docs/calculators_logp-plugin.md

    Parameters
    ----------
    mol : `Molecule`
        Input molecule
    method : `LogpMethod`
        This option is for selecting the applied method for the logP prediction:
        - CONSENSUS: Consensus model built on the Chemaxon and Klopman et al. models and the PhysProp database
        - CHEMAXON:  Chemaxon's own logP model, which is based on the VG method
    anion : `float`
        Cl- concentration
    kation : `float`
        Na+ K+ concentration
    consider_tautomerization: `bool`
        In case of tautomer structures, all dominant tautomers at the given pH are taken into account
        during the logP calculation
    pH : `float`
        Calculates logP value at this pH

    Returns
    -------
    logP : `LogPResult`
       The calculated logP
    """
    thread = _isolate_handler.get_isolate_thread()
    _cxn.logP.restype = ctypes.c_void_p
    _cxn.logP.argtypes = [ctypes.POINTER(_Opaque), ctypes.POINTER(_CMolecule), ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_bool, ctypes.c_double, ctypes.c_bool]
    cmol = mol._to_cmol()
    try:
        c_result = _CLogPResult.from_address(
            _cxn.logP(thread, cmol, method, anion, kation, consider_tautomerization, ph, True))
        result = LogPResult(c_result)
    finally:
        _cxn.free_logp_result(thread)
        _isolate_handler.cleanup_isolate_thread(thread)
    return result


def logp(mol: Molecule, method: LogpMethod = LogpMethod.CONSENSUS, anion: float = 0.1, kation: float = 0.1, consider_tautomerization: bool = False, ph: float = -1) -> float:
    """logP calculation.

    The logp function calculates the logarithm of the octanol/water partition coefficient (logP), which is used in QSAR analysis and rational drug design as a measure of molecular lipophylicity/hydrophobicity.

    Link: https://docs.chemaxon.com/display/docs/calculators_logp-plugin.md

    Parameters
    ----------
    mol : `Molecule`
        Input molecule
    method : `LogpMethod`
        This option is for selecting the applied method for the logP prediction:
        - CONSENSUS: Consensus model built on the Chemaxon and Klopman et al. models and the PhysProp database
        - CHEMAXON:  Chemaxon's own logP model, which is based on the VG method
    anion : `float`
        Cl- concentration
    kation : `float`
        Na+ K+ concentration
    consider_tautomerization: `bool`
        In case of tautomer structures, all dominant tautomers at the given pH are taken into account
        during the logP calculation
    pH : `float`
        Calculates logP value at this pH

    Returns
    -------
    logP : `float`
       The calculated logP
    """
    thread = _isolate_handler.get_isolate_thread()
    _cxn.logP.restype = ctypes.c_void_p
    _cxn.logP.argtypes = [ctypes.POINTER(_Opaque), ctypes.POINTER(_CMolecule), ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_bool, ctypes.c_double, ctypes.c_bool]
    cmol = mol._to_cmol()
    try:
        c_result = _CLogPResult.from_address(
            _cxn.logP(thread, cmol, method, anion, kation, consider_tautomerization, ph, False))
        result = LogPResult(c_result)
    finally:
        _cxn.free_logp_result(thread)
        _isolate_handler.cleanup_isolate_thread(thread)
    return result.logp