from pathlib import Path

import pandas as pd
from scipy.stats import kruskal


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRUBBED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "nyc_311_january_2025_scrubbed.parquet"
RESULTS_PATH = PROJECT_ROOT / "results"

PROBLEM_COLUMN = "Problem (formerly Complaint Type)"

MIN_GROUP_SIZE = 30
MIN_AGENCY_SAMPLE = 1000

RESOLUTION_BINS = [
    -float("inf"),
    4,
    24,
    72,
    168,
    float("inf")
]

RESOLUTION_LABELS = [
    "Very short",
    "Short",
    "Medium",
    "Long",
    "Very long"
]

RESULTS_PATH.mkdir(parents=True, exist_ok=True)


df = pd.read_parquet(SCRUBBED_DATA_PATH)


df["Created Date Parsed"] = pd.to_datetime(
    df["Created Date"],
    format="%m/%d/%Y %I:%M:%S %p",
    errors="coerce"
)

df["Closed Date Parsed"] = pd.to_datetime(
    df["Closed Date"],
    format="%m/%d/%Y %I:%M:%S %p",
    errors="coerce"
)

df["Resolution Time Hours"] = (
    df["Closed Date Parsed"] - df["Created Date Parsed"]
).dt.total_seconds() / 3600


valid_resolution_df = df[
    df["Resolution Time Hours"].notna()
    & (df["Resolution Time Hours"] >= 0)
].copy()


segment_summary = (
    valid_resolution_df
    .groupby(
        ["Agency", PROBLEM_COLUMN],
        observed=True
    )["Resolution Time Hours"]
    .agg(
        complaint_count="count",
        median_resolution="median",
        mean_resolution="mean"
    )
    .reset_index()
)

segment_summary = segment_summary[
    segment_summary["complaint_count"] >= MIN_GROUP_SIZE
].copy()

segment_summary = segment_summary.sort_values(
    "median_resolution",
    ascending=True
)


print("\nAgency × Problem Segments")

print(f"\nSegments with at least {MIN_GROUP_SIZE} valid complaints:")
print(len(segment_summary))

print("\n10 shortest median-resolution segments:")
print(
    segment_summary
    .head(10)
    .to_string(
        index=False,
        formatters={
            "median_resolution": "{:.2f}".format,
            "mean_resolution": "{:.2f}".format
        }
    )
)

print("\n10 longest median-resolution segments:")
print(
    segment_summary
    .sort_values(
        "median_resolution",
        ascending=False
    )
    .head(10)
    .to_string(
        index=False,
        formatters={
            "median_resolution": "{:.2f}".format,
            "mean_resolution": "{:.2f}".format
        }
    )
)


segment_summary.to_csv(
    RESULTS_PATH / "task3_model_segments.csv",
    index=False
)


valid_resolution_df["Resolution Band"] = pd.cut(
    valid_resolution_df["Resolution Time Hours"],
    bins=RESOLUTION_BINS,
    labels=RESOLUTION_LABELS,
    right=False
)


resolution_band_by_agency = pd.crosstab(
    valid_resolution_df["Agency"],
    valid_resolution_df["Resolution Band"]
)

print("\nResolution Bands by Agency:")
print(resolution_band_by_agency.to_string())

resolution_band_by_agency.to_csv(
    RESULTS_PATH / "task3_resolution_bands_by_agency.csv"
)


resolution_band_percentage_by_agency = (
    pd.crosstab(
        valid_resolution_df["Agency"],
        valid_resolution_df["Resolution Band"],
        normalize="index"
    )
    * 100
)

print("\nResolution Band Percentages by Agency:")
print(
    resolution_band_percentage_by_agency
    .round(2)
    .to_string()
)

resolution_band_percentage_by_agency.round(2).to_csv(
    RESULTS_PATH
    / "task3_resolution_band_percentages_by_agency.csv"
)


resolution_band_by_problem = pd.crosstab(
    valid_resolution_df[PROBLEM_COLUMN],
    valid_resolution_df["Resolution Band"]
)

print("\nResolution Bands by Problem:")
print(resolution_band_by_problem.to_string())

resolution_band_by_problem.to_csv(
    RESULTS_PATH / "task3_resolution_bands_by_problem.csv"
)


resolution_band_percentage_by_problem = (
    pd.crosstab(
        valid_resolution_df[PROBLEM_COLUMN],
        valid_resolution_df["Resolution Band"],
        normalize="index"
    )
    * 100
)

print("\nResolution Band Percentages by Problem:")
print(
    resolution_band_percentage_by_problem
    .round(2)
    .to_string()
)

resolution_band_percentage_by_problem.round(2).to_csv(
    RESULTS_PATH
    / "task3_resolution_band_percentages_by_problem.csv"
)


agency_resolution_count = (
    valid_resolution_df
    .groupby(
        "Agency",
        observed=True
    )["Resolution Time Hours"]
    .count()
    .sort_values(ascending=False)
)

selected_agencies = agency_resolution_count[
    agency_resolution_count >= MIN_AGENCY_SAMPLE
].index


statistical_df = valid_resolution_df[
    valid_resolution_df["Agency"].isin(selected_agencies)
].copy()


agency_sample_sizes = (
    statistical_df
    .groupby(
        "Agency",
        observed=True
    )["Resolution Time Hours"]
    .count()
    .sort_values(ascending=False)
)


print(
    f"\nAgencies with at least "
    f"{MIN_AGENCY_SAMPLE:,} valid resolution records:"
)
print(selected_agencies.tolist())

print("\nSample sizes used for Kruskal-Wallis:")
print(agency_sample_sizes)


groups = [
    group["Resolution Time Hours"].to_numpy()
    for _, group in statistical_df.groupby(
        "Agency",
        observed=True
    )
]


kruskal_result = None

if len(groups) >= 2:
    kruskal_result = kruskal(*groups)

    print("\nKruskal-Wallis test:")
    print(f"H statistic: {kruskal_result.statistic:.4f}")
    print(f"p-value: {kruskal_result.pvalue:.6g}")
else:
    print(
        "\nKruskal-Wallis test could not be performed "
        "because fewer than two agencies met the sample-size requirement."
    )


with open(
    RESULTS_PATH / "task3_kruskal_wallis.txt",
    "w",
    encoding="utf-8"
) as file:
    file.write("Kruskal-Wallis Test\n\n")

    file.write(
        f"Minimum agency sample size: "
        f"{MIN_AGENCY_SAMPLE}\n"
    )

    file.write(
        f"Number of agencies included: "
        f"{len(selected_agencies)}\n"
    )

    file.write(
        "Agencies included: "
        f"{', '.join(selected_agencies)}\n\n"
    )

    file.write("Sample sizes:\n")
    file.write(agency_sample_sizes.to_string())
    file.write("\n\n")

    if kruskal_result is not None:
        file.write(
            f"H statistic: "
            f"{kruskal_result.statistic:.4f}\n"
        )
        file.write(
            f"p-value: "
            f"{kruskal_result.pvalue:.12g}\n"
        )
    else:
        file.write(
            "Test not performed because fewer than "
            "two agencies met the sample-size requirement.\n"
        )


print("\nModel results saved to the results folder.")
