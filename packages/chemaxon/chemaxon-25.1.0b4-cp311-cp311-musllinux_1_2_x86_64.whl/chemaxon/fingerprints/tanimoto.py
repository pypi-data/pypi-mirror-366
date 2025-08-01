import ctypes

from .._isolate_handler import _cxn, _isolate_handler
from .fingerprint import Fingerprint, FloatVectorFingerprint
from .._exception_util import _CDoubleWithExceptionData, _DoubleWithExceptionData

def tanimoto(fp1: Fingerprint, fp2: Fingerprint) -> float:
    """Calculates the Tanimoto coefficient of the two Fingerprint.

    Parameters
    ----------
    fp1 : `Fingerprint`
        First fingerprint
    fp2 : `Fingerprint`
        Second fingerprint

    Returns
    -------
    tanimoto : `float`
       The calculated Tanimoto coefficient
    """
    thread = _isolate_handler.get_isolate_thread()
    carray1 = (ctypes.c_ulonglong * fp1.length)()
    carray2 = (ctypes.c_ulonglong * fp2.length)()
    for i in range(fp1.length):
        carray1[i] = fp1.array[i]
        carray2[i] = fp2.array[i]
    _cxn.tanimoto.restype = ctypes.c_void_p
    try:
        ctanimoto = _CDoubleWithExceptionData.from_address(_cxn.tanimoto(thread, carray1, carray2, fp1.length))
        tanimoto = _DoubleWithExceptionData(ctanimoto).result_double
    finally:
        _cxn.free_tanimoto_result(thread)
        _isolate_handler.cleanup_isolate_thread(thread)
    return tanimoto

def float_vector_tanimoto(fp1: FloatVectorFingerprint, fp2: FloatVectorFingerprint) -> float:
    """Calculates the Tanimoto coefficient of the two Fingerprint.

    Parameters
    ----------
    fp1 : `FloatVectorFingerprint`
        First fingerprint
    fp2 : `FloatVectorFingerprint`
        Second fingerprint

    Returns
    -------
    tanimoto : `float`
       The calculated Tanimoto coefficient
    """
    thread = _isolate_handler.get_isolate_thread()
    carray1 = (ctypes.c_float * fp1.length)()
    carray2 = (ctypes.c_float * fp2.length)()
    for i in range(fp1.length):
        carray1[i] = fp1.array[i]
        carray2[i] = fp2.array[i]
    _cxn.float_vector_tanimoto.restype = ctypes.c_void_p
    try:
        ctanimoto = _CDoubleWithExceptionData.from_address(
            _cxn.float_vector_tanimoto(thread, carray1, carray2, fp1.length))
        tanimoto = _DoubleWithExceptionData(ctanimoto).result_double
    finally:
        _cxn.free_tanimoto_result(thread)
        _isolate_handler.cleanup_isolate_thread(thread)
    return tanimoto
