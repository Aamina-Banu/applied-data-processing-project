# Task 4 Scaling Investigation

## Purpose

Task 4 Route A compares the existing Agency × Problem resolution-time aggregation from Task 3 using pandas and PySpark on the same local machine.

The comparison uses the same analytical operation in both implementations:

- parse Created Date and Closed Date;
- calculate resolution time in hours;
- exclude missing and negative resolution durations;
- group records by Agency and Problem (formerly Complaint Type);
- calculate complaint count, median resolution time, and mean resolution time;
- retain groups containing at least 30 complaints.

This operation was selected because the Spark groupBy aggregation requires data to be redistributed by the grouping keys, providing a real shuffle operation for the scaling investigation.

## Environment

- Python: 3.14.0
- PySpark: 4.2.0
- pandas: 3.0.5
- Java: 21.0.7 LTS
- Operating system: Windows, 64-bit, build 26200
- Processor: 13th Gen Intel(R) Core(TM) i7-13620H
- RAM: 16 GB
- Spark master: local[*]
- Spark default parallelism: 16

## Main pandas and Spark Comparison

The main comparison used the full January 2025 NYC 311 dataset containing 337,551 rows.

The source data was loaded before the analytical execution was timed. The Spark source DataFrame was cached and materialized before the measured analytical runs.

Timing procedure:

- 1 warm-up run;
- 5 measured runs;
- warm-up excluded from reported measurements;
- median, minimum, maximum, and range calculated from the 5 measured runs;
- Spark startup measured separately;
- Spark execution triggered using collect() so that lazy evaluation did not result in an incomplete timing.

### Validation

Both implementations produced:

- valid resolution-time rows: 334,913;
- qualifying Agency × Problem groups: 118.

T7 full-data group-level validation (7 October 2026) was completed by executing the existing pandas and Spark functions and matching results by `Agency` and `Problem (formerly Complaint Type)`, rather than row position because group row ordering differs.

- Valid rows: pandas = 334,913; Spark = 334,913.
- Qualifying groups: pandas = 118; Spark = 118; groups compared = 118.
- Missing pandas groups = 0; missing Spark groups = 0.
- Complaint-count mismatches = 0.
- Exact median mismatches = 0.
- Mean values showed only negligible floating-point differences; maximum absolute mean difference = 4.547473508864641e-13 hours.

pandas uses exact median. Spark uses `F.median`, which resolved to exact `percentile(..., 0.5, ...)` semantics in the executed plan.

This verifies analytical equivalence for the full-data comparison. It does not prove that pandas `iloc` and Spark `limit` select identical subsets during the crossover benchmark. The comparison scripts themselves still do not assert full result equivalence.

### Main Benchmark Results

| Framework | Median (s) | Minimum (s) | Maximum (s) | Range (s) |
|---|---:|---:|---:|---:|
| pandas | 1.603120 | 1.571851 | 1.701817 | 0.129966 |
| Spark | 1.062578 | 0.927366 | 1.097913 | 0.170547 |

Spark startup time was measured separately as 5.207211 seconds.

The execution measurements therefore represent the analytical workload after Spark has already started and the source data has been prepared. Spark startup should not be ignored when considering a one-off workload.

## Spark Physical Plan Evidence

The Spark physical plan was saved to:

`results/task4_spark_physical_plan.txt`

The relevant structure contains:

- partial ObjectHashAggregate;
- Exchange using hash partitioning on Agency and Problem;
- final ObjectHashAggregate;
- final complaint-count filter.

The Exchange is evidence that the groupBy operation requires a shuffle. Records must be redistributed according to the Agency and Problem grouping keys before the final aggregation can be completed.

In the existing implementation, date parsing/conversion and derived duration calculation are narrow transformations because each row can be processed independently within its partition. Filtering to retain valid, non-negative durations is also narrow: records can be filtered without redistributing data. Grouping by Agency and Problem is a wide transformation because records with the same keys must be brought together across partitions. The grouped aggregation therefore introduces a shuffle / Exchange stage, consistent with the saved physical plan.

The physical plan showed 200 shuffle partitions for the Exchange. This is different from Spark's default parallelism of 16. The default parallelism relates to the local execution environment, while `spark.sql.shuffle.partitions` controls the configured number of partitions used for SQL shuffle operations.

Adaptive Query Execution was enabled in the physical plan, so Spark may adjust the shuffle partition arrangement during execution.

## Crossover Experiment

A separate crossover experiment was used to investigate how the pandas and Spark execution times changed as the number of rows increased.

Tested dataset sizes:

- 50,000;
- 100,000;
- 200,000;
- 337,551;
- 675,102;
- 1,350,204.

The first four sizes use subsets of the January 2025 dataset.

The 675,102-row and 1,350,204-row datasets are synthetic scaling workloads created by repeating the existing January 2025 records. They do not represent additional NYC 311 observations and are used only for performance testing.

For every dataset size:

- pandas and Spark processed the same number of rows;
- 1 warm-up run was performed;
- 5 measured runs were performed;
- median, minimum, maximum, and range were calculated;
- dataset preparation and Spark caching were performed outside the analytical execution timing.

### Crossover Results

| Rows | pandas Median (s) | Spark Median (s) |
|---:|---:|---:|
| 50,000 | 0.218578 | 0.360008 |
| 100,000 | 0.422165 | 0.479237 |
| 200,000 | 0.857344 | 0.844417 |
| 337,551 | 1.445108 | 1.294357 |
| 675,102 | 3.127418 | 2.166003 |
| 1,350,204 | 5.912945 | 3.982850 |

pandas had the lower median analytical execution time at 50,000 and 100,000 rows.

Spark had the lower median analytical execution time at 200,000 rows and every larger tested workload.

The measured median ordering changes between the tested 100,000- and 200,000-row workloads on this hardware. This brackets an observed execution-only crossover, not a proven continuous or unique threshold. The first tested size at which Spark produced a lower median execution time was 200,000 rows.

No exact crossover row count was measured between 100,000 and 200,000, so an exact value should not be claimed.

The crossover result is specific to this hardware, software environment, analytical operation, and benchmark setup.

## Fixed Spark Overhead

The crossover experiment measures analytical execution after Spark has already been initialized and the source DataFrame has been prepared.

The separate main benchmark measured Spark startup at 5.207211 seconds.

Therefore, the execution-only crossover should not be interpreted as meaning that Spark is automatically faster for a one-off 200,000-row workload. For short one-off jobs, Spark's fixed JVM and framework startup overhead can outweigh its execution advantage.

## Evidence Files

Main comparison:

- `notebooks/task4_scaling_comparison.py`
- `results/task4_scaling_timings.csv`
- `results/task4_scaling_summary.csv`
- `results/task4_environment.txt`
- `results/task4_spark_physical_plan.txt`

Crossover experiment:

- `notebooks/task4_crossover_experiment.py`
- `results/task4_crossover_timings.csv`
- `results/task4_crossover_summary.csv`
- `results/task4_crossover_chart.png`

## Current Technical Status

Task 4 Route A scripts, timing evidence, physical plan, and crossover chart are present and were inspected in the final audit. The Spark feature branch was merged at `3636e8c`. Remaining validation and reproducibility limitations are listed below.

The final report explanation and interpretation must be written separately by the student using the measured evidence recorded here.

## Final audit limitations (12 September 2026)

All main and crossover summary statistics were recomputed from saved runs and agree. The chart is readable and visually consistent with the saved summary. At 200,000 rows, pandas' measured range is 0.832829-0.878679 s and Spark's is 0.818704-0.872626 s: the ranges overlap and the median advantage is about 0.012927 s. No significance test or stable exact threshold is established.

At the September audit, full group-key and aggregate-value equivalence had not been checked or saved. The later T7 validation above establishes full-data equivalence, with negligible mean rounding differences; crossover equivalence remains unverified. The crossover also uses pandas `iloc` and unordered Spark `limit`; equal row counts do not guarantee the same subset or repeated-record multiplicities. The student should verify identical inputs and aggregate results at every size before strengthening equivalence claims.

The saved plan is explicitly `isFinalPlan=false`. Its Exchange establishes planned shuffle work with 200 configured partitions; it does not record final adaptive partition counts, shuffle bytes, or runtime stage metrics. `local[*]` uses one machine, not a multi-node deployment.

Input loading, schema inference, Spark cache materialization, synthetic construction, and pandas' initial DataFrame copy are outside analytical timing. This is an execution-only comparison, not end-to-end latency. The main script reuses an existing Spark CSV without checking provenance. The audit confirmed that the current local CSV is byte-identical to the ZIP member, but the script does not enforce that condition.

The plan records the session timezone as Asia/Colombo; pandas uses naive timestamps. This documents the local setup, not a verified New York elapsed-time interpretation across daylight-saving boundaries. The crossover script does not save its own environment or per-size validation counts. Spark was not rerun during this documentation-only audit.
