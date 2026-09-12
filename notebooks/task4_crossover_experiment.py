import gc
import time
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


project_root = Path(__file__).resolve().parent.parent

data_path = (
    project_root
    / "data"
    / "processed"
    / "task4_spark_input.csv"
)

results_path = project_root / "results"
results_path.mkdir(parents=True, exist_ok=True)

DATASET_SIZES = [
    50_000,
    100_000,
    200_000,
    337_551,
    675_102,
    1_350_204,
]

WARMUP_RUNS = 1
MEASURED_RUNS = 5

df_base = pd.read_csv(data_path)


def make_dataset_size(source_df, target_rows):
    if target_rows <= len(source_df):
        return source_df.iloc[:target_rows].copy()

    repeats = (target_rows // len(source_df)) + 1

    expanded_df = pd.concat(
        [source_df] * repeats,
        ignore_index=True
    )

    return expanded_df.iloc[:target_rows].copy()


def run_pandas(source_df):
    df = source_df.copy()

    start_time = time.perf_counter()

    df["Created Date"] = pd.to_datetime(
        df["Created Date"],
        format="%m/%d/%Y %I:%M:%S %p",
        errors="coerce"
    )

    df["Closed Date"] = pd.to_datetime(
        df["Closed Date"],
        format="%m/%d/%Y %I:%M:%S %p",
        errors="coerce"
    )

    df["Resolution Time (hours)"] = (
        df["Closed Date"] - df["Created Date"]
    ).dt.total_seconds() / 3600

    valid_df = df[
        df["Resolution Time (hours)"].notna()
        & (df["Resolution Time (hours)"] >= 0)
    ]

    grouped = (
        valid_df
        .groupby(
            [
                "Agency",
                "Problem (formerly Complaint Type)"
            ],
            observed=True
        )["Resolution Time (hours)"]
        .agg(
            complaint_count="count",
            median_resolution_hours="median",
            mean_resolution_hours="mean"
        )
        .reset_index()
    )

    grouped = grouped[
        grouped["complaint_count"] >= 30
    ]

    execution_time = time.perf_counter() - start_time

    return grouped, execution_time


spark = (
    SparkSession.builder
    .master("local[*]")
    .appName("NYC311Task4Crossover")
    .getOrCreate()
)

spark_base = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(str(data_path))
)

spark_base_rows = spark_base.count()


def make_spark_dataset_size(source_df, source_rows, target_rows):
    if target_rows <= source_rows:
        return source_df.limit(target_rows)

    repeats = (target_rows // source_rows) + 1

    expanded_df = source_df

    for _ in range(repeats - 1):
        expanded_df = expanded_df.unionByName(source_df)

    return expanded_df.limit(target_rows)


def build_spark_pipeline(source_df):
    transformed_df = (
        source_df
        .withColumn(
            "Created Date",
            F.to_timestamp(
                F.col("Created Date"),
                "MM/dd/yyyy hh:mm:ss a"
            )
        )
        .withColumn(
            "Closed Date",
            F.to_timestamp(
                F.col("Closed Date"),
                "MM/dd/yyyy hh:mm:ss a"
            )
        )
        .withColumn(
            "Resolution Time (hours)",
            (
                F.col("Closed Date").cast("long")
                - F.col("Created Date").cast("long")
            ) / 3600
        )
    )

    valid_df = transformed_df.filter(
        F.col("Resolution Time (hours)").isNotNull()
        & (F.col("Resolution Time (hours)") >= 0)
    )

    grouped_df = (
        valid_df
        .groupBy(
            "Agency",
            "Problem (formerly Complaint Type)"
        )
        .agg(
            F.count(
                "Resolution Time (hours)"
            ).alias(
                "complaint_count"
            ),
            F.median(
                "Resolution Time (hours)"
            ).alias(
                "median_resolution_hours"
            ),
            F.avg(
                "Resolution Time (hours)"
            ).alias(
                "mean_resolution_hours"
            )
        )
        .filter(
            F.col("complaint_count") >= 30
        )
    )

    return valid_df, grouped_df


def run_spark(source_df):
    start_time = time.perf_counter()

    _, grouped_df = build_spark_pipeline(source_df)

    result = grouped_df.collect()

    execution_time = time.perf_counter() - start_time

    return result, execution_time


timing_rows = []

for size in DATASET_SIZES:
    print(f"\nDataset size: {size:,}")
    print("-" * 30)

    pandas_df = make_dataset_size(
        df_base,
        size
    )

    spark_df = make_spark_dataset_size(
        spark_base,
        spark_base_rows,
        size
    )

    spark_df = spark_df.cache()
    spark_row_count = spark_df.count()

    print(
        f"Pandas rows: {len(pandas_df):,}"
    )

    print(
        f"Spark rows: {spark_row_count:,}"
    )

    for _ in range(WARMUP_RUNS):
        run_pandas(pandas_df)
        run_spark(spark_df)

    for run_number in range(1, MEASURED_RUNS + 1):
        pandas_result, pandas_time = run_pandas(
            pandas_df
        )

        spark_result, spark_time = run_spark(
            spark_df
        )

        timing_rows.append(
            {
                "dataset_rows": size,
                "framework": "pandas",
                "run_number": run_number,
                "execution_time_seconds": pandas_time
            }
        )

        timing_rows.append(
            {
                "dataset_rows": size,
                "framework": "spark",
                "run_number": run_number,
                "execution_time_seconds": spark_time
            }
        )

        print(
            f"Run {run_number}: "
            f"pandas={pandas_time:.6f}s, "
            f"spark={spark_time:.6f}s"
        )

    spark_df.unpersist()

    del pandas_df
    del spark_df

    gc.collect()


timings_df = pd.DataFrame(timing_rows)

timings_output_path = (
    results_path
    / "task4_crossover_timings.csv"
)

timings_df.to_csv(
    timings_output_path,
    index=False
)


summary_df = (
    timings_df
    .groupby(
        [
            "dataset_rows",
            "framework"
        ]
    )["execution_time_seconds"]
    .agg(
        median_seconds="median",
        minimum_seconds="min",
        maximum_seconds="max"
    )
    .reset_index()
)

summary_df["range_seconds"] = (
    summary_df["maximum_seconds"]
    - summary_df["minimum_seconds"]
)

summary_output_path = (
    results_path
    / "task4_crossover_summary.csv"
)

summary_df.to_csv(
    summary_output_path,
    index=False
)


chart_df = summary_df.pivot(
    index="dataset_rows",
    columns="framework",
    values="median_seconds"
).reset_index()

plt.figure(figsize=(9, 5))

plt.plot(
    chart_df["dataset_rows"],
    chart_df["pandas"],
    marker="o",
    label="pandas"
)

plt.plot(
    chart_df["dataset_rows"],
    chart_df["spark"],
    marker="o",
    label="Spark"
)

plt.xlabel("Dataset size (rows)")
plt.ylabel("Median execution time (seconds)")
plt.title("Pandas vs Spark Execution Time by Dataset Size")
plt.legend()
plt.grid(alpha=0.25)
plt.tight_layout()

chart_output_path = (
    results_path
    / "task4_crossover_chart.png"
)

plt.savefig(
    chart_output_path,
    dpi=300
)

plt.close()

print(chart_output_path)

print("\nCrossover summary")
print("-----------------")

print(
    summary_df.to_string(
        index=False
    )
)



print("\nResults saved to:")
print(timings_output_path)
print(summary_output_path)

spark.stop()