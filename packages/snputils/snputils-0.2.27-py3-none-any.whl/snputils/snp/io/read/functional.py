import pathlib
from typing import Union

from snputils.snp.genobj import SNPObject


def read_snp(filename: Union[str, pathlib.Path], **kwargs) -> SNPObject:
    """
    Automatically detect the file format and read it into a SNPObject.

    Args:
        filename: Filename of the file to read.
        **kwargs: Additional arguments passed to the reader method.

    Raises:
        ValueError: If the filename does not have an extension or the extension is not supported.
    """
    from snputils.snp.io.read.auto import SNPReader

    return SNPReader(filename).read(**kwargs)


def read_bed(filename: Union[str, pathlib.Path], **kwargs) -> SNPObject:
    """
    Read a BED fileset into a SNPObject.

    Args:
        filename: Filename of the BED fileset to read.
        **kwargs: Additional arguments passed to the reader method. See :class:`snputils.snp.io.read.bed.BEDReader` for possible parameters.
    """
    from snputils.snp.io.read.bed import BEDReader

    return BEDReader(filename).read(**kwargs)


def read_pgen(filename: Union[str, pathlib.Path], **kwargs) -> SNPObject:
    """
    Read a PGEN fileset into a SNPObject.

    Args:
        filename: Filename of the PGEN fileset to read.
        **kwargs: Additional arguments passed to the reader method. See :class:`snputils.snp.io.read.pgen.PGENReader` for possible parameters.
    """
    from snputils.snp.io.read.pgen import PGENReader

    return PGENReader(filename).read(**kwargs)


def read_vcf(filename: Union[str, pathlib.Path], 
             backend: str = 'polars',
             **kwargs) -> SNPObject:
    """
    Read a VCF fileset into a SNPObject.

    Args:
        filename: Filename of the VCF fileset to read.
        backend: Backend to use for reading the VCF file. Options are 'polars' or 'scikit-allel'.
        **kwargs: Additional arguments passed to the reader method. See :class:`snputils.snp.io.read.vcf.VCFReader` for possible parameters.
    """
    from snputils.snp.io.read.vcf import VCFReader, VCFReaderPolars
    if backend == 'polars':
        print(f"Reading {filename} with polars backend")
        return VCFReaderPolars(filename).read(**kwargs)
    else:
        print(f"Reading {filename} with scikit-allel backend")
        return VCFReader(filename).read(**kwargs)
