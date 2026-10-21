"""Provenance failures must stop Task 4 before measurements are published."""
import hashlib
import zipfile

import pytest

from notebooks import task4_input


def test_verified_input_rejects_stale_csv(tmp_path, monkeypatch):
    raw = tmp_path / "data/raw/nyc_311_january_2025.zip"
    raw.parent.mkdir(parents=True)
    with zipfile.ZipFile(raw, "w") as archive:
        archive.writestr("source.csv", "Unique Key,Agency\n1,DOT\n")
    monkeypatch.setattr(task4_input, "RAW_SHA256", hashlib.sha256(raw.read_bytes()).hexdigest())
    target, expected = task4_input.verified_input(tmp_path)
    assert hashlib.sha256(target.read_bytes()).hexdigest() == expected
    target.write_text("stale input")
    with pytest.raises(ValueError, match="Existing Spark CSV differs"):
        task4_input.verified_input(tmp_path)
    assert target.read_text() == "stale input"


def test_verified_input_rejects_changed_archive(tmp_path):
    raw = tmp_path / "data/raw/nyc_311_january_2025.zip"
    raw.parent.mkdir(parents=True)
    raw.write_bytes(b"different archive")
    with pytest.raises(ValueError, match="Raw ZIP checksum differs"):
        task4_input.verified_input(tmp_path)
    assert not (tmp_path / "data/processed/task4_spark_input.csv").exists()
