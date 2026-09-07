from pathlib import Path
import time
import statistics
import platform

import pandas as pd
import pyarrow


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "nyc_311_january_2025.zip"
BENCHMARK_DIR = PROJECT_ROOT / "data" / "processed" / "storage_benchmark"
RESULTS_DIR = PROJECT_ROOT / "results"

BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

WARMUP_RUNS = 1
MEASURED_RUNS = 5

df = pd.read_csv(RAW_DATA_PATH)

print(df.shape)

COLUMN_TO_READ = "Problem (formerly Complaint Type)"

print(COLUMN_TO_READ in df.columns)

CSV_PATH = BENCHMARK_DIR / "nyc311.csv"
JSON_PATH = BENCHMARK_DIR / "nyc311.json"
PARQUET_PATH = BENCHMARK_DIR / "nyc311.parquet"

CSV_GZIP_PATH = BENCHMARK_DIR / "nyc311.csv.gz"
JSON_GZIP_PATH = BENCHMARK_DIR / "nyc311.json.gz"
PARQUET_GZIP_PATH = BENCHMARK_DIR / "nyc311_gzip.parquet"

TIMING_RESULTS_PATH = RESULTS_DIR / "storage_benchmark_results.csv"
FILE_SIZE_RESULTS_PATH = RESULTS_DIR / "storage_file_sizes.csv"
ENVIRONMENT_RESULTS_PATH = RESULTS_DIR / "storage_benchmark_environment.txt"


def benchmark_operation(operation):
    times = []

    for run in range(WARMUP_RUNS + MEASURED_RUNS):
        start = time.perf_counter()

        operation()

        elapsed = time.perf_counter() - start

        if run >= WARMUP_RUNS:
            times.append(elapsed)

    median_time = statistics.median(times)
    minimum_time = min(times)
    maximum_time = max(times)
    time_range = maximum_time - minimum_time

    return times, median_time, minimum_time, maximum_time, time_range


timing_results = []


csv_times, csv_write_time, csv_write_min, csv_write_max, csv_write_range = benchmark_operation(
    lambda: df.to_csv(CSV_PATH, index=False)
)

print("\nCSV write")
print(f"Runs: {[round(value, 4) for value in csv_times]}")
print(f"Median: {csv_write_time:.4f} seconds")
print(f"Range: {csv_write_range:.4f} seconds")
print(f"Min-Max: {csv_write_min:.4f}-{csv_write_max:.4f} seconds")

timing_results.append({
    "format": "CSV",
    "operation": "write_full",
    "run_1": csv_times[0],
    "run_2": csv_times[1],
    "run_3": csv_times[2],
    "run_4": csv_times[3],
    "run_5": csv_times[4],
    "median_seconds": csv_write_time,
    "min_seconds": csv_write_min,
    "max_seconds": csv_write_max,
    "range_seconds": csv_write_range,
})


json_times, json_write_time, json_write_min, json_write_max, json_write_range = benchmark_operation(
    lambda: df.to_json(JSON_PATH, orient="records")
)

print("\nJSON write")
print(f"Runs: {[round(value, 4) for value in json_times]}")
print(f"Median: {json_write_time:.4f} seconds")
print(f"Range: {json_write_range:.4f} seconds")
print(f"Min-Max: {json_write_min:.4f}-{json_write_max:.4f} seconds")

timing_results.append({
    "format": "JSON",
    "operation": "write_full",
    "run_1": json_times[0],
    "run_2": json_times[1],
    "run_3": json_times[2],
    "run_4": json_times[3],
    "run_5": json_times[4],
    "median_seconds": json_write_time,
    "min_seconds": json_write_min,
    "max_seconds": json_write_max,
    "range_seconds": json_write_range,
})


parquet_times, parquet_write_time, parquet_write_min, parquet_write_max, parquet_write_range = benchmark_operation(
    lambda: df.to_parquet(PARQUET_PATH, index=False, compression=None)
)

print("\nParquet write")
print(f"Runs: {[round(value, 4) for value in parquet_times]}")
print(f"Median: {parquet_write_time:.4f} seconds")
print(f"Range: {parquet_write_range:.4f} seconds")
print(f"Min-Max: {parquet_write_min:.4f}-{parquet_write_max:.4f} seconds")

timing_results.append({
    "format": "Parquet",
    "operation": "write_full",
    "run_1": parquet_times[0],
    "run_2": parquet_times[1],
    "run_3": parquet_times[2],
    "run_4": parquet_times[3],
    "run_5": parquet_times[4],
    "median_seconds": parquet_write_time,
    "min_seconds": parquet_write_min,
    "max_seconds": parquet_write_max,
    "range_seconds": parquet_write_range,
})


csv_read_times, csv_read_time, csv_read_min, csv_read_max, csv_read_range = benchmark_operation(
    lambda: pd.read_csv(CSV_PATH)
)

print("\nCSV full read")
print(f"Runs: {[round(value, 4) for value in csv_read_times]}")
print(f"Median: {csv_read_time:.4f} seconds")
print(f"Range: {csv_read_range:.4f} seconds")
print(f"Min-Max: {csv_read_min:.4f}-{csv_read_max:.4f} seconds")

timing_results.append({
    "format": "CSV",
    "operation": "read_full",
    "run_1": csv_read_times[0],
    "run_2": csv_read_times[1],
    "run_3": csv_read_times[2],
    "run_4": csv_read_times[3],
    "run_5": csv_read_times[4],
    "median_seconds": csv_read_time,
    "min_seconds": csv_read_min,
    "max_seconds": csv_read_max,
    "range_seconds": csv_read_range,
})


json_read_times, json_read_time, json_read_min, json_read_max, json_read_range = benchmark_operation(
    lambda: pd.read_json(JSON_PATH)
)

print("\nJSON full read")
print(f"Runs: {[round(value, 4) for value in json_read_times]}")
print(f"Median: {json_read_time:.4f} seconds")
print(f"Range: {json_read_range:.4f} seconds")
print(f"Min-Max: {json_read_min:.4f}-{json_read_max:.4f} seconds")

timing_results.append({
    "format": "JSON",
    "operation": "read_full",
    "run_1": json_read_times[0],
    "run_2": json_read_times[1],
    "run_3": json_read_times[2],
    "run_4": json_read_times[3],
    "run_5": json_read_times[4],
    "median_seconds": json_read_time,
    "min_seconds": json_read_min,
    "max_seconds": json_read_max,
    "range_seconds": json_read_range,
})


parquet_read_times, parquet_read_time, parquet_read_min, parquet_read_max, parquet_read_range = benchmark_operation(
    lambda: pd.read_parquet(PARQUET_PATH)
)

print("\nParquet full read")
print(f"Runs: {[round(value, 4) for value in parquet_read_times]}")
print(f"Median: {parquet_read_time:.4f} seconds")
print(f"Range: {parquet_read_range:.4f} seconds")
print(f"Min-Max: {parquet_read_min:.4f}-{parquet_read_max:.4f} seconds")

timing_results.append({
    "format": "Parquet",
    "operation": "read_full",
    "run_1": parquet_read_times[0],
    "run_2": parquet_read_times[1],
    "run_3": parquet_read_times[2],
    "run_4": parquet_read_times[3],
    "run_5": parquet_read_times[4],
    "median_seconds": parquet_read_time,
    "min_seconds": parquet_read_min,
    "max_seconds": parquet_read_max,
    "range_seconds": parquet_read_range,
})


csv_column_times, csv_column_read_time, csv_column_min, csv_column_max, csv_column_range = benchmark_operation(
    lambda: pd.read_csv(
        CSV_PATH,
        usecols=[COLUMN_TO_READ]
    )
)

print("\nCSV one-column read")
print(f"Runs: {[round(value, 4) for value in csv_column_times]}")
print(f"Median: {csv_column_read_time:.4f} seconds")
print(f"Range: {csv_column_range:.4f} seconds")
print(f"Min-Max: {csv_column_min:.4f}-{csv_column_max:.4f} seconds")

timing_results.append({
    "format": "CSV",
    "operation": "read_one_column",
    "run_1": csv_column_times[0],
    "run_2": csv_column_times[1],
    "run_3": csv_column_times[2],
    "run_4": csv_column_times[3],
    "run_5": csv_column_times[4],
    "median_seconds": csv_column_read_time,
    "min_seconds": csv_column_min,
    "max_seconds": csv_column_max,
    "range_seconds": csv_column_range,
})


json_column_times, json_column_read_time, json_column_min, json_column_max, json_column_range = benchmark_operation(
    lambda: pd.read_json(JSON_PATH)[[COLUMN_TO_READ]]
)

print("\nJSON one-column read")
print(f"Runs: {[round(value, 4) for value in json_column_times]}")
print(f"Median: {json_column_read_time:.4f} seconds")
print(f"Range: {json_column_range:.4f} seconds")
print(f"Min-Max: {json_column_min:.4f}-{json_column_max:.4f} seconds")

timing_results.append({
    "format": "JSON",
    "operation": "read_one_column",
    "run_1": json_column_times[0],
    "run_2": json_column_times[1],
    "run_3": json_column_times[2],
    "run_4": json_column_times[3],
    "run_5": json_column_times[4],
    "median_seconds": json_column_read_time,
    "min_seconds": json_column_min,
    "max_seconds": json_column_max,
    "range_seconds": json_column_range,
})


parquet_column_times, parquet_column_read_time, parquet_column_min, parquet_column_max, parquet_column_range = benchmark_operation(
    lambda: pd.read_parquet(
        PARQUET_PATH,
        columns=[COLUMN_TO_READ]
    )
)

print("\nParquet one-column read")
print(f"Runs: {[round(value, 4) for value in parquet_column_times]}")
print(f"Median: {parquet_column_read_time:.4f} seconds")
print(f"Range: {parquet_column_range:.4f} seconds")
print(f"Min-Max: {parquet_column_min:.4f}-{parquet_column_max:.4f} seconds")

timing_results.append({
    "format": "Parquet",
    "operation": "read_one_column",
    "run_1": parquet_column_times[0],
    "run_2": parquet_column_times[1],
    "run_3": parquet_column_times[2],
    "run_4": parquet_column_times[3],
    "run_5": parquet_column_times[4],
    "median_seconds": parquet_column_read_time,
    "min_seconds": parquet_column_min,
    "max_seconds": parquet_column_max,
    "range_seconds": parquet_column_range,
})


timing_df = pd.DataFrame(timing_results)
timing_df.to_csv(TIMING_RESULTS_PATH, index=False)

print(f"\nTiming results saved to: {TIMING_RESULTS_PATH}")


print("\nCreating gzip-compressed files...")

df.to_csv(
    CSV_GZIP_PATH,
    index=False,
    compression="gzip"
)

df.to_json(
    JSON_GZIP_PATH,
    orient="records",
    compression="gzip"
)

df.to_parquet(
    PARQUET_GZIP_PATH,
    index=False,
    compression="gzip"
)

print("Compressed files created.")


file_size_results = [
    {
        "format": "CSV",
        "compression": "none",
        "size_bytes": CSV_PATH.stat().st_size,
    },
    {
        "format": "CSV",
        "compression": "gzip",
        "size_bytes": CSV_GZIP_PATH.stat().st_size,
    },
    {
        "format": "JSON",
        "compression": "none",
        "size_bytes": JSON_PATH.stat().st_size,
    },
    {
        "format": "JSON",
        "compression": "gzip",
        "size_bytes": JSON_GZIP_PATH.stat().st_size,
    },
    {
        "format": "Parquet",
        "compression": "none",
        "size_bytes": PARQUET_PATH.stat().st_size,
    },
    {
        "format": "Parquet",
        "compression": "gzip",
        "size_bytes": PARQUET_GZIP_PATH.stat().st_size,
    },
]

for result in file_size_results:
    result["size_mb"] = result["size_bytes"] / (1024 ** 2)

file_size_df = pd.DataFrame(file_size_results)
file_size_df.to_csv(FILE_SIZE_RESULTS_PATH, index=False)

print(f"File-size results saved to: {FILE_SIZE_RESULTS_PATH}")


environment_lines = [
    f"Python version: {platform.python_version()}",
    f"Pandas version: {pd.__version__}",
    f"PyArrow version: {pyarrow.__version__}",
    f"Operating system: {platform.platform()}",
    f"Processor: {platform.processor()}",
    f"Warm-up runs: {WARMUP_RUNS}",
    f"Measured runs: {MEASURED_RUNS}",
    f"Dataset rows: {df.shape[0]}",
    f"Dataset columns: {df.shape[1]}",
    f"One-column benchmark field: {COLUMN_TO_READ}",
]

with open(ENVIRONMENT_RESULTS_PATH, "w", encoding="utf-8") as file:
    file.write("\n".join(environment_lines))

print(f"Environment details saved to: {ENVIRONMENT_RESULTS_PATH}")