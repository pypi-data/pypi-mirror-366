import ctypes

from .._isolate_handler import _isolate_handler, _cxn, _Opaque
from ..molecule import _CMolecule, Molecule, _init_mol
from ..io.importer import _to_svg

def major_microspecies(mol: Molecule, pH: float = 7.4, take_major_tautomeric_form: bool = False,
                       keep_explicit_hydrogens: bool = False) -> Molecule:
    """Major Microspecies calculation.

    The Major Microspecies determines the major (de)protonated form of the molecule at a specified pH.

    Link: https://docs.chemaxon.com/display/docs/calculators_major-microspecies-plugin.md

    Parameters
    ----------
    mol : `Molecule`
       Input molecule
    pH : `float`
       Calculates major microspecies at this pH
    take_major_tautomeric_form: `bool`
       If major tautomeric form should be taken
    keep_explicit_hydrogens: 'bool'
       If explicit hydrogens should be kept on the result molecule

    Returns
    -------
    major_microspecies : `Molecule`
       Major microspecies molecule
    """
    thread = _isolate_handler.get_isolate_thread()

    _cxn.major_microspecies.restype = ctypes.c_void_p
    _cxn.major_microspecies.argtypes = [ctypes.POINTER(_Opaque), ctypes.POINTER(_CMolecule), ctypes.c_double,
                                       ctypes.c_bool, ctypes.c_bool]
    cmol = mol._to_cmol()
    try:
        result_c_mol = _CMolecule.from_address(
            _cxn.major_microspecies(thread, cmol, pH, take_major_tautomeric_form, keep_explicit_hydrogens))

        molecule = _init_mol(_to_svg, cmolecule=result_c_mol)
    finally:
        _cxn.free_major_microspecies_result(thread)
        _isolate_handler.cleanup_isolate_thread(thread)
    return molecule
