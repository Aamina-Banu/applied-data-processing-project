# Task 5 professional practice progress

Technical evidence note updated 12 September 2026; not final report prose. This update supersedes the earlier Task 2-era progress checklist; that record remains in Git history.

## Version control

The local repository has 19 reachable commits spanning 2-12 September 2026 and is not shallow. Messages cover setup, provenance, OOP development, quality logging, storage experiments, OSEMN analysis, and Spark scaling.

| Evidence | Commit / branch |
|---|---|
| Initial project setup | `749a48f`, 2 September |
| Storage feature | `feature/storage-benchmarking`, `7785b10` |
| Storage merge, two parents | `33eafbc`, 7 September |
| OSEMN completion | `91a28b0`, 12 September |
| Spark feature | `feature/spark-scaling`, `a64ad7f` |
| Spark merge, two parents | `3636e8c`, 12 September |

Both feature branches remain locally and in remote-tracking refs. At audit start, `main` and the local `origin/main` ref pointed to `3636e8c` and the working tree was clean. Remote-tracking refs are local evidence; live remote synchronization was not checked.

Capture final submission evidence with:

```powershell
git log --graph --oneline --decorate --all
git log --all --format="%h %ad %s" --date=iso-strict
git branch -a
```

The student still needs to choose a concise screenshot/log and explain the actual branching decision. No commit or push was performed during this audit.

## Dataset-specific data protection

[The GDPR technical assessment](task5_gdpr_assessment.md) records all seven requested principles and the actual 44-field schema. Classification: **B, potential personal/location-related data requiring caution**. Location and descriptive fields prevent an assumption of anonymity merely because the source is public.

The note distinguishes implemented practices from recommendations. The student retention position adopted on 7 October 2026 covers raw and full-data processed copies only for as long as needed for completion, verification, assessment, moderation and applicable appeals. Review/deletion is triggered by the end of the relevant assessment/moderation/appeal period; unnecessary local full-data copies, including backups under the student's control, should then be deleted. The GDPR note specifies the copies covered, including the scrubbed Parquet, and the conditions for retaining code, documentation and aggregate outputs. Deleting the final exact archive ends exact numerical reproduction. This is a project position, not an asserted institutional policy or a claim that deletion has occurred.

No institution-approved lawful basis is independently claimed or evidenced. Public availability does not automatically make GDPR inapplicable, and academic use alone does not establish a lawful basis. If GDPR applies, the relevant data controller/institution must confirm the appropriate basis; this remains an evidential limitation, not a legal exemption. Verified access/encryption controls and comprehensive free-text review also remain outstanding.

## Reproducibility

README contains setup, editable installation, tests, Task 1 verification, Task 2/3/4 command order, Java prerequisite, raw-data requirement, and evidence locations.

All ten entries in `requirements.txt` use exact version pins, including SciPy 1.18.1 and PySpark 4.2.0. Current installed main versions match the recorded environment; `pip check` reports no broken requirements. The build dependency `setuptools>=68` is not exactly pinned, transitive dependencies are not fully locked, and `pyproject.toml` has no runtime dependency declarations or Python-version constraint. Follow both installation steps in README.

Recorded environment: Python 3.14.0; Windows 64-bit build 26200; i7-13620H; 16 GB RAM; Java 21.0.7; Spark local[*], parallelism 16. Evidence: `results/storage_benchmark_environment.txt`, `results/task4_environment.txt`, and `requirements.txt`.

The current regression test suite contains 28 passing tests. A later verification run confirmed all 28 tests passed successfully.

Clean-checkout reproducibility remains **PARTIAL**. Raw and processed data are Git-ignored; the exact ZIP has no recorded immutable download route. The extract has non-midnight time boundaries. No fresh install or full Spark/benchmark rerun was performed in this audit; existing scripts overwrite protected evidence outputs.

## Current status

| Component | Status | Remaining action |
|---|---|---|
| Version-control implementation | PASS | Student selects final history evidence |
| Dataset-specific GDPR technical assessment | PASS | Student reviews evidence and outstanding safeguards |
| Operational data-protection safeguards | PARTIAL | Carry out the adopted retention review when due; resolve access safeguards and applicable institutional lawful-basis obligations |
| Reproduction instructions | PASS | Follow README, with original ZIP and Java |
| Clean-checkout reproduction verified | CANNOT VERIFY | Fresh environment and complete controlled rerun |
| Overall submission readiness | PARTIAL | Review technical issues and prepare submission |