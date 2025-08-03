import logging
import pandas as pd
from pathlib import Path
from typing import Union

log = logging.getLogger(__name__)

from .base import PhenotypeBaseReader
from snputils.phenotype.genobj import UKBPhenotypeObject


class UKBPhenReader(PhenotypeBaseReader):
    """
    A class for reading data from a `.phe` file and constructing a `UKBPhenotypeObject`.
    """
    def __init__(self, file: Union[str, Path]) -> None:
        """
        Args:
            file (str or pathlib.Path): 
                Path to the `.phe` file containing UKB phenotype data.
        """
        self._file = file

    @property
    def file(self) -> Path:
        """
        Retrieve `file`.

        Returns:
            pathlib.Path: 
                Path to the `.phe` file containing UKB phenotype data.
        """
        return self.__file
    
    def read(self) -> 'UKBPhenotypeObject':
        """
        Read data from a `.phe ` file and construct a `UKBPhenotypeObject`.

        Returns:
            UKBPhenotypeObject: 
                A UKB phenotype object instance.
        """
        log.info(f"Reading .phe file from '{self.file}'...")
        
        # Load the `.phe` file with specified column names and data types
        phen_df = pd.read_csv(
            self.file,
            header=None,
            delim_whitespace=True,
            names=["FID", "IID", "status"],
            dtype={"FID": str, "IID": str, "status": int},
        )
        
        # Extract sample IDs for cases based on status
        cases_IDs = list(phen_df[phen_df["status"] == 2]["FID"])
        n_cases = len(cases_IDs)
        if n_cases == 0:
            raise ValueError("No case data available.")
        
        # Extract sample IDs for controls based on status
        controls_IDs = list(phen_df[phen_df["status"] == 1]["FID"])
        n_controls = len(controls_IDs)
        if n_controls == 0:
            raise ValueError("No control data available.")
        
        # Verify the sample count integrity
        sample_IDs = phen_df["FID"].tolist()
        n_samples = len(sample_IDs)
        if n_samples != (n_cases + n_controls):
            raise ValueError(
                "Total sample count does not match the combined count of cases and controls. "
                f"Expected {n_cases + n_controls}; found {n_samples}."
            )
        
        # Generate haplotypes for cases, controls, and all samples
        cases_haplotypes = [f"{case}.0" for case in cases_IDs] + [f"{case}.1" for case in cases_IDs]
        controls_haplotypes = [f"{control}.0" for control in controls_IDs] + [f"{control}.1" for control in controls_IDs]
        all_haplotypes = [f"{sample}.0" for sample in sample_IDs] + [f"{sample}.1" for sample in sample_IDs]
        
        return UKBPhenotypeObject(samples = sample_IDs,
                                  n_samples = n_samples,
                                  cases = cases_IDs,
                                  n_cases = n_cases,
                                  controls = controls_IDs,
                                  n_controls = n_controls,
                                  all_haplotypes = all_haplotypes,
                                  cases_haplotypes = cases_haplotypes,
                                  controls_haplotypes = controls_haplotypes
                                 )

PhenotypeBaseReader.register(UKBPhenReader)
