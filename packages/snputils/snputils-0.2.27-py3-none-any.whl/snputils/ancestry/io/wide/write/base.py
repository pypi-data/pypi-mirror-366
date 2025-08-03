import abc
from pathlib import Path
from typing import Union

from snputils.ancestry.genobj.wide import GlobalAncestryObject


class WideBaseWriter(abc.ABC):
    """
    Abstract class for global ancestry writers.
    """ 
    def __init__(
        self, 
        wideobj: GlobalAncestryObject, 
        file_prefix: Union[str, Path]
    ) -> None:
        """
        Args:
            wideobj (GlobalAncestryObject): 
                A GlobalAncestryObject instance.
            file_prefix (str or pathlib.Path): 
                Prefix for output file names, including directory path but excluding file extensions. 
                The prefix is used to generate specific file names for each output, with file-specific 
                suffixes appended as described above (e.g., `file_prefix.n_ancestries.Q` for the Q matrix file).
        """
        self.__wideobj = wideobj
        self.__file_prefix = Path(file_prefix)

    @property
    def wideobj(self) -> GlobalAncestryObject:
        """
        Retrieve `wideobj`.

        Returns:
            GlobalAncestryObject: A GlobalAncestryObject instance.
        """
        return self.__wideobj

    @property
    def file_prefix(self) -> Path:
        """
        Retrieve `file_prefix`.

        Returns:
            pathlib.Path: 
                Prefix for output file names, including directory path but excluding file extensions. 
                The prefix is used to generate specific file names for each output, with file-specific 
                suffixes appended as described above (e.g., `file_prefix.n_ancestries.Q` for the Q matrix file).
        """
        return self.__file_prefix

    @abc.abstractmethod
    def write(self) -> None:
        """
        Abstract method to write wide ancestry files.

        Subclasses must implement this method to write the data from the Q and P files, 
        as well as sample identifiers, SNPs, and ancestries if available.
        """
        pass
