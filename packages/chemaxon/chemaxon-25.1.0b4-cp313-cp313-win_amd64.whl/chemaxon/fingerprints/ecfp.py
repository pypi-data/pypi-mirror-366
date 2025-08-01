import ctypes

from .._isolate_handler import _cxn, _isolate_handler, _Opaque
from ..molecule import _CMolecule, Molecule
from .fingerprint import _CFingerprint, Fingerprint


def ecfp(mol: Molecule, diameter: int, length: int) -> Fingerprint:
    """ECFP fingerprint calculation.

    Extended-Connectivity Fingerprints (ECFPs) are circular topological fingerprints designed for molecular characterization, similarity searching, and structure-activity modeling. They are among the most popular similarity search tools in drug discovery and they are effectively used in a wide variety of applications.

    Link: https://docs.chemaxon.com/display/docs/fingerprints_extended-connectivity-fingerprint-ecfp.md

    Parameters
    ----------
    mol : `Molecule`
        Input molecule
    diameter : `int`
        It specifies the diameter of the circular neighborhood considered for each atom
    length : `int`
        Sets the length of the ECFP fingerprint

    Returns
    -------
    fingerprint : `Fingerprint`
       The generated ECFP fingerprint
    """
    thread = _isolate_handler.get_isolate_thread()
    _cxn.ecfp.restype = ctypes.c_void_p
    _cxn.ecfp.argtypes = [ctypes.POINTER(_Opaque), ctypes.POINTER(_CMolecule), ctypes.c_int, ctypes.c_int]
    try:
        cmol = mol._to_cmol()
        cresult = _CFingerprint.from_address(_cxn.ecfp(thread, cmol, diameter, length))
        fp = Fingerprint(cresult)
    finally:
        _cxn.free_ecfp(thread)
        _isolate_handler.cleanup_isolate_thread(thread)
    return fp
