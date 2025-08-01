import ctypes

from .._isolate_handler import _isolate_handler, _cxn, _Opaque
from ..molecule import _CMolecule, Molecule
from .._exception_util import _CStringWithExceptionData, _StringWithExceptionData


def chemterm(mol: Molecule, chemterm: str) -> str:
    """Chemterm function.

    Chemaxon's Chemical Terms is a language for adding advanced chemical intelligence to cheminformatics applications.

    Chemical Terms provides chemistry and mathematical functions including:
      - property predictions
      - functional group recognition
      - isomer enumeration
      - conformer selection
      - ring and distance based topological functions
      - other electronical, steric and structural functions

    Link: https://docs.chemaxon.com/display/docs/chemical-terms_index.md

    Parameters
    ----------
    mol : `Molecule`
        Input molecule
    chemterm: `str`
        chemterm function

    Returns
    -------
    result : `str`
    """
    thread = _isolate_handler.get_isolate_thread()
    _cxn.chemterm.restype = ctypes.c_void_p
    _cxn.chemterm.argtypes = [ctypes.POINTER(_Opaque), ctypes.POINTER(_CMolecule), ctypes.c_char_p]
    cmol = mol._to_cmol()
    try:
        cresult = _CStringWithExceptionData.from_address(_cxn.chemterm(thread, cmol, chemterm.encode("utf-8")))
        result = _StringWithExceptionData(cresult)
    finally:
        _cxn.free_chemterm_result(thread)
        _isolate_handler.cleanup_isolate_thread(thread)
    return result.result_str.decode("utf-8")
