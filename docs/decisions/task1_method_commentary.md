# Appendix A: change-log persistence method

This excerpt is from `DataQualityManager.save_change_log()` in
`src/nyc311/data_quality_manager.py`. Only its docstring, blank lines and
the cleanup comment are omitted. The method's statements and signatures
are unchanged. Line numbers below are local to this listing.

The method is interesting because it separates successful serialisation
from replacing an existing audit record. Its input validation rejects
non-string paths; filesystem errors propagate to the caller. The BBL,
ZIP and date treatment methods separately demonstrate `try`, `except`,
`else` and `finally` together, including the custom integrity exception.

```text
01  def save_change_log(
02      self,
03      file_path: str,
04  ) -> None:
05      if not isinstance(file_path, str):
06          raise TypeError(
07              "File path must be a string."
08          )
09      temporary_path = None
10      try:
11          with tempfile.NamedTemporaryFile(
12              mode="w",
13              encoding="utf-8",
14              dir=os.path.dirname(os.path.abspath(file_path)),
15              delete=False,
16          ) as file:
17              temporary_path = file.name
18              json.dump(
19                  self.__change_log,
20                  file,
21                  indent=4,
22              )
23          os.replace(temporary_path, file_path)
24          temporary_path = None
25      finally:
26          if temporary_path is not None:
27              try:
28                  os.unlink(temporary_path)
29              except OSError:
30                  pass
```

| Line | Commentary |
|---|---|
| 01 | Declares the public persistence method. |
| 02 | Receives the manager instance holding the private log. |
| 03 | Annotates the destination path as a string. |
| 04 | Declares that successful completion returns no value. |
| 05 | Checks the supplied argument's type at runtime. |
| 06 | Begins raising an informative input-contract exception. |
| 07 | Supplies its explanatory message. |
| 08 | Completes the exception construction; invalid input exits here. |
| 09 | Records that no temporary file has yet been allocated. |
| 10 | Begins the operation protected by unconditional cleanup. |
| 11 | Opens a uniquely named temporary file under a context manager. |
| 12 | Selects text-writing mode. |
| 13 | Sets an explicit text encoding. |
| 14 | Places the temporary file beside the destination, supporting replacement within the same filesystem. |
| 15 | Keeps the temporary file available after closing, so it can be renamed into place. |
| 16 | Binds the opened stream to `file`; the context manager closes it on exit. |
| 17 | Retains its path for replacement or cleanup. |
| 18 | Begins serialising the history as JSON. |
| 19 | Selects the private list of log-entry dictionaries. |
| 20 | Writes to the temporary stream rather than the destination. |
| 21 | Requests readable indentation. |
| 22 | Completes serialisation; leaving the surrounding context closes the file before replacement. |
| 23 | Replaces the destination only after writing and closing have succeeded. |
| 24 | Clears the temporary path because successful replacement consumed it. |
| 25 | Runs cleanup whether the protected operation succeeded or raised an exception. |
| 26 | Checks whether a temporary path still requires cleanup. |
| 27 | Protects the cleanup attempt from masking the original error. |
| 28 | Attempts to delete the leftover temporary file. |
| 29 | Catches an operating-system error occurring during cleanup only. |
| 30 | Suppresses that cleanup error; an original write or replacement failure continues to propagate. |

## Evidence and limitations

The tests `test_save_change_log_write_failure_preserves_destination` and
`test_save_change_log_replace_failure_preserves_destination` exercise
failure paths and check preservation of existing evidence. Successful
creation and replacement are also tested. This is protection against
ordinary partial-write failures, not a crash-durability guarantee:
explicit filesystem synchronisation is not performed. The method does
not create a missing destination directory.

Suggested main-text reference: "Appendix A presents the change-log
persistence method with line-by-line commentary, showing how temporary
file replacement protects existing audit evidence."
