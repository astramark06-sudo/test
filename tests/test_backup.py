from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from aiops.storage.backup import backup_database
from aiops.storage.sqlite import SQLiteStore


def make_source(path: Path) -> None:
    store = SQLiteStore(path)
    store.upsert_dataset_records(
        "laptops",
        [{"Candidate_ID": "S1-001", "raw_ocr": "Acer Aspire 3", "price_ocr": "42990"}],
        "Candidate_ID",
        "source.csv",
    )


def read_records(path: Path) -> list[tuple[str, str]]:
    uri = path.resolve().as_uri() + "?mode=ro"
    with sqlite3.connect(uri, uri=True) as connection:
        return connection.execute(
            "SELECT record_key, payload_json FROM dataset_records"
        ).fetchall()


def test_backup_database_copies_records_and_passes_integrity_check(tmp_path: Path):
    source = tmp_path / "source.sqlite"
    destination = tmp_path / "backups" / "source.backup.sqlite"
    make_source(source)

    result = backup_database(source, destination)

    assert result == destination
    assert read_records(destination) == read_records(source)
    with sqlite3.connect(destination) as connection:
        assert connection.execute("PRAGMA integrity_check").fetchone() == ("ok",)


def test_backup_refuses_to_overwrite_without_explicit_flag(tmp_path: Path):
    source = tmp_path / "source.sqlite"
    destination = tmp_path / "backup.sqlite"
    make_source(source)
    destination.write_bytes(b"preserve existing destination")

    with pytest.raises(FileExistsError):
        backup_database(source, destination)

    assert destination.read_bytes() == b"preserve existing destination"


def test_backup_overwrite_replaces_destination_only_after_success(tmp_path: Path):
    source = tmp_path / "source.sqlite"
    destination = tmp_path / "backup.sqlite"
    make_source(source)
    destination.write_bytes(b"old backup")

    backup_database(source, destination, overwrite=True)

    assert read_records(destination) == read_records(source)


def test_failed_backup_keeps_existing_destination_and_removes_temporary_files(
    tmp_path: Path,
):
    source = tmp_path / "corrupt.sqlite"
    destination = tmp_path / "backup.sqlite"
    source.write_bytes(b"not a sqlite database")
    destination.write_bytes(b"old backup")

    with pytest.raises(sqlite3.DatabaseError):
        backup_database(source, destination, overwrite=True)

    assert destination.read_bytes() == b"old backup"
    assert list(tmp_path.glob(".backup.sqlite.*.tmp")) == []


def test_backup_rejects_same_source_and_destination(tmp_path: Path):
    source = tmp_path / "same.sqlite"
    make_source(source)

    with pytest.raises(ValueError, match="differ from the source"):
        backup_database(source, source)
