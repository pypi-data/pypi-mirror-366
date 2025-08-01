from collections import defaultdict
from pathlib import Path

import numpy as np
from hypothesis import given
from hypothesis import strategies as st
from numpy.lib.stride_tricks import sliding_window_view

from flui.dna import iter_reads, open_as_text
from flui.subtype import BITS_TO_BASE, KmerSet, int_to_kmer

SEQ_ALPHABET = list(BITS_TO_BASE.values())
MAX_BASES = 2001

sequence_strategy = st.text(
    alphabet=SEQ_ALPHABET, min_size=len(BITS_TO_BASE), max_size=MAX_BASES
)
kmer_strategy = st.text(alphabet=SEQ_ALPHABET, min_size=9, max_size=15)

# Mapping of bases to 2-bit representations
BASE_TO_BITS = {ord("A"): 0b00, ord("C"): 0b01, ord("G"): 0b10, ord("T"): 0b11}


def kmer_to_int(kmer: bytes) -> int | None:
    """Convert a kmer to an integer representation.

    If any bases are not ACGT, then return None.
    """
    kmer_int = 0
    for base in kmer:
        b = BASE_TO_BITS.get(base)
        if b is None:
            return None
        kmer_int = (kmer_int << 2) | b
    return kmer_int


def py_get_kmers(sequence: bytes, kmer_size: int):
    """Find kmers, convert them to integers, keeping counts.

    This is a python equivalent of the numpy version we use.
    We use it to cross-check our algorithm.
    """
    sequence_bytes = np.frombuffer(sequence, dtype=np.uint8)
    windows = sliding_window_view(sequence_bytes, window_shape=kmer_size)
    kmer_counts: defaultdict[int, int] = defaultdict(int)

    for window in windows:
        kmer = window.tobytes()
        # Encode the kmer into a single integer.
        kmer_int = kmer_to_int(kmer)
        # If we get None, then there were bases we could not parse.
        if kmer_int is not None:
            kmer_counts[kmer_int] += 1


@given(kmer_strategy)
def test_kmers(bases: str):
    """Check our kmer encoding and decoding."""
    encoded = kmer_to_int(bases.encode("ascii"))
    assert encoded is not None
    assert int_to_kmer(encoded, len(bases)) == bases


def load_fastq(datadir: Path) -> KmerSet:
    ks = KmerSet(size=13)
    with open_as_text(datadir / "sample-reads.fastq.gz") as fd:
        for read in iter_reads(fd):
            ks.add_read(read.encode("ascii"))
    return ks


def test_read_counts(datadir: Path, snapshot):
    """Read in the fastq file, and check it against our snapshot.

    The results of this were checked against jellyfish:
        https://github.com/gmarcais/Jellyfish

    Here, we just ensure we don't deviate from those tested results.
    """
    ks = load_fastq(datadir)
    assert ks.to_sorted_list() == snapshot


def test_benchmark_fastq_kmers(datadir: Path, benchmark):
    benchmark(load_fastq, datadir)
