# Full Dataset Verification — January 2025 NYC 311

## Dataset

The full January 2025 NYC 311 extract was used for verification.

- Rows: 337,551
- Columns: 44

## Quality Issues Before Treatment

The full-dataset run identified:

- Encoding issues: 8,606
- Invalid BBL values equal to 0: 89
- Invalid ZIP values equal to 83: 1
- Closed Date earlier than Created Date: 96

## Treatment Results

After applying the current DataQualityManager treatment methods:

- Invalid BBL values: 89 -> 0
- Invalid ZIP values: 1 -> 0
- Invalid resolution dates: 96 -> 0
- Encoding detections: 8,606 -> 12

The number of rows remained unchanged at 337,551.

## Original Dataset Preservation

The original loaded DataFrame matched the untouched deep snapshot using full DataFrame equality. Its quality counts also remained identical to the pre-treatment results.

This confirms that the treatment methods returned new DataFrames rather than modifying the original DataFrame.

The raw ZIP file was only read and was not overwritten.

## Change Log Verification

Four treatment entries were recorded:

1. replace_invalid_bbl
2. handle_invalid_zip
3. handle_date_inconsistencies
4. correct_encoding

All four treatment attempts recorded an outcome of `success`.

The change log was saved to:

`results/data_quality_change_log.json`

The saved JSON contained four entries and matched the in-memory change log.

## Remaining Encoding Values

After encoding correction, 12 detected encoding values remained.

All 12 occurred in the `Resolution Description` field and contained the ending:

`Administrative Code.Â`

These values were left unchanged because the current encoding treatment only applies the configured Latin-1 to UTF-8 conversion when it can be performed safely.

The remaining values were therefore preserved rather than forcing an unsupported replacement.

## Verification Status

Full January 2025 dataset verification completed successfully.

The following were verified:

- confirmed quality issue counts on the full dataset;
- BBL treatment;
- ZIP treatment;
- date inconsistency treatment;
- encoding treatment;
- row-count preservation;
- original DataFrame preservation;
- successful treatment logging; and
- JSON change-log persistence.

No pandas date-parsing warning was observed during the latest verification run.