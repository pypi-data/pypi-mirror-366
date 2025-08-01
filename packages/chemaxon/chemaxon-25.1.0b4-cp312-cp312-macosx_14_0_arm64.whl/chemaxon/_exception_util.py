import ctypes

import logging

logger = logging.getLogger(__name__)


class _CExceptionData(ctypes.Structure):
    """:meta private:"""
    _fields_ = [
        ("exception", ctypes.c_char_p),
        ("stacktrace", ctypes.c_char_p)
    ]

class _CStringWithExceptionData(ctypes.Structure):
    """
    Class storing string (char*) result. Structured data is needed instead of the primitive to be able to store
    exception data. This class is in this general file because it is used in many calculations.
    """
    _fields_ = [("result_str", ctypes.c_char_p),
                ("exception_data", ctypes.POINTER(_CExceptionData))
                ]


class _StringWithExceptionData:
    def __init__(self, cresult: _CStringWithExceptionData):
        _checkException(cresult)
        self.result_str = cresult.result_str


class _CDoubleWithExceptionData(ctypes.Structure):
    """
    Class storing double result. Structured data is needed instead of the primitive to be able to store
    exception data. This class is in this general file because it is used in many calculations.
    """
    _fields_ = [("result_double", ctypes.c_double),
                ("exception_data", ctypes.POINTER(_CExceptionData))
                ]


class _DoubleWithExceptionData:
    def __init__(self, cresult: _CDoubleWithExceptionData):
        _checkException(cresult)
        self.result_double = cresult.result_double


def _checkException(cresult):
    """
    :meta private:
    Checks for exceptions in the native code and set as exception parameter on the provided result.
    The native stacktrace is the message of a cause exception.

    Parameters
    ----------
    cresult :
        the result object of the native code. Must have an exception field
    Raises
    ----------
    ValueError
        Raised if the parameter doesn't have an exception field
    RuntimeError
        Raised if there was an exception in the native code
    """
    if hasattr(cresult, 'exception_data'):
        exceptionMsg = cresult.exception_data.contents.exception.decode("utf-8")
        if exceptionMsg != "OK":
            stacktrace = cresult.exception_data.contents.stacktrace.decode("utf-8")
            nativeExc = RuntimeError(f'{exceptionMsg}\n\n{stacktrace}')
            raise RuntimeError("Error in chemaxon native library call: " + exceptionMsg) from nativeExc
    else:
        raise ValueError(
            'Parameter cresult should have an exception field. Was called on an instance of ' + cresult.__name__)
