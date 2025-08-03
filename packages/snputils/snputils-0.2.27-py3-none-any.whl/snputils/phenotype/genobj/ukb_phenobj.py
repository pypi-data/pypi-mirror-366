import copy
from typing import List


class UKBPhenotypeObject():
    """
    A class for UK Biobank (UKB) phenotype data.

    This class provides a structured way to handle phenotype information, including sample identifiers,
    the counts of cases and controls, and haplotype data.
    """
    def __init__(
        self, 
        samples: List, 
        n_samples: int, 
        cases: List, 
        n_cases: int, 
        controls: List, 
        n_controls: int, 
        all_haplotypes: List, 
        cases_haplotypes: List, 
        controls_haplotypes: List
    ) -> None:
        """
        Initialize the UKBPhenotypeObject with phenotype data.

        Args:
            samples (list of str): 
                A list of sample identifiers.
            n_samples (int): 
                The total number of samples.
            cases (list of str): 
                A list of identifiers for the cases.
            n_cases (int): 
                The total number of cases.
            controls (list of str): 
                A list of identifiers for the controls.
            n_controls (int): 
                The total number of controls.
            all_haplotypes (list of str): 
                A list of haplotypes for all samples.
            cases_haplotypes (list of str): 
                A list of haplotypes for the cases.
            controls_haplotypes (list of str): 
                A list of haplotypes for the controls.
        """
        self.__samples = samples
        self.__n_samples = n_samples
        self.__cases = cases
        self.__n_cases = n_cases
        self.__controls = controls
        self.__n_controls = n_controls
        self.__all_haplotypes = all_haplotypes
        self.__cases_haplotypes = cases_haplotypes
        self.__controls_haplotypes = controls_haplotypes

    def __getitem__(self, key):
        """
        To access an attribute of the class using the square bracket notation,
        similar to a dictionary.
        """
        try:
            return getattr(self, key)
        except:
            raise KeyError(f'Invalid key: {key}')

    def __setitem__(self, key, value):
        """
        To set an attribute of the class using the square bracket notation,
        similar to a dictionary.
        """
        try:
            setattr(self, key, value)
        except AttributeError:
            raise KeyError(f'Invalid key: {key}')

    @property
    def samples(self) -> List:
        """
        Retrieve `samples`.

        Returns:
            List of str: A list of sample identifiers.
        """
        return self.__samples
    
    @property
    def n_samples(self) -> int:
        """
        Retrieve `n_samples`.

        Returns:
            int: The total number of samples.
        """
        return self.__n_samples
    
    @property
    def cases(self) -> List:
        """
        Retrieve `cases`.

        Returns:
            List of str: A list of identifiers for the cases.
        """
        return self.__cases
    
    @property
    def n_cases(self) -> int:
        """
        Retrieve `n_cases`.

        Returns:
            int: The total number of cases.
        """
        return self.__n_cases
    
    @property
    def controls(self) -> List:
        """
        Retrieve `controls`.

        Returns:
            List of str: A list of identifiers for the controls.
        """
        return self.__controls
    
    @property
    def n_controls(self) -> int:
        """
        Retrieve `n_controls`.

        Returns:
            int: The total number of controls.
        """
        return self.__n_controls
    
    @property
    def all_haplotypes(self) -> List:
        """
        Retrieve `all_haplotypes`.

        Returns:
            List of str: A list of haplotypes for all samples.
        """
        return self.__all_haplotypes
    
    @property
    def cases_haplotypes(self) -> List:
        """
        Retrieve `cases_haplotypes`.

        Returns:
            List of str: A list of haplotypes for the cases.
        """
        return self.__cases_haplotypes
    
    @property
    def controls_haplotypes(self) -> List:
        """
        Retrieve `controls_haplotypes`.

        Returns:
            List of str: A list of haplotypes for the controls.
        """
        return self.__controls_haplotypes

    def copy(self):
        """
        Create and return a copy of the current `UKBPhenotypeObject` instance.

        Returns:
            UKBPhenotypeObject: A new instance of the current object.
        """
        return copy.copy(self)

    def keys(self) -> List:
        """
        Retrieve a list of public attribute names for this `UKBPhenotypeObject` instance.

        Returns:
            List: A list of attribute names, with internal name-mangling removed, 
                  for easier reference to public attributes in the instance.
        """
        return [attr.replace('_UKBPhenotypeObject__', '') for attr in vars(self)]
