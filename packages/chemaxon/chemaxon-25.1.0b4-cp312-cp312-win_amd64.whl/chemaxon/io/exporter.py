import ctypes

from .._isolate_handler import _isolate_handler, _cxn, _Opaque
from ..molecule import Molecule, _CMolecule
from .._exception_util import _CStringWithExceptionData, _StringWithExceptionData


def export_mol(mol: Molecule, format: str) -> str:
    """Molecule export

    You can find more information about file formats and options on the following link: https://docs.chemaxon.com/display/docs/formats_index.md

    Here you can find the supported formats: https://docs.chemaxon.com/display/docs/python-api_limitations.md

    Parameters
    ----------
    mol : `Molecule`
       Input molecule
    format : `str`
       This option is to specify the format and options for the export

    Returns
    -------
    exported : `str`
       The exported molecule
    """
    thread = _isolate_handler.get_isolate_thread()
    _cxn.export_mol.argtypes = [ctypes.POINTER(_Opaque), ctypes.POINTER(_CMolecule), ctypes.c_char_p]
    _cxn.export_mol.restype = ctypes.c_void_p
    cmol = mol._to_cmol()
    try:
        c_output = _CStringWithExceptionData.from_address(
            _cxn.export_mol(thread, ctypes.byref(cmol), format.encode("utf-8")))
        output = _StringWithExceptionData(c_output)
        result = output.result_str.decode("utf-8")
    finally:
        _cxn.free_export_mol_result(thread)
        _isolate_handler.cleanup_isolate_thread(thread)
    return result

