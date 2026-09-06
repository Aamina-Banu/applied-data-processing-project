DataQualityManager — Decision Notes

Purpose

DataQualityManager is responsible for identifying confirmed data-quality problems in the NYC 311 dataset and applying explicit treatments where a safe and justified rule exists.

The class is separate from DataInspector because DataInspector only describes the structure and basic characteristics of the dataset, while DataQualityManager judges whether certain values are problematic and applies treatments when appropriate.

1. Inherit from NYC311DataProcessor

Decision:
DataQualityManager inherits from NYC311DataProcessor.

Why:
It is one type of NYC 311 data processor and should follow the common interface defined by the abstract parent class.

The parent handles dataset validation and storage, so this logic does not need to be repeated.

Status:
Active.

2. Use a Private Change Log

Decision:
The class stores treatment history in:

__change_log

Why:
Every treatment applied to the data should be traceable.

The change log provides evidence of what treatment was performed, which fields were affected, how many rows were changed, why the change was made, whether the treatment succeeded or failed, and when it happened.

Status:
Active.

3. Return a Copy of the Change Log

Decision:
get_change_log() returns a copy of __change_log rather than the original list.

Why:
Returning the original list would allow external code to directly modify the internal treatment history.

Returning a copy supports encapsulation and follows the same principle used by NYC311DataProcessor.get_dataset().

Status:
Active.

4. Separate Quality Reporting from Treatment

Decision:
process_data() reports identified data-quality issues but does not automatically call every cleaning method.

Why:
Automatically applying all treatments would hide the distinction between identifying a problem and deciding how to treat it.

This class therefore keeps assessment and treatment as separate operations.

Status:
Active.

5. Validate Required Columns

Decision:
process_data() checks for the columns required for the current quality checks:

BBL

Incident Zip

Created Date

Closed Date

Why:
The method depends on these fields.

If one is missing, continuing would produce incomplete or misleading quality results.

A ValueError is therefore raised for missing required columns.

Status:
Active.

6. Use TypeError for Non-DataFrame Input

Decision:
Treatment methods raise TypeError when the supplied data argument is not a pandas DataFrame.

Why:
The problem is the type of object supplied rather than the value inside a valid DataFrame.

This is consistent with the validation already used by NYC311DataProcessor.

Status:
Active.

7. Use ValueError for Missing Required Fields

Decision:
Treatment methods raise ValueError when the supplied DataFrame does not contain the field required by that treatment.

Examples:

replace_invalid_bbl() requires BBL;

handle_invalid_zip() requires Incident Zip;

handle_date_inconsistencies() requires Created Date and Closed Date.

Why:
The input is still a valid DataFrame, but it does not contain the values required for the requested operation.

Status:
Active.

8. Return New DataFrames Instead of Modifying in Place

Decision:
Each treatment method creates and returns a copy of the supplied DataFrame.

Why:
The lecturer specifically required treatment methods to return a new DataFrame rather than modifying the original data in place.

This also makes treatment chaining clearer and protects the input dataset from unintended changes.

Status:
Active.

9. BBL Value 0 Is Treated as Invalid

Decision:
BBL values equal to 0 are replaced with a missing value.

Why:
The audit identified 89 records where BBL was 0.

A valid BBL cannot be safely inferred from this value, so the treatment marks it as unavailable instead of inventing a replacement.

Status:
Active.

10. Incident Zip Value 83 Is Treated as Invalid

Decision:
Incident Zip value 83 is replaced with a missing value.

Why:
This value was identified as a clearly invalid ZIP representation in the January 2025 extract.

The correct ZIP cannot be safely inferred, so the value is marked as missing rather than replaced with an invented code.

Status:
Active.

11. ZIP Values 7105 and 7307 Are Left Unchanged

Decision:
The values 7105 and 7307 are not automatically modified.

Why:
They may represent ZIP codes with lost leading zeros, but there is not enough evidence to safely transform them inside the current treatment method.

They are therefore treated as ambiguous rather than clearly invalid.

Status:
Active.

12. Negative Date Differences Are Treated Explicitly

Decision:
Where Closed Date occurs before Created Date, Closed Date is replaced with a missing value.

Why:
A negative complaint-resolution duration is not meaningful.

The correct closing date is unknown, so the method does not swap the two dates or invent a replacement.

The row itself is preserved.

Status:
Active.

13. Do Not Automatically Correct Status and Closed Date Conflicts

Decision:
Records where:

Status is Closed but Closed Date is missing; or

Status is non-Closed but Closed Date is present

are not automatically changed by DataQualityManager.

Why:
These combinations are inconsistent, but the correct state of the record cannot be confidently inferred.

They are therefore reported by the complaint analyzer rather than silently corrected.

Status:
Active.

14. Do Not Automatically Treat Resolution Action Updated Date Issues

Decision:
Records where Resolution Action Updated Date occurs before Created Date are not automatically modified.

Why:
The audit showed that these cases occur frequently and may reflect systematic source-system behavior.

Without stronger evidence, changing them could remove valid source information.

Status:
Active.

15. Encoding Problems Are Detected Using Known Mojibake Markers

Decision:
The current quality-reporting logic looks for characters commonly associated with mojibake, including:

Ã

Â

â

ð

Why:
The January 2025 dataset audit identified visible encoding corruption in text fields.

These markers provide a reproducible way of identifying likely affected values.

Status:
Active.

16. Encoding Correction Uses a Reproducible Conversion Rule

Decision:
correct_encoding() attempts a Latin-1 to UTF-8 conversion only for text values containing the selected encoding markers.

Why:
The method should not transform every text value.

Restricting the conversion to likely affected values reduces the risk of changing valid text unnecessarily.

If the conversion cannot be performed safely, the value is left unchanged.

Status:
Active.

17. Count Unique Affected Rows for Encoding Treatments

Decision:
correct_encoding() stores affected row indexes in a set and records the number of unique affected rows.

Why:
A single row may contain encoding problems in more than one text column.

Counting changed cells would not match the change-log field name rows_affected.

Using a set ensures each affected row is counted once.

Status:
Active.

18. Use a Consistent Change-Log Structure

Decision:
Treatment methods add a dictionary to __change_log containing:

treatment

fields

rows_affected

description

outcome

timestamp

For BBL, ZIP, and date treatments, the outcome field records either "success" or "failed".

correct_encoding() records "success" after completing its tolerant per-value conversion process.

Why:
A consistent structure makes the treatment history easier to inspect and use later for reproducibility and reporting.

Recording the outcome also makes failed treatment attempts traceable rather than only recording successful operations.

Status:
Active.

19. Preserve Ambiguous Values Rather Than Guess

Decision:
Where the correct replacement cannot be confidently determined, the implementation either leaves the value unchanged or marks a clearly invalid value as missing.

Why:
The project should not invent data.

This helps avoid introducing unsupported corrections into the dataset.

Status:
Active.

20. Use NYC311DataQualityError for Post-Treatment Integrity Failures

Decision:
NYC311DataQualityError is used when a treatment passes the initial input checks but fails a post-treatment integrity check.

It is currently used by:

replace_invalid_bbl();

handle_invalid_zip(); and

handle_date_inconsistencies().

Why:
TypeError and ValueError are still used for invalid input type and missing required fields.

The custom exception is reserved for a different situation: the input is valid enough for the treatment to run, but the treatment does not satisfy its expected post-treatment conditions.

Examples include:

row count changing unexpectedly;

a required treatment column disappearing; or

the invalid values remaining after the treatment should have removed them.

Status:
Active.

21. Post-Treatment Integrity Checks

Decision:
BBL, ZIP, and date treatment methods perform defensive integrity checks after applying their treatment rule.

For replace_invalid_bbl():

row count must remain unchanged;

BBL must still exist;

no BBL value equal to 0 may remain.

For handle_invalid_zip():

row count must remain unchanged;

Incident Zip must still exist;

no clearly invalid ZIP value 83 may remain.

For handle_date_inconsistencies():

row count must remain unchanged;

Created Date and Closed Date must still exist;

no remaining valid date pair may have Closed Date earlier than Created Date.

Why:
These checks verify that the treatment actually completed the intended operation without changing the structure of the dataset unexpectedly.

If a check fails, NYC311DataQualityError is raised.

Status:
Active.

22. Use try/except/else/finally for Treatment Failure Safety

Decision:
BBL, ZIP, and date treatment methods use try/except/else/finally around the treatment and post-treatment verification.

Why:
The structure gives each block a clear purpose:

try applies the treatment and checks the result;

except records the domain-specific failure and re-raises NYC311DataQualityError;

else marks the treatment outcome as successful when no domain exception occurs;

finally records the treatment attempt in the change log whether it succeeded or failed.

This means failed treatment attempts are still traceable.

Status:
Active.

23. Encoding Uses Tolerant Per-Value Exception Handling

Decision:
correct_encoding() uses try/except around individual Latin-1 to UTF-8 conversion attempts.

Why:
Some values containing a suspected encoding marker may still be unsuitable for the attempted conversion.

UnicodeEncodeError and UnicodeDecodeError are therefore handled so that one unsuitable value does not cause the complete encoding treatment to fail.

Such values are left unchanged and processing continues.

This behavior is intentionally different from the whole-treatment post-condition checks used for BBL, ZIP, and date treatments.

Status:
Active.

24. Unit Testing Strategy

Decision:
DataQualityManager is tested using small synthetic DataFrames.

The tests currently cover:

reporting identified quality issues;

replacing invalid BBL values;

handling the clearly invalid ZIP value;

recording change-log entries;

preserving the original DataFrame;

correcting an encoding example;

handling a negative date difference;

raising ValueError for a missing required field;

raising TypeError for a non-DataFrame input;

successful date-treatment logging;

NYC311DataQualityError when the date treatment fails its post-treatment check;

NYC311DataQualityError when the BBL treatment fails its post-treatment check; and

NYC311DataQualityError when the ZIP treatment fails its post-treatment check.

Why:
Small controlled DataFrames make it easier to verify specific behavior without depending on the full dataset.

The failure-path tests deliberately simulate treatment failure so that defensive integrity checks can be verified even though those failures should not normally occur during valid operation.

Status:
Active.

25. Current Test Status

The complete project test suite currently reports:

14 passed

This includes the DataInspector, ComplaintEffectivenessAnalyzer, and DataQualityManager tests.

The coursework requirement of at least five unit tests is therefore exceeded.

The current suite includes multiple exception assertions, including:

ValueError for missing required fields;

TypeError for non-DataFrame input;

ValueError for missing required ComplaintEffectivenessAnalyzer input; and

NYC311DataQualityError failure-path assertions for date, BBL, and ZIP treatments.

Status:
Active.

Current Implementation Status

DataQualityManager currently:

inherits from NYC311DataProcessor;

keeps a private change log;

returns a copy of the change log;

reports confirmed quality issues;

validates required columns;

returns new DataFrames from treatment methods;

replaces BBL value 0 with missing;

replaces ZIP value 83 with missing;

leaves ambiguous ZIP values unchanged;

identifies and treats negative Closed Date differences;

detects likely encoding corruption;

performs a controlled encoding correction;

logs treatment attempts with an outcome field;

preserves the supplied DataFrame;

uses TypeError and ValueError for relevant validation failures;

raises NYC311DataQualityError for post-treatment integrity failures;

uses try/except/else/finally for BBL, ZIP, and date treatment failure handling; and

keeps encoding conversion tolerant of individual Unicode conversion failures.

The current complete project test suite reports:

14 passed

The exception-handling implementation is now present and verified through the current synthetic unit-test suite.

This does not yet mean the complete Task 1 is finished because final verification against the full January 2025 dataset and the remaining Task 1 project-level checks are still pending.

Future Work

The treatment methods should be verified against the full January 2025 dataset before final Task 1 verification.

The final Task 1 review should also confirm that the package interface, documentation, tests, data-structure justification, and reproducibility evidence remain consistent with the implemented behavior.

If a treatment rule changes later, record:

the original rule;

the new rule;

why it changed;

the evidence supporting the change; and

any trade-off introduced.