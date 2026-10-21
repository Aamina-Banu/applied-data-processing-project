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

The repository state at that time was pushed successfully to the remote `main` branch on 7 October 2026. After the push:

```text
HEAD -> main
origin/main -> e68e051
```

## Task 4 verification update - 21 October 2026

The crossover now constructs each workload once and gives both engines the same temporary CSV. Both Task 4 scripts verify the raw ZIP checksum and extracted CSV provenance. Automated checks passed at all six sizes for request multiplicities, valid-row counts, group keys, counts, exact medians and tolerance-based means. The full current test suite passed: 30 tests, including two new input-provenance regression tests.

The crossover timing CSVs and chart were replaced with the successful 4 GB-driver-heap rerun. The new validation CSV and environment TXT record the checks and configuration. See `task4_scaling_investigation.md` for current results and limits. The earlier 7 October clean-checkout reproduction remains historical evidence; this revision was verified in the existing workspace, not through another fresh-clone reproduction.

These revision files are local working-tree changes at the time of this update; they have not been committed or pushed as part of this work. No new merge or remote publication is claimed.
