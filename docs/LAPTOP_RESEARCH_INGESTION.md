# Laptop research bundle ingestion

> **Version scope — intermediate importer profile.** This document describes an earlier 2026-11-01 CSV export profile, including 199 OCR-estimated price rows. The final Library delivery is a later 12-tab workbook carrying 195 OCR-observed price values. These counts belong to different artifact versions/definitions; do not merge or treat them as interchangeable. Confirm the exact CSV versions and row-level relationship in the next data-analysis read-back. For the authoritative delivery inventory and validation sequence, see [Laptop dataset runbook](LAPTOP_DATASET_RUNBOOK.md) and [Next analysis session checklist](NEXT_ANALYSIS_SESSION_CHECKLIST.md). Always run `--dry-run` against a versioned copy before importing.

This repository keeps application code public while the user's laptop screenshots, OCR records, workbooks and databases remain private.

## Expected input files

Run the importer against the bundle's `csv/` directory. It accepts the original source exports and the optional derived exports:

- `ocr_candidate_register.csv`
- `ocr_candidate_register_enriched_tokens.csv`
- `configuration_register.csv`
- `configuration_benchmark_join.csv`
- `cpu_benchmarks.csv`
- `source_register.csv`
- `extracted_listings_220.csv`
- `candidate_crosswalk_review.csv`
- `ocr_prices_199.csv`
- `manufacturer_spec_facts_2026-11-01.csv`
- `additional_spec_sources_2026-11-01.csv`

Missing optional files are reported as `missing`; they do not stop ingestion.

## Import

From the repository root:

```bash
python scripts/ingest_research_bundle.py /path/to/laptop_research_bundle/csv \
  --db data/laptop_research.sqlite
```

The importer writes structured records to SQLite's `dataset_records` table and records research URLs in `sources`. Re-running is safe: keyed datasets are upserted. The enriched candidate CSV is processed after the original candidate CSV and therefore updates each `Candidate_ID` with the extra review-only OCR token fields.

## Dataset semantics — intermediate export profile

- `laptop_candidates`: granular OCR hits. Candidate rows are not unique laptop SKUs.
- `extracted_listings`: earlier broad listing extraction, with stable `Listing_Record_ID` values assigned for import.
- `configurations`: original configuration register.
- `configurations_with_benchmarks`: configuration rows with exact normalized CPU-name joins only.
- `cpu_benchmarks`: benchmark observations with date and source reference.
- `research_sources`: source URLs and their stated claim scope.
- `candidate_crosswalk`: title-similarity review aid; never treat it as proof of SKU identity.
- `ocr_prices`: 199 populated OCR-estimated price values in this intermediate export; one suspect exchange-related value is flagged.
- `manufacturer_spec_facts`: manufacturer facts with exact-SKU/family scope and caveats.
- `manufacturer_spec_sources`: manufacturer source index for those fact records.

Do not merge the granular candidate register and broad listing extraction solely on title similarity. Preserve OCR price estimates separately from researched prices, bank offers and exchange values. The CSV crosswalk is only a manual-review aid.

## Data handling

Do not commit user screenshots, OCR data, workbooks, research bundles, SQLite databases or `.env` files to this public repository. Keep these files in the user's local project data directory.
