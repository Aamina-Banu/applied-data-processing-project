from pandas import DataFrame
from .data_processor import NYC311DataProcessor


class DataInspector(NYC311DataProcessor):
    """
    Inspects the structure and basic information of NYC 311 data.

    This class provides descriptive information about the dataset,
    such as its dimensions, column names, data types, and missing
    values. It does not evaluate or treat data quality problems.
    """

    def __init__(self, dataset: DataFrame):
        """
        Initialize the data inspector.

        Parameters
        ----------
        dataset : DataFrame
            The NYC 311 dataset to be inspected.

        Raises
        ------
        TypeError
            If dataset is not a pandas DataFrame.
        """
        super().__init__(dataset)

    def process_data(self) -> dict:
        """
        Return structural and basic information about the dataset.

        The method reports the number of rows and columns, column
        names, data types, and missing-value counts without modifying
        the stored dataset.

        Returns
        -------
        dict
            A dictionary containing the dataset row count, column
            count, column names, data types, and missing-value counts.
        """
        dataset = self.get_dataset()

        return {
            "row_count": len(dataset),
            "column_count": len(dataset.columns),
            "column_names": list(dataset.columns),
            "data_types": dataset.dtypes.to_dict(),
            "missing_values": dataset.isnull().sum().to_dict()
        }