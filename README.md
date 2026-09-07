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

The current package contains an abstract base processor and three related processors:

- `NYC311DataProcessor` — abstract base class that provides the common dataset-processing interface.
- `DataInspector` — describes the structure and basic characteristics of the dataset.
- `ComplaintEffectivenessAnalyzer` — analyzes complaint status, closure consistency, and resolution timing.
- `DataQualityManager` — identifies selected data-quality problems and applies controlled treatments while recording changes.
- `NYC311DataQualityError` — custom exception used for data-quality processing failures.

The package exposes its main classes through the `nyc311` public interface.

## Environment

Development and testing have been performed using:

- Python 3.14.0
- Windows 10 Pro 64-bit
- 13th Gen Intel Core i7-13620H
- 16 GB RAM

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

The current Task 1 test suite contains **15 passing tests**, including validation, exception-handling, data-treatment, change-log, and persistence checks.

## Data Quality Processing

The current data-quality workflow checks selected issues identified during the dataset audit, including:

- text encoding markers;
- invalid zero BBL values;
- the identified invalid ZIP value;
- complaint records where the Closed Date occurs before the Created Date.

Treatment methods work on copies of the supplied DataFrame so that the original dataset is not silently modified.

Data-quality treatment attempts are recorded in a change log. The log can also be explicitly saved as JSON for persistent evidence of the treatments performed.

Full-dataset verification results and generated evidence are stored in the `results/` directory.

## Design Documentation

Design decisions for the current classes are documented in:

```text
docs/decisions/
```

The project uses abstraction, inheritance, encapsulation, and polymorphism through the common `NYC311DataProcessor` interface and its subclasses.

The implementation also uses deliberate Python data structures, including a set for unique affected-row tracking and a list of dictionaries for ordered, JSON-friendly change-log records.

## Current Project Status

Task 1 currently includes:

- reusable `src`-layout Python package;
- abstract base class and three related subclasses;
- controlled dataset access;
- overridden processing behavior;
- input and required-column validation;
- built-in and custom exception handling;
- data-quality treatments;
- in-memory and persistent change logging;
- public package interface;
- unit tests;
- class diagrams and design-decision documentation;
- full January 2025 dataset verification.

Tasks 2–4 will be added to the repository as the project progresses.

## Reproducibility

Dependency versions are pinned in `requirements.txt`, and the project is configured as an installable `src`-layout package through `pyproject.toml`.

The intended setup sequence is:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pytest -q
```

Dataset provenance and integrity information are maintained separately in `DATA_SOURCE.md`.

## AI Use

Any permitted use of AI tools during the project is recorded in `AI_USE.md` in accordance with the coursework requirements.