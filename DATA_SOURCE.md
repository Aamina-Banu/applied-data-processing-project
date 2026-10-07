# Dataset Source Record

## File Integrity

Raw file: nyc_311_january_2025.zip

SHA-256:
66EB5D89668990C6F86AAF49C71DB026D1452CD974884A952529299240503866

## Source

Provider: NYC Open Data / NYC 311

Dataset: 311 Service Requests from 2020 to Present

Selected/intended period: January 2025
Recorded extraction date: 2 September 2026
Dataset identifier: erm2-nwe9
Recorded filter intent: Created Date restricted to January 2025

Recorded acquisition method: Manually downloaded as CSV from NYC Open Data after applying a Created Date filter intended to select January 2025.

Raw data modified: No

Reuse terms: NYC Open Data provides public reuse access, subject to applicable portal and provider terms. Public availability does not establish that every field is anonymous.

Official reference: https://opendata.cityofnewyork.us/faq/

## Provenance evidence and acquisition limitations

Dataset page: [NYC Open Data, erm2-nwe9](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2020-to-Present/erm2-nwe9).

[NYC Open Data public policies](https://cityofnewyork.github.io/opendatatsm/publicpolicies.html) describe access without a licensing requirement while retaining applicable terms, disclaiming completeness/accuracy warranties, and allowing source updates. An exact repeat export is not guaranteed.

The local ZIP checksum was recomputed and matches the value above. It contains one CSV member, named `. t.csv`, with 337,551 rows and 44 columns. The local Task 4 input CSV is byte-identical to that archive member.

Parsing Created Date with `%m/%d/%Y %I:%M:%S %p` gives:

- Minimum: `2025-01-01 15:43:03`.
- Maximum: `2025-01-31 15:42:07`.

These are observed extract boundaries, not a reconstructed portal filter. They leave full-calendar-month coverage uncertain. Exact filter times/timezone and export settings were not retained; the student must review them before claiming complete January coverage. No replacement extract was acquired during this audit.

The extraction date and manual acquisition method above are based on the project's recorded provenance information and were not independently reconstructed from the source portal.

Potential personal/location-related fields are assessed in [the GDPR technical note](docs/decisions/task5_gdpr_assessment.md). Retaining an immutable raw input is an integrity measure, not an indefinite-retention policy.