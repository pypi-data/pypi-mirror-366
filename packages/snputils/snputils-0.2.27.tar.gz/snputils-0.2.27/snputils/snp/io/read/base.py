from __future__ import annotations

import abc
import pathlib
from typing import Union


class SNPBaseReader(abc.ABC):
    """Abstract class for SNP readers.

    Attributes:
        _filename: The path to the file storing SNP data.

    """

    def __init__(self, filename: Union[str, pathlib.Path]):
        """Initialize the SNPBaseReader.

        Args:
            filename: The path to the file storing SNP data.

        """
        self._filename = pathlib.Path(filename)

    @abc.abstractmethod
    def read(self, *args, **kwargs):
        pass

    @property
    def filename(self) -> str:
        """Get the path to the file storing SNP data.

        Returns:
            filename: The path to the file storing SNP data.

        """
        return self._filename
