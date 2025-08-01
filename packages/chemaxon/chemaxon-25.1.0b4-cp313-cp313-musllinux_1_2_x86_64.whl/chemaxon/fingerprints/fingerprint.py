import ctypes
from .._util import _customresize
from .._exception_util import _CExceptionData, _checkException

class _CFingerprint(ctypes.Structure):
    """:meta private:"""
    _fields_ = [("length", ctypes.c_int),
                ("array", ctypes.c_ulonglong * 32),  # 64 * 32 = 2048 bit
                ("exception_data", ctypes.POINTER(_CExceptionData))
                ]

class Fingerprint:
    """Fingerprint

    Attributes
    ----------
    length: `int`
        Length of the array
    cresult: `CFingerprint`
        Fingerprint - every bit of every long in the array represents a fingerprint bit and exception data
    """

    def __init__(self, cresult: _CFingerprint):
        _checkException(cresult)
        self.length = cresult.length
        array = _customresize(cresult.array, self.length)
        self.array = [array[i] for i in range(self.length)]

    def to_bytes(self):
        """
        Returns
        -------
        bytes: `list[bytes]`
            The byte representation of the fingerprint
        """
        return [l.to_bytes(length=64) for l in self.array]

    def to_binary_string(self):
        """
        Returns
        -------
        binary_string: `str`
            The binary string representation of the fingerprint
        """
        return [bin(l)[2:].zfill(64) for l in self.array]

    def darkness(self):
        """
        Returns
        -------
        darkness: `int`
            The count of 1 bits in the fingerprint
        """
        return sum([bs.count('1') for bs in self.to_binary_string()])

class _CFloatVectorFingerprint(ctypes.Structure):
    """:meta private:"""
    _fields_ = [("length", ctypes.c_int),
                ("array", ctypes.c_float * 1000),
                ("exception_data", ctypes.POINTER(_CExceptionData))
                ]

class FloatVectorFingerprint:
    """FloatVectorFingerprint

    Attributes
    ----------
    length: `int`
        Length of the array
    cresult: `CFloatVectorFingerprint`
        Fingerprint object - fingerprint and exception data
    """

    def __init__(self, cresult: _CFloatVectorFingerprint):
        _checkException(cresult)
        self.length = cresult.length
        array = _customresize(cresult.array, self.length)
        self.array = [array[i] for i in range(self.length)]
