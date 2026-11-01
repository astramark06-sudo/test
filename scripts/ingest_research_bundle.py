"""Import the saved laptop research CSV bundle into the local SQLite project store."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from aiops.storage.sqlite import SQLiteStore

# Original source tables plus optional derived exports from the consolidated workbook.
# Later enriched candidate rows intentionally upsert the same Candidate_IDs, replacing
# the plain row payload with the same source fields plus review-only OCR token fields.
DATASETS = {
    "ocr_candidate_register.csv": ("laptop_candidates", "Candidate_ID"),
    "ocr_candidate_register_enriched_tokens.csv": ("laptop_candidates", "Candidate_ID"),
    "configuration_register.csv": ("configurations", None),
    "configuration_benchmark_join.csv": ("configurations_with_benchmarks", None),
    "cpu_benchmarks.csv": ("cpu_benchmarks", "CPU"),
    "source_register.csv": ("research_sources", "URL"),
    "extracted_listings_220.csv": ("extracted_listings", "Listing_Record_ID"),
    "candidate_crosswalk_review.csv": ("candidate_crosswalk", "Candidate_ID"),
    "ocr_prices_199.csv": ("ocr_prices", "Listing_Record_ID"),
    "manufacturer_spec_facts_2026-11-01.csv": ("manufacturer_spec_facts", "Spec_Fact_ID"),
    "additional_spec_sources_2026-11-01.csv": ("manufacturer_spec_sources", "URL"),
    "screenshot_manifest.csv": ("screenshot_manifest", "Screenshot_ID"),
    "screenshot_ocr_regions_2026-11-01.csv": ("screenshot_ocr_regions", "Region_ID"),
    "ocr_price_evidence_2026-11-01.csv": ("ocr_price_evidence", "Evidence_ID"),
    "verified_official_specs_2026-11-01.csv": ("verified_official_specs", "Spec_Fact_ID"),
    "data_dictionary.csv": ("data_dictionary", None),
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
        if dataset in {"research_sources", "manufacturer_spec_sources", "verified_official_specs"}:
            for row in rows:
                url = row.get("URL") or row.get("Official_source_URL")
                if not url:
                    continue
                claims = [
                    row.get("Claims / scope") or row.get("Scope") or "",
                    row.get("Evidence quality / caveat") or "",
                    row.get("Processor_and_CPU_layout") or "",
                    row.get("GPU") or "",
                    row.get("Memory") or "",
                    row.get("Storage") or "",
                    row.get("Display") or "",
                ]
                source_type = row.get("Source type") or "Manufacturer specification"
                title = row.get("Source title") or row.get("Model_family_or_SKU")
                store.record_source(
                    url, title, source_type,
                    [claim for claim in claims if claim],
                    {"source_file": filename, **row},
                )
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
