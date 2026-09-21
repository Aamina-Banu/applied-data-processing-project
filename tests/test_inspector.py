import pandas as pd

from nyc311 import DataInspector


def test_data_inspector():
    data = pd.DataFrame({
        "Complaint Type": ["Noise", "Parking", "Noise"],
        "Status": ["Open", "Closed", "Open"],
        "ZIP Code": [10001, 10002, None]
    })

    inspector = DataInspector(data)

    result = inspector.process_data()

    assert result["row_count"] == 3
    assert result["column_count"] == 3
    assert result["column_names"] == [
        "Complaint Type",
        "Status",
        "ZIP Code"
    ]
    assert result["missing_values"]["ZIP Code"] == 1


def test_constructor_owns_dataset_copy():
    data = pd.DataFrame({"Status": ["Open"]})
    snapshot = data.copy(deep=True)
    inspector = DataInspector(data)

    data.loc[0, "Status"] = "Closed"
    pd.testing.assert_frame_equal(inspector.get_dataset(), snapshot)

    returned = inspector.get_dataset()
    returned.loc[0, "Status"] = "Pending"
    pd.testing.assert_frame_equal(inspector.get_dataset(), snapshot)
