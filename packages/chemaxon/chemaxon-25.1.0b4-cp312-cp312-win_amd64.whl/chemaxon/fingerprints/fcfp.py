import ctypes

from .._isolate_handler import _cxn, _isolate_handler, _Opaque
from ..molecule import _CMolecule, Molecule
from .fingerprint import _CFingerprint, Fingerprint


def fcfp(mol: Molecule, diameter: int, length: int) -> Fingerprint:
    """FCFP fingerprint calculation.

    The default identifier configuration of ECFP captures highly specific atomic information enabling the representation of a large set of precisely defined structural features. In some applications, however, different kinds of abstraction may be desirable.
    The variants of ECFPs that applies generalizations and have focus on the functional roles of the atoms instead of full specificity are calledFunctional-Class Fingerprints (FCFPs).

    Link: https://docs.chemaxon.com/display/docs/fingerprints_extended-connectivity-fingerprint-ecfp.md#src-1806333-safe-id-rxh0zw5kzwrdb25uzwn0axzpdhlgaw5nzxjwcmludevdrlatrnvuy3rpb25hbc1dbgfzc0zpbmdlcnbyaw50cyhgq0zqcyk

    Parameters
    ----------
    mol : `Molecule`
        Input molecule
    diameter : `int`
        It specifies the diameter of the circular neighborhood considered for each atom
    length : `int`
        Sets the length of the FCFP fingerprint

    Returns
    -------
    fingerprint : `Fingerprint`
       The generated FCFP fingerprint
    """
    thread = _isolate_handler.get_isolate_thread()
    _cxn.fcfp.restype = ctypes.c_void_p
    _cxn.fcfp.argtypes = [ctypes.POINTER(_Opaque), ctypes.POINTER(_CMolecule), ctypes.c_int, ctypes.c_int]
    try:
        cmol = mol._to_cmol()
        cresult = _CFingerprint.from_address(_cxn.fcfp(thread, cmol, diameter, length))
        fp = Fingerprint(cresult)
    finally:
        _cxn.free_ecfp(thread) # ecfp and fcfp are both released by this call.
        _isolate_handler.cleanup_isolate_thread(thread)
    return fp