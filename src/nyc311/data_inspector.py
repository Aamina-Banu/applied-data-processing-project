from pandas import DataFrame
from .data_processor import NYC311DataProcessor


class DataInspector(NYC311DataProcessor):
    """Inspects the structure and basic information of NYC 311 data."""

    def __init__(self, dataset: DataFrame):
        super().__init__(dataset)

    def process_data(self) -> dict:
        """Returns basic information about the dataset."""
        dataset = self.get_dataset()

        return {
            "row_count": len(dataset),
            "column_count": len(dataset.columns),
            "column_names": list(dataset.columns),
            "data_types": dataset.dtypes.to_dict(),
            "missing_values": dataset.isnull().sum().to_dict()
        }