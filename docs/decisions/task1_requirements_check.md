# Task 1 implementation and report evidence

Checked against the supplied NIB7143CEM assignment brief on 22 October 2026.

| Requirement | Evidence |
|---|---|
| Importable package with public interface | `src/nyc311/__init__.py` exports the base class, three concrete processors and custom exception. |
| At least three related classes | Three concrete processors inherit from `NYC311DataProcessor`. |
| Encapsulation | Constructor/accessor DataFrame copies; name-mangled dataset and history; deep-copy history accessor. |
| Inheritance and overriding/shared interface | Abstract `process_data()` overridden by all three concrete processors. |
| Informative ValueError | Missing required columns are rejected by schema-dependent operations. |
| Custom domain exception | BBL, ZIP and date post-treatment integrity checks raise `NYC311DataQualityError`. |
| try/except/else/finally | BBL, ZIP and date treatments use all four constructs; errors propagate and outcomes are logged. |
| Failure integrity | Copy-returning treatments; temporary-file log replacement; regression tests for failed treatments and persistence. |
| Validation and docstrings | DataFrame arguments checked at construction/treatment boundaries; required columns checked at use; string path checked on log save. Parameterless getters use validated internal state. Public classes and methods have docstrings. |
| At least five tests, including two exception assertions | Full current suite: 30 passing cases, including Task 4 provenance tests; processor tests include missing-column, wrong-type and domain-failure assertions. |
| Material data-structure choice | Encoding uses a set of row positions to deduplicate affected rows correctly even with duplicate index labels; ordered log entries use a list of dictionaries. |
| Class diagram | `docs/diagrams/class_diagram.svg` and PNG, generated from current class declarations. |
| Method listing and line-by-line commentary | `docs/decisions/task1_method_commentary.md`, ready to incorporate as Appendix A. |

The report must still explain why these choices suit the workload, refer
to the figure, and include the appendix in the submitted PDF. Repository
evidence does not automatically become report evidence. This check covers
Task 1, not a final audit of all coursework deliverables.

## Changes from this check

- Expanded public class docstrings with construction contracts, schema
  timing, copy ownership and exception semantics.
- Added the missing method-listing/commentary report artifact.
- Kept the custom exception constructor inherited: the uploaded styled
  image's `__init__(message: str)` declaration does not exist in the code.
- Regenerated code-derived diagrams. `abc.ABC` is shown as a parent class,
  private names retain their two underscores, and the custom exception
  declares no methods.
- No processing rules or analytical populations were changed.

Verification: `.venv/Scripts/python.exe -B -m pytest -q -p no:cacheprovider`
completed with **30 passed**.
