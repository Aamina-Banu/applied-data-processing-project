# NYC311DataProcessor — Decision Notes

## Purpose

NYC311DataProcessor is the abstract parent class for the NYC 311 data processors. It stores the common dataset and defines the common processing interface that subclasses must follow.

---

## 1. Abstract Base Class

Decision:
Use NYC311DataProcessor as an abstract base class using ABC.

Why:
The different processors work with the same type of dataset but have different responsibilities. A common parent provides shared structure while allowing each subclass to implement its own processing behavior.

Trade-off:
This adds some class structure, but avoids repeating common behavior across the subclasses.

Status:
Active.

---

## 2. Private Dataset Attribute

Decision:
Store the supplied DataFrame in __dataset.

Why:
The dataset is internal state and should not normally be accessed or replaced directly from outside the class. This supports encapsulation.

Note:
The double underscore uses Python name mangling. It discourages direct access rather than providing absolute privacy.

Status:
Active.

---

## 3. Controlled Dataset Access

Decision:
Provide get_dataset() for subclasses and other permitted code to access the stored dataset.

Why:
Subclasses need the dataset for their processing, but an accessor provides a controlled interface instead of exposing __dataset directly.

Status:
Active.

---

## 4. Return a Copy of the Dataset

Decision:
get_dataset() returns self.__dataset.copy() instead of the original stored DataFrame.

Why:
This prevents code using get_dataset() from accidentally modifying the DataFrame stored inside the parent object.

Trade-off:
Creating a copy requires additional memory and processing time, especially with a large dataset.

Status:
Active.

---

## 5. Dataset Type Validation

Decision:
Check that the supplied dataset is a pandas DataFrame before storing it.

Why:
The processors are designed to operate on pandas DataFrames. Accepting another object type could cause unclear failures later during processing.

Status:
Active.

---

## 6. TypeError for Incorrect Dataset Type

Decision:
Raise TypeError when the supplied dataset is not a pandas DataFrame.

Why:
The problem is the type of object supplied, so TypeError describes the failure clearly.

Note:
The coursework also requires ValueError. An appropriate value-related case still needs to be identified elsewhere rather than using ValueError here only to satisfy the requirement.

Status:
Active.

---

## 7. Abstract process_data()

Decision:
Define process_data() as an abstract method.

Why:
Every concrete processor must perform processing, but the actual processing is different for each subclass. Making the method abstract requires subclasses to provide their own implementation.

Status:
Active.

---

## 8. Dictionary Return Contract

Decision:
Define process_data() with a dictionary return type.

Why:
All processors can return results through the same general type while still using different keys and values for their specific responsibilities.

Trade-off:
Because the contents can differ between subclasses, each subclass needs to make its returned results clear.

Status:
Active.

---

## Current Implementation

NYC311DataProcessor currently provides:

- DataFrame input validation
- private dataset storage
- controlled dataset access
- protection against accidental modification through DataFrame copying
- an abstract process_data() interface

No dataset-specific analysis or cleaning logic belongs in this parent class.

---

## Future Changes

If any of these decisions change during implementation, keep the original decision and record:

- what changed;
- why it changed;
- what evidence or problem caused the change; and
- the new trade-off introduced by the change.

This keeps a record of how the design developed during the project.