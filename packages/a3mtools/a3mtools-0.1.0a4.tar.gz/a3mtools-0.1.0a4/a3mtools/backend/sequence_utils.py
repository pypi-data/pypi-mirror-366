import re


class ProteinSequence:
    def __init__(self, header: str, sequence: str):
        self.header = header
        self.seq_str = sequence

    def __str__(self):
        return f">{self.header}\n{self.seq_str}"

    def __repr__(self):
        return f">{self.header}\n{self.seq_str}"

    def __len__(self):
        return len(self.seq_str)

    def __getitem__(self, index):
        """This should allow for slicing of the sequence"""
        return ProteinSequence(self.header, self.seq_str[index])

    def __add__(self, other):
        """This should allow for concatenation of the sequence"""
        if isinstance(other, ProteinSequence):
            return ProteinSequence(self.header, self.seq_str + other.seq_str)
        elif isinstance(other, str):
            return ProteinSequence(self.header, self.seq_str + other)
        else:
            raise TypeError(f"Cannot concatenate ProteinSequence with {type(other)}")

    def __radd__(self, other):
        """This should allow for concatenation of the sequence"""
        if isinstance(other, ProteinSequence):
            return ProteinSequence(self.header, other.seq_str + self.seq_str)
        elif isinstance(other, str):
            return ProteinSequence(self.header, other + self.seq_str)
        else:
            raise TypeError(f"Cannot concatenate ProteinSequence with {type(other)}")


def find_all(string: str, substring):
    start = 0
    while True:
        start = string.find(substring, start)
        if start == -1:
            return
        yield start
        # start += len(substring)
        start += 1


def percent_identity(seq1: str, seq2: str) -> float:
    """
    Returns a percent identity between 0 (no identical residues) and 1 (all residues are identical)
    - The sequences must be pre-aligned (i.e. they have the same length)
    - The returned percent identity is computed as the number of identical residues divided by the
    length of compared alignment sites. Alignment sites where both sequences are gaps ('-' characters)
    are not compared.

    Parameters
    ----------
    seq1 : str
        first sequence
    seq2 : str
        second sequence
    """
    assert len(seq1) == len(
        seq2
    ), "sequences are not the same length. Are they aligned?"
    num_same = 0
    length = len(seq1)
    for i in range(len(seq1)):
        if seq1[i] == "-" and seq2[i] == "-":
            length -= 1
            continue
        if seq1[i] == seq2[i]:
            num_same += 1
    pid = num_same / length
    return pid


def get_first_non_gap_index(s: str) -> int:
    """get the index of the first non-gap character (first character that is
    not `-`) in a string

    Parameters
    ----------
    s : str
        input string

    Returns
    -------
    int
        the index of the first non-gap character in the string (0-indexed)
    """
    index = 0
    while index < len(s) and s[index] == "-":
        index += 1
    return index


def get_non_gap_indexes(aln_seq: str) -> list[int]:
    """get list of nongap positions in `aln_seq`"""
    return [c for c, i in enumerate(aln_seq) if i != "-"]


def gen_kmers(seq: str, k: int) -> list[str]:
    """
    generates list of length k "kmers" comprising `seq`

    Parameters
    ----------
    seq : str
        input sequence to split into k-mers. Should be entry in fasta file
    k : int
        length of fragments (k-mers)

    Returns
    -------
    kmers : list
        list of strings - k-mers generated from seq
    """
    k2 = k - 1
    kmers = []
    for i in range(len(seq) - k2):
        kmers.append(seq[i : i + k])
    return kmers


def get_regex_matches(regex_pattern: str, seq_str: str):
    """searches for all matches of a regex pattern in a sequence string
    returns a generator object that yields the match sequence, start index, and end index

    Parameters
    ----------
    regex_pattern : str
        regular expression pattern
    seq_str : str
        string to search for matches

    Yields
    ------
    tuple
        (match sequence, start index, end index)
    """
    p = re.compile(regex_pattern)
    for m in p.finditer(seq_str):
        if m.start() == m.end():
            # even if there are groups in the lookahead, the first group should be the full match b/c that group surrounds the entire regex
            # so this will work whether or not there are groups in the lookahead
            match_seq = m.groups()[0]
        else:
            match_seq = seq_str[m.start() : m.end()]
        yield match_seq, m.start(), m.start() + len(match_seq) - 1


def reindex_alignment_str(seq_str):
    """convert indexes of an ungapped sequence to indexes of it's sequence with gaps

    Parameters
    ----------
    seq_str : str
        string of a sequence with gaps present

    Returns
    -------
    str
        ungapped sequence
    list
        list of indexes of nongap characters in the gapped sequence. index the return list with
        non-gap indexes to get the index of the gapped sequence. If the gapped sequence is `A--A--A`, the return list will be `[0, 3, 6]`

    Examples
    --------
    >>> aligned = 'A--A--A'
    >>> unaligned, ind = reindex_alignment_str(aligned)
    >>> print(unaligned)
    'AAA'
    >>> print(ind)
    [0, 3, 6]
    >>> print(aligned[ind[0]:ind[-1]+1])
    'A--A--A'
    """
    unal_seq = ""
    index_map = []
    for al_pos, i in enumerate(seq_str):
        # print(al_pos, i)
        if i != "-":
            unal_seq = unal_seq + i
            index_map.append(al_pos)
    return unal_seq, index_map
