from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RESULTS_DIR = PROJECT_ROOT / "results"

TIMING_RESULTS_PATH = RESULTS_DIR / "storage_benchmark_results.csv"
CHART_PATH = RESULTS_DIR / "storage_benchmark_timing_chart.png"


results_df = pd.read_csv(TIMING_RESULTS_PATH)

results_df = results_df[
    ["format", "operation", "median_seconds"]
]

operations = [
    "write_full",
    "read_full",
    "read_one_column"
]

formats = [
    "CSV",
    "JSON",
    "Parquet"
]


fig, ax = plt.subplots(figsize=(11, 6.5))

x = range(len(operations))
bar_width = 0.24

colors = {
    "CSV": "#4C78A8",
    "JSON": "#F28E2B",
    "Parquet": "#59A14F"
}


for i, file_format in enumerate(formats):
    format_data = results_df[
        results_df["format"] == file_format
    ].set_index("operation")

    values = [
        format_data.loc[operation, "median_seconds"]
        for operation in operations
    ]

    positions = [
        position + (i - 1) * bar_width
        for position in x
    ]

    bars = ax.bar(
        positions,
        values,
        bar_width,
        label=file_format,
        color=colors[file_format],
        edgecolor="white",
        linewidth=0.8
    )

    ax.bar_label(
        bars,
        labels=[f"{value:.3f}" for value in values],
        padding=3,
        fontsize=9
    )


ax.set_xlabel(
    "Benchmark Operation",
    fontsize=11
)

ax.set_ylabel(
    "Median Execution Time (seconds)",
    fontsize=11
)

ax.set_title(
    "Storage Format Performance Comparison",
    fontsize=14,
    fontweight="bold",
    pad=15
)


ax.set_xticks(list(x))

ax.set_xticklabels([
    "Full Dataset Write",
    "Full Dataset Read",
    "One-Column Read"
])


ax.legend(
    title="Storage Format",
    frameon=False
)


ax.grid(
    axis="y",
    linestyle="--",
    alpha=0.25
)

ax.set_axisbelow(True)


ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)


ax.margins(y=0.12)


plt.tight_layout()


plt.savefig(
    CHART_PATH,
    dpi=300,
    bbox_inches="tight"
)


plt.show()


print(f"Chart saved to: {CHART_PATH}")