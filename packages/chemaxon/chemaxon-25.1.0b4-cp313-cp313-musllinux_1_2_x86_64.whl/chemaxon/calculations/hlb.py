import ctypes
from enum import IntEnum

from .._isolate_handler import _isolate_handler, _cxn, _Opaque
from .._util import _PRECISION
from ..molecule import _CMolecule, Molecule
from .._exception_util import _CDoubleWithExceptionData, _DoubleWithExceptionData


class HlbMethod(IntEnum):
    """
    - CHEMAXON - This is a consensus method based on the other two methods with optimal weights
    - DAVIES - This is an extended version of the Davies method
    - GRIFFIN - This is an extended version of the Griffin method
    - REQUIRED - Experimental value, characteristic to the compound used in (O/W) emulsions
    """
    CHEMAXON = 0
    DAVIES = 1
    GRIFFIN = 2
    REQUIRED = 3


def hlb(mol: Molecule, method: HlbMethod = HlbMethod.CHEMAXON) -> float:
    """Hydrophilic-lipophilic balance calculation.

    The hydrophilic-lipophilic balance number (HLB number) measures the degree of a molecule being hydrophilic or lipophilic. This number is calculated based on identifying various hydrophil and liphophil regions in the molecule. This number is a commonly used descriptor in any workflow in which lipid based delivery can be an option (e.g. lipid-based drug delivery, cosmetics).

    Link: https://docs.chemaxon.com/display/docs/calculators_hlb-predictor.md

    Parameters
    ----------
    mol : `Molecule`
       Input molecule
    method : `HlbMethod`
       This option is for selecting the applied method for the HLB calculation:
        - CHEMAXON
        - DAVIES
        - GRIFFIN
        - REQUIRED

    Returns
    -------
    hlb : `float`
       The calculated HLB value
    """
    thread = _isolate_handler.get_isolate_thread()
    _cxn.hlb.restype = ctypes.c_void_p
    _cxn.hlb.argtypes = [ctypes.POINTER(_Opaque), ctypes.POINTER(_CMolecule), ctypes.c_int]
    try:
        cmol = mol._to_cmol()
        cresult = _CDoubleWithExceptionData.from_address(_cxn.hlb(thread, cmol, method))
        result = _DoubleWithExceptionData(cresult)
    finally:
        _cxn.free_hlb_result(thread)
        _isolate_handler.cleanup_isolate_thread(thread)
    return round(result.result_double, _PRECISION)
