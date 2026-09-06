# DataInspector — Decision Notes

## Purpose

DataInspector is responsible only for describing the structure and basic information of the NYC 311 dataset.

Its responsibility is to answer:

"What does the dataset look like?"

It does not decide whether the data is correct or incorrect and does not perform any cleaning or treatment.

---

## 1. Inherit from NYC311DataProcessor

Decision:
DataInspector inherits from NYC311DataProcessor.

Why:
DataInspector is one type of NYC 311 data processor, so it should follow the common structure defined by the parent class.

This also allows it to reuse the dataset handling provided by the parent rather than implementing the same behavior again.

Status:
Active.

---

## 2. Reuse the Parent Constructor

Decision:
The DataInspector constructor passes the supplied DataFrame to the parent constructor.

Why:
Dataset validation and storage are already responsibilities of NYC311DataProcessor.

DataInspector therefore does not need to duplicate this behavior or maintain a second copy of the dataset as its own attribute.

Status:
Active.

---

## 3. No Additional Private Attributes

Decision:
DataInspector currently has no additional private attributes.

Why:
Its responsibility is simply to inspect the supplied dataset and return descriptive information.

There is currently no additional state that needs to be stored specifically by DataInspector.

Status:
Active.

---

## 4. Access Dataset Through get_dataset()

Decision:
DataInspector obtains the dataset using the inherited get_dataset() method.

Why:
The original dataset is stored privately by NYC311DataProcessor.

Using the inherited accessor keeps DataInspector within the controlled interface established by the parent class rather than attempting to access the private attribute directly.

Note:
Because get_dataset() returns a copy, inspection is performed on a copy of the stored DataFrame.

Status:
Active.

---

## 5. Override process_data()

Decision:
DataInspector provides its own implementation of process_data().

Why:
The parent class defines process_data() as the common abstract processing operation.

DataInspector therefore implements that operation specifically for dataset inspection.

This is one of the subclass implementations that demonstrates method overriding and contributes to polymorphic behavior across the processors.

Status:
Active.

---

## 6. Keep DataInspector Descriptive

Decision:
DataInspector reports dataset characteristics without deciding whether those characteristics represent data-quality problems.

Why:
The project separates dataset inspection from data-quality management.

DataInspector answers:

"What does the dataset look like?"

DataQualityManager will later answer:

"What data-quality problems exist and what should be done about them?"

Keeping these responsibilities separate prevents unnecessary overlap between the two classes.

Status:
Active.

---

## 7. Information Returned by process_data()

Decision:
The current inspection includes:

- number of rows;
- number of columns;
- column names;
- data types; and
- missing-value counts.

Why:
These provide a basic structural overview of the DataFrame without performing analysis or making data-quality judgments.

Status:
Active.

---

## 8. Report Missing Values Without Treating Them

Decision:
DataInspector counts missing values for each column but does not clean, replace, remove, or classify them.

Why:
A missing-value count is descriptive information about the dataset.

Whether a missing value is expected, problematic, or requires treatment depends on the meaning of the field and belongs to DataQualityManager.

Status:
Active.

---

## 9. Return Results as a Dictionary

Decision:
process_data() returns its inspection results in a dictionary.

Why:
This follows the process_data() -> dict contract established by NYC311DataProcessor.

Named dictionary keys also make each returned result identifiable while allowing the other subclasses to return different information through the same general return type.

Status:
Active.

---

## 10. Convert pandas Results to Simple Structures

Decision:
Column names are returned as a list, while data types and missing-value counts are converted to dictionaries.

Why:
This produces clearly structured results rather than returning pandas Index or Series objects for these values.

Note:
This is useful implementation behavior, but it is not currently being treated as the coursework's required major data-structure justification. A stronger list/set/dict/tuple decision should be identified where the choice materially affects correctness or performance.

Status:
Active.

---

## Current Responsibility Boundary

DataInspector:
- describes dataset structure;
- reports basic information;
- reports missing-value counts;
- does not modify data;
- does not classify values as valid or invalid;
- does not perform cleaning.

DataQualityManager:
- identifies actual data-quality problems;
- determines which problems require treatment;
- applies justified treatments;
- records changes.

This boundary should be maintained as the project develops.

---

## Current Implementation Status

DataInspector currently:

- inherits from NYC311DataProcessor;
- reuses the parent constructor;
- has no additional private attributes;
- accesses the dataset through get_dataset();
- overrides process_data();
- returns a dictionary containing structural information; and
- performs no data modification.

The implementation has been reviewed structurally but still needs to be executed and tested before it should be considered fully verified.

---

## Future Changes

If an important design decision changes later, do not remove the original reasoning.

Record:

- what changed;
- why it changed;
- what problem or evidence caused the change;
- the new decision; and
- any new trade-off introduced.

This will preserve the development history for later review and viva preparation.

The current implementation has been executed using a small test DataFrame and the DataInspector unit test passed successfully.