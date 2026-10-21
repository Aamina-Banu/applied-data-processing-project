"""Verify Task 4 inputs against the immutable source archive."""
import hashlib
import shutil
import zipfile
from pathlib import Path

RAW_SHA256 = "66eb5d89668990c6f86aaf49c71db026d1452cd974884a952529299240503866"


def verified_input(project_root):
    """Return a CSV proven byte-identical to the checksum-verified ZIP member."""
    raw = Path(project_root) / "data/raw/nyc_311_january_2025.zip"
    target = Path(project_root) / "data/processed/task4_spark_input.csv"
    with raw.open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != RAW_SHA256:
            raise ValueError("Raw ZIP checksum differs from DATA_SOURCE.md")
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(raw) as archive:
        members = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if len(members) != 1:
            raise ValueError("Expected exactly one CSV in the raw ZIP")
        with archive.open(members[0]) as stream:
            expected = hashlib.file_digest(stream, "sha256").hexdigest()
        if not target.exists():
            with archive.open(members[0]) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)
    with target.open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != expected:
            raise ValueError("Existing Spark CSV differs from raw ZIP; move it aside and rerun")
    return target, expected
