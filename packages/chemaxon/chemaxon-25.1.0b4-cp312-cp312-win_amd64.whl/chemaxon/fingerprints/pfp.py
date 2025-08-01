import ctypes

from .._isolate_handler import _cxn, _isolate_handler, _Opaque
from ..molecule import _CMolecule, Molecule
from .fingerprint import _CFloatVectorFingerprint, FloatVectorFingerprint


def pharmacophore_fp(mol: Molecule) -> FloatVectorFingerprint:
    """Pharmacophore fingerprint calculation.

    Pharmacophore fingerprints attempt to model binding related structural or chemical properties of chemical compounds with the use of simple statistics of chemical features. In the case of pharmacophore fingerprints generated these features are always assigned to individual atoms of the molecule thus these fingerprints are atom based pharmacophore fingerprints.

    Link: https://docs.chemaxon.com/display/docs/fingerprints_pharmacophore-fingerprint.md

    Parameters
    ----------
    mol : `Molecule`
        Input molecule

    Returns
    -------
    fingerprint : `FloatVectorFingerprint`
       The generated pharmacophore fingerprint
    """
    thread = _isolate_handler.get_isolate_thread()
    _cxn.pharmacophore_fp.restype = ctypes.c_void_p
    _cxn.pharmacophore_fp.argtypes = [ctypes.POINTER(_Opaque), ctypes.POINTER(_CMolecule)]
    try:
        cmol = mol._to_cmol()
        cresult = _CFloatVectorFingerprint.from_address(
            _cxn.pharmacophore_fp(thread, cmol))
        fp = FloatVectorFingerprint(cresult)
    finally:
        _cxn.free_fp_result(thread)
        _isolate_handler.cleanup_isolate_thread(thread)
    return fp