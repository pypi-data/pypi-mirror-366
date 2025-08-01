import ctypes
import io
from .._isolate_handler import _isolate_handler, _cxn, _Opaque
from .._exception_util import _checkException, _CExceptionData
from ..io.importer import _to_svg
from ..molecule import _CMolecule, Molecule, _init_mol



class _CStructureCheckerResult(ctypes.Structure):
    """:meta private:"""
    _fields_ = [("description", ctypes.c_char_p),
                ("checker_name", ctypes.c_char_p),
                ("atom_count", ctypes.c_int),
                ("atom_indexes", ctypes.POINTER(ctypes.c_int)),
                ("bond_count", ctypes.c_int),
                ("bond_indexes", ctypes.POINTER(ctypes.c_int)),
                ("sgroup_count", ctypes.c_int),
                ("sgroup_indexes", ctypes.POINTER(ctypes.c_int)),
                ("rgroup_count", ctypes.c_int),
                ("rgroup_ids", ctypes.POINTER(ctypes.c_int)),
                ("colored_mol", ctypes.POINTER(_CMolecule)),
                ]


class _CStructureCheckerBatchResult(ctypes.Structure):
    """:meta private:"""
    _fields_ = [("results", ctypes.POINTER(_CStructureCheckerResult)),
                ("result_count", ctypes.c_int),
                ("exception_data", ctypes.POINTER(_CExceptionData)),
                ("aggregated_colored_mol", ctypes.POINTER(_CMolecule))
                ]


class StructureCheckerResult:
    """
    StructureCheckerResult

    Attributes
    ----------
    description : str
        Description of the found error
    checker_name : str
        name of the checker reporting the error
    colored_mol : Molecule
        colored molecule showing the errors, None if returnColoredHit is False
    atom_indexes : list
        list of atom indexes with errors
    bond_indexes : list
        list of bond indexes with errors

    """
    def __init__(self, result: _CStructureCheckerResult, returnColoredHit: bool):
        self.description = result.description.decode('utf-8')
        self.checker_name = result.checker_name.decode('utf-8')
        self.atom_indexes = [result.atom_indexes[i] for i in range(result.atom_count)]
        self.bond_indexes = [result.bond_indexes[i] for i in range(result.bond_count)]
        self.sgroup_indexes = [result.sgroup_indexes[i] for i in range(result.sgroup_count)]
        self.rgroup_ids = [result.rgroup_ids[i] for i in range(result.rgroup_count)]
        if (returnColoredHit):
            self.colored_mol = _init_mol(_to_svg, cmolecule=result.colored_mol.contents)
        else:
            self.colored_mol = None


class StructureCheckerBatchResult:
    """StuctureCheckerBatchResult

    Attributes
    ----------
    results:
        list of StructureCheckerResults
    aggregated_colored_mol:
        colored molecule showing all errors as union, None if returnedColoredHit is False or no errors found.
    """

    def __init__(self, result: _CStructureCheckerBatchResult, returnColoredHit: bool):
        _checkException(result)
        self.results = [StructureCheckerResult(result.results[i], returnColoredHit) for i in range(result.result_count)]
        if (returnColoredHit and self.results):
            self.aggregated_colored_mol = _init_mol(_to_svg, result.aggregated_colored_mol.contents)
        else:
            self.aggregated_colored_mol = None

    def is_error_free(self) -> bool:
        """
        Returns whether there is no error detected in the molecule.
        """
        return not self.results


class _CStructureFixerResult(ctypes.Structure):
    """:meta private:"""
    _fields_ = [("fixed_mol", ctypes.POINTER(_CMolecule)),
                ("is_fix_successful", ctypes.c_bool)
                ]


class StructureFixerResult:
    """StructureFixerResult
    Attributes
    ----------
    fixed_mol: Molecule,
        fixed molecule or the original if fix was not successful
    is_fix_successful: boolean,
        whether the fixing was successful.
    """

    def __init__(self, fixer_result: _CStructureFixerResult):
        self.fixed_mol = _init_mol(_to_svg, cmolecule=fixer_result.fixed_mol.contents)
        self.is_fix_successful = fixer_result.is_fix_successful


class StructureChecker:
    """
       Creates a structurechecker object.

       More info about structure checkers: https://docs.chemaxon.com/display/docs/structure-checker_index
   
       Parameters:
       ------------------
           config: Configuration parameter in any of the following formats:
                - xml string
                - action string
                - list of action strings
                - file object of the configuration file.
       Example:
       -------------------------
        structurechecker = StructureChecker("aromaticityerror:type=basic")

        structurechecker = StructureChecker(["wedgeerror", "valenceerror"])

        with open("config.xml") as f:
            structurechecker = StructureChecker(f)

    """
    config: str

    def __init__(self, config):
        if isinstance(config, list) and all(isinstance(configElem, str) for configElem in config):
            self.config = "..".join(config)
        elif isinstance(config, str):
            self.config = config
        elif isinstance(config, io.IOBase):
            self.config = ''.join([line for line in config])
        else:
            raise AttributeError("Wrong config: " + type(config).__name__)

    def check(self, mol: Molecule, returnColoredHit: bool = True) -> StructureCheckerBatchResult:
        """Molecule structure checking.

        Parameters
        ----------
        mol:
           The molecule to be checked.
        Raises
        ------
        RuntimeError
            If the molecule contains more than 500 atoms / bonds.
        Returns
        -------
        result
            structure checking batch result.
        """
        if not isinstance(mol, Molecule):
            raise AttributeError(f"mol must be a Molecule, not {type(mol).__name__}")

        thread = _isolate_handler.get_isolate_thread()
        _cxn.check.argtypes = [ctypes.POINTER(_Opaque), ctypes.POINTER(_CMolecule), ctypes.c_char_p, ctypes.c_bool]
        _cxn.check.restype = ctypes.c_void_p
        try:

            cresult = _CStructureCheckerBatchResult.from_address(
                _cxn.check(thread, ctypes.byref(mol._to_cmol()), self.config.encode("utf-8"), returnColoredHit))
            result = StructureCheckerBatchResult(cresult, returnColoredHit)
        finally:
            _cxn.free_structurechecker_result(thread)
            _isolate_handler.cleanup_isolate_thread(thread)
        return result

    def fix(self, mol: Molecule) -> StructureFixerResult:
        """Fixes the given structure based on the config provided during StructureChecker construction.

        Parameters
        -------------
        mol:
            Molecule to be fixed.
        Returns
        ---------------
        result:
            StructureFixerResult object containing the fixed molecule and a flag showing if the fix was successful.
            If fix was unsuccessful it returns the original mol.
        """
        if not isinstance(mol, Molecule):
            raise AttributeError(f"mol must be a Molecule, not {type(mol).__name__}")

        thread = _isolate_handler.get_isolate_thread()
        _cxn.fix.argtypes = [ctypes.POINTER(_Opaque), ctypes.POINTER(_CMolecule), ctypes.c_char_p]
        _cxn.fix.restype = ctypes.c_void_p
        try:
            fixer_result = _CStructureFixerResult.from_address(
                _cxn.fix(thread, ctypes.byref(mol._to_cmol()), self.config.encode("utf-8")))
            result = StructureFixerResult(fixer_result)
        finally:
            _cxn.free_fixer_result(thread)
            _isolate_handler.cleanup_isolate_thread(thread)
        return result
