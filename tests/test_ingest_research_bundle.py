import csv
import importlib.util
import json
import sys
from pathlib import Path

from aiops.storage.sqlite import SQLiteStore


def load_importer():
    path = Path(__file__).parents[1] / "scripts" / "ingest_research_bundle.py"
    spec = importlib.util.spec_from_file_location("ingest_research_bundle", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_importer_loads_screenshot_evidence_and_official_specs(tmp_path, monkeypatch, capsys):
    data_dir = tmp_path / "csv"
    data_dir.mkdir()
    db_path = tmp_path / "laptop.sqlite"

    write_csv(
        data_dir / "screenshot_ocr_regions_2026-11-01.csv",
        ["Region_ID", "OCR_text_raw"],
        [{"Region_ID": "S1-T00", "OCR_text_raw": "sample screenshot OCR"}],
    )
    write_csv(
        data_dir / "ocr_price_evidence_2026-11-01.csv",
        ["Evidence_ID", "OCR_price_line_raw"],
        [{"Evidence_ID": "S1-T00-L001", "OCR_price_line_raw": "50% ₹50,000 ₹25,000"}],
    )
    write_csv(
        data_dir / "verified_official_specs_2026-11-01.csv",
        ["Spec_Fact_ID", "Model_family_or_SKU", "Official_source_URL", "Processor_and_CPU_layout"],
        [{
            "Spec_Fact_ID": "CONF-001",
            "Model_family_or_SKU": "Example model",
            "Official_source_URL": "https://manufacturer.example/spec",
            "Processor_and_CPU_layout": "Example processor",
        }],
    )

    monkeypatch.setattr(
        sys,
        "argv",
        ["ingest_research_bundle.py", str(data_dir), "--db", str(db_path)],
    )
    load_importer().main()
    report = json.loads(capsys.readouterr().out)

    store = SQLiteStore(db_path)
    assert store.count_dataset_records("screenshot_ocr_regions") == 1
    assert store.count_dataset_records("ocr_price_evidence") == 1
    assert store.count_dataset_records("verified_official_specs") == 1
    assert report["datasets"]["screenshot_ocr_regions"]["status"] == "imported"
    assert report["datasets"]["ocr_price_evidence"]["rows"] == 1
    source = next(
        item for item in store.list_sources()
        if item["uri"] == "https://manufacturer.example/spec"
    )
    assert source["title"] == "Example model"
