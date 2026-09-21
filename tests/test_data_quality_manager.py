import json

import pandas as pd
import pytest
import nyc311.data_quality_manager as data_quality_module

from nyc311 import (
    DataQualityManager,
    NYC311DataQualityError,
)


def test_process_data_reports_quality_issues():
    data = pd.DataFrame({
        "BBL": [0, 1234567890, 0],
        "Incident Zip": [83, 10001, 10002],
        "Created Date": [
            "01/01/2025 10:00:00 AM",
            "01/02/2025 10:00:00 AM",
            "01/03/2025 03:00:00 PM"
        ],
        "Closed Date": [
            "01/01/2025 12:00:00 PM",
            "01/02/2025 12:00:00 PM",
            "01/03/2025 10:00:00 AM"
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


def test_change_log_entries_are_independent_copies():
    data = pd.DataFrame({
        "BBL": [0, 1234567890]
    })

    manager = DataQualityManager(data)

    manager.replace_invalid_bbl(data)

    log = manager.get_change_log()
    log[0]["outcome"] = "mutated"

    fresh_log = manager.get_change_log()

    assert fresh_log[0]["outcome"] == "success"


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
            "01/01/2025 10:00:00 AM",
            "01/02/2025 10:00:00 AM"
        ],
        "Closed Date": [
            "01/01/2025 09:00:00 AM",
            "01/02/2025 12:00:00 PM"
        ]
    })

    manager = DataQualityManager(data)

    result = manager.handle_date_inconsistencies(data)

    # First Closed Date is earlier than Created Date,
    # so it should become missing
    assert pd.isna(result.loc[0, "Closed Date"])

    # Valid date should remain unchanged
    assert result.loc[1, "Closed Date"] == "01/02/2025 12:00:00 PM"

    # Original DataFrame must remain unchanged
    assert data.loc[0, "Closed Date"] == "01/01/2025 09:00:00 AM"

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
            "01/02/2025 10:00:00 AM"
        ],
        "Closed Date": [
            "01/01/2025 10:00:00 AM"
        ]
    })

    manager = DataQualityManager(data)

    call_count = 0

    original_to_datetime = pd.to_datetime

    def fake_to_datetime(
        values,
        format=None,
        errors="coerce"
    ):
        nonlocal call_count
        call_count += 1

        # First two calls:
        # allow the method to correctly detect the original
        # invalid date pair.
        if call_count <= 2:
            return original_to_datetime(
                values,
                format=format,
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


@pytest.mark.parametrize("existing", [False, True])
def test_save_change_log(tmp_path, existing):
    data = pd.DataFrame({
        "BBL": [0, 1234567890]
    })

    manager = DataQualityManager(data)

    manager.replace_invalid_bbl(data)

    file_path = tmp_path / "change_log.json"

    if existing:
        file_path.write_text("previous contents", encoding="utf-8")

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


def test_correct_encoding_with_duplicate_index_labels():
    data = pd.DataFrame(
        {
            "Description": ["Caf\u00c3\u00a9", "Caf\u00c3\u00a9", "Normal"],
            "Details": ["Caf\u00c3\u00a9", "Normal", "Normal"],
        },
        index=[7, 7, 7],
    )
    snapshot = data.copy(deep=True)
    manager = DataQualityManager(data)

    result = manager.correct_encoding(data)

    expected = pd.DataFrame(
        {
            "Description": ["Caf\u00e9", "Caf\u00e9", "Normal"],
            "Details": ["Caf\u00e9", "Normal", "Normal"],
        },
        index=[7, 7, 7],
    )
    pd.testing.assert_frame_equal(result, expected)
    pd.testing.assert_frame_equal(data, snapshot)
    log = manager.get_change_log()
    assert len(log) == 1
    assert log[0]["treatment"] == "correct_encoding"
    assert log[0]["fields"] == ["Description", "Details"]
    assert log[0]["rows_affected"] == 2
    assert log[0]["outcome"] == "success"


@pytest.mark.parametrize("existing", [False, True])
@pytest.mark.parametrize("error_type", [OSError, ValueError])
def test_save_change_log_write_failure_preserves_destination(
    tmp_path, monkeypatch, existing, error_type
):
    manager = DataQualityManager(pd.DataFrame({"BBL": [0]}))
    manager.replace_invalid_bbl(manager.get_dataset())
    snapshot = manager.get_change_log()
    destination = tmp_path / "change_log.json"
    if existing:
        destination.write_bytes(b"previous contents")
    failure = error_type("simulated partial write failure")

    def fail_dump(data, file, **kwargs):
        file.write("partial JSON")
        raise failure

    monkeypatch.setattr(data_quality_module.json, "dump", fail_dump)

    with pytest.raises(error_type) as raised:
        manager.save_change_log(str(destination))

    assert raised.value is failure
    if existing:
        assert destination.read_bytes() == b"previous contents"
    else:
        assert not destination.exists()
    assert list(tmp_path.iterdir()) == ([destination] if existing else [])
    assert manager.get_change_log() == snapshot


@pytest.mark.parametrize("existing", [False, True])
def test_save_change_log_replace_failure_preserves_destination(
    tmp_path, monkeypatch, existing
):
    import os

    manager = DataQualityManager(pd.DataFrame({"BBL": [0]}))
    manager.replace_invalid_bbl(manager.get_dataset())
    snapshot = manager.get_change_log()
    destination = tmp_path / "change_log.json"
    if existing:
        destination.write_bytes(b"previous contents")
    failure = PermissionError("simulated replacement failure")

    def fail_replace(source, target):
        raise failure

    monkeypatch.setattr(os, "replace", fail_replace)

    with pytest.raises(PermissionError) as raised:
        manager.save_change_log(str(destination))

    assert raised.value is failure
    if existing:
        assert destination.read_bytes() == b"previous contents"
    else:
        assert not destination.exists()
    assert list(tmp_path.iterdir()) == ([destination] if existing else [])
    assert manager.get_change_log() == snapshot


@pytest.mark.parametrize(
    "method,values",
    [
        ("replace_invalid_bbl", {"BBL": [0]}),
        ("handle_invalid_zip", {"Incident Zip": [83]}),
        (
            "handle_date_inconsistencies",
            {
                "Created Date": ["01/02/2025 10:00:00 AM"],
                "Closed Date": ["01/01/2025 10:00:00 AM"],
            },
        ),
    ],
)
def test_unexpected_treatment_failure_is_logged(monkeypatch, method, values):
    data = pd.DataFrame(values)
    snapshot = data.copy(deep=True)
    manager = DataQualityManager(data)
    failure = RuntimeError("simulated assignment failure")

    def fail_assignment(self, key, value):
        raise failure

    monkeypatch.setattr(type(data.loc), "__setitem__", fail_assignment)

    with pytest.raises(RuntimeError) as raised:
        getattr(manager, method)(data)

    assert raised.value is failure
    pd.testing.assert_frame_equal(data, snapshot)
    pd.testing.assert_frame_equal(manager.get_dataset(), snapshot)
    log = manager.get_change_log()
    assert len(log) == 1
    assert log[0]["treatment"] == method
    assert log[0]["outcome"] == "failed"
    assert log[0]["rows_affected"] == 1
    assert log[0]["description"] == "RuntimeError: simulated assignment failure"
