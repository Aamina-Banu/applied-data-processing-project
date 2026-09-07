import json
from copy import deepcopy

import pandas as pd
from pandas import DataFrame
from datetime import datetime

from .data_processor import NYC311DataProcessor


class NYC311DataQualityError(Exception):
    """Represents an error during NYC 311 data quality processing."""
    pass


class DataQualityManager(NYC311DataProcessor):
    """Manages identified data quality issues in NYC 311 data."""

    def __init__(self, dataset: DataFrame):
        """
        Initialize the data quality manager.

        Parameters
        ----------
        dataset : DataFrame
            The NYC 311 dataset to be processed.

        Raises
        ------
        TypeError
            If dataset is not a pandas DataFrame.
        """
        super().__init__(dataset)
        self.__change_log = []

    def process_data(self) -> dict:
        """
        Report identified data quality issues in the stored dataset.

        The method checks for invalid BBL values, invalid ZIP values,
        Closed Dates occurring before Created Dates, and likely
        encoding issues in text columns.

        Returns
        -------
        dict
            A dictionary containing counts of the identified
            data quality issues.

        Raises
        ------
        ValueError
            If one or more required columns are missing.
        """
        dataset = self.get_dataset()

        required_columns = [
            "BBL",
            "Incident Zip",
            "Created Date",
            "Closed Date",
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in dataset.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Required columns are missing: {missing_columns}"
            )

        created_date = pd.to_datetime(
            dataset["Created Date"],
            format="%m/%d/%Y %I:%M:%S %p",
            errors="coerce",
        )

        closed_date = pd.to_datetime(
            dataset["Closed Date"],
            format="%m/%d/%Y %I:%M:%S %p",
            errors="coerce",
        )

        invalid_bbl_count = (
            dataset["BBL"] == 0
        ).sum()

        invalid_zip_count = (
            dataset["Incident Zip"] == 83
        ).sum()

        invalid_date_count = (
            created_date.notna()
            & closed_date.notna()
            & (closed_date < created_date)
        ).sum()

        encoding_issue_count = 0

        text_columns = dataset.select_dtypes(
            include=["object", "string"]
        ).columns

        encoding_markers = [
            "Ã",
            "Â",
            "â",
            "ð",
        ]

        for column in text_columns:
            for value in dataset[column].dropna():
                if isinstance(value, str):
                    if any(
                        marker in value
                        for marker in encoding_markers
                    ):
                        encoding_issue_count += 1

        return {
            "encoding_issue_count": encoding_issue_count,
            "invalid_bbl_count": invalid_bbl_count,
            "invalid_zip_count": invalid_zip_count,
            "invalid_resolution_date_count": invalid_date_count,
        }

    def correct_encoding(
        self,
        data: DataFrame,
    ) -> DataFrame:
        """
        Correct confidently identifiable encoding issues.

        Likely mojibake values are identified using selected encoding
        markers and a Latin-1 to UTF-8 conversion is attempted.
        Values that cannot be safely converted are left unchanged.

        The supplied DataFrame is not modified in place.

        Parameters
        ----------
        data : DataFrame
            The DataFrame containing text values to be checked.

        Returns
        -------
        DataFrame
            A new DataFrame containing any successfully corrected
            encoding values.

        Raises
        ------
        TypeError
            If data is not a pandas DataFrame.
        """
        if not isinstance(data, DataFrame):
            raise TypeError(
                "Data must be a pandas DataFrame."
            )

        result = data.copy()

        text_columns = result.select_dtypes(
            include=["object", "string"]
        ).columns

        encoding_markers = [
            "Ã",
            "Â",
            "â",
            "ð",
        ]

        affected_rows = set()

        for column in text_columns:
            for index in result.index:
                value = result.at[index, column]

                if not isinstance(value, str):
                    continue

                if not any(
                    marker in value
                    for marker in encoding_markers
                ):
                    continue

                try:
                    corrected_value = (
                        value
                        .encode("latin1")
                        .decode("utf-8")
                    )

                    if corrected_value != value:
                        result.at[
                            index,
                            column,
                        ] = corrected_value

                        affected_rows.add(index)

                except (
                    UnicodeEncodeError,
                    UnicodeDecodeError,
                ):
                    continue

        self.__change_log.append({
            "treatment": "correct_encoding",
            "fields": list(text_columns),
            "rows_affected": len(affected_rows),
            "description": (
                "Corrected confidently identifiable "
                "mojibake values using a consistent "
                "encoding conversion."
            ),
            "outcome": "success",
            "timestamp": datetime.now().isoformat(),
        })

        return result

    def replace_invalid_bbl(
        self,
        data: DataFrame,
    ) -> DataFrame:
        """
        Replace invalid BBL values of 0 with missing values.

        The correct BBL is not inferred or invented. The supplied
        DataFrame is not modified in place.

        Parameters
        ----------
        data : DataFrame
            The DataFrame containing the BBL column.

        Returns
        -------
        DataFrame
            A new DataFrame with BBL values equal to 0 replaced
            with missing values.

        Raises
        ------
        TypeError
            If data is not a pandas DataFrame.
        ValueError
            If the BBL column is missing.
        NYC311DataQualityError
            If the treatment fails a post-treatment integrity check.
        """
        if not isinstance(data, DataFrame):
            raise TypeError(
                "Data must be a pandas DataFrame."
            )

        if "BBL" not in data.columns:
            raise ValueError(
                "Required column 'BBL' is missing."
            )

        result = data.copy()

        original_row_count = len(data)
        outcome = "failed"
        failure_message = None

        invalid_bbl = result["BBL"] == 0

        affected_count = int(
            invalid_bbl.sum()
        )

        try:
            result.loc[
                invalid_bbl,
                "BBL",
            ] = pd.NA

            if len(result) != original_row_count:
                raise NYC311DataQualityError(
                    "BBL treatment changed the number "
                    "of rows in the dataset."
                )

            if "BBL" not in result.columns:
                raise NYC311DataQualityError(
                    "BBL treatment removed the required "
                    "'BBL' column."
                )

            if (result["BBL"] == 0).any():
                raise NYC311DataQualityError(
                    "BBL treatment did not remove all "
                    "invalid BBL values."
                )

        except NYC311DataQualityError as error:
            outcome = "failed"
            failure_message = str(error)
            raise

        else:
            outcome = "success"

        finally:
            self.__change_log.append({
                "treatment": "replace_invalid_bbl",
                "fields": ["BBL"],
                "rows_affected": affected_count,
                "description": (
                    "Replaced BBL values equal to 0 "
                    "with missing values because a valid "
                    "BBL could not be safely inferred."
                    if outcome == "success"
                    else failure_message
                ),
                "outcome": outcome,
                "timestamp": datetime.now().isoformat(),
            })

        return result

    def handle_invalid_zip(
        self,
        data: DataFrame,
    ) -> DataFrame:
        """
        Replace the clearly invalid ZIP value 83 with a missing value.

        Other ambiguous ZIP representations are left unchanged.
        The supplied DataFrame is not modified in place.

        Parameters
        ----------
        data : DataFrame
            The DataFrame containing the Incident Zip column.

        Returns
        -------
        DataFrame
            A new DataFrame with ZIP value 83 replaced with
            a missing value.

        Raises
        ------
        TypeError
            If data is not a pandas DataFrame.
        ValueError
            If the Incident Zip column is missing.
        NYC311DataQualityError
            If the treatment fails a post-treatment integrity check.
        """
        if not isinstance(data, DataFrame):
            raise TypeError(
                "Data must be a pandas DataFrame."
            )

        if "Incident Zip" not in data.columns:
            raise ValueError(
                "Required column 'Incident Zip' is missing."
            )

        result = data.copy()

        original_row_count = len(data)
        outcome = "failed"
        failure_message = None

        invalid_zip = (
            result["Incident Zip"] == 83
        )

        affected_count = int(
            invalid_zip.sum()
        )

        try:
            result.loc[
                invalid_zip,
                "Incident Zip",
            ] = pd.NA

            if len(result) != original_row_count:
                raise NYC311DataQualityError(
                    "ZIP treatment changed the number "
                    "of rows in the dataset."
                )

            if "Incident Zip" not in result.columns:
                raise NYC311DataQualityError(
                    "ZIP treatment removed the required "
                    "'Incident Zip' column."
                )

            if (result["Incident Zip"] == 83).any():
                raise NYC311DataQualityError(
                    "ZIP treatment did not remove all "
                    "clearly invalid ZIP values."
                )

        except NYC311DataQualityError as error:
            outcome = "failed"
            failure_message = str(error)
            raise

        else:
            outcome = "success"

        finally:
            self.__change_log.append({
                "treatment": "handle_invalid_zip",
                "fields": ["Incident Zip"],
                "rows_affected": affected_count,
                "description": (
                    "Replaced the clearly invalid ZIP "
                    "value 83 with a missing value. "
                    "Other ambiguous ZIP representations "
                    "were left unchanged."
                    if outcome == "success"
                    else failure_message
                ),
                "outcome": outcome,
                "timestamp": datetime.now().isoformat(),
            })

        return result

    def handle_date_inconsistencies(
        self,
        data: DataFrame,
    ) -> DataFrame:
        """
        Handle records where Closed Date occurs before Created Date.

        For an affected record, Closed Date is replaced with a
        missing value because the correct closing date cannot be
        safely inferred. The row itself is retained.

        The supplied DataFrame is not modified in place.

        Parameters
        ----------
        data : DataFrame
            The DataFrame containing Created Date and Closed Date.

        Returns
        -------
        DataFrame
            A new DataFrame in which invalid Closed Date values
            are replaced with missing values.

        Raises
        ------
        TypeError
            If data is not a pandas DataFrame.
        ValueError
            If Created Date or Closed Date is missing.
        NYC311DataQualityError
            If the treatment fails one of the post-treatment
            integrity checks.
        """
        if not isinstance(data, DataFrame):
            raise TypeError(
                "Data must be a pandas DataFrame."
            )

        required_columns = [
            "Created Date",
            "Closed Date",
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in data.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Required columns are missing: "
                f"{missing_columns}"
            )

        result = data.copy()

        original_row_count = len(data)

        outcome = "failed"
        failure_message = None

        created_date = pd.to_datetime(
            result["Created Date"],
            format="%m/%d/%Y %I:%M:%S %p",
            errors="coerce",
        )

        closed_date = pd.to_datetime(
            result["Closed Date"],
            format="%m/%d/%Y %I:%M:%S %p",
            errors="coerce",
        )

        invalid_dates = (
            created_date.notna()
            & closed_date.notna()
            & (closed_date < created_date)
        )

        affected_count = int(
            invalid_dates.sum()
        )

        try:
            result.loc[
                invalid_dates,
                "Closed Date",
            ] = pd.NaT

            if len(result) != original_row_count:
                raise NYC311DataQualityError(
                    "Date treatment changed the number "
                    "of rows in the dataset."
                )

            if (
                "Created Date" not in result.columns
                or "Closed Date" not in result.columns
            ):
                raise NYC311DataQualityError(
                    "Date treatment removed a required "
                    "date column."
                )

            treated_created_date = pd.to_datetime(
                result["Created Date"],
                format="%m/%d/%Y %I:%M:%S %p",
                errors="coerce",
            )

            treated_closed_date = pd.to_datetime(
                result["Closed Date"],
                format="%m/%d/%Y %I:%M:%S %p",
                errors="coerce",
            )

            remaining_invalid_dates = (
                treated_created_date.notna()
                & treated_closed_date.notna()
                & (
                    treated_closed_date
                    < treated_created_date
                )
            )

            if remaining_invalid_dates.any():
                raise NYC311DataQualityError(
                    "Date treatment did not remove all "
                    "invalid date inconsistencies."
                )

        except NYC311DataQualityError as error:
            outcome = "failed"
            failure_message = str(error)
            raise

        else:
            outcome = "success"

        finally:
            self.__change_log.append({
                "treatment": (
                    "handle_date_inconsistencies"
                ),
                "fields": [
                    "Created Date",
                    "Closed Date",
                ],
                "rows_affected": affected_count,
                "description": (
                    "Replaced Closed Date with a missing "
                    "value when it occurred before Created "
                    "Date. No replacement date was invented."
                    if outcome == "success"
                    else failure_message
                ),
                "outcome": outcome,
                "timestamp": datetime.now().isoformat(),
            })

        return result

    def save_change_log(
        self,
        file_path: str,
    ) -> None:
        """
        Save the data quality change log to a JSON file.

        Parameters
        ----------
        file_path : str
            The path where the JSON change log should be saved.

        Raises
        ------
        TypeError
            If file_path is not a string.
        OSError
            If the change log cannot be written to the specified file.
        """
        if not isinstance(file_path, str):
            raise TypeError(
                "File path must be a string."
            )

        try:
            with open(
                file_path,
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    self.__change_log,
                    file,
                    indent=4,
                )

        except OSError:
            raise

    def get_change_log(self) -> list:
        """
        Return a copy of the data quality treatment history.

        Returning an independent copy prevents external code from
        modifying the private change log.

        Returns
        -------
        list
            An independent copy of the recorded data quality
            treatment entries.
        """
        return deepcopy(self.__change_log)