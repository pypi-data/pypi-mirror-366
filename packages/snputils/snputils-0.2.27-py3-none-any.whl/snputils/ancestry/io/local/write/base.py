import abc
from pathlib import Path
from typing import Union

from snputils.ancestry.genobj.local import LocalAncestryObject


class LAIBaseWriter(abc.ABC):
    """
    Abstract class for local ancestry writers.
    """
    def __init__(self, laiobj: LocalAncestryObject, file: Union[str, Path]) -> None:
        """
        Args:
            laiobj (LocalAncestryObject):
                A LocalAncestryObject instance.
            file (str or pathlib.Path): 
                Path to the file where the data will be saved. It should end with `.msp` or `.msp.tsv`. 
                If the provided path does not have one of these extensions, the `.msp` extension will be appended.
        """
        self.__laiobj = laiobj
        self.__file = Path(file)

    @property
    def laiobj(self) -> LocalAncestryObject:
        """
        Retrieve `laiobj`. 

        Returns:
            laiobj (LocalAncestryObject):
                A LocalAncestryObject instance.
        """
        return self.__laiobj

    @property
    def file(self) -> Path:
        """
        Retrieve `file`.

        Returns:
            pathlib.Path: 
                Path to the file where the data will be saved. It should end with `.msp` or `.msp.tsv`. 
                If the provided path does not have one of these extensions, the `.msp` extension will be appended.
        """
        return self.__file

    @abc.abstractmethod
    def write(self) -> None:
        """
        Abstract method to write the data from `laiobj` to the specified output `file`.

        Subclasses must implement this method to perform the actual writing of data.
        """
        pass
