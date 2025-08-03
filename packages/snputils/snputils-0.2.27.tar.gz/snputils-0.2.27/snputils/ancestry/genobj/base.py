import abc
import copy


class AncestryObject(abc.ABC):
    """
    Abstract class for ancestry data.
    """
    def __init__(self, n_samples, n_ancestries) -> None:
        self.__n_samples = n_samples
        self.__n_ancesties = n_ancestries

    @property
    def n_ancestries(self) -> int:
        """
        Retrieve `n_ancestries`.

        Returns:
            int: The total number of unique ancestries.
        """
        return self.__n_ancesties

    @property
    def n_samples(self) -> int:
        """
        Retrieve number of samples

        Returns:
            int: number of sample in the data.
        """
        return self.__n_samples

    @property
    def copy(self):
        """
        Create a copy of the Ancestry Object

        Returns:
            dict: new Ancestry Object being a copy of the original Ancestry Object.
        """
        return copy.deepcopy(self)

    @abc.abstractmethod
    def _sanity_check(self) -> None:
        return
