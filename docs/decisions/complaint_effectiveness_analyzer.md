# ComplaintEffectivenessAnalyzer — Decision Notes

## Purpose

ComplaintEffectivenessAnalyzer is responsible for examining how NYC 311 complaints are handled and resolved.

Its responsibility is to answer questions such as:

- How many complaints are recorded?
- What statuses do complaints have?
- How many complaints can be consistently classified as closed or non-closed?
- Are Status and Closed Date consistent?
- How long do valid closed complaints take to resolve?

The class performs analysis only. It does not clean or modify inconsistent records.

---

## 1. Inherit from NYC311DataProcessor

Decision:
ComplaintEffectivenessAnalyzer inherits from NYC311DataProcessor.

Why:
It is one type of NYC 311 data processor and should therefore follow the common processing structure established by the abstract parent class.

The dataset is validated and stored by the parent rather than duplicating that responsibility in this class.

Status:
Active.

---

## 2. Access the Dataset Through get_dataset()

Decision:
The analyzer obtains the dataset using the inherited get_dataset() method.

Why:
The dataset is privately stored by NYC311DataProcessor.

Using the controlled accessor maintains encapsulation and means the analyzer works with the copy returned by the parent rather than directly accessing the private dataset.

Status:
Active.

---

## 3. Override process_data()

Decision:
ComplaintEffectivenessAnalyzer provides its own implementation of process_data().

Why:
NYC311DataProcessor defines process_data() as the common abstract processing operation.

This subclass implements that operation specifically for complaint-handling effectiveness analysis.

Status:
Active.

---

## 4. Report Complaint Volume and Status Counts

Decision:
The analyzer reports the total number of complaints and the number of records belonging to each Status value.

Why:
Complaint volume and status distribution provide basic information needed before evaluating closure and resolution behavior.

Status:
Active.

---

## 5. Use Actual Status Values Found in the Dataset

Decision:
Status classification is based on the values observed in the January 2025 dataset rather than assuming possible status categories.

Observed values:

- Closed
- In Progress
- Open
- Assigned
- Pending
- Started
- Unspecified

The January 2025 extract contained:

- Closed: 335,732
- In Progress: 845
- Open: 425
- Assigned: 274
- Pending: 163
- Started: 76
- Unspecified: 36

Why:
Inspecting the actual values avoids inventing categories that may not exist in the dataset.

Status:
Active.

---

## 6. Define Closed and Non-Closed Status Groups

Decision:
"Closed" is treated as the closed-status category.

The following values are treated as non-closed statuses:

- Open
- In Progress
- Assigned
- Pending
- Started

"Unspecified" is kept separate.

Why:
Unspecified does not provide enough information to confidently classify the complaint as either closed or non-closed.

Status:
Active.

---

## 7. Consider Status and Closed Date Together

Decision:
Closed Date alone is not used to determine whether a complaint is closed.

Status and Closed Date are considered together.

Classification:

- Closed status + Closed Date present = valid closed
- Closed status + Closed Date missing = anomaly
- Non-closed status + Closed Date missing = valid non-closed
- Non-closed status + Closed Date present = anomaly
- Unspecified status = kept separate

Why:
The dataset contains cases where Status and Closed Date disagree.

Automatically using Closed Date alone could silently reclassify inconsistent records and hide data-quality problems.

Status:
Active.

---

## 8. Status and Closed Date Cross-Check

Decision:
The relationship between Status and Closed Date was checked before implementing the classification.

Observed results:

| Status | Closed Date Missing | Closed Date Present |
|---|---:|---:|
| Assigned | 189 | 85 |
| Closed | 1,025 | 334,707 |
| In Progress | 844 | 1 |
| Open | 344 | 81 |
| Pending | 67 | 96 |
| Started | 72 | 4 |
| Unspecified | 1 | 35 |

This identified:

- 334,707 records with Closed status and a present Closed Date;
- 1,025 Closed records with a missing Closed Date;
- 267 non-closed records with a present Closed Date;
- 36 Unspecified records.

Why:
These results confirmed that Status and Closed Date cannot safely be treated as interchangeable indicators.

Status:
Active.

---

## 9. Keep Inconsistent Records Visible

Decision:
Status/Closed Date conflicts are counted and reported separately rather than silently corrected or removed.

The analyzer currently reports:

- Closed status with missing Closed Date;
- non-closed status with present Closed Date; and
- Unspecified status.

Why:
The analyzer's responsibility is to describe complaint effectiveness, not repair data-quality problems.

Any justified treatment belongs to DataQualityManager.

Status:
Active.

---

## 10. Closure Rate Uses Consistently Classified Records

Decision:
The closure rate is calculated using:

Valid Closed / (Valid Closed + Valid Non-Closed) × 100

Why:
Records where Status and Closed Date conflict are excluded rather than silently forcing them into the closed or non-closed category.

Unspecified records are also excluded because their state is uncertain.

This means the metric represents the closure rate among consistently classified records rather than a raw closure percentage across every row.

Status:
Active.

---

## 11. Handle an Unavailable Closure Rate

Decision:
If there are no valid closed or valid non-closed records, closure_rate is returned as None.

Why:
A denominator of zero means there is not enough consistently classified data to calculate this metric.

This does not necessarily mean that the entire dataset is invalid, so the whole processing operation should not fail.

Status:
Active.

---

## 12. Parse Dates Without Crashing on Invalid Values

Decision:
Created Date and Closed Date are converted to datetime values using errors="coerce".

Why:
If a value cannot be interpreted as a date, it becomes a missing datetime value rather than immediately causing the complete analysis to fail.

This allows unsuitable date records to be excluded from resolution-time calculations.

Status:
Active.

---

## 13. Restrict Resolution-Time Calculations

Decision:
Resolution time is calculated only when:

- the record belongs to the valid-closed category;
- Created Date can be interpreted as a date; and
- Closed Date is equal to or later than Created Date.

Why:
Resolution time is meaningful only when the complaint has consistent closure information and a valid chronological date sequence.

Status:
Active.

---

## 14. Exclude Negative Resolution Times

Decision:
Records where Closed Date is earlier than Created Date are not included in average or median resolution time.

They are counted separately as invalid resolution-date records.

Why:
A negative resolution duration is not meaningful for complaint-resolution analysis and would distort the timing results.

The analyzer does not attempt to invent or replace the correct date.

Status:
Active.

---

## 15. Measure Resolution Time in Hours

Decision:
Resolution duration is converted from a timedelta into hours.

Why:
Complaints may be resolved within part of a day.

Using whole days would discard this detail, while hours preserve shorter resolution durations.

Status:
Active.

---

## 16. Report Both Average and Median Resolution Time

Decision:
The analyzer reports both average and median resolution time.

Why:
The average summarizes overall resolution duration, while the median provides a middle value that is less affected by unusually long resolution times.

Both are calculated only from eligible resolution records.

Status:
Active.

---

## 17. Handle Unavailable Resolution-Time Metrics

Decision:
If no records are eligible for resolution-time analysis:

- average_resolution_hours = None
- median_resolution_hours = None

Why:
The absence of eligible records means these metrics cannot be calculated, but it does not necessarily make the complete dataset invalid.

Status:
Active.

---

## 18. Do Not Perform Cleaning in the Analyzer

Decision:
ComplaintEffectivenessAnalyzer does not:

- replace missing Closed Dates;
- change Status values;
- swap incorrect dates;
- delete anomalous records;
- create artificial resolution dates.

Why:
These actions would mix analytical and data-quality-management responsibilities.

Potential treatments belong to DataQualityManager and must be explicitly justified and logged.

Status:
Active.

---

## 19. Validate Required Columns

Decision:
Before performing complaint-effectiveness analysis, process_data() checks that the following required columns are present:

- Status
- Created Date
- Closed Date

If one or more of these columns are missing, a ValueError is raised identifying the missing columns.

Why:
The analyzer directly depends on these fields.

Checking them before beginning the analysis provides a clear and informative failure instead of allowing a less understandable pandas error to occur later.

Status:
Active.

---

## 20. Current process_data() Output

The current implementation returns:

### Complaint Volume
- total_complaints
- status_counts

### Closure Classification
- valid_closed_count
- valid_non_closed_count
- closure_rate

### Status/Date Conflicts
- closed_missing_date_count
- non_closed_present_date_count
- unspecified_count

### Resolution Analysis
- resolution_record_count
- average_resolution_hours
- median_resolution_hours
- invalid_resolution_date_count

Status:
Active.

---

## 21. Unit Test Design

Decision:
A small synthetic DataFrame is used to test multiple complaint situations.

The test includes:

- a valid closed complaint;
- a valid non-closed complaint;
- Closed status with a missing Closed Date;
- non-closed status with a present Closed Date;
- a Closed Date earlier than Created Date; and
- an Unspecified complaint.

Why:
This checks the important classification branches without depending on the full 337,551-row dataset.

Status:
Active.

---

## 22. Closure Rate Test

Decision:
The unit test also checks the calculated closure rate.

In the current test data:

- valid closed = 2
- valid non-closed = 1

Therefore, the expected valid-record closure rate is approximately 66.67%.

Why:
Testing only the underlying counts would not directly verify that the closure-rate calculation itself behaves as intended.

Status:
Active.

---

## 23. Missing Required Column Test

Decision:
A separate unit test supplies a DataFrame that is missing the Closed Date column and verifies that process_data() raises ValueError.

Why:
This verifies that the analyzer rejects incomplete input through its own validation rather than failing later during processing.

Status:
Active.

---

## Current Implementation Status

ComplaintEffectivenessAnalyzer currently:

- inherits from NYC311DataProcessor;
- uses controlled dataset access;
- validates that Status, Created Date, and Closed Date are present;
- raises ValueError when a required column is missing;
- reports complaint volume and Status distribution;
- distinguishes valid closed and valid non-closed records;
- identifies Status/Closed Date conflicts;
- keeps Unspecified records separate;
- calculates a closure rate from consistently classified records;
- handles an unavailable closure rate;
- parses Created Date and Closed Date;
- excludes invalid chronological records from resolution-time calculations;
- reports average and median resolution time in hours;
- reports invalid resolution-date counts; and
- does not modify the source data.

The ComplaintEffectivenessAnalyzer implementation has been executed and verified through its unit tests, including the required-column validation test.

The current overall project test suite reports:

11 passed.

---

## Future Work

The core ComplaintEffectivenessAnalyzer behavior and its current input validation are implemented and covered by the existing tests.

Remaining Task 1 exception-handling work is being handled at the wider package/data-quality-management level, including the required custom domain exception and appropriate try/except/else/finally structure.

Final package-level and end-to-end verification will be completed before Task 1 is considered finished.

If an important design decision changes later, keep a record of:

- the original decision;
- what changed;
- why it changed;
- the evidence or problem that caused the change; and
- any trade-off introduced by the new approach.