import ctypes

_PRECISION = 2
""":meta private:"""

def _customresize(array, new_size):
    """:meta private:"""
    return (array._type_ * new_size).from_address(ctypes.addressof(array))
