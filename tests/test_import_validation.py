from pathlib import Path

import pytest

from aiops.research.import_validation import load_csv_batch


def test_load_csv_batch_preserves_utf8_values_and_raw_cells(tmp_path: Path):
    source = tmp_path / "candidates.csv"
    source.write_text(
        "Candidate_ID,OCR_title,OCR_context\n"
        "S1-001,Samsung Galaxy Book4,Core i3-1315U; 8 GB\n",
        encoding="utf-8",
    )

    batch = load_csv_batch(source, "Candidate_ID")

    assert batch.fieldnames == ("Candidate_ID", "OCR_title", "OCR_context")
    assert batch.rows == [{
        "Candidate_ID": "S1-001",
        "OCR_title": "Samsung Galaxy Book4",
        "OCR_context": "Core i3-1315U; 8 GB",
    }]
    assert batch.duplicate_content_rows == 0


def test_keyed_csv_requires_key_column(tmp_path: Path):
    source = tmp_path / "missing_key.csv"
    source.write_text("Name,CPU\nLaptop,Core i3\n", encoding="utf-8")

    with pytest.raises(ValueError, match="required key column"):
        load_csv_batch(source, "Candidate_ID")


@pytest.mark.parametrize(
    ("rows", "message"),
    [
        ("S1-001,Laptop\n,Other laptop\n", "blank 'Candidate_ID'"),
        ("S1-001,Laptop\nS1-001,Second laptop\n", "duplicate 'Candidate_ID'"),
        (" S1-001,Laptop\n", "whitespace around 'Candidate_ID'"),
    ],
)
def test_keyed_csv_rejects_blank_duplicate_or_padded_keys(
    tmp_path: Path, rows: str, message: str
):
    source = tmp_path / "bad_keys.csv"
    source.write_text("Candidate_ID,Title\n" + rows, encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_csv_batch(source, "Candidate_ID")


def test_csv_rejects_duplicate_headers(tmp_path: Path):
    source = tmp_path / "duplicate_headers.csv"
    source.write_text("Candidate_ID,Title,Title\nS1-001,Laptop,Laptop\n", encoding="utf-8")

    with pytest.raises(ValueError, match="duplicate column names"):
        load_csv_batch(source, "Candidate_ID")


@pytest.mark.parametrize(
    ("row", "message"),
    [
        ("S1-001,Laptop,unexpected\n", "more cells than the header"),
        ("S1-001\n", "shorter than the header"),
    ],
)
def test_csv_rejects_malformed_row_width(tmp_path: Path, row: str, message: str):
    source = tmp_path / "malformed.csv"
    source.write_text("Candidate_ID,Title\n" + row, encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_csv_batch(source, "Candidate_ID")


def test_keyless_csv_reports_duplicate_content(tmp_path: Path):
    source = tmp_path / "configurations.csv"
    source.write_text(
        "Brand,Model_family,Processor\n"
        "Acer,Aspire 3,Core i3-1315U\n"
        "Acer,Aspire 3,Core i3-1315U\n"
        "HP,15s,Core i3-1315U\n",
        encoding="utf-8",
    )

    batch = load_csv_batch(source)

    assert len(batch.rows) == 3
    assert batch.duplicate_content_rows == 1
