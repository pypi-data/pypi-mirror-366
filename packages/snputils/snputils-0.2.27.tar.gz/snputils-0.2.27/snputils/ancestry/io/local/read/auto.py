from __future__ import annotations

from pathlib import Path
from typing import Union


class LAIReader:
    def __new__(
        cls,
        file: Union[str, Path]
    ) -> object:
        """
        A factory class that automatically detects the local ancestry data file format from the 
        file's extension and returns the corresponding reader object.

        **Supported formats:**

        - `.msp`: Text-based MSP format.
        - `.msp.tsv`: Text-based MSP format with TSV extension.

        Args:
            file (str or pathlib.Path): 
                Path to the file to be read. It should end with `.msp` or `.msp.tsv`.
        
        Returns:
            **object:** A reader object corresponding to the file format (e.g., `MSPReader`).
        """
        file = Path(file)
        suffixes = [suffix.lower() for suffix in file.suffixes]
        if not suffixes:
            raise ValueError("The file must have an extension. Supported extensions are: .msp, .msp.tsv.")

        if suffixes[-2:] == ['.msp', '.tsv'] or suffixes[-1] == '.msp':
            from snputils.ancestry.io.local.read.msp import MSPReader

            return MSPReader(file)
        else:
            raise ValueError(
                f"Unsupported file extension: {suffixes[-1]}. "
                "Supported extensions are: .msp, .msp.tsv."
            )
