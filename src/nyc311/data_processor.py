from abc import ABC, abstractmethod
from pandas import DataFrame


class NYC311DataProcessor(ABC):
    """Base class for processing NYC 311 data."""

    def __init__(self, dataset: DataFrame):
        if not isinstance(dataset, DataFrame):
            raise TypeError("Dataset must be a pandas DataFrame.")

        self.__dataset = dataset

    def get_dataset(self) -> DataFrame:
        """Returns a copy of the stored dataset."""
        return self.__dataset.copy()

    @abstractmethod
    def process_data(self) -> dict:
        """Processes the dataset and returns the results as a dictionary."""
        pass
