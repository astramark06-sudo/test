"""Import the saved laptop research CSV bundle into the local SQLite project store."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from aiops.storage.sqlite import SQLiteStore

DATASETS = {
    "ocr_candidate_register.csv": ("laptop_candidates", "Candidate_ID"),
    "configuration_register.csv": ("configurations", None),
    "cpu_benchmarks.csv": ("cpu_benchmarks", "CPU"),
    "source_register.csv": ("research_sources", "URL"),
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir", type=Path, help="Directory containing saved research CSV files")
    parser.add_argument("--db", type=Path, default=Path("./data/laptop_research.sqlite"))
    args = parser.parse_args()
    store = SQLiteStore(args.db)
    report = {"database": str(args.db), "datasets": {}}
    for filename, (dataset, key_field) in DATASETS.items():
        path = args.input_dir / filename
        if not path.exists():
            report["datasets"][dataset] = {"status": "missing", "source": str(path)}
            continue
        with path.open(newline="", encoding="utf-8-sig") as stream:
            rows = list(csv.DictReader(stream))
        imported = store.upsert_dataset_records(dataset, rows, key_field, str(path))
        report["datasets"][dataset] = {
            "status": "imported",
            "rows": imported,
            "stored_rows": store.count_dataset_records(dataset),
            "source": str(path),
        }
        if dataset == "research_sources":
            for row in rows:
                store.record_source(
                    row["URL"], row["Source title"], row["Source type"],
                    [row["Claims / scope"]], {"source_file": filename},
                )
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
