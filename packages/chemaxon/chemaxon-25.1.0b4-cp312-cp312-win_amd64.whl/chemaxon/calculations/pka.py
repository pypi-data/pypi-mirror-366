import ctypes
from enum import IntEnum

from .._util import _customresize
from .._isolate_handler import _isolate_handler, _cxn, _Opaque
from ..io.importer import _to_svg
from ..molecule import _CMolecule, Molecule, _init_mol
from .._exception_util import _checkException, _CExceptionData


class PkaType(IntEnum):
    """
    - ACIDIC
    - BASIC
    """
    ACIDIC = 0
    BASIC = 1

    def __str__(self):
        return f'{self.name}'


class _CPkaResult(ctypes.Structure):
    """:meta private:"""
    _fields_ = [("length", ctypes.c_int),
                ("atom_indexes", ctypes.c_int * _CMolecule.MAX_ATOM_OR_BOND_COUNT),
                # could not make test having that much pka values
                ("pka_types", ctypes.c_int * _CMolecule.MAX_ATOM_OR_BOND_COUNT),
                ("pka_values", ctypes.c_double * _CMolecule.MAX_ATOM_OR_BOND_COUNT),
                ("structure", ctypes.POINTER(_CMolecule)),
                ("exception_data", ctypes.POINTER(_CExceptionData))
                ]

class PkaValue:
    """PkaValue

    Attributes
    ----------
    atom_index: `int`
        Index of the atom
    type: `PkaType`
        Pka type
    value: `float`
        Pka value
    """
    def __init__(self, atom_index: int, type: PkaType, value: float):
        self.atom_index = atom_index
        self.type = type
        self.value = value

    def __str__(self):
        return f'[atom: {self.atom_index},  pka: {round(self.value, 2)} ({self.type})]'

class PkaResult:
    """PkaResult

    Attributes
    ----------
    acidic_values : `PkaValue[]`
        The calculated acidic pka values
    basic_values : `PkaValue[]`
        The calculated basic pka values
    min_acidic : `PkaValue`
        The most acidic pka value
    max_basic : `PkaValue`
        The most basic pka value
    structure : `Molecule`
        The input structure extended by pka values as atomic properties.

    """
    def __init__(self, result: _CPkaResult):
        _checkException(result)
        c_atom_indexes = _customresize(result.atom_indexes, result.length)
        c_pka_types = _customresize(result.pka_types, result.length)
        c_pka_values = _customresize(result.pka_values, result.length)

        self.pka_values = []
        for i in range(result.length):
            self.pka_values.append(PkaValue(c_atom_indexes[i], PkaType(c_pka_types[i]), c_pka_values[i]))

        self.structure = _init_mol(_to_svg, cmolecule=result.structure.contents)


    def acidic_values(self):
        return sorted(
            [item for item in self.pka_values if item.type == PkaType.ACIDIC],
            key=lambda x: x.value)

    def basic_values(self):
        return sorted(
            [item for item in self.pka_values if item.type == PkaType.BASIC],
            key=lambda x: x.value,
            reverse=True)

    def min_acidic(self):
        return self.acidic_values()[0]

    def max_basic(self):
        return self.basic_values()[0]

    def __str__(self):
        return ', '.join([str(pka_value) for pka_value in self.pka_values])


def pka(mol: Molecule) -> PkaResult:
    """pKa calculation.

    Most molecules contain some specific functional groups likely to lose or gain proton(s) under specific circumstances. Each equilibrium between the protonated and deprotonated forms of the molecule can be described with a constant value called p K a. The pka function calculates the pKa values of the molecule based on its partial charge distribution.

    Link: https://docs.chemaxon.com/display/docs/calculators_pka-plugin.md

    Parameters
    ----------
    mol : `Molecule`
        Input molecule

    Returns
    -------
    pka : `PkaResult`
    """
    thread = _isolate_handler.get_isolate_thread()
    _cxn.pka.restype = ctypes.c_void_p
    _cxn.pka.argtypes = [ctypes.POINTER(_Opaque), ctypes.POINTER(_CMolecule)]
    try:
        cmol = mol._to_cmol()
        c_result = _CPkaResult.from_address(_cxn.pka(thread, cmol))
        result = PkaResult(c_result)
    finally:
        _cxn.free_pka_result(thread)
        _isolate_handler.cleanup_isolate_thread(thread)

    return result
