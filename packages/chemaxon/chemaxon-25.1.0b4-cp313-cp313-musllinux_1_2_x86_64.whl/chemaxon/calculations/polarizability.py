import ctypes

from .._isolate_handler import _isolate_handler, _cxn, _Opaque
from ..molecule import _CMolecule, Molecule
from .._util import _PRECISION
from .._exception_util import _CExceptionData, _checkException


class _CPolarizabilityResult(ctypes.Structure):
    """:meta private:"""
    _fields_ = [("molecular_polarizability", ctypes.c_double),
                ("length", ctypes.c_int),
                ("atom_indexes", ctypes.c_int * _CMolecule.MAX_ATOM_OR_BOND_COUNT),
                ("atomic_polarizability", ctypes.c_double * _CMolecule.MAX_ATOM_OR_BOND_COUNT),
                ("exception_data", ctypes.POINTER(_CExceptionData))
                ]


class PolarizabilityResult:
    """PolarizabilityResult

    Attributes
    ----------
    molecular_polarizability : `float`
       The calculated molecular value
    atomic_polarizability : `dict`
        Atomic polarizability values by atom indexes
    """
    def __init__(self, result: _CPolarizabilityResult):
        _checkException(result)
        self.molecular_polarizability = round(result.molecular_polarizability, _PRECISION)
        if result.length != 0:
            self.atomic_polarizability = {result.atom_indexes[i]: round(result.atomic_polarizability[i], 2) for i in range(result.length)}
        else:
            self.atomic_polarizability = None


def atomic_polarizability(mol: Molecule, pH: float = -1) -> PolarizabilityResult:
    """Atomic Polarizability calculation.

    Polarizability is the relative tendency of an electron cloud (a charge distribution) of a molecule to be distorted by an external electric field. The more stable an ionized (charged) site is the more polarizable its vicinity is.
    Atomic polarizability is altered by partial charges of atoms. The polarizability function is able to calculate the atomic and molecular polarizability values.

    Link: https://docs.chemaxon.com/display/docs/calculators_polarizability-plugin.md

    Parameters
    ----------
    mol : `Molecule`
       Input molecule
    pH : `float`
       Calculates polarizability value at this pH

    Returns
    -------
    polarizability : `PolarizabilityResult`
    """
    thread = _isolate_handler.get_isolate_thread()
    _cxn.polarizability.restype = ctypes.c_void_p
    _cxn.polarizability.argtypes = [ctypes.POINTER(_Opaque), ctypes.POINTER(_CMolecule), ctypes.c_double, ctypes.c_bool]
    try:
        cmol = mol._to_cmol()
        c_result = _CPolarizabilityResult.from_address(_cxn.polarizability(thread, cmol, pH, True))
        result = PolarizabilityResult(c_result)
    finally:
        _cxn.free_polarizability_result(thread)
        _isolate_handler.cleanup_isolate_thread(thread)
    return result


def polarizability(mol: Molecule, pH: float = -1) -> float:
    """Polarizability calculation.

    Polarizability is the relative tendency of an electron cloud (a charge distribution) of a molecule to be distorted by an external electric field. The more stable an ionized (charged) site is the more polarizable its vicinity is.
    Atomic polarizability is altered by partial charges of atoms. The polarizability function is able to calculate the atomic and molecular polarizability values.

    Link: https://docs.chemaxon.com/display/docs/calculators_polarizability-plugin.md

    Parameters
    ----------
    mol : `Molecule`
       Input molecule
    pH : `float`
       Calculates polarizability value at this pH

    Returns
    -------
    polarizability : `float`
    """
    thread = _isolate_handler.get_isolate_thread()
    _cxn.polarizability.restype = ctypes.c_void_p
    _cxn.polarizability.argtypes = [ctypes.POINTER(_Opaque), ctypes.POINTER(_CMolecule), ctypes.c_double, ctypes.c_bool]
    try:
        cmol = mol._to_cmol()
        c_result = _CPolarizabilityResult.from_address(_cxn.polarizability(thread, cmol, pH, False))
        result = PolarizabilityResult(c_result)
    finally:
        _cxn.free_polarizability_result(thread)
        _isolate_handler.cleanup_isolate_thread(thread)
    return result.molecular_polarizability
