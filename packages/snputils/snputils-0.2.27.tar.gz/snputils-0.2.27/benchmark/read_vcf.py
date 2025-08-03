import pytest
import numpy as np
from .utils import create_benchmark_test


def read_vcf_snputils(path):
    """Read VCF file using snputils"""
    import snputils
    return snputils.read_vcf(path, sum_strands=True).calldata_gt


def read_vcf_snputils_polars(path):
    """Read VCF file using snputils and polars"""
    from snputils.snp.io.read.vcf import VCFReaderPolars
    return VCFReaderPolars(path).read(fields=[], sum_strands=True).calldata_gt


def read_vcf_scikit_allel(path):
    """Read VCF file using scikit-allel"""
    import allel
    return np.sum(allel.read_vcf(path, fields=['calldata/GT'])['calldata/GT'] > 0, axis=2, dtype=np.uint8)


def read_vcf_hail(path):
    """Read VCF file using hail"""
    import hail as hl
    hl.init()
    mt = hl.import_vcf(path)
    n_variants = mt.count_rows()
    n_samples = mt.count_cols()
    mt = np.array(mt.GT.n_alt_alleles().collect(), dtype=np.uint8).reshape((n_variants, n_samples))
    hl.stop()
    return mt


def read_vcf_pyvcf3(path):
    """Read VCF file using PyVCF3"""
    import vcf
    return np.array([[s.data.GT.count('1') for s in record.samples] for record in vcf.Reader(filename=path)], dtype=np.uint8)


def read_vcf_cyvcf2(path):
    """Read VCF file using cyvcf2"""
    import cyvcf2
    return np.array([record.genotypes for record in cyvcf2.VCF(path)])[:, :, :2].sum(axis=2, dtype=np.uint8)


def read_vcf_pysam(path):
    """Read VCF file using pysam"""
    import pysam
    with pysam.VariantFile(path) as vcf:
        return np.array([[s.get('GT').count(1) for s in record.samples.values()] for record in vcf], dtype=np.uint8)


# Benchmark Configuration
READERS = [
    (read_vcf_snputils, "snputils"),
    (read_vcf_snputils_polars, "snputils-polars"),
    (read_vcf_scikit_allel, "scikit-allel"),
    (read_vcf_hail, "hail"),
    (read_vcf_pyvcf3, "pyvcf3"),
    (read_vcf_cyvcf2, "cyvcf2"),
    (read_vcf_pysam, "pysam"),
]


@pytest.mark.benchmark(group="VCF-readers", warmup=False, min_rounds=3)
@pytest.mark.parametrize("reader,name", READERS)
def test_vcf_readers(benchmark, reader, name, path, memory_profile):
    """Benchmark readers and verify output"""
    if path.suffixes[-2:] != ['.vcf', '.gz']:
        path = path.with_suffix('.vcf.gz')
    ref_array = read_vcf_snputils(path)
    create_benchmark_test(benchmark, reader, path, name, ref_array, memory_profile)
