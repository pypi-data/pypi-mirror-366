import ctypes

from .._isolate_handler import _cxn, _isolate_handler
from ..molecule import Molecule, _CMolecule, _init_mol
from .exporter import export_mol


def _to_svg(mrv: str):
    """:meta private:"""
    cxn_mol = import_mol(mrv)
    return export_mol(cxn_mol, "svg:headless,nosource,w300")

def import_mol(mol: str, options: str = "") -> Molecule:
    """Molecule import

    You can find more information about file formats and options on the following link: https://docs.chemaxon.com/display/docs/formats_index.md

    Here you can find the supported formats: https://docs.chemaxon.com/display/docs/python-api_limitations.md

    Parameters
    ----------
    mol : `str`
       Input molecule string
    options : `str`
       This option is to specify the input format and options for the import
    Raises
    ------
    RuntimeError
        If the molecule contains more than 800 atoms / bonds
    Returns
    -------
    molecule : `Molecule`
       The imported molecule
    """
    thread = _isolate_handler.get_isolate_thread()

    _cxn.import_mol.restype = ctypes.c_void_p
    try:
        cmolecule = _CMolecule.from_address(_cxn.import_mol(thread, mol.encode("utf-8"), options.encode("utf-8")))
        molecule = _init_mol(_to_svg, cmolecule)
    finally:
        _cxn.free_import_mol_result(thread)
        _isolate_handler.cleanup_isolate_thread(thread)
    return molecule

