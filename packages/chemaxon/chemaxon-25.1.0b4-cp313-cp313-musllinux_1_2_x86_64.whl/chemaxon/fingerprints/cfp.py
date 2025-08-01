import ctypes

from .._isolate_handler import _cxn, _isolate_handler, _Opaque
from .fingerprint import _CFingerprint, Fingerprint
from ..molecule import _CMolecule, Molecule



def cfp(mol: Molecule, bondCount: int = 7, bitsPerPattern: int = 3, length: int = 1024,
        considerRings: bool = True) -> Fingerprint:
    """CFP fingerprint calculation.

    The chemical hashed fingerprint of a molecule is bit string (a sequence of 0 and 1 digits) that contains information on the structure.

    Link: https://docs.chemaxon.com/display/docs/fingerprints_chemical-hashed-fingerprint.md

    Parameters
    ----------
    mol : `Molecule`
        Input molecule
    bondCount : `int`
        The maximum length of consecutive bonds in the linear paths that are considered during the fragmentation
        of the molecule
    bitsPerPattern : `int`
        The number of bits used to code each pattern in the hashed binary vector representation
    length : `int`
        Default length (bit count) for CFP - folded binary fingerprint representation
    considerRings : `bool`

    Returns
    -------
    fingerprint : `Fingerprint`
       The generated CFP fingerprint
    """
    thread = _isolate_handler.get_isolate_thread()
    _cxn.cfp.restype = ctypes.c_void_p
    _cxn.cfp.argtypes = [ctypes.POINTER(_Opaque), ctypes.POINTER(_CMolecule), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_bool]
    try:
        cmol = mol._to_cmol()
        cresult = _CFingerprint.from_address(
            _cxn.cfp(thread, cmol, bondCount, bitsPerPattern, length, considerRings))
        fp = Fingerprint(cresult)
    finally:
        _cxn.free_cfp(thread)
        _isolate_handler.cleanup_isolate_thread(thread)
    return fp