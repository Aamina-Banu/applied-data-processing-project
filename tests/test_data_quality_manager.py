import json

import pandas as pd
import pytest
import nyc311.data_quality_manager as data_quality_module

from nyc311.data_quality_manager import (
    DataQualityManager,
    NYC311DataQualityError,
)


def test_process_data_reports_quality_issues():
    data = pd.DataFrame({
        "BBL": [0, 1234567890, 0],
        "Incident Zip": [83, 10001, 10002],
        "Created Date": [
            "2025-01-01 10:00:00",
            "2025-01-02 10:00:00",
            "2025-01-03 15:00:00"
        ],
        "Closed Date": [
            "2025-01-01 12:00:00",
            "2025-01-02 12:00:00",
            "2025-01-03 10:00:00"
        ],
        "Description": [
            "Normal text",
            "CafÃ© complaint",
            "Another normal value"
        ]
    })

    manager = DataQualityManager(data)

    result = manager.process_data()

    assert result["invalid_bbl_count"] == 2
    assert result["invalid_zip_count"] == 1
    assert result["invalid_resolution_date_count"] == 1
    assert result["encoding_issue_count"] == 1


def test_replace_invalid_bbl_returns_new_dataframe():
    data = pd.DataFrame({
        "BBL": [0, 1234567890]
    })

    manager = DataQualityManager(data)

    result = manager.replace_invalid_bbl(data)

    assert pd.isna(result.loc[0, "BBL"])
    assert data.loc[0, "BBL"] == 0


def test_handle_invalid_zip():
    data = pd.DataFrame({
        "Incident Zip": [83, 10001, 7105]
    })

    manager = DataQualityManager(data)

    result = manager.handle_invalid_zip(data)

    assert pd.isna(result.loc[0, "Incident Zip"])
    assert result.loc[1, "Incident Zip"] == 10001
    assert result.loc[2, "Incident Zip"] == 7105


def test_change_log_records_treatment():
    data = pd.DataFrame({
        "BBL": [0, 1234567890]
    })

    manager = DataQualityManager(data)

    manager.replace_invalid_bbl(data)

    log = manager.get_change_log()

    assert len(log) == 1
    assert log[0]["treatment"] == "replace_invalid_bbl"
    assert log[0]["rows_affected"] == 1
    assert log[0]["fields"] == ["BBL"]
    assert log[0]["outcome"] == "success"


def test_missing_bbl_column_raises_value_error():
    data = pd.DataFrame({
        "Incident Zip": [10001, 10002]
    })

    manager = DataQualityManager(data)

    with pytest.raises(ValueError):
        manager.replace_invalid_bbl(data)


def test_correct_encoding():
    data = pd.DataFrame({
        "Description": [
            "CafÃ© complaint",
            "Normal complaint"
        ]
    })

    manager = DataQualityManager(data)

    result = manager.correct_encoding(data)

    assert result.loc[0, "Description"] == "Café complaint"
    assert result.loc[1, "Description"] == "Normal complaint"

    # Original DataFrame must remain unchanged
    assert data.loc[0, "Description"] == "CafÃ© complaint"

    log = manager.get_change_log()

    assert len(log) == 1
    assert log[0]["treatment"] == "correct_encoding"
    assert log[0]["rows_affected"] == 1
    assert log[0]["outcome"] == "success"


def test_handle_date_inconsistencies():
    data = pd.DataFrame({
        "Created Date": [
            "2025-01-01 10:00:00",
            "2025-01-02 10:00:00"
        ],
        "Closed Date": [
            "2025-01-01 09:00:00",
            "2025-01-02 12:00:00"
        ]
    })

    manager = DataQualityManager(data)

    result = manager.handle_date_inconsistencies(data)

    # First Closed Date is earlier than Created Date,
    # so it should become missing
    assert pd.isna(result.loc[0, "Closed Date"])

    # Valid date should remain unchanged
    assert result.loc[1, "Closed Date"] == "2025-01-02 12:00:00"

    # Original DataFrame must remain unchanged
    assert data.loc[0, "Closed Date"] == "2025-01-01 09:00:00"

    log = manager.get_change_log()

    assert len(log) == 1
    assert log[0]["treatment"] == "handle_date_inconsistencies"
    assert log[0]["rows_affected"] == 1
    assert log[0]["outcome"] == "success"


def test_non_dataframe_raises_type_error():
    data = pd.DataFrame({
        "BBL": [0, 1234567890]
    })

    manager = DataQualityManager(data)

    with pytest.raises(TypeError):
        manager.replace_invalid_bbl(
            ["this", "is", "not", "a", "dataframe"]
        )


def test_handle_date_inconsistencies_failure(monkeypatch):
    data = pd.DataFrame({
        "Created Date": [
            "2025-01-02 10:00:00"
        ],
        "Closed Date": [
            "2025-01-01 10:00:00"
        ]
    })

    manager = DataQualityManager(data)

    call_count = 0

    original_to_datetime = pd.to_datetime

    def fake_to_datetime(values, errors="coerce"):
        nonlocal call_count
        call_count += 1

        # First two calls:
        # allow the method to correctly detect the original
        # invalid date pair.
        if call_count <= 2:
            return original_to_datetime(
                values,
                errors=errors
            )

        # Post-treatment Created Date check
        if call_count == 3:
            return pd.Series([
                pd.Timestamp("2025-01-02 10:00:00")
            ])

        # Post-treatment Closed Date check:
        # deliberately simulate the invalid date still remaining.
        return pd.Series([
            pd.Timestamp("2025-01-01 10:00:00")
        ])

    monkeypatch.setattr(
        pd,
        "to_datetime",
        fake_to_datetime
    )

    with pytest.raises(
        NYC311DataQualityError,
        match="did not remove all invalid date inconsistencies"
    ):
        manager.handle_date_inconsistencies(data)

    log = manager.get_change_log()

    assert log[-1]["outcome"] == "failed"
    assert (
        "invalid date inconsistencies"
        in log[-1]["description"]
    )


def test_replace_invalid_bbl_failure(monkeypatch):
    data = pd.DataFrame({
        "BBL": [0, 1234567890]
    })

    manager = DataQualityManager(data)

    monkeypatch.setattr(
        data_quality_module.pd,
        "NA",
        0
    )

    with pytest.raises(
        NYC311DataQualityError,
        match="did not remove all invalid BBL values"
    ):
        manager.replace_invalid_bbl(data)

    log = manager.get_change_log()

    assert log[-1]["outcome"] == "failed"
    assert "invalid BBL values" in log[-1]["description"]


def test_handle_invalid_zip_failure(monkeypatch):
    data = pd.DataFrame({
        "Incident Zip": [83, 12345]
    })

    manager = DataQualityManager(data)

    monkeypatch.setattr(
        data_quality_module.pd,
        "NA",
        83
    )

    with pytest.raises(
        NYC311DataQualityError,
        match="did not remove all clearly invalid ZIP values"
    ):
        manager.handle_invalid_zip(data)

    log = manager.get_change_log()

    assert log[-1]["outcome"] == "failed"
    assert "clearly invalid ZIP values" in log[-1]["description"]


def test_save_change_log(tmp_path):
    data = pd.DataFrame({
        "BBL": [0, 1234567890]
    })

    manager = DataQualityManager(data)

    manager.replace_invalid_bbl(data)

    file_path = tmp_path / "change_log.json"

    manager.save_change_log(str(file_path))

    assert file_path.exists()

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:
        saved_log = json.load(file)

    assert len(saved_log) == 1
    assert saved_log[0]["treatment"] == "replace_invalid_bbl"
    assert saved_log[0]["fields"] == ["BBL"]
    assert saved_log[0]["rows_affected"] == 1
    assert saved_log[0]["outcome"] == "success"