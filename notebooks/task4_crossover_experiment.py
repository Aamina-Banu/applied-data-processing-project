import gc
import hashlib
import platform
import sys
import tempfile
from datetime import datetime, timezone
import numpy as np
from task4_input import verified_input
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

data_path, source_csv_sha256 = verified_input(project_root)
df_base = pd.read_csv(data_path)
if not df_base["Unique Key"].is_unique:
    raise ValueError("Source request keys must be unique")


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

    return grouped, len(valid_df), execution_time


spark = (
    SparkSession.builder
    .master("local[*]")
    .appName("NYC311Task4Crossover")
    .config("spark.driver.memory", "4g")
    .getOrCreate()
)

# UTC preserves naive wall-clock subtraction consistently across the two tools.
spark.conf.set("spark.sql.session.timeZone", "UTC")
spark.sparkContext.setLogLevel("ERROR")


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
validation_rows = []
keys = ["Agency", "Problem (formerly Complaint Type)"]
metrics = ["complaint_count", "median_resolution_hours", "mean_resolution_hours"]


for size in DATASET_SIZES:
    print(f"\nDataset size: {size:,}")
    print("-" * 30)

    pandas_df = make_dataset_size(
        df_base,
        size
    )

    # One canonical file per workload; both engines read the same records.
    # Preparation, input checks and result validation are outside timing.
    workload_dir = tempfile.TemporaryDirectory(dir=project_root / "data/processed")
    workload_path = Path(workload_dir.name) / "workload.csv"
    pandas_df.to_csv(workload_path, index=False)
    with workload_path.open("rb") as stream:
        workload_sha256 = hashlib.file_digest(stream, "sha256").hexdigest()
    pandas_df = pd.read_csv(workload_path)
    spark_df = spark.read.csv(str(workload_path), header=True, inferSchema=True).cache()
    spark_row_count = spark_df.count()
    if len(pandas_df) != size or spark_row_count != size:
        raise ValueError("Workload row counts differ")
    expected_keys = pandas_df["Unique Key"].value_counts().sort_index()
    actual_keys = pd.Series({row["Unique Key"]: row["count"] for row in
                             spark_df.groupBy("Unique Key").count().collect()}).sort_index()
    pd.testing.assert_series_equal(expected_keys, actual_keys, check_names=False,
                                   check_dtype=False, check_index_type=False)
    pandas_check, pandas_valid, _ = run_pandas(pandas_df)
    valid_check, grouped_check = build_spark_pipeline(spark_df)
    spark_valid = valid_check.count()
    spark_check = pd.DataFrame([row.asDict() for row in grouped_check.collect()])
    left = pandas_check.set_index(keys).sort_index()[metrics]
    right = spark_check.set_index(keys).sort_index()[metrics]
    pd.testing.assert_index_equal(left.index, right.index)
    if pandas_valid != spark_valid:
        raise ValueError("Valid-row counts differ")
    np.testing.assert_array_equal(left["complaint_count"], right["complaint_count"])
    np.testing.assert_array_equal(left["median_resolution_hours"], right["median_resolution_hours"])
    np.testing.assert_allclose(left["mean_resolution_hours"], right["mean_resolution_hours"],
                               rtol=1e-12, atol=1e-9)
    validation_rows.append(dict(dataset_rows=size, workload_sha256=workload_sha256,
        input_key_multiplicities_match=True, pandas_valid_rows=pandas_valid,
        spark_valid_rows=spark_valid, qualifying_groups=len(left),
        group_keys_match=True, counts_match=True, exact_medians_match=True,
        max_mean_absolute_difference_hours=float((left["mean_resolution_hours"]-
            right["mean_resolution_hours"]).abs().max()), validation_passed=True))
    print(f"Validation passed: {pandas_valid:,} valid rows, {len(left)} groups", flush=True)

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
        pandas_result, _, pandas_time = run_pandas(
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

    spark_df.unpersist(blocking=True)
    workload_dir.cleanup()

    del pandas_df
    del spark_df

    gc.collect()


pd.DataFrame(validation_rows).to_csv(results_path / "task4_crossover_validation.csv", index=False)
environment = [
    f"Run UTC: {datetime.now(timezone.utc).isoformat()}",
    f"Python: {sys.version}", f"pandas: {pd.__version__}", f"NumPy: {np.__version__}",
    f"Spark: {spark.version}", f"OS: {platform.platform()}",
    f"Processor: {platform.processor()}",
    f"Java: {spark.sparkContext._jvm.java.lang.System.getProperty('java.version')}",
    f"Master: {spark.sparkContext.master}",
    f"Driver memory: {spark.conf.get('spark.driver.memory')}",
    f"JVM maximum heap bytes: {spark.sparkContext._jvm.java.lang.Runtime.getRuntime().maxMemory()}",
    f"Default parallelism: {spark.sparkContext.defaultParallelism}",
    f"Shuffle partitions: {spark.conf.get('spark.sql.shuffle.partitions')}",
    f"AQE: {spark.conf.get('spark.sql.adaptive.enabled')}",
    f"Session timezone: {spark.conf.get('spark.sql.session.timeZone')}",
    f"Source CSV SHA256: {source_csv_sha256}",
    f"Warmups per size: {WARMUP_RUNS}; measured runs: {MEASURED_RUNS}",
    "Timing excludes input I/O, workload construction, caching, validation and pandas initial copy.",
    "Means tolerance: rtol=1e-12, atol=1e-9 hours; counts and medians exact.",
    "Synthetic larger workloads repeat source observations; no new observations.",
]
(results_path / "task4_crossover_environment.txt").write_text("\n".join(environment), encoding="utf-8")
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

for framework in ["pandas", "spark"]:
    series = summary_df[summary_df.framework == framework].sort_values("dataset_rows")
    plt.errorbar(series.dataset_rows, series.median_seconds,
        yerr=[series.median_seconds-series.minimum_seconds,
              series.maximum_seconds-series.median_seconds],
        marker="o", capsize=3, label=framework)


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