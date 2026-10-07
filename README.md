# Applied Data Processing Project

This repository contains the code and supporting files for the NIB7143CEM Programming for Data Science coursework project.

The project uses the NYC 311 Service Requests dataset to examine complaint tracking and resolution while also identifying and treating selected data-quality inconsistencies.

## Dataset

The project uses the **311 Service Requests from 2020 to Present** dataset published by NYC Open Data.

For this project, the dataset was filtered to service requests from **January 2025**.

- Provider: NYC Open Data
- Dataset: 311 Service Requests from 2020 to Present
- Dataset identifier: `erm2-nwe9`
- Selected period: January 2025
- Rows: 337,551
- Columns: 44
- Raw dataset archive: `data/raw/nyc_311_january_2025.zip`
- Expected SHA-256: `66EB5D89668990C6F86AAF49C71DB026D1452CD974884A952529299240503866`

The raw dataset is kept unchanged and is not committed to Git. Additional information about the dataset source, extraction, reuse information, checksum, and reproduction limitations is recorded in `DATA_SOURCE.md`.

## Project Structure

```text
applied-data-processing-project/
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   └── decisions/
├── notebooks/
├── results/
├── src/
│   └── nyc311/
├── tests/
├── AI_USE.md
├── DATA_SOURCE.md
├── pyproject.toml
├── README.md
└── requirements.txt
```

## Python Package

The reusable Python package is located in:

```text
src/nyc311/
```

The package contains an abstract base processor and three related processors:

- `NYC311DataProcessor` — abstract base class that provides the common dataset-processing interface.
- `DataInspector` — describes the structure and basic characteristics of the dataset.
- `ComplaintEffectivenessAnalyzer` — analyzes complaint status, closure consistency, and resolution timing.
- `DataQualityManager` — identifies selected data-quality problems and applies controlled treatments while recording changes.
- `NYC311DataQualityError` — custom exception used for data-quality processing failures.

The package exposes its main classes through the `nyc311` public interface.

## Environment

Development, testing, and final clean-checkout reproduction were performed using:

- Python 3.14.0
- Windows 64-bit, build 26200
- 13th Gen Intel Core i7-13620H
- 16 GB RAM
- pandas 3.0.5
- PyArrow 25.0.1
- Matplotlib 3.11.1
- SciPy 1.18.1
- PySpark 4.2.0
- Java 21.0.7 LTS for Task 4

Main Python dependencies are pinned in `requirements.txt`.

Development tools used for UML generation include Pylint/Pyreverse 4.0.8 and Graphviz 16.1.0. These tools are not required to run the package or its unit tests.

## Setup

Clone the repository and move into the project directory.

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the pinned dependencies:

```powershell
python -m pip install -r requirements.txt
```

Install the local package in editable mode:

```powershell
python -m pip install -e .
```

Verify that the installed dependencies are consistent:

```powershell
python -m pip check
```

The package can then be imported through its public interface, for example:

```python
from nyc311 import DataInspector
from nyc311 import ComplaintEffectivenessAnalyzer
from nyc311 import DataQualityManager
```

## Raw Data Requirement

The raw archive is ignored by Git and is therefore absent from a clean clone.

Create the raw-data directory if required:

```powershell
New-Item -ItemType Directory -Force data/raw
```

Place the original archive at:

```text
data/raw/nyc_311_january_2025.zip
```

Then verify its integrity:

```powershell
Get-FileHash -Algorithm SHA256 data/raw/nyc_311_january_2025.zip
```

The expected SHA-256 value is:

```text
66EB5D89668990C6F86AAF49C71DB026D1452CD974884A952529299240503866
```

No immutable download URL for this exact historical archive is available. Exact numerical reproduction therefore requires a checksum-matching copy of the original archive. A newly exported copy from the source portal may differ.

See `DATA_SOURCE.md` for the complete provenance record, extraction limitations, observed time boundaries, and reuse information.

## Running the Tests

Run the complete unit test suite from the project root:

```powershell
python -m pytest -q
```

The current test suite contains **28 passing tests**, including regression coverage for constructor ownership, duplicate-index encoding, unexpected treatment failures, and change-log write/replacement failures.

## Data Quality Processing

The data-quality workflow checks selected issues identified during the dataset audit, including:

- text encoding markers;
- invalid zero BBL values;
- the identified invalid ZIP value;
- complaint records where the Closed Date occurs before the Created Date.

Treatment methods work on copies of the supplied DataFrame so that the original dataset is not silently modified.

Data-quality treatment attempts are recorded in a change log. The log can also be explicitly saved as JSON for persistent evidence of the treatments performed.

Running:

```powershell
python notebooks/full_dataset_verification.py
```

performs the full-dataset Scrub workflow and writes the treated dataset to:

```text
data/processed/nyc_311_january_2025_scrubbed.parquet
```

The process preserves all **337,551 rows** while treating the selected quality problems. The resulting Parquet dataset is then used by the Task 3 Explore and Model stages.

Generated data-quality evidence is stored in the `results/` directory.

## Task 2 - Storage Format Investigation

Task 2 investigates three storage formats using the full January 2025 dataset:

- CSV
- JSON
- Parquet

The benchmark measures:

- full-dataset write time;
- full-dataset read time;
- one-column read time;
- uncompressed file size;
- Gzip-compressed file size.

Each timing operation uses one discarded warm-up run followed by five measured runs. Median, minimum, maximum, and range values are retained.

Run the benchmark using:

```powershell
python notebooks/storage_benchmark.py
```

The benchmark results are stored in:

```text
results/storage_benchmark_results.csv
results/storage_file_sizes.csv
results/storage_benchmark_environment.txt
```

Generate the benchmark timing chart using:

```powershell
python notebooks/storage_benchmark_chart.py
```

The chart is stored as:

```text
results/storage_benchmark_timing_chart.png
```

Based on the measured benchmark results, **Parquet** was selected as the storage format for the project.

The complete Task 2 technical record, including the benchmark method, measurements, environment, limitations, and storage decision, is maintained in:

```text
docs/decisions/task2_storage_investigation.md
```

## Task 3 - Data Pipeline and Analysis

Task 3 follows the OSEMN workflow and includes Obtain, Scrub, Explore, Model, and iNterpret activities.

The executable analysis pipeline is:

```text
Raw January 2025 ZIP
        ↓
Scrub / full-dataset verification
        ↓
nyc_311_january_2025_scrubbed.parquet
        ↓
Explore
        ↓
Model
```

Run the Scrub stage first:

```powershell
python notebooks/full_dataset_verification.py
```

Then run Explore:

```powershell
python notebooks/task3_exploratory_analysis.py
```

Then run Model:

```powershell
python notebooks/task3_model.py
```

Both Explore and Model read:

```text
data/processed/nyc_311_january_2025_scrubbed.parquet
```

rather than re-reading the raw ZIP.

The clean-checkout reproduction produced:

- 337,551 rows in the scrubbed dataset;
- 334,913 records with valid recorded resolution intervals;
- 2,638 records without a usable Closed Date;
- 0 negative resolution-time records after treatment;
- 1,025 Closed-status records without a usable Closed Date;
- 206 non-Closed records with a usable Closed Date;
- 118 qualifying Agency × Problem segments using the minimum group-size threshold;
- Kruskal-Wallis H statistic of `189258.3886` across the qualifying agency comparison.

Task 3 generates exploratory summaries, tracking-consistency evidence, figures, segmentation outputs, resolution-band outputs, and statistical results under `results/`.

Further Task 3 provenance and validation evidence is recorded in:

```text
docs/decisions/task3_analysis_progress.md
```

## Task 4 - pandas and PySpark Scaling Investigation

Task 4 reimplements the selected Task 3 processing workflow using PySpark and compares its behaviour and scaling with pandas.

Java is required separately for PySpark and must be available on PATH:

```powershell
java -version
```

Run the main pandas/PySpark comparison using:

```powershell
python notebooks/task4_scaling_comparison.py
```

The main comparison validates the full-data outputs before recording benchmark timings.

The clean-checkout reproduction produced:

- pandas valid rows: 334,913;
- Spark valid rows: 334,913;
- pandas qualifying Agency × Problem groups: 118;
- Spark qualifying Agency × Problem groups: 118.

The main comparison generates:

```text
results/task4_scaling_timings.csv
results/task4_scaling_summary.csv
results/task4_environment.txt
results/task4_spark_physical_plan.txt
```

The physical-plan evidence is retained to support discussion of Spark execution behaviour, including narrow transformations and the wide grouping operation that requires a shuffle.

After the main comparison, run the crossover experiment:

```powershell
python notebooks/task4_crossover_experiment.py
```

The experiment evaluates pandas and Spark across six workload sizes:

```text
50,000
100,000
200,000
337,551
675,102
1,350,204
```

Each framework is measured five times at each workload size. The experiment is intended to investigate scaling behaviour and the point at which Spark's processing characteristics become favourable relative to pandas on the recorded hardware.

The crossover experiment generates:

```text
results/task4_crossover_timings.csv
results/task4_crossover_summary.csv
results/task4_crossover_chart.png
```

Benchmark timings are hardware- and run-specific and should not be expected to reproduce exactly.

The complete Task 4 technical evidence and limitations are documented in:

```text
docs/decisions/task4_scaling_investigation.md
```

The Spark feature branch was merged into the main development history at commit `3636e8c`.

## Design Documentation

Design decisions for the current classes are documented in:

```text
docs/decisions/
```

The project uses abstraction, inheritance, encapsulation, and polymorphism through the common `NYC311DataProcessor` interface and its subclasses.

The implementation also uses deliberate Python data structures, including a set for unique affected-row tracking and a list of dictionaries for ordered, JSON-friendly change-log records.

## Task 5 - Professional Practice

Professional-practice evidence includes:

- Git history maintained throughout development;
- meaningful commits;
- feature-branch development and merge workflow;
- pinned Python dependencies;
- recorded Python and Java versions;
- dataset provenance and SHA-256 integrity documentation;
- reproducibility instructions;
- clean-checkout reproduction;
- GDPR Article 5 assessment;
- data-retention considerations;
- technical and analytical decision records.

The GDPR assessment is recorded in:

```text
docs/decisions/task5_gdpr_assessment.md
```

Professional-practice evidence is recorded in:

```text
docs/decisions/task5_professional_practice_progress.md
```

The AI-use disclosure in `AI_USE.md` must be completed and checked against the coursework requirements before final submission.

## Complete Reproduction Workflow

Use the project root for all commands.

### 1. Create and activate a clean environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install and verify dependencies

```powershell
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pip check
```

### 3. Provide and verify the raw archive

Create the directory:

```powershell
New-Item -ItemType Directory -Force data/raw
```

Place `nyc_311_january_2025.zip` inside `data/raw/`, then run:

```powershell
Get-FileHash -Algorithm SHA256 data/raw/nyc_311_january_2025.zip
```

Expected SHA-256:

```text
66EB5D89668990C6F86AAF49C71DB026D1452CD974884A952529299240503866
```

### 4. Run the tests

```powershell
python -m pytest -q
```

Expected test-suite result:

```text
28 passed
```

### 5. Reproduce Task 2

```powershell
python notebooks/storage_benchmark.py
python notebooks/storage_benchmark_chart.py
```

### 6. Reproduce Task 3

Run the stages in this order:

```powershell
python notebooks/full_dataset_verification.py
python notebooks/task3_exploratory_analysis.py
python notebooks/task3_model.py
```

Scrub must run before Explore and Model because it creates:

```text
data/processed/nyc_311_january_2025_scrubbed.parquet
```

Both downstream Task 3 scripts consume this treated Parquet dataset.

### 7. Reproduce Task 4

Confirm that Java is available:

```powershell
java -version
```

Then run:

```powershell
python notebooks/task4_scaling_comparison.py
python notebooks/task4_crossover_experiment.py
```

The main Task 4 script must run before the crossover experiment because it creates:

```text
data/processed/task4_spark_input.csv
```

If this CSV already exists, the script may reuse it, so a clean checkout is preferable when independently verifying the complete workflow.

## Reproduction Outputs

| Stage | Main outputs |
|---|---|
| Full-dataset verification / Scrub | `data/processed/nyc_311_january_2025_scrubbed.parquet`, `results/data_quality_change_log.json` and console verification |
| Task 2 | `results/storage_*.csv`, environment TXT, timing PNG and benchmark-format files under `data/processed/storage_benchmark/` |
| Task 3 Explore | `results/task3_explore_summary.csv`, agency/problem summaries, tracking-consistency TXT and three PNG figures |
| Task 3 Model | `results/task3_model_segments.csv`, resolution-band CSVs and Kruskal-Wallis TXT |
| Task 4 main | scaling timing/summary CSVs, environment TXT and Spark physical-plan TXT |
| Task 4 crossover | crossover timing/summary CSVs and crossover PNG |

Running the reproduction workflow can overwrite generated evidence. Benchmark timings, timestamps, environment details, and some generated file bytes can differ between runs even when the analytical results are equivalent.

## Clean-Checkout Reproduction Evidence

A complete clean-checkout reproduction was performed on **7 October 2026**.

The verification used a separate clone of the repository rather than the existing development working directory. A new Python 3.14.0 virtual environment was created and the pinned dependencies were installed from `requirements.txt`. The project was then installed in editable mode.

The clean-checkout verification confirmed:

- `python -m pip check` reported no broken requirements;
- all required Python dependencies imported successfully;
- the supplied raw archive matched the documented SHA-256 checksum;
- the complete test suite passed with **28 tests**;
- Task 2 completed successfully and regenerated its benchmark evidence;
- Task 3 Scrub completed successfully and produced a 337,551-row treated Parquet dataset;
- Task 3 Explore reproduced 334,913 valid recorded resolution intervals;
- Task 3 Model reproduced 118 qualifying Agency × Problem segments and a Kruskal-Wallis H statistic of `189258.3886`;
- the Task 4 pandas and Spark implementations each produced 334,913 valid rows and 118 qualifying groups;
- the six-size Task 4 crossover experiment completed successfully and regenerated its timing evidence and chart.

Benchmark timings were different from the previously saved runs, as expected for performance measurements. Generated timestamps also changed. These differences do not affect the structural and analytical reproduction checks described above.

The raw dataset remains an external prerequisite because the exact archive is intentionally excluded from Git. Exact numerical reproduction therefore depends on access to the checksum-matching archive documented in `DATA_SOURCE.md`.

## Reproducibility Limitations

The following limitations should be considered when reproducing the project:

- the exact raw archive is not stored in Git;
- no immutable public download URL for the exact historical archive is available;
- a new export from the source portal may not be byte-for-byte identical;
- benchmark timings depend on hardware, operating-system state, Java/Spark startup behaviour, and background processes;
- Task 4 results are therefore hardware-specific rather than universal performance claims;
- PySpark may display non-fatal local Windows/Hadoop warnings when running without native Hadoop utilities;
- the Task 4 crossover experiment uses controlled workload-size subsets/expansions for scaling investigation and should not be treated as additional independent real-world observations.

## GDPR and Data Handling

The dataset is publicly available, but public availability does not by itself make every record anonymous or remove data-protection considerations.

The project considers risks associated with record-level information including addresses, coordinates, identifiers, timestamps, and descriptive text.

Aggregate analytical outputs are preferred where possible to reduce unnecessary disclosure. Full-data local copies remain necessary during development, verification, assessment, moderation, and any applicable appeal period.

Raw and derived full-data copies under the student's control should be reviewed when the relevant assessment, moderation, and appeal period ends and deleted where they are no longer necessary. This includes the raw ZIP, scrubbed Parquet data, Task 2 benchmark copies, Spark input CSVs, temporary files, exports, and backups containing unnecessary record-level data.

Code, documentation, and aggregate outputs may be retained where they do not expose unnecessary identifiable or record-level information.

Deleting the final checksum-matching raw archive will mean that exact numerical reproduction can no longer be guaranteed.

The project does not independently claim a GDPR Article 6 lawful basis where no controller- or institution-approved basis has been established in the available project evidence. If GDPR applies to the processing, the appropriate lawful basis should be confirmed by the relevant controller or institution.

See:

```text
docs/decisions/task5_gdpr_assessment.md
```

for the detailed technical assessment.

## AI Use

`AI_USE.md` is reserved for the project's AI-use disclosure.

It must be completed before final submission using the student's actual AI-use history and checked against the coursework rules. The declaration should accurately distinguish permitted assistance from work that remained the student's own assessed design, analytical reasoning, interpretation, and report writing.

## Current Project Status

### Task 1 - Object-Oriented Data Processing

**Complete**

Implemented evidence includes:

- reusable `src`-layout Python package;
- abstract base class and three related subclasses;
- controlled dataset access and encapsulation;
- overridden processing behaviour;
- input and required-column validation;
- built-in and custom exception handling;
- data-quality treatments;
- in-memory and persistent change logging;
- public package interface;
- 28 passing unit tests;
- class diagrams and design-decision documentation;
- full January 2025 dataset verification.

### Task 2 - Storage Format Investigation

**Complete**

Implemented evidence includes:

- CSV, JSON, and Parquet comparison;
- uncompressed and Gzip-compressed file-size measurements;
- full-dataset write benchmarks;
- full-dataset read benchmarks;
- one-column read benchmarks;
- one discarded warm-up and five measured runs per timing operation;
- median and range calculations;
- benchmark environment recording;
- benchmark timing chart;
- technical investigation documentation;
- Parquet selected as the project storage format.

### Task 3 - Data Pipeline and Analysis

**Implemented with saved evidence**

The Scrub stage writes a treated Parquet dataset that is consumed by both Explore and Model. Exploratory figures, summaries, segmentation, resolution bands, statistical results, and supporting decision records are present.

### Task 4 - Scaling Investigation

**Implemented with saved evidence**

The pandas/PySpark comparison, output validation, Spark physical-plan evidence, six-size crossover experiment, chart, and supporting investigation documentation are present.

### Task 5 - Professional Practice

**Implemented with final AI-use disclosure remaining**

Version-control evidence, reproducibility documentation, clean-checkout verification, dependency/environment records, dataset provenance, GDPR assessment, retention considerations, and professional-practice documentation are present.

`AI_USE.md` remains to be completed before final submission.