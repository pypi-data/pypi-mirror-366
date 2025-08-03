import pytest
import numpy as np
from .utils import create_benchmark_test


def read_pgen_snputils(path):
    """Read PGEN file using snputils"""
    import snputils
    return snputils.read_pgen(path, sum_strands=True, fields=["GT"]).calldata_gt


def read_pgen_pgenlib(path):
    """Read PGEN fileset using Pgenlib"""
    import pgenlib
    pgen = pgenlib.PgenReader(str.encode(path + '.pgen'))  # No need for raw_sample_ct with pgen
    variant_ct = pgen.get_variant_ct()
    sample_ct = pgen.get_raw_sample_ct()
    genotypes = np.empty((variant_ct, sample_ct), dtype=np.int8)
    variant_idxs = np.arange(variant_ct, dtype=np.uint32)
    pgen.read_list(variant_idxs, genotypes)
    pgen.close()
    return genotypes


READERS = [
    (read_pgen_snputils, "snputils"),
    (read_pgen_pgenlib, "pgenlib"),
]


@pytest.mark.benchmark(group="PGEN-readers", warmup=False, min_rounds=3)
@pytest.mark.parametrize("reader,name", READERS)
def test_pgen_readers(benchmark, reader, name, path, memory_profile):
    """Benchmark readers and verify output"""
    ref_array = read_pgen_snputils(path)
    create_benchmark_test(benchmark, reader, path, name, ref_array, memory_profile)
