import pandas as pd
from pandas import DataFrame
from .data_processor import NYC311DataProcessor


class ComplaintEffectivenessAnalyzer(NYC311DataProcessor):
    """
    Analyzes how effectively NYC 311 complaints are handled.

    The analyzer evaluates complaint status information, identifies
    status/date inconsistencies, calculates closure statistics, and
    measures complaint resolution times where valid dates exist.
    """

    def __init__(self, dataset: DataFrame):
        """
        Initialize the complaint effectiveness analyzer.

        Parameters
        ----------
        dataset : DataFrame
            The NYC 311 dataset to be analyzed.

        Raises
        ------
        TypeError
            If dataset is not a pandas DataFrame.
        """
        super().__init__(dataset)

    def process_data(self) -> dict:
        """
        Analyze complaint closure and resolution effectiveness.

        Complaints are classified using both Status and Closed Date.

        A complaint is considered valid closed when:
        - Status is 'Closed'
        - Closed Date is present

        A complaint is considered valid non-closed when:
        - Status is one of:
          Open, In Progress, Assigned, Pending, Started
        - Closed Date is missing

        Records that contain contradictory information are reported
        separately as anomalies.

        Resolution time statistics are calculated only for valid
        closed complaints whose Closed Date occurs on or after the
        Created Date.

        Returns
        -------
        dict
            A dictionary containing complaint counts, closure
            statistics, anomaly counts, and resolution-time metrics.
        """
        dataset = self.get_dataset()

        total_complaints = len(dataset)
        status_counts = dataset["Status"].value_counts().to_dict()

        closed_status = dataset["Status"] == "Closed"

        non_closed_status = dataset["Status"].isin(
            ["Open", "In Progress", "Assigned", "Pending", "Started"]
        )

        unspecified_status = dataset["Status"] == "Unspecified"

        closed_date_present = dataset["Closed Date"].notna()
        closed_date_missing = dataset["Closed Date"].isna()

        valid_closed = closed_status & closed_date_present

        valid_non_closed = (
            non_closed_status
            & closed_date_missing
        )

        closed_missing_date = (
            closed_status
            & closed_date_missing
        )

        non_closed_present_date = (
            non_closed_status
            & closed_date_present
        )

        valid_total = (
            valid_closed.sum()
            + valid_non_closed.sum()
        )

        if valid_total > 0:
            closure_rate = (
                valid_closed.sum()
                / valid_total
            ) * 100
        else:
            closure_rate = None

        created_date = pd.to_datetime(
            dataset["Created Date"],
            errors="coerce"
        )

        closed_date = pd.to_datetime(
            dataset["Closed Date"],
            errors="coerce"
        )

        created_date_present = created_date.notna()

        valid_resolution_records = (
            valid_closed
            & created_date_present
            & (closed_date >= created_date)
        )

        resolution_record_count = (
            valid_resolution_records.sum()
        )

        if resolution_record_count > 0:

            resolution_time = (
                closed_date[valid_resolution_records]
                - created_date[valid_resolution_records]
            )

            resolution_hours = (
                resolution_time.dt.total_seconds()
                / (60 * 60)
            )

            average_resolution_hours = (
                resolution_hours.mean()
            )

            median_resolution_hours = (
                resolution_hours.median()
            )

        else:
            average_resolution_hours = None
            median_resolution_hours = None

        invalid_resolution_dates = (
            valid_closed
            & created_date.notna()
            & closed_date.notna()
            & (closed_date < created_date)
        )

        invalid_resolution_date_count = (
            invalid_resolution_dates.sum()
        )

        return {
            "total_complaints": total_complaints,
            "status_counts": status_counts,
            "valid_closed_count": valid_closed.sum(),
            "valid_non_closed_count": valid_non_closed.sum(),
            "closure_rate": closure_rate,
            "closed_missing_date_count": closed_missing_date.sum(),
            "non_closed_present_date_count": non_closed_present_date.sum(),
            "unspecified_count": unspecified_status.sum(),
            "resolution_record_count": resolution_record_count,
            "average_resolution_hours": average_resolution_hours,
            "median_resolution_hours": median_resolution_hours,
            "invalid_resolution_date_count": invalid_resolution_date_count
        }