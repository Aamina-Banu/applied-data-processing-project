from abc import ABC, abstractmethod
from pandas import DataFrame


class NYC311DataProcessor(ABC):
    """
    Abstract base class for processing NYC 311 data.

    The class provides shared dataset storage and controlled dataset
    access for NYC 311 data processors. Subclasses must implement
    their own version of process_data().
    """

    def __init__(self, dataset: DataFrame):
        """
        Initialize the processor with an NYC 311 dataset.

        Parameters
        ----------
        dataset : DataFrame
            The pandas DataFrame to be stored by the processor.

        Raises
        ------
        TypeError
            If dataset is not a pandas DataFrame.
        """
        if not isinstance(dataset, DataFrame):
            raise TypeError(
                "Dataset must be a pandas DataFrame."
            )

        self.__dataset = dataset

    def get_dataset(self) -> DataFrame:
        """
        Return a copy of the stored dataset.

        Returning a copy prevents external code and subclasses from
        directly modifying the DataFrame stored by the processor.

        Returns
        -------
        DataFrame
            A copy of the stored pandas DataFrame.
        """
        return self.__dataset.copy()

    @abstractmethod
    def process_data(self) -> dict:
        """
        Process the stored dataset.

        Each subclass must provide its own implementation according
        to its specific processing responsibility.

        Returns
        -------
        dict
            A dictionary containing the processing results.
        """
        pass