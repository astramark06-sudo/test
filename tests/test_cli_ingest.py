import sys
from pathlib import Path

import pytest

from aiops.cli import main
from aiops.storage.sqlite import SQLiteStore


def invoke_cli(monkeypatch, *args: str) -> None:
    monkeypatch.setattr(sys, "argv", ["aiops", *args])
    main()


@pytest.mark.parametrize(
    ("csv_text", "key_field", "message"),
    [
        ("Candidate_ID,Title\nS1-001,A\nS1-001,B\n", "Candidate_ID", "duplicate"),
        ("Candidate_ID,Title\n,A\n", "Candidate_ID", "blank"),
        ("Candidate_ID,Title\nS1-001\n", "Candidate_ID", "shorter than the header"),
        ("Candidate_ID,Title,Title\nS1-001,A,B\n", "Candidate_ID", "duplicate column"),
    ],
)
def test_cli_preflights_invalid_csv_before_creating_database(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    csv_text: str,
    key_field: str,
    message: str,
):
    source = tmp_path / "invalid.csv"
    database = tmp_path / "must_not_exist.sqlite"
    source.write_text(csv_text, encoding="utf-8")

    with pytest.raises(SystemExit, match="CSV preflight failed"):
        invoke_cli(
            monkeypatch,
            "ingest-csv",
            str(source),
            "candidates",
            "--key-field",
            key_field,
            "--db",
            str(database),
        )

    assert not database.exists()


def test_cli_ingest_preserves_source_fields_and_keyed_rows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    source = tmp_path / "candidates.csv"
    database = tmp_path / "laptop.sqlite"
    source.write_text(
        "Candidate_ID,OCR_title,OCR_context\n"
        "S1-001,Samsung Galaxy Book4,\"Core i3-1315U; 8 GB\"\n"
        "S1-002,Dell Latitude 5420,\"Core i5-1145G7; 16 GB\"\n",
        encoding="utf-8",
    )

    invoke_cli(
        monkeypatch,
        "ingest-csv",
        str(source),
        "laptop_candidates",
        "--key-field",
        "Candidate_ID",
        "--db",
        str(database),
    )

    store = SQLiteStore(database)
    assert store.count_dataset_records("laptop_candidates") == 2
    restored = store.list_dataset_records("laptop_candidates", "S1-001")[0]["record"]
    assert restored == {
        "Candidate_ID": "S1-001",
        "OCR_title": "Samsung Galaxy Book4",
        "OCR_context": "Core i3-1315U; 8 GB",
    }


def test_cli_reports_keyless_duplicate_rows_that_hash_to_one_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    source = tmp_path / "sources.csv"
    database = tmp_path / "sources.sqlite"
    source.write_text(
        "Source,Claim\n"
        "Manufacturer,CPU specification\n"
        "Manufacturer,CPU specification\n",
        encoding="utf-8",
    )

    invoke_cli(monkeypatch, "ingest-csv", str(source), "sources", "--db", str(database))

    output = capsys.readouterr().out
    assert "2 source rows" in output
    assert "1 exact duplicate-content" in output
    assert SQLiteStore(database).count_dataset_records("sources") == 1


def test_cli_ingest_rejects_missing_file_before_database_creation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    database = tmp_path / "must_not_exist.sqlite"
    missing = tmp_path / "missing.csv"

    with pytest.raises(SystemExit, match="CSV preflight failed"):
        invoke_cli(
            monkeypatch,
            "ingest-csv",
            str(missing),
            "candidates",
            "--db",
            str(database),
        )

    assert not database.exists()
