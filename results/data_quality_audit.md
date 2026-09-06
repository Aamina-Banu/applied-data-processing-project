# Data Quality Audit

## 1. Dataset Structure and Data Types

### Dataset dimensions

- Rows: 337,551
- Columns: 44
- Selected period: January 2025
- Source: NYC Open Data – 311 Service Requests

### Observed data types

The dataset contains a mixture of numeric and categorical/text fields. The main observations from the initial profiling were:

- `Unique Key` is stored as `int64`.
- Date/time fields such as `Created Date`, `Closed Date`, `Due Date`, and `Resolution Action Updated Date` are stored as strings.
- `Incident Zip`, `Council District`, and `BBL` are stored as `float64`.
- `Latitude` and `Longitude` are stored as `float64`.
- `X Coordinate (State Plane)` and `Y Coordinate (State Plane)` are stored as strings.
- Most descriptive and categorical fields are stored as strings.

The string representation of date fields is treated as a preprocessing requirement rather than automatically being classified as a data-quality error. Date fields will be converted to appropriate datetime types during the cleaning stage.

### Initial assessment

The dataset satisfies the structural requirement for the project, with 337,551 records and 44 fields containing a mixture of numeric, categorical, and date/time information.

Further checks were performed to identify genuine data-quality problems and determine appropriate treatment during the cleaning stage.

---

## 2. Missing-Value Analysis

The dataset contains 4,015,232 missing cells across 337,551 records.

The highest missing-value rates were observed in:

| Field | Missing | Percentage |
|---|---:|---:|
| Taxi Company Borough | 337,389 | 99.95% |
| Road Ramp | 336,955 | 99.82% |
| Bridge Highway Direction | 336,758 | 99.77% |
| Facility Type | 336,522 | 99.70% |
| Due Date | 336,256 | 99.62% |
| Bridge Highway Segment | 336,117 | 99.58% |
| Bridge Highway Name | 336,115 | 99.57% |
| Taxi Pick Up Location | 334,959 | 99.23% |
| Vehicle Type | 326,817 | 96.82% |
| Additional Details | 186,418 | 55.23% |

Several other fields also contain missing values, including `Location Type`, `BBL`, `City`, `Problem Detail`, `Council District`, geographic coordinates, `Closed Date`, and `Incident Zip`.

Missing values were not automatically classified as data-quality errors because many fields are conditional and are only relevant to particular types of service requests. Further cross-field analysis was therefore used to distinguish expected missingness from potential quality problems.

Total missing cells: **4,015,232**.

No blanket deletion or imputation of missing values will be performed. Treatment will depend on the meaning and importance of each field during the cleaning stage.

---

## 3. Duplicate Analysis

Two duplicate checks were performed:

| Check | Result |
|---|---:|
| Exact duplicate rows | 0 |
| Duplicate `Unique Key` values | 0 |

No exact duplicate records were identified, and every service request has a unique `Unique Key`.

Therefore, duplicate records are not identified as a data-quality problem in this dataset.

---

## 4. Date and Time Consistency

Date/time fields were converted to datetime values for validation.

### Date parsing

| Check | Result |
|---|---:|
| Invalid `Created Date` values | 0 |
| Missing/invalid `Closed Date` values | 2,542 |
| Records with both Created and Closed dates | 335,009 |

The 2,542 missing `Closed Date` values were not automatically classified as errors because a service request may legitimately remain open or have no recorded closure timestamp.

### Created Date and Closed Date consistency

A logical consistency check was performed to identify records where `Closed Date` occurred before `Created Date`.

| Check | Result |
|---|---:|
| `Closed Date` before `Created Date` | 96 |
| Percentage of all records | 0.0284% |
| Largest observed inconsistency | 14.35 days |

The 96 records contain a temporal inconsistency because the recorded closure timestamp precedes the recorded creation timestamp.

Further investigation showed:

- All 96 records belonged to the `DOT` agency.
- All 96 had `Pending` status.
- 95 were `Street Light Condition` requests.
- 1 was a `Traffic Signal Condition` request.
- January 27 contained 38 of the 96 affected records.

The concentration within one agency, status, and mainly one problem type suggests a potentially systematic recording pattern.

Therefore, these records will not be deleted or automatically corrected. Further investigation or documented treatment will be performed during cleaning.

---

### Status and Closed Date consistency

A cross-field consistency check was performed between `Status` and `Closed Date`.

| Check | Records |
|---|---:|
| `Closed` status with missing `Closed Date` | 1,025 |
| Non-`Closed` status with a `Closed Date` | 302 |
| Total `Closed` records | 335,732 |
| Total non-`Closed` records | 1,819 |

#### Closed status with missing Closed Date

The 1,025 records marked as `Closed` but missing a `Closed Date` were investigated further.

| Category | Records |
|---|---:|
| Total affected records | 1,025 |
| DHS | 1,024 |
| DSNY | 1 |
| Homeless Person Assistance | 1,024 |
| Derelict Vehicles | 1 |

All 1,025 affected records also contained:

| Check | Result |
|---|---:|
| Resolution Description populated | 1,025 |
| Resolution Action Updated Date populated | 1,025 |

The strong concentration within DHS and `Homeless Person Assistance`, together with the presence of resolution-related information, suggests that the missing `Closed Date` may be related to agency-specific recording practices rather than simply incomplete records.

No closure dates will be imputed because there is insufficient evidence to determine a reliable replacement timestamp.

#### Non-Closed status with Closed Date

The 302 records containing a `Closed Date` while their current status was not `Closed` were also investigated.

| Status | Records |
|---|---:|
| Pending | 96 |
| Assigned | 85 |
| Open | 81 |
| Unspecified | 35 |
| Started | 4 |
| In Progress | 1 |

The records were mainly associated with:

| Agency | Records |
|---|---:|
| DOT | 131 |
| DOB | 124 |
| NYPD | 34 |
| DOHMH | 7 |
| DEP | 5 |
| DPR | 1 |

This may represent a difference between current request status and historical closure information. Therefore, these records are not automatically classified as erroneous or removed.

---

### Due Date consistency

The `Due Date` field was compared against `Created Date`.

| Check | Result |
|---|---:|
| Missing/invalid `Due Date` | 336,256 |
| `Due Date` before `Created Date` | 0 |
| Earliest observed `Due Date` | 2025-01-07 06:08:55 |
| Latest observed `Due Date` | 2025-04-04 11:10:44 |

No records were identified where `Due Date` occurred before `Created Date`.

The missingness of `Due Date` is therefore treated separately from temporal validity because the field appears to be conditional.

No `Due Date` values require correction based on the checks performed.

---

### Resolution Action Updated Date consistency

The `Resolution Action Updated Date` field was compared against `Created Date`.

| Check | Result |
|---|---:|
| Missing/invalid `Resolution Action Updated Date` | 678 |
| `Resolution Action Updated Date` before `Created Date` | 10,214 |
| Earliest observed update date | 2023-03-20 14:11:31 |
| Latest observed update date | 2026-08-31 00:00:00 |

A total of 10,214 records contain a `Resolution Action Updated Date` earlier than their `Created Date`.

The records were strongly concentrated within:

| Agency | Records |
|---|---:|
| HPD | 8,631 |
| DOB | 950 |
| DSNY | 447 |
| DOT | 183 |
| DEP | 3 |

The main problem types included:

| Problem Type | Records |
|---|---:|
| HEAT/HOT WATER | 7,575 |
| General Construction/Plumbing | 452 |
| Derelict Vehicles | 374 |
| PLUMBING | 256 |
| Real Time Enforcement | 211 |
| Street Light Condition | 167 |
| PAINT/PLASTER | 163 |
| UNSANITARY CONDITION | 135 |
| GENERAL | 124 |
| Building/Use | 117 |

The magnitude of the discrepancy was also examined:

| Difference | Records |
|---|---:|
| Up to 1 day earlier | 10,067 |
| 1–7 days earlier | 109 |
| 7–30 days earlier | 12 |
| 30–90 days earlier | 2 |
| 90–365 days earlier | 14 |
| More than 365 days earlier | 10 |
| Total | 10,214 |

The median difference was approximately 0.4 days, while the maximum difference was approximately 653.91 days.

The strong concentration within HPD and `HEAT/HOT WATER`, combined with the fact that most discrepancies are less than one day, suggests that the issue may be associated with system recording or timestamp handling rather than random corruption.

The field will therefore be retained in the raw dataset and will not be automatically corrected for all 10,214 records. Any cleaning treatment will be documented and validated.

---

## 5. Text Encoding Quality

The `Resolution Description` field was examined for common indicators of character encoding corruption, including `â`, `Ã`, `Â`, and the replacement character `�`.

| Check | Result |
|---|---:|
| Non-missing Resolution Description values | 334,556 |
| Potentially corrupted values | 8,606 |
| Percentage affected | 2.5724% |

Several values contained malformed character sequences consistent with possible encoding corruption (mojibake).

The issue affects 8,606 non-missing descriptions and represents a significant text-quality problem.

The affected values will be investigated and corrected during the cleaning stage where a reliable encoding correction can be established. The raw dataset will remain unchanged.

---

## 6. Categorical Consistency

The main categorical fields were examined for unexpected, blank, or malformed category values.

| Field | Unique values | Main observations |
|---|---:|---|
| Status | 7 | Closed, In Progress, Open, Assigned, Pending, Started, Unspecified |
| Agency | 14 | 14 agency codes identified |
| Borough | 6 | Five boroughs plus Unspecified |
| Open Data Channel Type | 4 | ONLINE, MOBILE, PHONE, UNKNOWN |

No blank category values were identified in these fields.

The values `Unspecified` and `UNKNOWN` were retained as recorded categories because they may represent cases where the relevant information was not specified or known.

No definite categorical consistency problem was identified in the fields examined.

---

## 7. Numeric and Geographic Validity

### Numeric range validation

| Field | Minimum | Maximum | Initial assessment |
|---|---:|---:|---|
| Latitude | 40.498949 | 40.912295 | Geographically plausible |
| Longitude | -74.254326 | -73.700723 | Geographically plausible |
| Incident Zip | 83 | 36,602 | Potentially invalid values identified |
| Council District | 1 | 51 | Values appear plausible |
| BBL | 0 | 5,200,170,000 | Zero values require treatment |

Negative longitude values were not classified as errors because locations west of the Prime Meridian are conventionally represented using negative longitude values.

---

### Incident Zip validation

The `Incident Zip` field was checked for values that do not conform to a five-digit ZIP-code representation.

| Check | Result |
|---|---:|
| Non-missing ZIP values | 335,275 |
| Potentially invalid values | 3 |
| Percentage affected | 0.0009% |

The three values were:

| Recorded value | Frequency |
|---:|---:|
| 83 | 1 |
| 7105 | 1 |
| 7307 | 1 |

Further investigation showed:

| Recorded ZIP | Associated information | Assessment |
|---:|---|---|
| 7105 | Newark, New Jersey | Likely leading-zero representation of `07105` |
| 83 | Bethesda Fountain, Manhattan, New York | Suspicious/inconsistent ZIP value |
| 7307 | Jersey City, New Jersey | Likely leading-zero representation of `07307` |

The values `7105` and `7307` may represent valid ZIP codes where leading zeros were lost because the field was stored as numeric data.

The value `83` is more problematic because it is associated with Bethesda Fountain in Manhattan and does not represent a valid five-digit ZIP-code value.

Therefore:

- `7105` and `7307` are treated as representation issues.
- `83` is classified as a genuine data-quality issue.
- The raw value will be preserved.
- The cleaned dataset will apply an appropriate invalid/missing-value treatment to the `83` value.

---

### BBL validation

The `BBL` field was examined for zero and non-zero values.

| Check | Result |
|---|---:|
| Non-missing BBL values | 312,705 |
| BBL values equal to 0 | 89 |
| Percentage affected | 0.0285% |
| Minimum non-zero BBL | 1,000,010,000 |
| Maximum non-zero BBL | 5,200,170,000 |

A total of 89 records contain a `BBL` value of `0`.

The observed non-zero BBL values indicate that zero is inconsistent with the normal BBL identifier pattern.

The affected records contain other location information such as addresses, boroughs, ZIP codes, and, in many cases, geographic coordinates.

Therefore, `BBL = 0` is treated as an unavailable or invalid property identifier.

During cleaning, the 89 zero values will be converted to missing values (`NaN`). The raw dataset will remain unchanged.

---

### Geographic field consistency

The relationship between the main geographic fields was examined.

| Check | Result |
|---|---:|
| Latitude missing | 3,020 |
| Longitude missing | 3,020 |
| Location missing | 3,020 |
| X Coordinate missing | 3,018 |
| Y Coordinate missing | 3,015 |
| Latitude present + Longitude missing | 0 |
| Longitude present + Latitude missing | 0 |
| Latitude/Longitude present + Location missing | 0 |

No records were found where only one of `Latitude` or `Longitude` was missing.

There were also no records where both latitude and longitude were present while `Location` was missing.

The geographic fields therefore show coordinated missingness rather than isolated coordinate loss. This does not by itself indicate a data-quality error.

No geographic values require correction based on this check.

---

### Geographic coordinate range validation

A broad geographic screening range was used to identify coordinates clearly outside the expected NYC area.

| Check | Result |
|---|---:|
| Records outside broad NYC screening range | 0 |
| Percentage | 0% |

No records were identified with latitude or longitude values outside the broad screening range.

Therefore, no obvious geographic coordinate outliers were identified.

---

### Borough and City consistency

The relationship between `Borough` and `City` was examined to identify potentially inconsistent geographic combinations.

The `City` field contains both borough-level names and locality/neighborhood names. For example, records associated with `QUEENS` include localities such as `JAMAICA`, `FLUSHING`, `ASTORIA`, `RIDGEWOOD`, `FRESH MEADOWS`, and `JACKSON HEIGHTS`.

Similarly, Manhattan records commonly use `NEW YORK` or `MANHATTAN`.

These combinations do not provide sufficient evidence of data-quality errors because the `City` field can represent different locality names within a borough.

Therefore, no definite Borough/City consistency problem was identified.

---

## 8. Blank and Whitespace Value Analysis

Text and string-based fields were examined for values that were empty or contained only whitespace after trimming.

The check identified 3,977,831 blank/whitespace cells. However, these counts closely correspond to the missing-value counts identified during the missing-value analysis because empty CSV fields are interpreted as missing values during import.

Therefore, the blank/whitespace check did not identify a substantial additional category of missing data beyond the missing values already documented in Section 2.

No separate whitespace-related data-quality issue was identified.

---

# 9. Final Data Quality Issues Summary

The audit identified a mixture of confirmed issues, potential issues, and clean validation results.

### Confirmed or treatment-required issues

| Issue | Affected records | Percentage | Planned treatment |
|---|---:|---:|---|
| Potential encoding corruption in `Resolution Description` | 8,606 | 2.5724% of non-missing descriptions | Investigate and correct where reliable |
| `Closed Date` before `Created Date` | 96 | 0.0284% of all records | Investigate and apply documented treatment |
| Invalid `BBL = 0` | 89 | 0.0285% of non-missing BBL values | Convert to missing (`NaN`) |
| Suspicious `Incident Zip = 83` | 1 | 0.0003% of all records | Treat as invalid/missing in cleaned data |

### Potential issues requiring cautious treatment

| Issue | Affected records | Assessment |
|---|---:|---|
| `Closed` status with missing `Closed Date` | 1,025 | Strongly concentrated in DHS/Homeless Person Assistance; do not impute automatically |
| Non-`Closed` status with `Closed Date` | 302 | May represent historical closure information |
| `Resolution Action Updated Date` before `Created Date` | 10,214 | Strong agency/problem concentration suggests systematic recording behavior |
| `Incident Zip` values 7105 and 7307 | 2 | Likely leading-zero representation rather than invalid locations |

### Clean checks

| Check | Result |
|---|---|
| Exact duplicate rows | 0 |
| Duplicate `Unique Key` values | 0 |
| Invalid `Created Date` values | 0 |
| `Due Date` before `Created Date` | 0 |
| Coordinates outside broad NYC range | 0 |
| Partial Latitude/Longitude missingness | 0 |
| Definite Borough/City inconsistencies | None identified |
| Additional whitespace-only issue | None identified |
| Unexpected categories in main categorical fields | None identified |

---

## 10. Data Quality Assessment

Overall, the dataset is structurally suitable for further analysis, with 337,551 records and 44 fields.

The audit identified several issues that require attention during preprocessing, particularly text encoding corruption, invalid BBL values, a suspicious ZIP-code value, and temporal inconsistencies between date fields.

At the same time, several important quality checks were clean. No duplicate records or duplicate service-request identifiers were identified, no invalid `Created Date` values were found, no `Due Date` values occurred before request creation, and no geographic coordinates were found outside the broad NYC screening range.

Importantly, missing values were not treated as errors automatically. Many high-missingness fields appear to be conditional fields that are not applicable to every service request. Similarly, potentially inconsistent status and timestamp combinations were investigated rather than being corrected without evidence.

The raw dataset will remain unchanged throughout the cleaning process. All cleaning operations will be performed on a separate processed dataset so that the original data can be preserved for reproducibility, traceability, and validation.

The findings from this audit will be used to define the cleaning rules in the next stage of the project.