# Task 5 GDPR Technical Assessment

Initial technical audit: 12 September 2026. Retention and lawful-basis position updated: 7 October 2026. Scope: local January 2025 NYC 311 extract, tracked repository, and reachable Git history. This is a technical development note, not final report prose or legal advice. The academic purpose is analysis of complaint tracking, duration, and data quality. GDPR territorial applicability and an institutional lawful basis are not established by repository evidence.

## Classification and Inspection

**B. Potential personal/location-related data requiring caution.**

All 44 column names and non-null counts were inspected from the checksum-matching local ZIP containing 337,551 rows. No dedicated complainant-name, personal-email, or personal-phone column is evident. This does not demonstrate anonymity: incident locations, timestamps, request identifiers, and complaint descriptions can relate to natural persons when combined. An incident address is not automatically the complainant's home.

| Field family | Actual fields / observed evidence | Technical risk |
|---|---|---|
| Request identifier | Unique Key: 337,551 populated, unique values | Request identifier, not proven person identifier; enables linkage |
| Precise location | Incident Address: 327,580 populated; Street Name; Cross Street 1/2; Intersection Street 1/2; Landmark; Taxi Pick Up Location: 2,592 populated | Residential or person-associated locations can be disclosed |
| Coordinates | Latitude, Longitude, Location: each 334,531 populated; X Coordinate (State Plane), Y Coordinate (State Plane) | Fine-grained location linkage; no anonymization implied |
| Property / area | BBL: 312,705 populated; Incident Zip: 335,275; Address Type, City, Borough, Community Board, Council District, Police Precinct | Property and area identifiers narrow locations |
| Descriptive text | Problem (formerly Complaint Type); Problem Detail (formerly Descriptor): 332,174 populated; Additional Details: 151,133; Resolution Description: 334,556 | Descriptions may concern people; category-like samples do not certify every value |
| Temporal / workflow | Created Date, Closed Date, Due Date, Resolution Action Updated Date, Status, Open Data Channel Type | Time/location combinations enable linkage; statuses can be misleading |
| Organizational / contextual | Agency, Agency Name, Location Type, Facility Type, Park Facility Name, Park Borough, Vehicle Type, Taxi Company Borough, Bridge Highway Name, Bridge Highway Direction, Road Ramp, Bridge Highway Segment | Mostly organizational/category fields; context can still narrow incidents |

Small descriptive samples included category-like values such as Trash, Other/Unknown, and HALLS AND STAIRS ONLY. No individual address, request identifier, or coordinate values were copied into this note.

An email-shaped-text scan of the three detailed description fields found 1,292 matching Resolution Description cells, containing three distinct addresses across `health.nyc.gov`, `dsny.nyc.gov`, and `dec.ny.gov` domains. No matches occurred in Additional Details or Problem Detail. Government domains alone do not determine whether a mailbox is personal or generic. This was not an exhaustive free-text identity assessment.

Evidence includes the local ignored `data/raw/nyc_311_january_2025.zip`, `DATA_SOURCE.md`, `results/data_quality_audit.md`, `results/data_quality_change_log.json`, and the 44-field ReadSchema in `results/task4_spark_physical_plan.txt`.

## Article 5 Assessment

The headings follow GDPR Article 5. The positions describe repository evidence, not a compliance certification. Public reuse access is separate from any applicable personal-data processing obligations.

| Principle | Repository/dataset evidence | Current project position | Practical implication | Limitation or risk | Evidence files |
|---|---|---|---|---|---|
| Lawfulness, fairness and transparency | Source and academic question documented; precise locations and descriptions present | Provenance transparent; no institution-approved lawful basis independently claimed or evidenced | If GDPR applies to this processing, the appropriate lawful basis must be confirmed by the relevant data controller/institution; attribute source and explain metric limits | Public availability and academic use alone do not settle lawful basis or fairness | `DATA_SOURCE.md`; `README.md`; Task 3 decision note |
| Purpose limitation | Code analyzes quality, agency/problem groups, and performance; no external identity joins found | Inspected use stays within coursework analysis and benchmarks | Assess any new linkage purpose separately | Offline activity and future reuse cannot be established from code | `notebooks/task3_model.py`; `notebooks/task4_crossover_experiment.py` |
| Data minimization | Analysis mainly needs dates, Agency, and Problem, but loads all 44 fields; storage benchmarks duplicate full schema and the scrubbed Parquet is another full-data local copy | Published numerical outputs aggregated; local input minimization incomplete | Consider reduced analytical inputs and avoid locations in reports; keep full-schema benchmarking needs explicit | Full-data copies retain fields unnecessary to the analytical question | `notebooks/storage_benchmark.py`; `notebooks/task3_exploratory_analysis.py`; `data/processed/` |
| Accuracy | 96 reversed dates, 89 zero BBL values, one targeted ZIP issue; four treatments logged | Conservative treatments preserve raw input; Task 3 consumes the treated Parquet and excludes invalid intervals | Retain counts, provenance, and uncertainty; do not equate timestamps with actual service quality | 12 encoding detections remain; status conflicts and extract boundaries limit interpretation | `results/data_quality_audit.md`; `results/full_dataset_verification.md`; `results/data_quality_change_log.json` |
| Storage limitation | Raw ZIP, scrubbed Parquet, Spark CSV, and six benchmark files present | Student retention position: retain only as needed for coursework completion, verification, assessment, moderation and applicable appeals | Review at the end of the relevant assessment/moderation/appeal period and delete unnecessary local full-data copies, including controlled backups | No institutional retention period evidenced; immutability must not mean perpetual retention | `.gitignore`; `DATA_SOURCE.md`; `data/raw/`; `data/processed/` |
| Integrity and confidentiality | SHA-256 matches; raw/processed paths absent from the inspected Git history; numerical outputs aggregate | Integrity and Git-exclusion measures exist | Keep local copies access-controlled; inspect screenshots/exports; transfer exact archive securely | Gitignore is not access control; encryption, device security, backup and remote permissions unverified | `.gitignore`; `DATA_SOURCE.md`; Git history; `results/` |
| Accountability | Provenance, change log, decisions, tests, and Git history trace development | Evidence available; remaining gaps documented | Student should retain validation/handling decisions, complete AI disclosure, and carry out the adopted retention review for copies under their control | Comprehensive identity review and institutional data-protection approval not evidenced | `AI_USE.md`; `docs/decisions/task5_professional_practice_progress.md`; `tests/`; Git history |

## Source, Handling, and Retention

Source: NYC Open Data dataset `erm2-nwe9`, **311 Service Requests from 2020 to Present**.

The existing source record states manual CSV acquisition on 2 September 2026. The archive checksum was verified; its observed date boundaries do not prove a complete calendar month.

NYC Open Data public policies retain applicable terms and state that data may be updated. Public reuse access should not be interpreted as establishing unrestricted personal-data processing rights.

### Lawful-basis position

The dataset is publicly available, but public availability does not automatically make GDPR inapplicable, and academic use alone does not establish a lawful basis.

The project does not independently claim or evidence an institution-approved lawful basis. If GDPR applies to this processing, the appropriate lawful basis must be confirmed by the relevant data controller or institution.

This is an acknowledged limitation and evidential boundary rather than a legal exemption. No Article 6 basis is asserted by this project.

### Raw and processed data handling

Scripts read the original archive while Git ignores the raw-data location. The original archive is retained unchanged.

Storage benchmarking creates full CSV, JSON, Parquet, and Gzip variants. Task 4 also uses a full extracted CSV. These copies retain location-related fields and are not treated as anonymized datasets.

For Task 3, `notebooks/full_dataset_verification.py` reads the immutable raw ZIP, applies the existing treatments to copies, and writes:

```text
data/processed/nyc_311_january_2025_scrubbed.parquet
```

Both:

```text
notebooks/task3_exploratory_analysis.py
notebooks/task3_model.py
```

consume this treated Parquet dataset.

The scrubbed Parquet preserves the full dataset and therefore represents another local full-data copy relevant to data minimization and retention.

Saved analytical tables primarily contain agency/problem aggregates. Aggregation reduces unnecessary record-level disclosure but should not automatically be treated as a formal anonymization guarantee.

No re-identification attempt or external identity join was found in the inspected implementation, and none was performed during the technical audit. Activity outside the repository cannot be certified.

### Retention position

The student retention position adopted on 7 October 2026 is to retain the raw ZIP and full-data processed copies only for as long as needed to complete, verify, assess, moderate and, where applicable, appeal the coursework.

The review/deletion trigger is the end of the relevant assessment, moderation, and applicable appeal period.

At that point, unnecessary local full-data copies under the student's control should be reviewed and deleted where they are no longer required.

This includes, where present:

- the original raw ZIP;
- the scrubbed Parquet dataset;
- Task 2 benchmark copies;
- the Task 4 Spark input CSV;
- temporary files;
- exports;
- backups containing unnecessary record-level data under the student's control.

Code, documentation, and aggregate outputs may be retained where they do not expose unnecessary raw or identifiable record-level information.

Aggregate outputs are not automatically anonymous, so their suitability for retention should still be considered.

Deleting the final checksum-matching raw archive ends the ability to guarantee exact numerical reproduction. Dataset retention therefore covers the assessment and reproduction period rather than being treated as indefinite retention.

This is the student's project position and is not presented as an institutional retention policy. No deletion has been performed as part of this documentation update.

## Additional Safeguards

If direct personal data were established to be present, appropriate safeguards would need to include:

- an institution-reviewed purpose and lawful-basis position;
- stronger minimization or redaction where appropriate;
- restricted and auditable access;
- secure storage and transfer;
- appropriate backup controls;
- explicit retention and deletion arrangements;
- disclosure review before sharing outputs.

Any necessary data-subject-rights handling or incident procedures should be determined with the responsible institution.

These are prospective safeguards and are not claims that all such controls are currently implemented.

## Verification Boundary

The initial repository audit inspected the schema and aggregate field profiles, selected text samples, current project files, seven PNGs, and 101 unique file blobs across 19 commits then reachable during the September audit for common credential patterns. No raw/processed dataset paths or credential-pattern matches were found in that inspected history.

Subsequent repository work added further commits, including the final pipeline and reproducibility improvements. The earlier credential/history scan was not repeated across every later Git object, so its result should not be interpreted as verification of all subsequent repository history.

A separate clean-checkout reproduction was completed on 7 October 2026. This verified that the committed project could be installed and executed from a fresh clone when supplied with the checksum-matching raw archive. The clean reproduction included dependency installation and verification, the complete 28-test suite, Task 2 benchmarking, the Task 3 Scrub → Explore → Model workflow, and the Task 4 pandas/PySpark scaling and crossover workflows.

These checks are bounded technical evidence rather than proof that every possible personal datum or secret is absent.

Ordinary author/contact metadata in Git differs from accidental disclosure of service-request records. Remote settings, unreachable Git objects, and exhaustive semantic review of all descriptive text remain unverified.
## Task 4 handling update - 21 October 2026

The revised crossover creates one temporary full-schema CSV per workload under the Git-ignored `data/processed/` directory. These retain the same location-related fields as the source and are not anonymized. Both engines read the same file; it is removed after that size completes. An interrupted run can leave temporary files requiring review under the existing retention position.

The successful six-size rerun removed its workload CSVs after use. Published validation evidence contains only workload hashes, aggregate counts, numerical differences and check outcomes, rather than request identifiers or record-level locations. The current suite passed 30 tests. This update does not establish a lawful basis, change the retention position, or constitute a new full-history/privacy audit or clean-checkout reproduction.
