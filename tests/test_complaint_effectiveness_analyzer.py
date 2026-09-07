import pandas as pd
import pytest

from nyc311 import ComplaintEffectivenessAnalyzer


def test_complaint_effectiveness_analyzer():
    data = pd.DataFrame({
        "Status": [
            "Closed",
            "Open",
            "Closed",
            "Open",
            "Closed",
            "Unspecified"
        ],
        "Created Date": [
            "2025-01-01 10:00:00",
            "2025-01-02 10:00:00",
            "2025-01-03 10:00:00",
            "2025-01-04 10:00:00",
            "2025-01-05 15:00:00",
            "2025-01-06 10:00:00"
        ],
        "Closed Date": [
            "2025-01-01 14:00:00",
            None,
            None,
            "2025-01-04 12:00:00",
            "2025-01-05 10:00:00",
            None
        ]
    })

    analyzer = ComplaintEffectivenessAnalyzer(data)

    result = analyzer.process_data()

    assert result["total_complaints"] == 6
    assert result["valid_closed_count"] == 2
    assert result["valid_non_closed_count"] == 1
    assert round(result["closure_rate"], 2) == 66.67
    assert result["closed_missing_date_count"] == 1
    assert result["non_closed_present_date_count"] == 1
    assert result["unspecified_count"] == 1
    assert result["resolution_record_count"] == 1
    assert result["average_resolution_hours"] == 4.0
    assert result["median_resolution_hours"] == 4.0
    assert result["invalid_resolution_date_count"] == 1


def test_complaint_effectiveness_missing_required_column():
    data = pd.DataFrame({
        "Status": ["Closed"],
        "Created Date": ["2025-01-01 10:00:00"]
    })

    analyzer = ComplaintEffectivenessAnalyzer(data)

    with pytest.raises(ValueError):
        analyzer.process_data()