# Laptop Research Dataset Runbook

This runbook separates the saved, read-only research snapshot from the canonical platform importer. It is designed for repeatable local operations without publishing private OCR evidence.

## Current evidence baseline

The saved delivery manifest records the following baseline:

| Evidence set | Count | Interpretation |
|---|---:|---|
| OCR candidate IDs | 348 | Candidate observations, not 348 verified unique laptop SKUs |
| Detailed listing extraction | 220 | Listing-level OCR records from 99 segments across four screenshots |
| Conservative crosswalk links | 215 | Candidate-to-listing links; use as review links, not proof of SKU identity |
| Unmatched OCR candidates | 133 | Retained without a forced listing match |
| Unpaired detailed listings | 5 | Retained without a forced candidate match |
| OCR-observed price values | 195 | Values carried from the detailed OCR extraction; not current researched prices |
| Configuration research rows | 89 | Mostly model-family/configuration evidence; exact SKU remains provisional unless explicitly proven |
| CPU benchmark rows | 39 | Preserve CPU identity, benchmark date, score type and confidence |
| Research source references | 27 | Source register, not a claim that every source was rechecked against a current retail SKU |
| Tesseract audit tiles | 80 | Independent tile-level OCR audit; 16,044 recognized words, mean confidence 79.91 |

One final Tesseract tile contains clipped listing-like text without enough identity to create a safe product record or assign a price. It remains a review gap.

## Immutable data rules

1. Never edit the original screenshots, raw OCR register, raw OCR text, or original detailed workbook in place.
2. Keep OCR-observed price, current researched selling price, MRP, bank/card offer, exchange value, coupon price and EMI in separate fields.
3. A numeric token is not a price until its meaning is clear from the same listing context.
4. Never turn model-family evidence into an exact SKU assertion. RAM topology, panel, battery, ports, weight and warranty can vary by SKU.
5. Never copy a benchmark from a related CPU name. Require exact CPU identity and preserve the benchmark source/date.
6. Treat crosswalk links as navigation/review aids. Do not deduplicate or merge based on title similarity alone.
7. Preserve conflicts and blanks. Missing evidence is preferable to a fabricated specification.
8. Keep private datasets, screenshots, generated workbooks, databases, exports and credentials out of this public repository.

## Saved read-only workbench

The private delivery bundle contains a SQLite snapshot and a standard-library-only read-only CLI. Extract the private workbench bundle locally, enter the extracted folder, and run:

```bash
python workbench_cli.py datasets
python workbench_cli.py qa
python workbench_cli.py count candidate_master_348
python workbench_cli.py count detailed_listings_220
python workbench_cli.py prices
python workbench_cli.py gaps
python workbench_cli.py sources
```

Useful targeted lookup:

```bash
python workbench_cli.py search candidate_master_348 "Core i3-1315U"
python workbench_cli.py show candidate_master_348 S1-001
```

The helper opens SQLite in read-only mode. It is intended for inspection, not updates. Work on a copy of the source archive when reprocessing.

## Canonical platform ingestion

The canonical executable implementation is this GitHub repository. Install its lightweight development dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Keep the private source bundle in a local directory ignored by Git. Place the importer-compatible CSV exports in one input directory, then run:

```bash
# First validate the complete source directory without creating or changing a database:
python scripts/ingest_research_bundle.py ./data/private/laptop-research-csv --db ./data/laptop_research.sqlite --dry-run

# Only after reviewing a successful dry-run report, perform the import:
python scripts/ingest_research_bundle.py ./data/private/laptop-research-csv --db ./data/laptop_research.sqlite
```

The importer recognises these source filenames when present:

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
- `screenshot_manifest.csv`
- `screenshot_ocr_regions_2026-11-01.csv`
- `ocr_price_evidence_2026-11-01.csv`
- `verified_official_specs_2026-11-01.csv`
- `data_dictionary.csv`

The importer reports each expected file as imported or missing. Missing optional files are not treated as zero-record datasets. If both the plain and enriched candidate-register exports are present, the enriched file is imported second and upserts the same candidate IDs; use it only when it contains the intended superset of source fields.

The importer now preflights every present CSV before opening the target database for writes. It rejects missing key headers, blank/whitespace-padded keys, duplicate stable keys, duplicate headers and malformed row widths. Keyless tables report exact duplicate-content rows because hash-key imports would otherwise collapse identical rows. The importer requires at least one recognised CSV file and stops before database writes if any present file fails preflight. Import outcomes are reported per source filename, so the plain and enriched candidate CSVs cannot overwrite each other's report entries when both are present. When both candidate-register files are supplied, preflight also requires the enriched export to retain every raw-register column and exactly the same Candidate_ID set; otherwise import stops before any database writes. The full bundle is written inside one SQLite transaction, including source-index rows, and rolls back as a unit if a write fails.

After import, inspect counts (dataset names are the left-hand values in the import report):

```bash
aiops dataset-count laptop_candidates --db ./data/laptop_research.sqlite
aiops dataset-count extracted_listings --db ./data/laptop_research.sqlite
aiops dataset-count cpu_benchmarks --db ./data/laptop_research.sqlite
aiops dataset-count research_sources --db ./data/laptop_research.sqlite
```

Re-importing a dataset with stable keys is idempotent for row counts, but an incoming row with the same key replaces the stored payload. Preserve an immutable copy of each input batch and its hash before importing.

## Reconciliation and enrichment acceptance checks

Before promoting any later workbook/database revision, verify:

- 348 raw candidate IDs remain present; no input row disappears during normalization.
- 220 detailed listing rows remain separately addressable.
- Candidate crosswalk counts are reported as matched, unmatched, and ambiguous; links are never silently treated as unique-product identity.
- The 195 OCR-observed price values remain unchanged and are not replaced by researched price fields.
- Each researched price has a separate source URL, observation date, price type, seller/marketplace and exact SKU match status.
- Every manufacturer specification fact has its own source URL and scope (exact SKU, product family, or generic platform).
- Benchmark rows preserve exact CPU name, score type, date and confidence.
- The clipped Tesseract coverage gap remains explicitly flagged until the source pixels support a product identity.
- Spreadsheet read-back validates sheet names, row counts, formulas/links and key columns; database QA validates dataset counts and source links.
- Final outputs have SHA-256 checksums. Keep the checksum manifest beside the private deliverables.

## Boundary between completed and pending deployment

The saved data delivery and SQLite snapshot exist in the user's Library. The platform source is maintained in this public repository, but device-local services are not thereby installed. Ollama models, MCP processes, Playwright browser binaries and n8n require a separate local installation and explicit start on the user's machine. Remote model access remains disabled by default; do not enable paid providers without an explicit decision.
