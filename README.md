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

The current Task 1 test suite contains **16 passing tests**, including validation, exception-handling, data-treatment, change-log, persistence, and encapsulation checks.

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
- 16 passing unit tests;
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

**Pending**

### Task 4 - Scaling Investigation

**Pending**

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
- AI-use documentation maintained during development.

Additional Task 5 requirements will be completed as the project progresses.

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

Any permitted use of AI tools during the project is recorded in `AI_USE.md` in accordance with the coursework requirements.