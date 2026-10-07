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

The raw dataset is kept unchanged. Additional information about the dataset source, extraction, reuse information, and checksum is recorded in `DATA_SOURCE.md`.

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

Development and testing have been performed using:

- Python 3.14.0
- Windows 64-bit, build 26200
- 13th Gen Intel Core i7-13620H
- 16 GB RAM
- pandas 3.0.5
- PyArrow 25.0.1
- Matplotlib 3.11.1
- SciPy 1.18.1
- PySpark 4.2.0
- Java 21.0.7 LTS (Task 4 prerequisite)

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

The package can then be imported using its public interface, for example:

```python
from nyc311 import DataInspector
from nyc311 import ComplaintEffectivenessAnalyzer
from nyc311 import DataQualityManager
```

## Running the Tests

Run the complete unit test suite from the project root:

```powershell
python -m pytest -q
```

The current test suite contains **28 passing tests**, including regression coverage for constructor ownership, duplicate-index encoding, unexpected treatment failures, and change-log write/replacement failures.

## Data Quality Processing

The current data-quality workflow checks selected issues identified during the dataset audit, including:

- text encoding markers;
- invalid zero BBL values;
- the identified invalid ZIP value;
- complaint records where the Closed Date occurs before the Created Date.

Treatment methods work on copies of the supplied DataFrame so that the original dataset is not silently modified.

Data-quality treatment attempts are recorded in a change log. The log can also be explicitly saved as JSON for persistent evidence of the treatments performed.

Full-dataset verification results and generated evidence are stored in the `results/` directory.

## Storage Format Investigation

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

The benchmark implementation is located at:

```text
notebooks/storage_benchmark.py
```

The benchmark results are stored in:

```text
results/storage_benchmark_results.csv
results/storage_file_sizes.csv
results/storage_benchmark_environment.txt
```

The benchmark timing chart is generated from the saved results using:

```text
notebooks/storage_benchmark_chart.py
```

and stored as:

```text
results/storage_benchmark_timing_chart.png
```

Based on the measured benchmark results, **Parquet** was selected as the storage format for the project.

The complete Task 2 technical record, including the benchmark method, measurements, environment, limitations, and storage decision, is maintained in:

```text
docs/decisions/task2_storage_investigation.md
```

## Design Documentation

Design decisions for the current classes are documented in:

```text
docs/decisions/
```

The project uses abstraction, inheritance, encapsulation, and polymorphism through the common `NYC311DataProcessor` interface and its subclasses.

The implementation also uses deliberate Python data structures, including a set for unique affected-row tracking and a list of dictionaries for ordered, JSON-friendly change-log records.

## Current Project Status

### Task 1 - Object-Oriented Data Processing

**Complete**

Implemented components include:

- reusable `src`-layout Python package;
- abstract base class and three related subclasses;
- controlled dataset access and encapsulation;
- overridden processing behavior;
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

Completed work includes:

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

**Implemented with saved evidence.** Explore and Model scripts, three dataset figures, segmentation, resolution bands, and statistical results are present. Scrub writes a treated Parquet dataset that both Explore and Model consume. See [Task 3 evidence](docs/decisions/task3_analysis_progress.md) for provenance and validation.

### Task 4 - Scaling Investigation

**Implemented with saved evidence.** The pandas/PySpark comparison, physical plan, six-size crossover experiment, and chart are present. The Spark feature branch was merged at `3636e8c`. See [Task 4 evidence](docs/decisions/task4_scaling_investigation.md) for verified timings and validation limitations.

Route A has been selected for the scaling investigation.

### Task 5 - Professional Practice

**In progress**

Current professional-practice work includes:

- Git history maintained throughout development;
- meaningful commits;
- feature-branch development and merge workflow;
- pinned dependencies;
- dataset provenance and checksum documentation;
- reproducibility setup;
- AI-use record for this confirmed audit; earlier use remains for student verification.

The [GDPR technical assessment](docs/decisions/task5_gdpr_assessment.md) and [final requirement audit](docs/decisions/final_repository_audit.md) record current evidence and remaining student actions. Final clean-checkout reproduction and submission evidence remain outstanding.

## Reproducibility

Dependency versions are pinned in `requirements.txt`, and the project is configured as an installable `src`-layout package through `pyproject.toml`.

The core setup and verification sequence is:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pytest -q
```

Task 2 benchmark results can be reproduced using:

```powershell
python notebooks/storage_benchmark.py
```

The Task 2 timing chart can then be generated from the saved benchmark results using:

```powershell
python notebooks/storage_benchmark_chart.py
```

Dataset provenance and integrity information are maintained separately in `DATA_SOURCE.md`.

## AI Use

`AI_USE.md` records this confirmed audit interaction. The student must complete any earlier AI-use history from their own records and check the coursework disclosure requirements.

## Complete reproduction workflow and limits

Use the project root for all commands. Follow the setup and test commands above first. The recorded Python version is 3.14.0. Install Java 21 separately for Task 4 and make `java` available on PATH; verify with `java -version`. Python dependency installation does not install Java.

The raw archive is ignored by Git and absent from a clean clone. Create `data/raw/` and obtain the original `nyc_311_january_2025.zip` from the student through an appropriate transfer route. No immutable download link for that exact archive is recorded. Exact numerical reproduction requires the checksum-matching raw archive. A fresh portal export may differ; see [DATA_SOURCE.md](DATA_SOURCE.md) for its checksum and observed time boundaries.

```powershell
New-Item -ItemType Directory -Force data/raw
Get-FileHash -Algorithm SHA256 data/raw/nyc_311_january_2025.zip
python -m pip check
python notebooks/full_dataset_verification.py
python notebooks/storage_benchmark.py
python notebooks/storage_benchmark_chart.py
python notebooks/task3_exploratory_analysis.py
python notebooks/task3_model.py
python notebooks/task4_scaling_comparison.py
python notebooks/task4_crossover_experiment.py
```

Place the archive before running the checksum command. The main Task 4 script must precede the crossover script because it creates `data/processed/task4_spark_input.csv`. If that CSV already exists, the script reuses it without checking its provenance.

| Stage | Outputs |
|---|---|
| Full-dataset verification | `data/processed/nyc_311_january_2025_scrubbed.parquet`, console checks and `results/data_quality_change_log.json`; the quality Markdown evidence files are not generated by this script |
| Task 2 | `results/storage_*.csv`, environment TXT, timing PNG; six full-data files under `data/processed/storage_benchmark/` |
| Task 3 Explore | `results/task3_explore_summary.csv`, agency/problem summaries, tracking TXT, three PNGs |
| Task 3 Model | `results/task3_model_segments.csv`, four band CSVs, Kruskal-Wallis TXT |
| Task 4 main | Scaling timing/summary CSVs, environment TXT, physical-plan TXT |
| Task 4 crossover | Crossover timing/summary CSVs and PNG |

These commands regenerate and can overwrite evidence; benchmark times and log timestamps vary between runs. The Task 2 chart opens a Matplotlib window. For Task 3, `notebooks/full_dataset_verification.py` reads the immutable raw ZIP and writes the treated dataset to `data/processed/nyc_311_january_2025_scrubbed.parquet`. Both `notebooks/task3_exploratory_analysis.py` and `notebooks/task3_model.py` read that scrubbed Parquet file and apply their existing duration logic. Run Scrub before Explore and Model, as shown above; Model reads the same scrubbed dataset rather than an Explore output.

Audit verification on 12 September 2026: **16 tests passed in 0.58 s**; `pip check` found no broken requirements. Timing summaries were recalculated from saved runs and Task 3 numerical tables were checked against the raw archive. A fresh environment installation and full clean-checkout Spark/benchmark rerun were not performed during this documentation-only audit. Implementation is present for Tasks 1-4; remaining requirement gaps are listed in the final audit.
