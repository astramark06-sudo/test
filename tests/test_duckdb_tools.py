from pathlib import Path

import pytest

from aiops.data.duckdb_tools import query_file


def test_duckdb_queries_are_limited_to_loaded_source(tmp_path: Path):
    pytest.importorskip("duckdb")
    source = tmp_path / "inventory.csv"
    source.write_text("brand,price\nAcer,42000\nHP,51000\n", encoding="utf-8")

    rows = query_file(source, "SELECT brand, price FROM input_data ORDER BY price")
    assert rows == [
        {"brand": "Acer", "price": 42000},
        {"brand": "HP", "price": 51000},
    ]


def test_duckdb_external_access_is_disabled_before_query(tmp_path: Path):
    pytest.importorskip("duckdb")
    source = tmp_path / "inventory.csv"
    source.write_text("brand\nAcer\n", encoding="utf-8")

    rows = query_file(source, "SELECT current_setting('enable_external_access') AS enabled")
    assert rows == [{"enabled": False}]


def test_duckdb_rejects_multiple_statements(tmp_path: Path):
    source = tmp_path / "inventory.csv"
    source.write_text("brand\nAcer\n", encoding="utf-8")
    with pytest.raises(ValueError):
        query_file(source, "SELECT * FROM input_data; SELECT 1")



def test_duckdb_rejects_multiple_trailing_delimiters(tmp_path: Path):
    source = tmp_path / "inventory.csv"
    source.write_text("brand\nAcer\n", encoding="utf-8")

    with pytest.raises(ValueError, match="one SQL statement"):
        query_file(source, "SELECT * FROM input_data;;")
