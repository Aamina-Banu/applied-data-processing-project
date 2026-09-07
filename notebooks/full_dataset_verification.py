import json
import pandas as pd

from nyc311 import DataQualityManager


zip_path = "data/raw/nyc_311_january_2025.zip"
log_path = "results/data_quality_change_log.json"


# --------------------------------------------------
# 1. Load the original January dataset
# --------------------------------------------------

df = pd.read_csv(
    zip_path,
    compression="zip"
)

print("\n--- DATASET LOADED ---")
print("Rows:", len(df))
print("Columns:", len(df.columns))


# --------------------------------------------------
# 2. Check quality issues before treatment
# --------------------------------------------------

manager = DataQualityManager(df)

before_results = manager.process_data()

print("\n--- BEFORE TREATMENT ---")
print(before_results)


# --------------------------------------------------
# 3. Apply all treatments sequentially
# --------------------------------------------------

working_df = manager.replace_invalid_bbl(df)

working_df = manager.handle_invalid_zip(
    working_df
)

working_df = manager.handle_date_inconsistencies(
    working_df
)

working_df = manager.correct_encoding(
    working_df
)


# --------------------------------------------------
# 4. Check quality issues after treatment
# --------------------------------------------------

after_manager = DataQualityManager(
    working_df
)

after_results = after_manager.process_data()

print("\n--- AFTER TREATMENT ---")
print(after_results)


# --------------------------------------------------
# 5. Verify row preservation
# --------------------------------------------------

print("\n--- ROW COUNT CHECK ---")
print("Original rows:", len(df))
print("Treated rows:", len(working_df))
print(
    "Row count unchanged:",
    len(df) == len(working_df)
)


# --------------------------------------------------
# 6. Verify original DataFrame was not modified
# --------------------------------------------------

original_check = DataQualityManager(
    df
).process_data()

print("\n--- ORIGINAL DATAFRAME CHECK ---")
print(original_check)

print(
    "Original still unchanged:",
    original_check == before_results
)


# --------------------------------------------------
# 7. Inspect the in-memory change log
# --------------------------------------------------

change_log = manager.get_change_log()

print("\n--- CHANGE LOG ---")
print("Number of treatment entries:", len(change_log))

for entry in change_log:
    print(entry)


# --------------------------------------------------
# 8. Save the real change log
# --------------------------------------------------

manager.save_change_log(
    log_path
)

print("\n--- CHANGE LOG SAVED ---")
print("Saved to:", log_path)


# --------------------------------------------------
# 9. Read the JSON back to verify persistence
# --------------------------------------------------

with open(
    log_path,
    "r",
    encoding="utf-8"
) as file:
    saved_log = json.load(file)

print(
    "Saved entries:",
    len(saved_log)
)

print(
    "Saved log matches in-memory log:",
    saved_log == change_log
)


# --------------------------------------------------
# 10. Final verification summary
# --------------------------------------------------

print("\n--- FINAL VERIFICATION SUMMARY ---")

print(
    "Invalid BBL:",
    before_results["invalid_bbl_count"],
    "->",
    after_results["invalid_bbl_count"]
)

print(
    "Invalid ZIP:",
    before_results["invalid_zip_count"],
    "->",
    after_results["invalid_zip_count"]
)

print(
    "Invalid resolution dates:",
    before_results["invalid_resolution_date_count"],
    "->",
    after_results["invalid_resolution_date_count"]
)

print(
    "Encoding issues:",
    before_results["encoding_issue_count"],
    "->",
    after_results["encoding_issue_count"]
)

print(
    "Rows preserved:",
    len(df) == len(working_df)
)

print(
    "Original DataFrame preserved:",
    original_check == before_results
)

print(
    "Change log persisted:",
    saved_log == change_log
)

markers = ["Ã", "Â", "â", "ð"]

print("\n--- REMAINING ENCODING ISSUES ---")

for column in working_df.select_dtypes(
    include=["object", "string"]
).columns:
    mask = working_df[column].astype(
        "string"
    ).str.contains(
        "|".join(markers),
        regex=True,
        na=False
    )

    if mask.any():
        print("\nColumn:", column)
        print(working_df.loc[mask, column].to_list())