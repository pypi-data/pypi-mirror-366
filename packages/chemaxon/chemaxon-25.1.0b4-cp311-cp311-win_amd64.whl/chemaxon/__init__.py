"""
This is the Chemaxon Python API main package.
Version: <python-api-version>
"""

import sys

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.1.0"
finally:
    del version, PackageNotFoundError

from .info import ccl_version, ccl_build_date, licenses
from .molecule import Molecule, Atom, Bond

from .calculations import charge, charge_by_atoms, ChargeResult
from .calculations import chemterm
from .calculations import hlb, HlbMethod
from .calculations import logd
from .calculations import logp, logp_by_atoms, LogPResult
from .calculations import LogpMethod
from .calculations import major_microspecies
from .calculations import pka, PkaResult, PkaValue, PkaType
from .calculations import polarizability, atomic_polarizability, PolarizabilityResult


from .fingerprints import cfp
from .fingerprints import ecfp
from .fingerprints import fcfp
from .fingerprints import Fingerprint, FloatVectorFingerprint
from .fingerprints import pharmacophore_fp
from .fingerprints import tanimoto, float_vector_tanimoto

from .io import export_mol
from .io import import_mol

from .standardizer import Standardizer
from .structurechecker import StructureChecker
