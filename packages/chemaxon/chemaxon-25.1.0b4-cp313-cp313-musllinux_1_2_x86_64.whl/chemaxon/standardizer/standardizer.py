import ctypes

from .._isolate_handler import _isolate_handler, _cxn, _Opaque
from ..molecule import Molecule, _CMolecule, _init_mol
from ..io.importer import _to_svg

class Standardizer:
    """
    Creates a standardizer object.

    More information about molecule standardization: https://docs.chemaxon.com/display/docs/standardizer_working-with-standardizer.md


    Parameters:
        config: Configuration string in xml or action string format or a file object of the configuration file.
    """

    config: str
    def __init__(self, config):
        if isinstance (config, str) :
            self.config = config
        else :
            self.config = ''.join([line for line in config])

    def standardize(self, mol: Molecule) -> Molecule:
        """Molecule standardization

        More information about molecule standardsization: https://docs.chemaxon.com/display/docs/standardizer_working-with-standardizer.md

        Parameters
        ----------
        mol : `str`
           Input molecule object.
        Raises
        ------
        RuntimeError
            If the molecule contains more than 800 atoms / bonds.
        Returns
        -------
        molecule : `Molecule`
           The standardized molecule.
        """
        thread = _isolate_handler.get_isolate_thread()
        _cxn.standardize.argtypes = [ctypes.POINTER(_Opaque), ctypes.POINTER(_CMolecule), ctypes.c_char_p]
        _cxn.standardize.restype = ctypes.c_void_p
        try:
            c_molecule = _CMolecule.from_address(_cxn.standardize(thread, ctypes.byref(mol._to_cmol()), self.config.encode("utf-8")))
            standardized = _init_mol(_to_svg, cmolecule=c_molecule)
        finally:
            _cxn.free_standardized_molecule(thread)
            _isolate_handler.cleanup_isolate_thread(thread)
        return standardized
