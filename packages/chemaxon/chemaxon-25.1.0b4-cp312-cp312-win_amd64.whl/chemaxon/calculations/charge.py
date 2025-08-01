import ctypes

from .._util import _customresize
from .._isolate_handler import _isolate_handler, _cxn, _Opaque
from ..molecule import _CMolecule, Molecule
from .._exception_util import _CExceptionData, _checkException

class _CChargeResult(ctypes.Structure):
    """:meta private:"""
    _fields_ = [("formal_charge", ctypes.c_int),
                ("length", ctypes.c_int),
                ("formal_charge_indices", ctypes.c_int * _CMolecule.MAX_ATOM_OR_BOND_COUNT),
                ("formal_charge_by_atoms", ctypes.c_int * _CMolecule.MAX_ATOM_OR_BOND_COUNT),
                ("total_charge_indices", ctypes.c_int * _CMolecule.MAX_ATOM_OR_BOND_COUNT),
                ("total_charge_by_atoms", ctypes.c_double * _CMolecule.MAX_ATOM_OR_BOND_COUNT),
                ("exception_data", ctypes.POINTER(_CExceptionData))
                ]

class ChargeResult:
    """ChargeResult

    Attributes
    ----------
    formal_charge : `int`
        The calculated charge value
    formal_charge_by_atoms : `dict`
        Formal charge values by atom indexes
    total_charge_by_atoms : `dict`
        Total charge values by atom indexes
    """
    def __init__(self, result: _CChargeResult):
        _checkException(result)
        self.formal_charge = result.formal_charge
        c_formal_charge_by_atoms = _customresize(result.formal_charge_by_atoms, result.length)
        c_formal_indices = _customresize(result.formal_charge_indices, result.length)
        self.formal_charge_by_atoms  = {c_formal_indices[i]:c_formal_charge_by_atoms[i] for i in range(result.length)}

        c_total_charge_by_atoms = _customresize(result.total_charge_by_atoms, result.length)
        c_total_indices = _customresize(result.total_charge_indices, result.length)
        self.total_charge_by_atoms = {c_formal_indices[i]:c_total_charge_by_atoms[i] for i in range(result.length)}


def charge_by_atoms(mol: Molecule) -> ChargeResult:
    """Partial charge calculation.

    The partial charge distribution determines many physico-chemical properties of a molecule, such as ionization constants, reactivity and pharmacophore pattern.
    The charge function is able to compute the partial charge value of each atom. Total charge is calculated from sigma and pi charge components.

    Link: https://docs.chemaxon.com/display/docs/calculators_charge-plugin.md

    Parameters
    ----------
    mol : `Molecule`
        Input molecule

    Returns
    -------
    charge : `ChargeResult`
    """
    thread = _isolate_handler.get_isolate_thread()
    _cxn.charge.restype = ctypes.c_void_p
    _cxn.charge.argtypes = [ctypes.POINTER(_Opaque), ctypes.POINTER(_CMolecule)]
    cmol = mol._to_cmol()
    try:
        c_result = _CChargeResult.from_address(_cxn.charge(thread, cmol))
        result = ChargeResult(c_result)
    finally:
        _cxn.free_charge_result(thread)
        _isolate_handler.cleanup_isolate_thread(thread)
    return result


def charge(mol: Molecule) -> int:
    """Charge calculation.

    The partial charge distribution determines many physico-chemical properties of a molecule, such as ionization constants, reactivity and pharmacophore pattern.
    The charge function is able to compute the partial charge value of each atom. Total charge is calculated from sigma and pi charge components.

    Link: https://docs.chemaxon.com/display/docs/calculators_charge-plugin.md

    Parameters
    ----------
    mol : `Molecule`
        Input molecule

    Returns
    -------
    formal_charge : `int`
    """
    thread = _isolate_handler.get_isolate_thread()
    _cxn.charge.restype = ctypes.c_void_p
    _cxn.charge.argtypes = [ctypes.POINTER(_Opaque), ctypes.POINTER(_CMolecule)]
    cmol = mol._to_cmol()
    try:
        c_result = _CChargeResult.from_address(_cxn.charge(thread, cmol))
        result = ChargeResult(c_result)
    finally:
        _cxn.free_charge_result(thread)
        _isolate_handler.cleanup_isolate_thread(thread)
    return result.formal_charge
