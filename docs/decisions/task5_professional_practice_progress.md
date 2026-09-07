# Task 5 – Professional and Legal Practice Progress Record

## Purpose

This document records technical evidence and development progress relevant to Task 5 – Professional and Legal Practice.

Task 5 consists of three areas:

1. Version control – 7 marks
2. Data protection – 5 marks
3. Reproducibility – 3 marks

This file is maintained during development so that evidence is recorded when it is produced rather than reconstructed at the end of the project.

---

# 1. Version Control

## 1.1 Repository

The project is maintained using Git and a remote GitHub repository.

Repository:

`https://github.com/Aamina-Banu/applied-data-processing-project`

Development has been committed throughout the project rather than being added in a single final commit.

---

## 1.2 Development History

Git has been used from the initial project setup through the completion of Tasks 1 and 2.

The repository currently contains commits covering:

- initial project structure;
- dataset source documentation;
- dataset checksum and provenance;
- initial object-oriented processing classes;
- completion of the core OOP implementation;
- validation and data-quality improvements;
- persistent data-quality change logging;
- Task 1 reproducibility improvements;
- Task 1 encapsulation and verification fixes;
- Task 2 dependency setup;
- Task 2 storage benchmarking;
- Task 2 documentation and evidence;
- README updates following Task 2.

This provides a development history showing the project changing over time rather than only its final state.

---

## 1.3 Feature Branch and Merge

A dedicated feature branch was used for the Task 2 storage-format investigation:

`feature/storage-benchmarking`

The branch was created after the Task 1 implementation had been completed and stabilized.

Storage benchmarking was treated as a separate experimental feature because it introduced:

- storage-format comparison;
- PyArrow/Parquet support;
- benchmark scripts;
- timing measurements;
- compression measurements;
- benchmark result files;
- visualization of benchmark results.

Keeping this work on a feature branch allowed the storage experiment to be developed and verified separately from the stable Task 1 implementation.

Task 2 work was committed to the feature branch before integration.

Relevant Task 2 feature commit:

`7785b10 feat: complete storage format benchmarking`

After verification, the feature branch was merged into `main` using a non-fast-forward merge:

```text
git merge --no-ff feature/storage-benchmarking -m "merge: complete storage benchmarking"
```

The `--no-ff` merge preserves the feature branch as a visible development path in the Git history.

The merged `main` branch was then pushed to the remote repository.

The README was subsequently updated and committed:

`8a7e14a docs: update project status after Task 2`

---

## 1.4 Current Version-Control Evidence

Current evidence includes:

- multiple commits created throughout development;
- descriptive commit messages;
- separate commits for different development activities;
- a genuine feature branch;
- development performed on the feature branch;
- a non-fast-forward merge into `main`;
- remote repository synchronized after completed work;
- clean working tree checkpoints.

The branch-and-merge requirement has therefore been technically implemented.

---

## 1.5 Evidence Still Required

Before final submission:

- continue committing Task 3 development throughout implementation;
- continue committing Task 4 development throughout implementation;
- use additional feature branches where they naturally support development;
- avoid combining unrelated changes into large final commits;
- capture a concise Git history for report evidence;
- capture the branch and merge in the history;
- verify the final repository has a clear development timeline.

A useful final evidence command will be:

```powershell
git log --graph --oneline --decorate --all
```

The final report must contain a short screenshot or log of the repository history and the student's own explanation of the branching decision.

---

# 2. Data Protection

## 2.1 Current Status

The full Task 5 GDPR Article 5 assessment has not yet been completed.

This section remains in progress.

The assessment must be based specifically on the January 2025 NYC 311 dataset used by the project rather than being a generic description of GDPR principles.

---

## 2.2 Dataset Context

Dataset:

NYC Open Data – 311 Service Requests from 2020 to Present

Dataset identifier:

`erm2-nwe9`

Selected project period:

January 2025

Dataset dimensions:

- 337,551 rows
- 44 columns

The raw dataset archive is maintained unchanged in:

`data/raw/nyc_311_january_2025.zip`

Dataset provenance, extraction information, reuse information, and SHA-256 checksum are maintained in:

`DATA_SOURCE.md`

Raw archive SHA-256:

`66EB5D89668990C6F86AAF49C71DB026D1452CD974884A952529299240503866`

---

## 2.3 Required GDPR Investigation

The dataset must be assessed against the GDPR Article 5 principles using evidence from the actual dataset.

The investigation must consider:

- lawfulness, fairness and transparency;
- purpose limitation;
- data minimization;
- accuracy;
- storage limitation;
- integrity and confidentiality;
- accountability.

The assessment must determine whether the selected dataset contains personal data.

This conclusion must be supported by evidence from the dataset fields and values rather than assumed from the fact that the dataset is publicly available.

---

## 2.4 If No Personal Data Is Identified

If the investigation determines that the project dataset does not contain personal data, evidence must be retained showing how this was established.

The project must also consider what would change if personal data were present, including areas such as:

- lawful basis;
- minimization;
- access controls;
- storage;
- retention;
- disclosure;
- processing safeguards.

The final report must apply these considerations specifically to the project rather than only listing GDPR definitions.

---

## 2.5 If Personal Data Is Identified

If personal data is found during the investigation, additional assessment will be required, including:

- identification of the relevant fields;
- lawful basis for processing;
- minimization applied by the project;
- retention position;
- security and access considerations.

No final determination is recorded here until the dataset-specific investigation is completed.

---

## 2.6 Data Protection Work Remaining

Remaining work:

- inspect the actual 44 dataset fields for potential personal data;
- inspect relevant sample values where field names alone are insufficient;
- document evidence;
- determine whether personal data is present;
- perform the Article 5 assessment against the actual project;
- document what would change if personal data were present, where applicable;
- retain evidence for the final report.

Status:

**Pending dedicated GDPR assessment.**

---

# 3. Reproducibility

## 3.1 README

A root-level `README.md` is maintained.

It currently documents:

- project purpose;
- dataset;
- dataset dimensions;
- project structure;
- Python package;
- development environment;
- setup instructions;
- package installation;
- unit-test command;
- data-quality processing;
- Task 2 storage investigation;
- design documentation;
- current project status;
- reproducibility instructions;
- AI-use documentation.

The README was updated after completion of Task 2.

---

## 3.2 Dependency Pinning

Python dependencies are pinned in:

`requirements.txt`

Current pinned dependencies include:

- numpy 2.5.2
- pandas 3.0.5
- pyarrow 25.0.1
- python-dateutil 2.9.0.post0
- six 1.17.0
- tzdata 2026.3
- pytest 9.1.1
- matplotlib 3.11.1

The project is configured as an installable `src`-layout package through:

`pyproject.toml`

---

## 3.3 Recorded Environment

Current environment information:

- Python: 3.14.0
- Operating system: Windows, 64-bit, build 26200
- Processor: 13th Gen Intel(R) Core(TM) i7-13620H
- RAM: 16 GB

Task 2 additionally records:

- pandas 3.0.5
- PyArrow 25.0.1
- Matplotlib 3.11.1
- warm-up runs: 1
- measured runs: 5
- dataset rows: 337,551
- dataset columns: 44

Task 2 environment evidence is stored in:

`results/storage_benchmark_environment.txt`

---

## 3.4 Dataset Reproducibility and Integrity

Dataset provenance is recorded in:

`DATA_SOURCE.md`

The raw dataset is retained unchanged.

A SHA-256 checksum is recorded for the raw archive so that its integrity can be verified.

This separates raw source data from processed/generated outputs and provides evidence of the exact input used by the project.

---

## 3.5 Package Reproduction

Current package setup sequence:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
```

The test suite can then be executed using:

```powershell
python -m pytest -q
```

The current Task 1 test suite contains 16 passing tests.

A separate clean virtual-environment installation has previously been performed to verify that the package can be installed from the pinned dependencies and imported through its public interface.

---

## 3.6 Task 1 Reproducibility

Task 1 contains:

- reusable source package;
- automated unit tests;
- full-dataset verification;
- data-quality audit evidence;
- persistent change-log evidence;
- design documentation.

Full-dataset verification is implemented in:

`notebooks/full_dataset_verification.py`

Relevant evidence is retained in the `results/` directory.

---

## 3.7 Task 2 Reproducibility

Task 2 benchmark implementation:

`notebooks/storage_benchmark.py`

Saved benchmark results:

`results/storage_benchmark_results.csv`

Saved file-size results:

`results/storage_file_sizes.csv`

Environment evidence:

`results/storage_benchmark_environment.txt`

Timing visualization:

`results/storage_benchmark_timing_chart.png`

Chart generation script:

`notebooks/storage_benchmark_chart.py`

Technical investigation record:

`docs/decisions/task2_storage_investigation.md`

The benchmark can be reproduced using:

```powershell
python notebooks/storage_benchmark.py
```

The chart can then be reproduced from the saved results using:

```powershell
python notebooks/storage_benchmark_chart.py
```

The benchmark uses one discarded warm-up run and five measured runs for each timing operation.

---

## 3.8 Reproducibility Work Remaining

Reproducibility cannot be considered final until Tasks 3 and 4 are complete because the coursework requires the README to allow a competent reader to reproduce every number reported in the final report.

Remaining work:

- document Task 3 reproduction commands;
- document Task 3 generated results and figures;
- document Task 4 reproduction commands;
- document Task 4 benchmark/results evidence;
- update pinned dependencies if Tasks 3 or 4 introduce new libraries;
- update README after Task 3;
- update README after Task 4;
- perform a final clean-checkout reproduction test;
- verify all report numbers can be traced to reproducible outputs.

Status:

**Mostly implemented but not final.**

---

# 4. Task 5 Current Status Summary

| Component | Marks | Current status |
|---|---:|---|
| Version control | 7 | Mostly complete – continue throughout Tasks 3 and 4 and capture final evidence |
| Data protection | 5 | Pending dedicated dataset-specific GDPR assessment |
| Reproducibility | 3 | Mostly complete – finalization depends on Tasks 3 and 4 |
| Overall Task 5 | 15 | In progress |

---

# 5. Final Task 5 Checklist

Before Task 5 can be considered complete:

## Version Control

- [x] Git repository established
- [x] Commits made throughout development
- [x] Feature branch created
- [x] Work completed on feature branch
- [x] Feature branch merged into main
- [x] Merge preserved in history
- [x] Remote repository updated
- [ ] Continue meaningful commits for Task 3
- [ ] Continue meaningful commits for Task 4
- [ ] Capture final Git graph/log
- [ ] Select concise history evidence for report
- [ ] Student explains branching decision in final report

## Data Protection

- [ ] Inspect dataset for personal data
- [ ] Record evidence supporting conclusion
- [ ] Apply GDPR Article 5 principles to actual dataset
- [ ] Determine lawful-basis implications where relevant
- [ ] Assess minimization
- [ ] Assess accuracy implications
- [ ] Assess retention/storage limitation
- [ ] Assess security/integrity/confidentiality
- [ ] Explain what would change if personal data were present, if applicable
- [ ] Retain evidence for report

## Reproducibility

- [x] README created
- [x] Pinned `requirements.txt`
- [x] Python version recorded
- [x] Operating system/build recorded
- [x] CPU recorded
- [x] RAM recorded
- [x] Dataset provenance recorded
- [x] Raw dataset checksum recorded
- [x] Package installation instructions documented
- [x] Unit-test command documented
- [x] Task 2 reproduction commands documented
- [ ] Task 3 reproduction instructions added
- [ ] Task 4 reproduction instructions added
- [ ] All final report figures/results traceable to scripts
- [ ] Final clean-checkout reproduction performed
- [ ] Confirm every reported number can be reproduced