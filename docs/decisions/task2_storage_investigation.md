# Task 2 - Storage Format Investigation

## 1. Dataset

- Dataset: NYC 311 Service Requests from 2020 to Present
- Selected period: January 2025
- Rows: 337,551
- Columns: 44
- Raw dataset source: `data/raw/nyc_311_january_2025.zip`
- The benchmark used the full selected dataset.

## 2. Formats Tested

Three storage formats were investigated:

- CSV
- JSON
- Parquet

For each format, an uncompressed version and a Gzip-compressed version were created.

Parquet was explicitly written with `compression=None` for the uncompressed baseline so that its uncompressed file size could be compared with the uncompressed CSV and JSON files.

## 3. Benchmark Method

The storage benchmark measured the following operations for each format:

1. Writing the full dataset.
2. Reading the full dataset.
3. Reading one selected column.

Each timing operation used:

- 1 warm-up run, which was discarded.
- 5 measured runs.
- Median execution time as the main timing result.
- Minimum and maximum measured times.
- Range calculated as maximum time minus minimum time.

Timing was performed using `time.perf_counter()`.

The benchmark results were saved separately so that charts and documentation could be generated without rerunning the benchmark.

## 4. Compression Method

Gzip was used as the common compression codec for the compressed comparison.

The following versions were therefore measured:

| Format | Uncompressed | Compressed |
|---|---|---|
| CSV | CSV without compression | CSV with Gzip |
| JSON | JSON without compression | JSON with Gzip |
| Parquet | Parquet with `compression=None` | Parquet with Gzip |

The compressed files were used for the file-size comparison. Timing measurements were performed using the uncompressed benchmark files.

## 5. Timing Results

All values below are measured in seconds.

| Format | Operation | Median | Minimum | Maximum | Range |
|---|---|---:|---:|---:|---:|
| CSV | Full dataset write | 8.3247 | 8.2115 | 8.9415 | 0.7300 |
| JSON | Full dataset write | 5.4357 | 5.2077 | 5.5558 | 0.3481 |
| Parquet | Full dataset write | 1.3357 | 1.3239 | 1.3979 | 0.0740 |
| CSV | Full dataset read | 4.8851 | 4.7751 | 4.9490 | 0.1739 |
| JSON | Full dataset read | 11.6888 | 11.3957 | 11.7979 | 0.4022 |
| Parquet | Full dataset read | 0.1428 | 0.1322 | 0.1890 | 0.0568 |
| CSV | One-column read | 1.4503 | 1.4382 | 1.4646 | 0.0264 |
| JSON | One-column read | 18.5254 | 12.0745 | 18.5547 | 6.4802 |
| Parquet | One-column read | 0.0362 | 0.0346 | 0.0416 | 0.0070 |

The complete individual timing runs are retained in:

`results/storage_benchmark_results.csv`

## 6. File Size Results

File sizes are shown in MiB.

| Format | Compression | Size (bytes) | Size (MiB) |
|---|---|---:|---:|
| CSV | None | 224,677,634 | 214.27 |
| CSV | Gzip | 36,146,841 | 34.47 |
| JSON | None | 531,256,995 | 506.65 |
| JSON | Gzip | 50,622,011 | 48.28 |
| Parquet | None | 62,889,198 | 59.98 |
| Parquet | Gzip | 20,304,607 | 19.36 |

The complete file-size evidence is retained in:

`results/storage_file_sizes.csv`

## 7. One-Column Read Method

The field selected for the one-column benchmark was:

`Problem (formerly Complaint Type)`

The formats were read using the following approaches:

- CSV: `pd.read_csv(..., usecols=[COLUMN_TO_READ])`
- JSON: `pd.read_json(...)[[COLUMN_TO_READ]]`
- Parquet: `pd.read_parquet(..., columns=[COLUMN_TO_READ])`

### JSON Measurement Limitation

The JSON one-column measurement is not equivalent to storage-level column projection.

The JSON file is read before the selected column is extracted from the resulting DataFrame. In contrast, the CSV benchmark uses `usecols` and the Parquet benchmark requests the selected column through the read operation.

This difference must be considered when interpreting the JSON one-column timing.

## 8. Benchmark Environment

The final recorded benchmark environment was:

- Python: 3.14.0
- pandas: 3.0.5
- PyArrow: 25.0.1
- Matplotlib: 3.11.1
- Operating system: Windows, 64-bit, build 26200
- Processor: 13th Gen Intel(R) Core(TM) i7-13620H
- RAM: 16 GB
- Warm-up runs per operation: 1
- Measured runs per operation: 5
- Dataset rows: 337,551
- Dataset columns: 44

Environment evidence is stored in:

`results/storage_benchmark_environment.txt`

## 9. Generated Evidence

Task 2 produced the following evidence files:

- `results/storage_benchmark_results.csv` - individual timing runs and calculated timing statistics.
- `results/storage_file_sizes.csv` - uncompressed and Gzip-compressed file sizes.
- `results/storage_benchmark_environment.txt` - benchmark environment and configuration.
- `results/storage_benchmark_timing_chart.png` - chart comparing median execution times.
- `notebooks/storage_benchmark.py` - storage benchmark implementation.
- `notebooks/storage_benchmark_chart.py` - chart generation script.

The chart is generated from the saved benchmark results and does not rerun the storage benchmark.

## 10. Storage Format Decision

Selected format: **Parquet**

The selection is based on the measured results from this machine and dataset.

Measured evidence supporting the selection:

- Lowest median full-dataset write time: 1.3357 seconds.
- Lowest median full-dataset read time: 0.1428 seconds.
- Lowest median one-column read time: 0.0362 seconds.
- Smallest uncompressed file: 59.98 MiB.
- Smallest Gzip-compressed file: 19.36 MiB.

The project does not require the stored dataset to be frequently opened and manually edited as plain text.

No claim about RAM or memory efficiency is made because memory consumption was not measured in this investigation.

## 11. Workload Where Parquet Would Be Unsuitable

A workload involving a small dataset that needs frequent manual viewing, editing, or simple sharing with non-technical users would make Parquet less suitable.

For that type of workload, a plain-text format such as CSV may be more practical because it can be easily opened and inspected using common spreadsheet or text-editing software.

## 12. Task 2 Status

- Three storage formats tested: Complete
- Uncompressed file sizes measured: Complete
- Gzip-compressed file sizes measured: Complete
- Full-dataset write timing: Complete
- Full-dataset read timing: Complete
- One-column read timing: Complete
- One warm-up run discarded: Complete
- Five measured runs retained: Complete
- Median and range calculated: Complete
- Hardware and library environment recorded: Complete
- Timing chart generated: Complete
- Storage format selected: Parquet
- Unsuitable workload identified: Complete