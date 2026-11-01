# Laptop research bundle ingestion

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

Missing optional files are reported as `missing`; they do not stop ingestion.

## Import

From the repository root:

```bash
python scripts/ingest_research_bundle.py /path/to/laptop_research_bundle/csv \
  --db data/laptop_research.sqlite
```

The importer writes structured records to SQLite's `dataset_records` table and records research URLs in `sources`. Re-running is safe: keyed datasets are upserted. The enriched candidate CSV is processed after the original candidate CSV and therefore updates each `Candidate_ID` with the extra review-only OCR token fields.

## Dataset semantics

- `laptop_candidates`: granular OCR hits. Candidate rows are not unique laptop SKUs.
- `extracted_listings`: earlier broad listing extraction, with stable `Listing_Record_ID` values assigned for import.
- `configurations`: original configuration register.
- `configurations_with_benchmarks`: configuration rows with exact normalized CPU-name joins only.
- `cpu_benchmarks`: benchmark observations with date and source reference.
- `research_sources`: source URLs and their stated claim scope.
- `candidate_crosswalk`: title-similarity review aid; never treat it as proof of SKU identity.

Do not merge the granular candidate register and broad listing extraction solely on title similarity. Preserve OCR price estimates separately from researched prices, bank offers and exchange values. The CSV crosswalk is only a manual-review aid.

## Data handling

Do not commit user screenshots, OCR data, workbooks, research bundles, SQLite databases or `.env` files to this public repository. Keep these files in the user's local project data directory.
