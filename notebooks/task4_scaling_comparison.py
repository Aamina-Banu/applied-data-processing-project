import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path

from task4_input import verified_input

import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


project_root = Path(__file__).resolve().parent.parent

data_path = (
    project_root
    / "data"
    / "raw"
    / "nyc_311_january_2025.zip"
)

spark_input_path = (
    project_root
    / "data"
    / "processed"
    / "task4_spark_input.csv"
)

results_path = project_root / "results"
results_path.mkdir(parents=True, exist_ok=True)

timings_path = results_path / "task4_scaling_timings.csv"
summary_path = results_path / "task4_scaling_summary.csv"
environment_path = results_path / "task4_environment.txt"

WARMUP_RUNS = 1
MEASURED_RUNS = 5


spark_input_path.parent.mkdir(parents=True, exist_ok=True)

spark_input_path, source_csv_sha256 = verified_input(project_root)

df_raw = pd.read_csv(data_path)


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
            ["Agency", "Problem (formerly Complaint Type)"],
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

    return (
        grouped,
        len(valid_df),
        execution_time
    )


spark_start = time.perf_counter()

spark = (
    SparkSession.builder
    .master("local[*]")
    .appName("NYC311Task4")
    .getOrCreate()
)

spark_startup_time = time.perf_counter() - spark_start

spark_df = spark.read.csv(
    str(spark_input_path),
    header=True,
    inferSchema=True
)

spark_df = spark_df.cache()
spark_source_rows = spark_df.count()


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


valid_spark_check, grouped_spark_check = build_spark_pipeline(
    spark_df
)
plan_path = results_path / "task4_spark_physical_plan.txt"

plan_text = grouped_spark_check._sc._jvm.PythonSQLUtils.explainString(
    grouped_spark_check._jdf.queryExecution(),
    "formatted"
)

plan_path.write_text(
    plan_text,
    encoding="utf-8"
)
valid_spark_count = valid_spark_check.count()
spark_group_count = grouped_spark_check.count()

timing_rows = []


for run_number in range(1, WARMUP_RUNS + 1):
    pandas_result, pandas_valid_count, pandas_time = run_pandas(
        df_raw
    )

    timing_rows.append(
        {
            "framework": "pandas",
            "run_type": "warmup",
            "run_number": run_number,
            "execution_time_seconds": pandas_time
        }
    )

    spark_result, spark_time = run_spark(spark_df)

    timing_rows.append(
        {
            "framework": "spark",
            "run_type": "warmup",
            "run_number": run_number,
            "execution_time_seconds": spark_time
        }
    )


for run_number in range(1, MEASURED_RUNS + 1):
    pandas_result, pandas_valid_count, pandas_time = run_pandas(
        df_raw
    )

    timing_rows.append(
        {
            "framework": "pandas",
            "run_type": "measured",
            "run_number": run_number,
            "execution_time_seconds": pandas_time
        }
    )

    print(
        f"Pandas measured run {run_number}: "
        f"{pandas_time:.6f} seconds"
    )

    spark_result, spark_time = run_spark(spark_df)

    timing_rows.append(
        {
            "framework": "spark",
            "run_type": "measured",
            "run_number": run_number,
            "execution_time_seconds": spark_time
        }
    )

    print(
        f"Spark measured run {run_number}: "
        f"{spark_time:.6f} seconds"
    )


timings_df = pd.DataFrame(timing_rows)

timings_df.to_csv(
    timings_path,
    index=False
)

measured_df = timings_df[
    timings_df["run_type"] == "measured"
]

summary_rows = []

for framework in ["pandas", "spark"]:
    framework_times = measured_df.loc[
        measured_df["framework"] == framework,
        "execution_time_seconds"
    ].tolist()

    minimum = min(framework_times)
    maximum = max(framework_times)

    summary_rows.append(
        {
            "framework": framework,
            "median_seconds": statistics.median(
                framework_times
            ),
            "minimum_seconds": minimum,
            "maximum_seconds": maximum,
            "range_seconds": maximum - minimum
        }
    )


summary_df = pd.DataFrame(summary_rows)

summary_df.to_csv(
    summary_path,
    index=False
)


try:
    java_result = subprocess.run(
        ["java", "-version"],
        capture_output=True,
        text=True,
        check=False
    )

    java_version = (
        java_result.stderr.strip()
        or java_result.stdout.strip()
    )

    java_version = java_version.replace(
        "\n",
        " | "
    )

except OSError:
    java_version = "Unable to retrieve Java version"


environment_lines = [
    f"Python version: {sys.version.split()[0]}",
    f"Pandas version: {pd.__version__}",
    f"PySpark version: {spark.version}",
    f"Java version: {java_version}",
    f"Operating system: {platform.platform()}",
    f"Processor: {platform.processor()}",
    f"Spark master: {spark.sparkContext.master}",
    (
        "Spark default parallelism: "
        f"{spark.sparkContext.defaultParallelism}"
    ),
    f"Spark startup time: {spark_startup_time:.6f} seconds",
    f"Dataset rows: {len(df_raw)}",
    f"Dataset columns: {len(df_raw.columns)}",
    f"Spark source rows: {spark_source_rows}",
    f"Valid pandas rows: {pandas_valid_count}",
    f"Valid Spark rows: {valid_spark_count}",
    f"Pandas qualifying groups: {len(pandas_result)}",
    f"Spark qualifying groups: {spark_group_count}",
    f"Warm-up runs: {WARMUP_RUNS}",
    f"Measured runs: {MEASURED_RUNS}",
    (
        "Grouping fields: Agency, "
        "Problem (formerly Complaint Type)"
    ),
    "Minimum complaint count per group: 30"
]

environment_path.write_text(
    "\n".join(environment_lines),
    encoding="utf-8"
)


print("\nValidation")
print("----------")
print(
    f"Pandas valid rows: "
    f"{pandas_valid_count:,}"
)
print(
    f"Spark valid rows: "
    f"{valid_spark_count:,}"
)
print(
    f"Pandas qualifying groups: "
    f"{len(pandas_result):,}"
)
print(
    f"Spark qualifying groups: "
    f"{spark_group_count:,}"
)

print("\nBenchmark summary")
print("-----------------")
print(summary_df.to_string(index=False))

print(
    f"\nSpark startup time: "
    f"{spark_startup_time:.6f} seconds"
)

print("\nResults saved to:")
print(timings_path)
print(summary_path)
print(environment_path)
print(plan_path)

spark.stop()