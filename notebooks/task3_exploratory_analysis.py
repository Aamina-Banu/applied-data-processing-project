from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRUBBED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "nyc_311_january_2025_scrubbed.parquet"
RESULTS_PATH = PROJECT_ROOT / "results"

PROBLEM_COLUMN = "Problem (formerly Complaint Type)"

RESULTS_PATH.mkdir(parents=True, exist_ok=True)


# Load the dataset
df = pd.read_parquet(SCRUBBED_DATA_PATH)


agency_counts = (
    df["Agency"]
    .value_counts()
    .sort_values(ascending=False)
)

problem_counts = (
    df[PROBLEM_COLUMN]
    .value_counts()
    .sort_values(ascending=False)
)

top_15_problems = problem_counts.head(15).index

agency_problem_crosstab = pd.crosstab(
    df["Agency"],
    df[PROBLEM_COLUMN]
)

top_problem_crosstab = agency_problem_crosstab[top_15_problems]

print("\nAgency complaint counts:")
print(agency_counts)

print("\nTop 15 problem types:")
print(problem_counts.head(15))

print("\nAgency and top problem-type crosstab:")
print(top_problem_crosstab.to_string())


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

print("\nResolution-time statistics before filtering:")
print(df["Resolution Time Hours"].describe())

negative_resolution_count = (
    df["Resolution Time Hours"] < 0
).sum()

print("\nNegative resolution-time records:")
print(negative_resolution_count)


# Keep only valid non-negative resolution times
valid_resolution_df = df[
    df["Resolution Time Hours"] >= 0
]

print("\nValid resolution-time statistics:")
print(valid_resolution_df["Resolution Time Hours"].describe())


agency_median_resolution = (
    valid_resolution_df
    .groupby("Agency")["Resolution Time Hours"]
    .median()
    .sort_values()
)

agency_resolution_count = (
    valid_resolution_df
    .groupby("Agency")["Resolution Time Hours"]
    .count()
)

print("\nValid resolution records by agency:")
print(agency_resolution_count)

print("\nMedian resolution time by agency:")
print(agency_median_resolution)


problem_median_resolution = (
    valid_resolution_df
    .groupby(PROBLEM_COLUMN)["Resolution Time Hours"]
    .median()
    .sort_values()
)

top_problem_median_resolution = (
    problem_median_resolution
    .loc[top_15_problems]
    .sort_values()
)

print("\nMedian resolution time for top 15 problem types:")
print(top_problem_median_resolution)


closed_date_present_count = (
    df["Closed Date Parsed"]
    .notna()
    .sum()
)

closed_date_missing_count = (
    df["Closed Date Parsed"]
    .isna()
    .sum()
)

print("\nRecords with a usable Closed Date:")
print(closed_date_present_count)

print("\nRecords without a usable Closed Date:")
print(closed_date_missing_count)


missing_closed_by_agency = (
    df[df["Closed Date Parsed"].isna()]["Agency"]
    .value_counts()
    .sort_values(ascending=False)
)

print("\nMissing Closed Dates by agency:")
print(missing_closed_by_agency)


agency_closed_percentage = (
    df[df["Closed Date Parsed"].notna()]
    .groupby("Agency")
    .size()
    .div(agency_counts)
    .mul(100)
    .sort_values()
)

print("\nPercentage of complaints with a usable Closed Date by agency:")
print(agency_closed_percentage)


closed_status_missing_date = (
    (df["Status"] == "Closed")
    & df["Closed Date Parsed"].isna()
).sum()

non_closed_status_with_date = (
    (df["Status"] != "Closed")
    & df["Closed Date Parsed"].notna()
).sum()

non_closed_with_date_statuses = (
    df[
        (df["Status"] != "Closed")
        & df["Closed Date Parsed"].notna()
    ]["Status"]
    .value_counts()
)

print("\nClosed status but missing Closed Date:")
print(closed_status_missing_date)

print("\nNon-Closed status but Closed Date present:")
print(non_closed_status_with_date)

print("\nStatuses of non-Closed records with a Closed Date:")
print(non_closed_with_date_statuses)


explore_summary = pd.DataFrame(
    {
        "metric": [
            "total_records",
            "usable_closed_dates",
            "missing_closed_dates",
            "negative_resolution_times",
            "closed_status_missing_date",
            "non_closed_status_with_date",
            "valid_resolution_records",
            "median_resolution_hours",
            "mean_resolution_hours"
        ],
        "value": [
            len(df),
            closed_date_present_count,
            closed_date_missing_count,
            negative_resolution_count,
            closed_status_missing_date,
            non_closed_status_with_date,
            len(valid_resolution_df),
            valid_resolution_df["Resolution Time Hours"].median(),
            valid_resolution_df["Resolution Time Hours"].mean()
        ]
    }
)

explore_summary.to_csv(
    RESULTS_PATH / "task3_explore_summary.csv",
    index=False
)


agency_resolution_summary = pd.DataFrame(
    {
        "complaint_count": agency_counts,
        "valid_resolution_count": agency_resolution_count,
        "median_resolution_hours": agency_median_resolution,
        "closed_date_completeness_percent": agency_closed_percentage
    }
)

agency_resolution_summary.to_csv(
    RESULTS_PATH / "task3_agency_resolution_summary.csv"
)


problem_resolution_summary = pd.DataFrame(
    {
        "complaint_count": problem_counts,
        "median_resolution_hours": problem_median_resolution
    }
)

problem_resolution_summary.to_csv(
    RESULTS_PATH / "task3_problem_resolution_summary.csv"
)


with open(
    RESULTS_PATH / "task3_tracking_consistency.txt",
    "w",
    encoding="utf-8"
) as file:
    file.write(
        f"Closed status but missing Closed Date: "
        f"{closed_status_missing_date}\n"
    )
    file.write(
        f"Non-Closed status but Closed Date present: "
        f"{non_closed_status_with_date}\n\n"
    )
    file.write(
        "Statuses of non-Closed records with a Closed Date:\n"
    )
    file.write(non_closed_with_date_statuses.to_string())
    file.write("\n")


top_15_problem_counts = (
    problem_counts
    .head(15)
    .sort_values()
)

fig, ax = plt.subplots(figsize=(11, 7))

bars = ax.barh(
    top_15_problem_counts.index,
    top_15_problem_counts.values
)

ax.set_title(
    "Top 15 NYC 311 Complaint Types – January 2025",
    fontsize=16,
    pad=14
)
ax.set_xlabel("Number of Complaints", fontsize=12)
ax.set_ylabel("Complaint Type", fontsize=12)

ax.grid(axis="x", alpha=0.25)

for bar in bars:
    width = bar.get_width()
    ax.text(
        width + 700,
        bar.get_y() + bar.get_height() / 2,
        f"{int(width):,}",
        va="center",
        fontsize=9
    )

ax.set_xlim(
    0,
    top_15_problem_counts.max() * 1.12
)

fig.tight_layout()

fig.savefig(
    RESULTS_PATH / "task3_top_15_complaint_types.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


fig, ax = plt.subplots(figsize=(11, 7))

bars = ax.barh(
    agency_median_resolution.index,
    agency_median_resolution.values
)

ax.set_title(
    "Median Resolution Time by Agency – January 2025",
    fontsize=16,
    pad=14
)
ax.set_xlabel(
    "Median Resolution Time (Hours, Log Scale)",
    fontsize=12
)
ax.set_ylabel("Agency", fontsize=12)

ax.set_xscale("log")
ax.grid(axis="x", alpha=0.25)

for bar, value in zip(
    bars,
    agency_median_resolution.values
):
    ax.text(
        value * 1.08,
        bar.get_y() + bar.get_height() / 2,
        f"{value:.1f} h",
        va="center",
        fontsize=9
    )

ax.set_xlim(
    max(agency_median_resolution.min() * 0.7, 0.5),
    agency_median_resolution.max() * 1.6
)

fig.tight_layout()

fig.savefig(
    RESULTS_PATH / "task3_median_resolution_by_agency.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)


fig, ax = plt.subplots(figsize=(11, 7))

bars = ax.barh(
    agency_closed_percentage.index,
    agency_closed_percentage.values
)

ax.set_title(
    "Closed Date Completeness by Agency – January 2025",
    fontsize=16,
    pad=14
)
ax.set_xlabel(
    "Complaints with a Usable Closed Date (%)",
    fontsize=12
)
ax.set_ylabel("Agency", fontsize=12)

ax.grid(axis="x", alpha=0.25)

for bar, value in zip(
    bars,
    agency_closed_percentage.values
):
    ax.text(
        min(value + 1, 101),
        bar.get_y() + bar.get_height() / 2,
        f"{value:.1f}%",
        va="center",
        fontsize=9
    )

ax.set_xlim(0, 106)

fig.tight_layout()

fig.savefig(
    RESULTS_PATH / "task3_closed_date_completeness_by_agency.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)

print("\nExplore results and figures saved to the results folder.")
