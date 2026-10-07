# Task 5 Professional Practice Evidence

This document records technical evidence supporting Task 5 professional practice requirements. It is supporting repository documentation rather than final report prose.

## Version Control

Git was used throughout the project to record development across project setup, dataset provenance, object-oriented implementation, data-quality processing, storage-format investigation, OSEMN analysis, PySpark scaling, testing, documentation, and final reproducibility improvements.

Important points in the development history include:

| Evidence | Commit / branch |
|---|---|
| Initial project setup | `749a48f`, 2 September 2026 |
| Storage feature development | `feature/storage-benchmarking`, `7785b10` |
| Storage feature merge | `33eafbc`, 7 September 2026 |
| OSEMN analysis completion | `91a28b0`, 12 September 2026 |
| Spark scaling feature | `feature/spark-scaling`, `a64ad7f` |
| Spark feature merge | `3636e8c`, 12 September 2026 |
| Data ownership and quality error-handling improvements | `1582f9f` |
| Final analysis pipeline and reproducibility improvements | `e68e051`, 7 October 2026 |

The feature-development history demonstrates the use of branches and merge commits rather than carrying out all development directly on `main`.

The final repository state was pushed successfully to the remote `main` branch on 7 October 2026. After the push:

```text
HEAD -> main
origin/main -> e68e051