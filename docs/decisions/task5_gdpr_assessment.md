# Task 5 GDPR technical assessment

Audit date: 12 September 2026. Scope: local January 2025 NYC 311 extract, tracked repository, and reachable Git history. This is a technical development note, not final report prose or legal advice. The academic purpose is analysis of complaint tracking, duration, and data quality. GDPR territorial applicability and an institutional lawful basis are not established by repository evidence.

## Classification and inspection

**B. Potential personal/location-related data requiring caution.**

All 44 column names and non-null counts were inspected from the checksum-matching local ZIP (337,551 rows). No dedicated complainant-name, personal-email, or personal-phone column is evident. This does not demonstrate anonymity: incident locations, timestamps, request identifiers, and complaint descriptions can relate to natural persons when combined. An incident address is not automatically the complainant's home.

| Field family | Actual fields / observed evidence | Technical risk |
|---|---|---|
| Request identifier | Unique Key: 337,551 populated, unique values | Request identifier, not proven person identifier; enables linkage |
| Precise location | Incident Address: 327,580 populated; Street Name; Cross Street 1/2; Intersection Street 1/2; Landmark; Taxi Pick Up Location: 2,592 populated | Residential or person-associated locations can be disclosed |
| Coordinates | Latitude, Longitude, Location: each 334,531 populated; X Coordinate (State Plane), Y Coordinate (State Plane) | Fine-grained location linkage; no anonymization implied |
| Property / area | BBL: 312,705 populated; Incident Zip: 335,275; Address Type, City, Borough, Community Board, Council District, Police Precinct | Property and area identifiers narrow locations |
| Descriptive text | Problem (formerly Complaint Type); Problem Detail (formerly Descriptor): 332,174 populated; Additional Details: 151,133; Resolution Description: 334,556 | Descriptions may concern people; category-like samples do not certify every value |
| Temporal / workflow | Created Date, Closed Date, Due Date, Resolution Action Updated Date, Status, Open Data Channel Type | Time/location combinations enable linkage; statuses can be misleading |
| Organizational / contextual | Agency, Agency Name, Location Type, Facility Type, Park Facility Name, Park Borough, Vehicle Type, Taxi Company Borough, Bridge Highway Name, Bridge Highway Direction, Road Ramp, Bridge Highway Segment | Mostly organizational/category fields; context can still narrow incidents |

Small descriptive samples included category-like values such as Trash, Other/Unknown, and HALLS AND STAIRS ONLY. No individual address, request identifier, or coordinate values were copied into this note. An email-shaped-text scan of the three detailed description fields found 1,292 matching Resolution Description cells, containing three distinct addresses across health.nyc.gov, dsny.nyc.gov, and dec.ny.gov domains. No matches occurred in Additional Details or Problem Detail. Government domains alone do not determine whether a mailbox is personal or generic. This was not an exhaustive free-text identity assessment.

Evidence: local ignored `data/raw/nyc_311_january_2025.zip`, `DATA_SOURCE.md`, `results/data_quality_audit.md`, `results/data_quality_change_log.json`, and the 44-field ReadSchema in `results/task4_spark_physical_plan.txt`.

## Article 5 assessment

The headings follow [GDPR Article 5](https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng). The positions describe repository evidence, not a compliance certification. Public reuse access is separate from any applicable personal-data processing obligations.

| Principle | Repository/dataset evidence | Current project position | Practical implication | Limitation or risk | Evidence files |
|---|---|---|---|---|---|
| Lawfulness, fairness and transparency | Source and academic question documented; precise locations and descriptions present | Provenance transparent; no institution-approved lawful basis independently claimed or evidenced | If GDPR applies to this processing, the appropriate lawful basis must be confirmed by the relevant data controller/institution; attribute source and explain metric limits | Public availability and academic use alone do not settle lawful basis or fairness | DATA_SOURCE.md; README.md; Task 3 decision note |
| Purpose limitation | Code analyzes quality, agency/problem groups, and performance; no external identity joins found | Inspected use stays within coursework analysis and benchmarks | Assess any new linkage purpose separately | Offline activity and future reuse cannot be established from code | notebooks/task3_model.py; notebooks/task4_crossover_experiment.py |
| Data minimization | Analysis mainly needs dates, Agency, and Problem, but loads all 44 fields; storage benchmarks duplicate full schema and the scrubbed Parquet is another full-data local copy | Published numerical outputs aggregated; local input minimization incomplete | Consider reduced analytical inputs and avoid locations in reports; keep full-schema benchmarking needs explicit | Full-data copies retain fields unnecessary to the analytical question | notebooks/storage_benchmark.py; notebooks/task3_exploratory_analysis.py; data/processed/ |
| Accuracy | 96 reversed dates, 89 zero BBL values, one targeted ZIP issue; four treatments logged | Conservative treatments preserve raw input; Task 3 consumes the treated Parquet and excludes invalid intervals | Retain counts, provenance, and uncertainty; do not equate timestamps with actual service quality | 12 encoding detections remain; status conflicts and extract boundaries limit interpretation | results/data_quality_audit.md; results/full_dataset_verification.md; results/data_quality_change_log.json |
| Storage limitation | Raw ZIP, scrubbed Parquet, Spark CSV, and six benchmark files present | Student retention position: retain only as needed for coursework completion, verification, assessment, moderation and applicable appeals | Review at the end of the relevant assessment/moderation/appeal period and delete unnecessary local full-data copies, including controlled backups | No institutional retention period evidenced; immutability must not mean perpetual retention | .gitignore; DATA_SOURCE.md; data/raw/; data/processed/ |
| Integrity and confidentiality | SHA-256 matches; raw/processed paths absent from all reachable commits; numerical outputs aggregate | Integrity and Git-exclusion measures exist | Keep local copies access-controlled; inspect screenshots/exports; transfer exact archive securely | Gitignore is not access control; encryption, device security, backup and remote permissions unverified | .gitignore; DATA_SOURCE.md; Git history; results/ |
| Accountability | Provenance, change log, decisions, tests, and Git history trace development | Evidence available; remaining gaps documented | Student should retain validation/handling decisions, complete AI disclosure, and carry out the adopted retention review for copies under their control | Comprehensive identity review and institutional data-protection approval not evidenced | AI_USE.md; docs/decisions/final_repository_audit.md; tests/; Git history |

## Source, handling, and retention

Source: [NYC Open Data, erm2-nwe9](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2020-to-Present/erm2-nwe9). The existing source record states manual CSV acquisition on 2 September 2026. The archive checksum was verified; its observed date boundaries do not prove a complete calendar month.

[NYC Open Data public policies](https://cityofnewyork.github.io/opendatatsm/publicpolicies.html) retain applicable terms and state that data may be updated. Do not infer unrestricted personal-data processing from reuse access.

Lawful-basis position (7 October 2026): the dataset is publicly available, but public availability does not automatically make GDPR inapplicable, and academic use alone does not establish a lawful basis. The project does not independently claim or evidence an institution-approved lawful basis. If GDPR applies to this processing, the appropriate lawful basis must be confirmed by the relevant data controller/institution. This is an acknowledged limitation/evidential boundary, not a legal exemption; no Article 6 basis is asserted.

Raw handling: scripts read the archive and Git ignores it. The audit did not alter it. Processed handling: storage benchmarks create full CSV, JSON, Parquet, and gzip variants; Task 4 uses a full extracted CSV. These retain location data and are not anonymized. For Task 3, `notebooks/full_dataset_verification.py` reads the immutable raw ZIP, applies the existing treatments to copies, and writes `data/processed/nyc_311_january_2025_scrubbed.parquet`. Both `notebooks/task3_exploratory_analysis.py` and `notebooks/task3_model.py` read that treated Parquet file. The scrubbed Parquet preserves the full dataset and is another local full-data copy relevant to minimisation and retention. Saved analytical tables contain agency/problem aggregates; low-count categories remain in some summaries, so aggregation is not a formal anonymization guarantee.

No re-identification attempt or external identity join was found in the inspected implementation, and none was performed during this audit. Activity outside the repository cannot be certified.

Student retention position (7 October 2026): the raw ZIP and full-data processed copies are retained only for as long as needed to complete, verify, assess, moderate and, where applicable, appeal the coursework. The review/deletion trigger is the end of the relevant assessment/moderation/appeal period. At that point, the student should review and delete unnecessary local full-data copies under their control. This covers, where present, the raw ZIP, scrubbed Parquet, Task 2 benchmark copies, Spark input CSV, temporary files, exports and backups under the student's control.

Code, documentation and aggregate outputs may be retained where they do not expose raw or identifiable record-level data. Aggregate outputs are not automatically anonymous; suitability for retention must be assessed. Deleting the final exact archive ends exact numerical reproduction, so dataset retention covers the assessment/reproduction period. This is the student's project position, not an asserted institutional retention policy. No deletion has been performed as part of this documentation update.

If direct personal data were present, safeguards would need an institution-reviewed purpose/lawful-basis position, stronger minimization or redaction, restricted and auditable access, secure storage/transfer and backup controls, explicit retention/deletion arrangements, and disclosure review before sharing. Any necessary rights-handling or incident procedures should be determined with the responsible institution. These are prospective safeguards, not claims of implementation.

## Verification boundary

The audit inspected the schema and aggregate field profiles, selected text samples, current project files, seven PNGs, and 101 unique file blobs across 19 reachable commits for common credential patterns. No raw/processed dataset paths or credential-pattern matches were found in those commits. This is a bounded scan, not proof that every possible personal datum or secret is absent. Ordinary author/contact metadata in Git differs from accidental disclosure of service-request records. Remote settings, unreachable objects, and exhaustive semantic review of all descriptions remain unverified.
