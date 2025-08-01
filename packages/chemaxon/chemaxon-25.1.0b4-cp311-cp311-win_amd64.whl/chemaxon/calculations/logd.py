import ctypes

from .logp_method import LogpMethod
from .._isolate_handler import _isolate_handler, _cxn, _Opaque
from .._util import _PRECISION
from ..molecule import _CMolecule, Molecule
from .._exception_util import _CDoubleWithExceptionData, _DoubleWithExceptionData

def logd(mol: Molecule, pH: float = 7.4, method: LogpMethod = LogpMethod.CONSENSUS,
         consider_tautomerization: bool = False) -> float:
    """logD calculation.

    Compounds having ionizable groups exist in solution as a mixture of different ionic forms. The ionization of those groups, thus the ratio of the ionic forms depends on the pH. Since logP describes the hydrophobicity of one form only, the apparent logP value can be different. The logD represents the octanol-water coefficient of compounds at a given pH value.

    Link: https://docs.chemaxon.com/display/docs/calculators_logd-plugin.md

    Parameters
    ----------
    mol : `Molecule`
       Input molecule
    pH : `float`
       Calculates logD value at this pH
    method : `LogpMethod`
       This option is for selecting the applied method for the logP prediction:
        - CONSENSUS
        - CHEMAXON
    consider_tautomerization: `bool`
       In case of tautomer structures, all dominant tautomers at the given pH are taken into account
       during the logD calculation

    Returns
    -------
    logD : `float`
       The calculated logD value
    """
    thread = _isolate_handler.get_isolate_thread()
    _cxn.logD.restype = ctypes.c_void_p
    _cxn.logD.argtypes = [ctypes.POINTER(_Opaque), ctypes.POINTER(_CMolecule), ctypes.c_double, ctypes.c_int,
                         ctypes.c_bool]
    try:
        cmol = mol._to_cmol()
        cresult = _CDoubleWithExceptionData.from_address(_cxn.logD(thread, cmol, pH, method, consider_tautomerization))
        result = _DoubleWithExceptionData(cresult)
    finally:
        _cxn.free_logd_result(thread)
        _isolate_handler.cleanup_isolate_thread(thread)
    return round(result.result_double, _PRECISION)
