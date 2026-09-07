# NYC311DataProcessor — Decision Notes

## Purpose

NYC311DataProcessor is the common parent class for processors that work with the NYC 311 dataset.

It provides the shared structure that all processors follow while allowing each subclass to perform its own type of processing.

---

## 1. Use an Abstract Base Class

Decision:
NYC311DataProcessor is implemented as an abstract base class using Python's ABC class.

Why:
The class represents the general concept of processing NYC 311 data, but it does not have one specific processing responsibility itself.

The actual processing belongs to the subclasses.

Using an abstract parent also provides a common structure for DataInspector, ComplaintEffectivenessAnalyzer, and DataQualityManager.

Status:
Active.

---

## 2. Define process_data() as an Abstract Method

Decision:
process_data() is declared using @abstractmethod.

Why:
Every processor must provide its own implementation of process_data() according to its responsibility.

For example:

- DataInspector uses it to describe the dataset.
- ComplaintEffectivenessAnalyzer uses it to analyze complaint handling.
- DataQualityManager uses it for data-quality processing.

This provides a shared interface while allowing different behavior in each subclass.

Status:
Active.

---

## 3. Use a Dictionary as the Common Return Type

Decision:
The abstract method has the following return type:

process_data() -> dict

Why:
The processors return several related results rather than a single value.

A dictionary allows each result to have a meaningful key and gives all subclasses a common return structure while still allowing them to return different types of processing results.

Status:
Active.

---

## 4. Store the Dataset in the Parent Class

Decision:
The dataset is stored by NYC311DataProcessor rather than separately by every subclass.

Why:
All processors require access to the same type of input data.

Keeping this responsibility in the parent avoids repeating the same dataset-storage logic in each subclass.

Status:
Active.

---

## 5. Make the Dataset Private

Decision:
The dataset is stored in:

__dataset

Why:
The dataset is part of the internal state of the processor and should not be directly modified from outside the class.

Using a private attribute supports encapsulation and makes access to the stored dataset controlled by the parent class.

Status:
Active.

---

## 6. Provide Controlled Dataset Access

Decision:
A public method is provided:

get_dataset() -> DataFrame

Why:
Subclasses need to access the dataset, but the __dataset attribute is private.

The accessor provides a controlled way for subclasses to obtain the data without directly accessing the private attribute.

Status:
Active.

---

## 7. Return a Copy from get_dataset()

Decision:
get_dataset() returns:

self.__dataset.copy()

rather than returning the original DataFrame object.

Why:
Returning the original DataFrame would allow code receiving it to modify the same object stored internally by the processor.

Returning a copy provides additional protection for the internal dataset and supports the decision to keep the stored data encapsulated.

Trade-off:
Creating a copy requires additional memory and processing time, especially for a large dataset.

The current design prioritizes protection of the stored dataset over this additional cost.

Status:
Active.

---

## 8. Validate the Dataset Type in the Constructor

Decision:
The constructor checks whether the supplied dataset is a pandas DataFrame.

Why:
The processors depend on DataFrame operations.

Allowing an incompatible object to be stored could cause less clear errors later during processing.

Checking the input at the point where the object is created makes the expected input type explicit.

Status:
Active.

---

## 9. Use TypeError for an Incorrect Dataset Type

Decision:
If dataset is not a pandas DataFrame, the constructor raises TypeError.

Why:
The problem in this situation is the type of object supplied rather than the value contained in a valid DataFrame.

For example, passing a string or list where a DataFrame is required is a type error.

ValueError is used where an input has the expected general type but is missing required information, such as required DataFrame columns.

Status:
Active.

---

## 10. Let Subclasses Reuse the Parent Constructor

Decision:
Subclasses call:

super().__init__(dataset)

Why:
Dataset validation and storage are responsibilities already handled by NYC311DataProcessor.

Reusing the parent constructor avoids duplicating these operations in every subclass.

Status:
Active.

---

## 11. Keep the Parent Class Focused on Shared Behavior

Decision:
NYC311DataProcessor does not contain complaint-analysis or data-cleaning logic.

Why:
Only behavior genuinely shared by the processors should belong in the parent.

Specific responsibilities remain in the appropriate subclasses.

This keeps the boundary between the parent and its subclasses clear.

Status:
Active.

---

## 12. OOP Concepts Supported by This Design

The parent class contributes to several object-oriented concepts used in the project:

### Abstraction
NYC311DataProcessor defines the general processing concept without implementing a specific analysis.

### Encapsulation
The dataset is stored privately and accessed through get_dataset().

### Inheritance
DataInspector, ComplaintEffectivenessAnalyzer, and DataQualityManager inherit the common behavior.

### Polymorphism
Each subclass provides its own implementation of process_data() while following the same interface.

Status:
Active.

---

## Current Implementation Status

NYC311DataProcessor currently:

- inherits from ABC;
- accepts a pandas DataFrame through its constructor;
- validates the dataset type;
- raises TypeError for an incorrect dataset type;
- stores the dataset in the private __dataset attribute;
- provides controlled access through get_dataset();
- returns a copy of the stored DataFrame;
- defines process_data() as an abstract method; and
- establishes dict as the common process_data() return contract.

The parent class is currently being used by all three implemented subclasses:

- DataInspector;
- ComplaintEffectivenessAnalyzer; and
- DataQualityManager.

All three subclasses are currently exercised through the project's unit test suite.

The current test suite reports:

16 passed.

---

## Future Work

The required custom exception handling and try/except/else/finally structure are implemented and covered by the current tests.

If an important parent-class design decision changes later, record:

- the original decision;
- what changed;
- why it changed; and
- any trade-off introduced by the change.