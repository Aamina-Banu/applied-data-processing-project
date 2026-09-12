# Task 3 – OSEMN Analysis Progress

## Purpose

This document records the technical progress, analytical decisions, results, and limitations for Task 3 of the project.

The analysis addresses the research question:

> How effectively are NYC 311 complaints tracked and resolved, and how can data-quality inconsistencies in complaint-tracking data be identified and appropriately treated?

This file is a development and evidence record. It is not final report prose.

---

## 1. Obtain

### Dataset

- Dataset: NYC 311 Service Requests from 2020 to Present
- Provider: NYC Open Data
- Dataset identifier: `erm2-nwe9`
- Extract used: January 2025
- Raw dataset rows: 337,551
- Raw dataset columns: 44
- Extraction date: 2 September 2026
- Raw file: `data/raw/nyc_311_january_2025.zip`
- Raw ZIP file retained unchanged.

### Raw-data integrity

SHA-256 checksum:

`66EB5D89668990C6F86AAF49C71DB026D1452CD974884A952529299240503866`

The raw ZIP is treated as immutable. Data-quality treatments are performed on DataFrame copies rather than overwriting the source dataset.

Detailed source, acquisition, reuse, and checksum information is recorded in `DATA_SOURCE.md`.

---

## 2. Scrub

A full data-quality investigation was performed before the exploratory analysis.

Detailed findings are recorded in:

- `results/data_quality_audit.md`
- `results/full_dataset_verification.md`
- `results/data_quality_change_log.json`

### Dataset-level findings

- Total rows: 337,551
- Total columns: 44
- Exact duplicate rows: 0
- Duplicate `Unique Key` values: 0
- Total missing cells: 4,015,232

A large amount of missing data occurs in fields that are conditional and therefore cannot automatically be interpreted as data-quality errors.

### Date consistency

`Created Date` and `Closed Date` were parsed using the explicit format:

`%m/%d/%Y %I:%M:%S %p`

Findings included:

- Invalid `Created Date` values: 0
- Missing or unusable `Closed Date` values: 2,542
- Records containing both usable Created and Closed dates: 335,009
- Records where `Closed Date` occurred before `Created Date`: 96
- Maximum negative discrepancy: approximately 14.35 days

The 96 negative-duration records were treated as date inconsistencies rather than valid resolution durations.

### Status and Closed Date consistency

Two important tracking inconsistencies were identified:

- `Status = Closed` but no usable `Closed Date`: 1,025 records
- `Status != Closed` but a usable `Closed Date` exists: 302 records

The 302 non-Closed records containing a Closed Date consisted of:

- Pending: 96
- Assigned: 85
- Open: 81
- Unspecified: 35
- Started: 4
- In Progress: 1

This means `Status` and `Closed Date` cannot automatically be treated as interchangeable indicators of complaint resolution.

### Resolution Action Updated Date

Findings included:

- Missing or unusable values: 678
- Records where Resolution Action Updated Date preceded Created Date: 10,214
- Most of these records were associated with HPD
- Median discrepancy: approximately 0.4 days
- Maximum discrepancy: approximately 653.91 days

The pattern may reflect systematic behavior in the source data. Unsupported automatic correction was therefore avoided.

### Incident ZIP

Suspicious ZIP values included:

- `83.0`: one record associated with Bethesda Fountain, Manhattan
- `7105.0`: likely represents ZIP `07105`
- `7307.0`: likely represents ZIP `07307`

The clearly invalid `83.0` value was treated conservatively. Potential leading-zero cases were not automatically modified without sufficient evidence.

### BBL

- Records with `BBL = 0`: 89

Zero was treated as an unavailable/invalid BBL value rather than a valid identifier.

### Encoding

Initial encoding-related detections:

- 8,606 records

After safe encoding treatment:

- 12 detections remained

The remaining values were preserved because automatic conversion could not be performed safely without risking incorrect modification.

### Treatment verification

After applying the implemented treatments:

- Invalid BBL values: 89 → 0
- Invalid ZIP values targeted by the treatment: 1 → 0
- Invalid reversed resolution dates: 96 → 0
- Encoding detections: 8,606 → 12
- Row count before treatment: 337,551
- Row count after treatment: 337,551

No rows were silently deleted.

The original loaded DataFrame was also verified against a deep snapshot to confirm that the treatment process did not modify the original dataset.

The data-quality change log was persisted to:

`results/data_quality_change_log.json`

---

## 3. Explore

Exploratory analysis is implemented in:

`notebooks/task3_exploratory_analysis.py`

The script also saves numerical evidence and figures to the `results` directory.

### 3.1 Complaint distribution

Agency complaint counts showed substantial differences in workload.

Largest agencies by complaint count:

- NYPD: 145,980
- HPD: 108,883
- DSNY: 25,973
- DOT: 16,027
- DEP: 15,111

The two largest agencies therefore account for a substantial share of the January 2025 extract.

### Top complaint types

The largest complaint categories included:

- Noise - Residential: 66,783
- HEAT/HOT WATER: 66,297
- Illegal Parking: 41,874
- Blocked Driveway: 14,115
- UNSANITARY CONDITION: 9,820
- PLUMBING: 7,261
- Water System: 6,581
- Abandoned Vehicle: 5,504
- PAINT/PLASTER: 5,486
- Street Condition: 5,281
- Snow or Ice: 5,161
- DOOR/WINDOW: 4,834
- Noise: 4,158
- Traffic Signal Condition: 4,124
- Noise - Commercial: 4,034

### Agency and complaint-type relationship

The Agency × Problem crosstab showed that major complaint categories are strongly associated with particular agencies.

Examples:

- NYPD:
  - Noise - Residential: 66,783
  - Illegal Parking: 41,874
  - Blocked Driveway: 14,115
  - Abandoned Vehicle: 5,504
  - Noise - Commercial: 4,034

- HPD:
  - HEAT/HOT WATER: 66,297
  - UNSANITARY CONDITION: 9,820
  - PLUMBING: 7,261
  - PAINT/PLASTER: 5,486
  - DOOR/WINDOW: 4,834

- DEP:
  - Water System: 6,581
  - Noise: 4,158

- DOT:
  - Street Condition: 5,281
  - Traffic Signal Condition: 4,124

- DSNY:
  - Snow or Ice: 5,161

This relationship is important when interpreting agency-level resolution times because agencies do not handle equivalent complaint workloads.

### 3.2 Resolution-time distribution

Resolution time was calculated as:

`Closed Date Parsed - Created Date Parsed`

and converted to hours.

Before excluding invalid negative durations:

- Valid numeric durations: 335,009
- Mean: approximately 240.42 hours
- Median: approximately 15.04 hours
- First quartile: approximately 1.94 hours
- Third quartile: approximately 69.69 hours
- Minimum: approximately -344.43 hours
- Maximum: approximately 14,491.33 hours
- Negative durations: 96

The 96 negative durations correspond to the previously identified date inconsistencies.

For resolution-duration analysis, these records were excluded from the analytical subset rather than deleted from the raw dataset.

After filtering:

- Valid non-negative resolution records: 334,913
- Mean: approximately 240.51 hours
- Median: approximately 15.06 hours
- First quartile: approximately 1.95 hours
- Third quartile: approximately 69.71 hours
- Maximum: approximately 14,491.33 hours

The large difference between the mean and median indicates a strongly right-skewed distribution. Median resolution time was therefore emphasized in group comparisons.

### 3.3 Resolution time by agency

Median valid resolution time differed substantially between agencies.

Examples:

- NYPD: approximately 2.05 hours
- DHS: approximately 11.87 hours
- DEP: approximately 21.25 hours
- DOT: approximately 29.93 hours
- DSNY: approximately 32.39 hours
- DOHMH: approximately 40.39 hours
- HPD: approximately 65.92 hours
- DCWP: approximately 85.92 hours
- DPR: approximately 143.46 hours
- DOB: approximately 149.20 hours
- OTI: approximately 351.41 hours
- DOE: approximately 835.63 hours
- TLC: approximately 1,651.94 hours
- EDC: approximately 3,411.29 hours

These values must not be interpreted as a direct ranking of agency performance because complaint composition and sample size differ between agencies.

### 3.4 Resolution time by complaint type

Median resolution time also varied substantially between the top complaint categories.

Examples:

- Noise - Commercial: approximately 0.92 hours
- Illegal Parking: approximately 1.63 hours
- Abandoned Vehicle: approximately 2.10 hours
- Blocked Driveway: approximately 2.12 hours
- Traffic Signal Condition: approximately 2.45 hours
- Water System: approximately 2.82 hours
- Noise - Residential: approximately 3.34 hours
- Street Condition: approximately 23.43 hours
- HEAT/HOT WATER: approximately 45.57 hours
- Noise: approximately 53.17 hours
- Snow or Ice: approximately 53.20 hours
- PAINT/PLASTER: approximately 220.58 hours
- PLUMBING: approximately 259.75 hours
- DOOR/WINDOW: approximately 412.87 hours
- UNSANITARY CONDITION: approximately 425.31 hours

This supports the decision to consider complaint composition when examining agency-level resolution differences.

### 3.5 Closed Date completeness

Usable `Closed Date` values:

- Present: 335,009
- Missing/unusable: 2,542

Missing Closed Dates by agency included:

- DHS: 1,024
- DPR: 380
- DOT: 248
- DEP: 215
- DOHMH: 203
- HPD: 187
- TLC: 172
- DSNY: 113

Closed Date completeness varied across agencies.

Examples:

- DHS: approximately 52.19%
- DPR: approximately 90.17%
- TLC: approximately 93.46%
- DOHMH: approximately 96.64%
- DOT: approximately 98.45%
- DEP: approximately 98.58%
- DSNY: approximately 99.56%
- HPD: approximately 99.83%

Several other agencies had 100% usable Closed Date values in this extract.

Closed Date completeness is a data-tracking measure and must not automatically be interpreted as the actual complaint resolution rate.

### Explore evidence files

The Explore script generates:

- `results/task3_explore_summary.csv`
- `results/task3_agency_resolution_summary.csv`
- `results/task3_problem_resolution_summary.csv`
- `results/task3_tracking_consistency.txt`

### Explore figures

The Explore stage generates:

- `results/task3_top_15_complaint_types.png`
- `results/task3_median_resolution_by_agency.png`
- `results/task3_closed_date_completeness_by_agency.png`

Each figure is generated directly from the January 2025 dataset.

---

## 4. Model

The Model stage uses non-machine-learning analytical methods.

Implementation:

`notebooks/task3_model.py`

Three related approaches are used:

1. Agency × complaint-type segmentation
2. Resolution-time bands
3. Kruskal-Wallis statistical comparison

No train/test split is required because no predictive machine-learning model is fitted.

---

## 4.1 Agency × Problem Segmentation

Valid non-negative resolution records were grouped by:

- Agency
- Problem type

For each group, the analysis calculates:

- complaint count
- median resolution time
- mean resolution time

Groups with fewer than 30 valid records were excluded from this comparison to reduce the influence of very small segments.

Minimum segment size:

`30`

Number of qualifying Agency × Problem segments:

`118`

### Short-duration examples

Examples among the shortest median-resolution segments included:

- DOHMH / Unleashed Dog:
  - 53 complaints
  - median: 0.00 hours
  - mean: 0.00 hours

- DOHMH / Unsanitary Animal Pvt Property:
  - 154 complaints
  - median: 0.00 hours
  - mean: approximately 16.31 hours

- DOHMH / Rodent:
  - 2,118 complaints
  - median: 0.00 hours
  - mean: approximately 27.71 hours

- DSNY / Vendor Enforcement:
  - 1,270 complaints
  - median: approximately 0.40 hours
  - mean: approximately 3.07 hours

- NYPD / Drug Activity:
  - 1,616 complaints
  - median: approximately 0.60 hours
  - mean: approximately 1.49 hours

### Long-duration examples

Examples among the longest median-resolution segments included:

- DPR / New Tree Request:
  - 39 complaints
  - median: approximately 3,546.48 hours
  - mean: approximately 3,482.87 hours

- EDC / Noise - Helicopter:
  - 1,802 complaints
  - median: approximately 3,411.29 hours
  - mean: approximately 3,752.37 hours

- TLC / For Hire Vehicle Complaint:
  - 1,368 complaints
  - median: approximately 1,851.98 hours
  - mean: approximately 1,999.35 hours

- TLC / Taxi Complaint:
  - 547 complaints
  - median: approximately 1,785.78 hours
  - mean: approximately 2,215.05 hours

- DHS / Encampment:
  - 638 complaints
  - median: approximately 1,554.07 hours
  - mean: approximately 1,194.74 hours

The segmentation demonstrates that resolution duration differs substantially between specific types of agency workload.

These values do not establish that one agency performs better or worse than another.

---

## 4.2 Resolution-Time Bands

Valid resolution durations were divided into researcher-defined operational bands:

| Band | Duration |
|---|---|
| Very short | Less than 4 hours |
| Short | 4 hours to less than 24 hours |
| Medium | 24 hours to less than 72 hours |
| Long | 72 hours to less than 168 hours |
| Very long | 168 hours or more |

The boundaries correspond to interpretable operational periods:

- within a few hours;
- within one day;
- approximately one to three days;
- approximately three to seven days;
- one week or longer.

These categories are analytical groupings created for this project. They are not presented as official NYC 311 service standards.

Both counts and within-group percentages were calculated.

Percentages are important because agencies have substantially different numbers of complaints.

### Selected agency patterns

Examples from the agency percentage results:

- NYPD:
  - Very short: approximately 66.51%
  - Short: approximately 31.39%
  - Medium: approximately 1.85%
  - Long: approximately 0.20%
  - Very long: approximately 0.04%

- HPD:
  - Very short: approximately 10.91%
  - Short: approximately 22.57%
  - Medium: approximately 19.60%
  - Long: approximately 14.91%
  - Very long: approximately 32.01%

- EDC:
  - Very long: 100%

The results demonstrate large differences in resolution-duration composition between agencies.

They must be interpreted together with the different complaint types handled by each agency.

---

## 4.3 Kruskal-Wallis Statistical Comparison

A Kruskal-Wallis test was used to assess whether the resolution-time distributions of selected agencies were identical.

The test was chosen because:

- multiple independent agency groups were compared;
- the resolution-time distribution was strongly right-skewed;
- the analysis did not rely only on a comparison of means.

To reduce comparisons involving very small agency samples, only agencies with at least 1,000 valid resolution records were included.

Minimum agency sample size:

`1,000`

Number of agencies included:

`12`

Included agencies:

- NYPD
- HPD
- DSNY
- DOT
- DEP
- DOB
- DOHMH
- DPR
- TLC
- EDC
- DCWP
- DHS

Sample sizes included:

- NYPD: 145,980
- HPD: 108,696
- DSNY: 25,860
- DOT: 15,683
- DEP: 14,896
- DOB: 7,484
- DOHMH: 5,839
- DPR: 3,485
- TLC: 2,458
- EDC: 1,802
- DCWP: 1,314
- DHS: 1,118

### Statistical result

Kruskal-Wallis H statistic:

`189258.3886`

The calculated p-value underflowed to `0` at floating-point precision.

This should not be interpreted as a literal probability of zero.

The result provides extremely strong statistical evidence that the resolution-time distributions are not identical across all selected agencies.

However, the test does not establish:

- which specific agency pairs differ;
- the practical importance of each difference;
- that agency performance caused the differences;
- why the differences occurred.

Complaint-type composition and other operational factors may contribute to the observed differences.

---

## 4.4 Model Evidence Files

The Model script generates:

- `results/task3_model_segments.csv`
- `results/task3_resolution_bands_by_agency.csv`
- `results/task3_resolution_band_percentages_by_agency.csv`
- `results/task3_resolution_bands_by_problem.csv`
- `results/task3_resolution_band_percentages_by_problem.csv`
- `results/task3_kruskal_wallis.txt`

These files preserve the numerical evidence used by the Model stage.

---

## 5. iNterpret

### Analysis classification

The analysis is classified as:

**Primarily descriptive with diagnostic elements**

### Descriptive components

The analysis describes:

- complaint volumes;
- complaint distribution by agency;
- complaint distribution by problem type;
- resolution-time distributions;
- agency-level median resolution times;
- problem-level median resolution times;
- resolution-duration bands;
- Closed Date completeness.

These analyses primarily answer questions about what occurred in the January 2025 dataset.

### Diagnostic elements

The analysis also investigates:

- where resolution-time differences occur;
- how complaint composition differs between agencies;
- where Status and Closed Date disagree;
- where tracking completeness differs;
- which Agency × Problem segments have unusually short or long resolution durations.

These provide diagnostic elements because they help locate patterns and inconsistencies requiring further investigation.

### Why the analysis is not classified as fully diagnostic

The analysis identifies where differences and inconsistencies occur but does not establish their underlying causes.

For example, a long resolution duration may potentially relate to:

- complaint complexity;
- agency workflow;
- operational priorities;
- staffing or workload;
- geographic conditions;
- reporting practices;
- administrative closure procedures;
- other variables not examined in the current analysis.

The current evidence therefore should not be used to claim causal explanations.

### Why the analysis is not predictive

No model is used to predict future complaint outcomes.

The analysis does not predict:

- whether a future complaint will be resolved;
- how long a future complaint will take;
- whether an agency will miss a target;
- future complaint volume.

### Why the analysis is not prescriptive

The analysis does not calculate an optimal operational decision or automatically recommend resource allocation.

It provides evidence that can support further investigation and decision-making rather than prescribing a mathematically optimal action.

---

## 5.1 Actionable Findings

### Compare similar workloads

Agency-wide median resolution times should not be used alone to rank agencies.

The analysis shows that agencies handle substantially different complaint categories and that complaint types themselves have very different resolution durations.

Monitoring resolution time within comparable Agency × Problem segments provides more context than an overall agency median alone.

### Investigate long-duration segments

Segments with unusually high median resolution durations can be prioritized for further operational investigation.

Examples include:

- DPR / New Tree Request
- EDC / Noise - Helicopter
- TLC / For Hire Vehicle Complaint
- TLC / Taxi Complaint
- DHS / Encampment

The analysis identifies these as long-duration segments but does not establish the reason for their duration.

### Improve tracking consistency

The identified Status/Closed Date conflicts indicate that complaint tracking should not rely on either field without validation.

Relevant inconsistencies include:

- 1,025 Closed records without a usable Closed Date
- 302 non-Closed records containing a usable Closed Date

These records could be investigated when producing operational metrics based on complaint closure.

### Use percentages alongside counts

Agency complaint volumes differ substantially.

Raw counts are useful for understanding workload, but percentages provide additional context when comparing the composition of agencies with very different sample sizes.

### Use robust summary statistics

Resolution times are strongly right-skewed.

Median resolution time is therefore useful alongside the mean because extreme long-duration records substantially increase the arithmetic mean.

---

## 5.2 Limitations

### Limited time period

The analysis uses a January 2025 extract.

Patterns observed during this month may not represent:

- other months;
- seasonal changes;
- annual performance;
- longer-term trends.

### Different agency responsibilities

Agencies handle different complaint types and operational responsibilities.

Direct agency comparisons therefore do not represent controlled comparisons of equivalent work.

### Resolution time is not complete service quality

A short recorded resolution duration does not necessarily indicate better service.

The dataset does not establish factors such as:

- quality of the resolution;
- customer satisfaction;
- whether the underlying issue permanently disappeared;
- resource requirements;
- complaint complexity.

### Tracking inconsistencies

Status and Closed Date contain conflicting records.

This creates uncertainty when determining whether some complaints should be considered resolved.

### Researcher-defined resolution bands

The 4-, 24-, 72-, and 168-hour thresholds are analytical categories selected for interpretability.

They are not treated as official NYC 311 performance standards.

### Statistical significance and practical significance

The dataset contains very large groups.

A highly significant statistical result does not automatically mean that every observed difference is operationally important.

Median durations, distributions, sample sizes, complaint composition, and practical context must also be considered.

### Kruskal-Wallis limitations

The Kruskal-Wallis test indicates that at least one selected agency's resolution-time distribution differs from the others.

It does not identify which specific groups differ and does not establish causation.

### Observational data

The analysis is based on observational administrative records.

No experimental controls or random assignment exist, so causal conclusions about agency behavior cannot be made.

### Data-quality treatment

Some ambiguous values were deliberately retained because there was insufficient evidence for safe automatic correction.

This conservative approach reduces the risk of altering legitimate source data but means some unresolved source-data issues remain.

---

## 5.3 Progression to Higher Analysis Types

### Current level

**Primarily descriptive with diagnostic elements**

The current project measures what happened and identifies where notable patterns and inconsistencies occur.

### To become more fully diagnostic

Further analysis would need to investigate explanatory variables that may account for resolution-time differences.

Potential factors for investigation could include:

- complaint type;
- location;
- workload;
- time of day;
- day of week;
- complaint complexity;
- agency-specific workflow;
- seasonal conditions.

Additional evidence would be required before claiming that these factors cause resolution differences.

### To become predictive

A predictive version of the project would require a clearly defined future outcome.

Possible outcomes could include:

- predicted resolution duration;
- probability that resolution exceeds a defined duration;
- probability that a complaint remains unresolved after a defined period.

A predictive model would require appropriate feature preparation, train/test separation, evaluation metrics, leakage controls, and validation on unseen data.

### To become prescriptive

A prescriptive system would go beyond prediction and recommend actions.

For example, it could potentially combine predictions with operational constraints such as:

- staffing;
- available resources;
- complaint priority;
- service targets;
- workload.

The current project does not perform this optimization.

---

## 6. OSEMN Status

| Stage | Technical Status | Main Evidence |
|---|---|---|
| Obtain | Complete | `DATA_SOURCE.md`, raw ZIP, SHA-256 checksum |
| Scrub | Complete | data-quality audit, verification, change log |
| Explore | Complete | Explore script, CSV evidence, three figures |
| Model | Complete | segmentation, resolution bands, Kruskal-Wallis, saved evidence |
| iNterpret | Complete | findings, limitations, analysis classification and progression |

Task 3 OSEMN technical analysis is therefore complete, subject to a final requirement audit and repository/reproducibility checks.

---

## 7. Important Interpretation Rules

The following rules should be preserved when using these results:

1. Do not rank agencies as best or worst using overall resolution time alone.
2. Do not interpret a missing Closed Date automatically as proof that a complaint was unresolved.
3. Do not treat `Status` and `Closed Date` as perfectly interchangeable.
4. Do not describe the researcher-defined resolution bands as official NYC 311 standards.
5. Do not report the Kruskal-Wallis p-value as a literal mathematical zero.
6. Do not interpret statistical significance as proof of practical importance.
7. Do not claim that agency membership caused resolution-time differences.
8. Keep the 96 negative-duration records documented as data-quality inconsistencies rather than silently deleting them from the source dataset.
9. Distinguish analytical filtering from modification of the immutable raw dataset.
10. Interpret agency results together with complaint-type composition and sample size.

---

## 8. Task 3 Reproducibility Evidence

Main scripts:

- `notebooks/task3_exploratory_analysis.py`
- `notebooks/task3_model.py`

Explore outputs:

- `results/task3_explore_summary.csv`
- `results/task3_agency_resolution_summary.csv`
- `results/task3_problem_resolution_summary.csv`
- `results/task3_tracking_consistency.txt`
- `results/task3_top_15_complaint_types.png`
- `results/task3_median_resolution_by_agency.png`
- `results/task3_closed_date_completeness_by_agency.png`

Model outputs:

- `results/task3_model_segments.csv`
- `results/task3_resolution_bands_by_agency.csv`
- `results/task3_resolution_band_percentages_by_agency.csv`
- `results/task3_resolution_bands_by_problem.csv`
- `results/task3_resolution_band_percentages_by_problem.csv`
- `results/task3_kruskal_wallis.txt`

Data-quality evidence:

- `results/data_quality_audit.md`
- `results/full_dataset_verification.md`
- `results/data_quality_change_log.json`

Additional dependency introduced for the statistical analysis:

`scipy==1.18.1`

This version should remain pinned in `requirements.txt`.