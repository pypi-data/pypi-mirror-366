import ctypes
import json

from ._isolate_handler import _isolate_handler, _cxn, _Opaque
from ._exception_util import _CStringWithExceptionData, _StringWithExceptionData

def ccl_version() -> str:
    """Chemaxon Core Library (CCL) version

    Returns
    -------
    version : `str`
       The underlying CCL version, e.g. 23.5.1
    """
    thread = _isolate_handler.get_isolate_thread()
    _cxn.ccl_version.restype = ctypes.c_char_p
    _cxn.ccl_version.argtypes = [ctypes.POINTER(_Opaque)]
    try:
        result = _cxn.ccl_version(thread)
    finally:
        _cxn.free_ccl_version(thread)
        _isolate_handler.cleanup_isolate_thread(thread)
    return result.decode("utf-8")

def ccl_build_date() -> str:
    """Chemaxon Core Library (CCL) build date

    Returns
    -------
    version : `str`
       The underlying CCL build date, e.g. 2023-10-12
    """
    thread = _isolate_handler.get_isolate_thread()
    _cxn.ccl_build_date.restype = ctypes.c_char_p
    _cxn.ccl_build_date.argtypes = [ctypes.POINTER(_Opaque)]
    try:
        result = _cxn.ccl_build_date(thread)
    finally:
        _cxn.free_ccl_build_date(thread)
        _isolate_handler.cleanup_isolate_thread(thread)
    return result.decode("utf-8")

def licenses() -> list:
    """The imported Chemaxon licenses

    Returns
    -------
    version : `list`
       The list of available licenses
    """
    thread = _isolate_handler.get_isolate_thread()
    _cxn.licenses.restype = ctypes.c_char_p
    _cxn.licenses.argtypes = [ctypes.POINTER(_Opaque)]
    try:
        result = _cxn.licenses(thread)
    finally:
        _cxn.free_licenses(thread)
        _isolate_handler.cleanup_isolate_thread(thread)
    return json.loads(result.decode("utf-8"))

def _charset_test() -> str:
    """tests Charset support.

    Returns
    -------
    loadedCharsets : `str`
       test string
    """
    thread = _isolate_handler.get_isolate_thread()
    _cxn.charset_test.restype = ctypes.c_char_p
    try:
        result = _cxn.charset_test(thread)
    finally:
        _cxn.free_charsets(thread)
        _isolate_handler.cleanup_isolate_thread(thread)
    return result.decode("utf-8")
