from a3mtools.backend.sequence_utils import ProteinSequence
import a3mtools.backend.sequence_utils as utils
from pathlib import Path
from a3mtools.backend.a3m_tools import MSAa3m
import collections
from Bio import Align, AlignIO, Seq, SeqIO
from Bio.SeqRecord import SeqRecord
# I am using the biopython fasta parser b/c it is so robust
# it seems weird to do this however because I am using my own ProteinSequence class

class FastaImporter:
    """import fasta file and return seqrecord objects in various formats

    Parameters
    ----------
    fasta_path : str
        file path to fasta file
    """

    def __init__(self, fasta_path: str | Path):
        self.fasta_path = fasta_path

    def import_as_list(self) -> list[SeqRecord]:
        """return list of SeqRecord objects for each sequence in the fasta file

        Returns
        -------
        List[SeqRecord]
            list of SeqRecord objects
        """
        with open(self.fasta_path) as handle:
            return list(SeqIO.parse(handle, "fasta"))

    def import_as_dict(self) -> dict[str, SeqRecord]:
        """return dictionary of SeqRecord objects for each sequence in the fasta file

        Returns
        -------
        dict[str, SeqRecord]
            dictionary of SeqRecord objects, keys are the sequence ids and values are the SeqRecord objects
        """
        with open(self.fasta_path) as handle:
            return SeqIO.to_dict(SeqIO.parse(handle, "fasta"))

    def import_as_str_dict(self) -> dict[str, str]:
        """return dictionary of strings for each sequence in the fasta file

        Returns
        -------
        dict[str, str]
            dictionary of sequence strings, keys are the sequence ids and values are the sequences as strings
        """
        with open(self.fasta_path) as handle:
            d = SeqIO.to_dict(SeqIO.parse(handle, "fasta"))
        return {k: str(v.seq) for k, v in d.items()}

    def import_as_alignment(self) -> Align.MultipleSeqAlignment:
        """return multiple sequence alignment object

        Returns
        -------
        Align.MultipleSeqAlignment
            multiple sequence alignment object
        """
        with open(self.fasta_path) as handle:
            return AlignIO.read(handle, "fasta")


def import_fasta(filepath):
    faimporter = FastaImporter(filepath)
    seqrecord_list = faimporter.import_as_list()
    return [ProteinSequence(seq.id, str(seq.seq)) for seq in seqrecord_list]
 

class MSAfasta:

    def __init__(self, sequences: list[ProteinSequence]):
        self.sequences = sequences
        if len(sequences) == 0:
            raise ValueError("MSAfasta object must contain at least one sequence")
        if not all([isinstance(seq, ProteinSequence) for seq in sequences]):
            raise ValueError("All sequences in MSAfasta object must be of type ProteinSequence")
        if not all([len(seq) == len(sequences[0]) for seq in sequences]):
            raise ValueError("All sequences in MSAfasta object must be the same length")
        # ensure unique headers
        self.headers = [seq.header for seq in sequences]
        if len(self.headers) != len(set(self.headers)):
            duplicates = [item for item, count in collections.Counter(self.headers).items() if count > 1]
            raise ValueError(f"All sequences in MSAfasta object must have unique headers, duplicate headers found: {duplicates}")
        self.n_columns = len(sequences[0])
        self.n_rows = len(sequences)
        
    def __str__(self):
        return "\n".join([str(seq) for seq in self.sequences])

    def __repr__(self):
        return self.__str__()
    
    def __getitem__(self, index):
        new_seqs = []
        for seq in self.sequences:
            new_seqs.append(seq[index])
        return MSAfasta(new_seqs)
    
    def __iter__(self):
        return iter(self.sequences)
    
    def __contains__(self, item):
        return item in [i.header for i in self.sequences]
    
    def to_dict(self):
        return {seq.header: seq for seq in self.sequences}

    def __add__(self, other):
        if isinstance(other, MSAfasta):
            # make sure headers are the same using sets
            if set(self.headers) != set(other.headers):
                raise ValueError("Cannot concatenate MSAs with different headers")
            new_seqs = []
            other_dict = other.to_dict()
            for seq1 in self.sequences:
                new_seqs.append(seq1 + other_dict[seq1.header])
            return MSAfasta(new_seqs)
        # elif isinstance(other, ProteinSequence):
        #     return MSAfasta(self.sequences + [other])
        else:
            raise TypeError(f"Cannot concatenate MSAfasta with {type(other)}")

    def append(self, other):
        if isinstance(other, ProteinSequence):
            return MSAfasta(self.sequences + [other])
        else:
            raise TypeError(f"Cannot append {type(other)} to MSAfasta")

    @classmethod
    def from_fasta_file(cls, file_path: Path | str):
        """create an MSAfasta object from a fasta file

        Parameters
        ----------
        file_path : Path | str
            path to the fasta file

        Returns
        -------
        MSAfasta
            an a3mtools.MSAfasta object
        """        
        sequences = import_fasta(file_path)
        return cls(sequences)

    def print_MSA(self):
        for seq in self.sequences:
            print(seq.seq_str)

    def to_a3m(self, query_header: str):
        """convert the MSAfasta object to an MSAa3m object

        Parameters
        ----------
        query_header : str
            The header of the sequence to use as the query sequence. Insertions
            in the a3m will all be relative to the query sequence. Gaps will
            also be removed from the query sequence.

        Returns
        -------
        a3mtools.backend.a3m_tools.MSAa3m
            a MSAa3m object with the newly formatted sequences
        """        
        aligned_query = [i for i in self.sequences if i.header == query_header][0]
        unaligned_query, inds = utils.reindex_alignment_str(aligned_query.seq_str)
        # query = ProteinSequence(aligned_query.header, unaligned_query)
        query = ProteinSequence('101', unaligned_query)
        new_seqs = []
        for pseq in self.sequences:
            if pseq.header == aligned_query.header:
                continue
            new_seq_str = ''
            for c in range(len(pseq.seq_str)):
                if c in inds:
                    new_seq_str += pseq.seq_str[c]
                else:
                    if pseq.seq_str[c] != '-':
                        new_seq_str += pseq.seq_str[c].lower()
            new_seqs.append(ProteinSequence(pseq.header, new_seq_str))
        info_line = f'#{len(query.seq_str)}\t1'
        return MSAa3m(info_line, query, new_seqs)

    def save(self, filepath):
        with open(filepath, "w") as handle:
            handle.write(str(self))






# def read_lines_and_strip(handle):
#     return [line.strip() for line in handle.readlines() if line.strip()]


# def parse_fasta(handle):
#     lines = read_lines_and_strip(handle)
#     for i in range(0, len(lines), 2):
#         header = lines[i].rstrip()
#         if not header.startswith('>'):
#             raise ValueError(f'Header line in FASTA should begin with >, instead saw: {header} at line {i}')
#         if lines[i + 1].startswith('>'):
#             raise ValueError(f'Expected sequence line after header ({header}), instead saw: {lines[i + 1]} at line {i + 1}')
#         sequence = lines[i + 1]
#         yield ProteinSequence(header[1:], sequence)


# def import_fasta(filepath):
#     with open(filepath) as handle:
#         return list(parse_fasta(handle))


