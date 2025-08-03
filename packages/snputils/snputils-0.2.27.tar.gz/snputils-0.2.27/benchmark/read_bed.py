import pytest
import numpy as np
from .utils import create_benchmark_test


def read_bed_snputils(path):
    """Read BED fileset using snputils"""
    import snputils
    return snputils.read_bed(path, sum_strands=True, fields=["GT"]).calldata_gt


def read_bed_pgenlib(path):
    """Read BED fileset using Pgenlib"""
    import pgenlib
    with open(path + '.fam', 'r') as f:
        sample_ct = sum(1 for _ in f)  # Get sample count from fam file
    pgen = pgenlib.PgenReader(str.encode(path + '.bed'), raw_sample_ct=sample_ct)
    variant_ct = pgen.get_variant_ct()
    genotypes = np.empty((variant_ct, sample_ct), dtype=np.int8)
    variant_idxs = np.arange(variant_ct, dtype=np.uint32)
    pgen.read_list(variant_idxs, genotypes)
    pgen.close()
    return genotypes


def read_bed_hail(path):
    """Read BED fileset using hail"""
    import hail as hl
    hl.init()
    mt = hl.import_plink(path + '.bed', path + '.bim', path + '.fam')
    n_variants = mt.count_rows()
    n_samples = mt.count_cols()
    mt = np.array(mt.GT.n_alt_alleles().collect(), dtype=np.uint8).reshape((n_variants, n_samples))
    hl.stop()
    return mt


def read_bed_sgkit(path):
    """Read BED fileset using sgkit"""
    from sgkit.io import plink
    return np.sum(plink.read_plink(path=path).call_genotype.to_numpy() == 0, axis=2, dtype=np.uint8)


def read_bed_pandas_plink(path):
    """Read BED fileset using pandas-plink"""
    import pandas_plink
    _, _, genotypes = pandas_plink.read_plink(path)
    return 2 - genotypes.compute().astype(np.uint8)


def read_bed_plinkio(path):
    """Read BED fileset using plinkio"""
    from plinkio import plinkfile
    return np.array([2 - np.array(row) for row in plinkfile.open(path)], dtype=np.uint8)


def read_bed_pysnptools(path):
    """Read BED fileset using pysnptools"""
    from pysnptools.snpreader import Bed
    return (2 - Bed(path).read().val.T.astype(np.uint8))


READERS = [
    (read_bed_snputils, "snputils"),
    (read_bed_pgenlib, "pgenlib"),
    (read_bed_hail, "hail"),
    (read_bed_sgkit, "sgkit"),
    (read_bed_pandas_plink, "pandas-plink"),
    (read_bed_plinkio, "plinkio"),
    (read_bed_pysnptools, "pysnptools"),
]


@pytest.mark.benchmark(group="BED-readers", warmup=False, min_rounds=3)
@pytest.mark.parametrize("reader,name", READERS)
def test_bed_readers(benchmark, reader, name, path, memory_profile):
    """Benchmark readers and verify output"""
    ref_array = read_bed_snputils(path)
    create_benchmark_test(benchmark, reader, path, name, ref_array, memory_profile)
