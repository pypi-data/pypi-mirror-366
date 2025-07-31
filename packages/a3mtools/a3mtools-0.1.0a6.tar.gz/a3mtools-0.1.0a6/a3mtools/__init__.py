import warnings
warnings.warn(
    "This package has been renamed and is no longer maintained. "
    "Please use `a3mcat` instead\npip install a3mcat\nhttps://pypi.org/project/a3mcat.",
    UserWarning,
)
from a3mtools import examples
from a3mtools.backend.sequence_utils import ProteinSequence
from a3mtools.backend.a3m_tools import MSAa3m, import_a3m
from a3mtools.backend.fasta_tools import MSAfasta, import_fasta
__all__ = ["examples", "MSAa3m", "import_a3m", "ProteinSequence", "MSAfasta", "import_fasta"]
