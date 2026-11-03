# Laptop Research Dataset Runbook

This runbook separates the saved, read-only research snapshot from the canonical platform importer. It is designed for repeatable local operations without publishing private OCR evidence.

## Current release baseline — 2026-11-02

The latest private delivery is documented in [Laptop release notes](LAPTOP_RELEASE_2026-11-02.md). Its files remain in the user's private Library; this public repository contains no workbook, screenshot, raw OCR export or private database.

| Evidence set | Count | Interpretation |
|---|---:|---|
| OCR candidate IDs | 348 | Candidate observations, not 348 verified unique laptop SKUs |
| Detailed listing extraction | 220 | Listing-level OCR records |
| Conservative crosswalk links | 215 | Candidate-to-listing review links; not proof of SKU identity |
| Unmatched OCR candidates | 133 | Retained without a forced listing match |
| Unpaired detailed listings | 5 | Retained without a forced candidate match |
| OCR-observed price values in reconciled master / SQLite | 195 | Historical OCR estimates; not researched/current prices |
| Expanded workbook OCR price records | 199 | Separate expanded price register; do not merge its count with the 195-value master/SQLite register |
| Screenshot-level price evidence | 299 | OCR lines with discount/price-like tokens; price roles are not inferred |
| Evidence lines with nearby “Bank offer” text | 285 | Context only; numeric tokens remain unclassified OCR evidence |
| Configuration research rows | 89 | Model-family/configuration evidence unless exact SKU is proven |
| CPU benchmark rows | 39 | Preserve exact processor identity, date, score type and source |
| Research source references | 27 | Source register, not proof that every source maps to a current retail SKU |
| Tesseract audit tiles | 80 | 16,044 recognized words; mean word confidence 79.91 |
| Screenshot OCR regions | 40 | Four source screenshots processed in vertical regions |
| Manufacturer source-audit entries | 30 | Model/variant source checks with scope warnings |
| Conflict-review records | 16 | Explicitly retained for adjudication |

The release also includes nine manufacturer fact records, nine additional specification-source records and four focused official-spec cross-check profiles. The 19-tab expanded workbook includes the candidate/listing registers, source audit, price evidence, conflict review and data dictionary; the 12-tab reconciled master remains the canonical 348-candidate reconciliation workbook.

The final Tesseract tile was linked to existing candidate `S4-348`. It did not create a new candidate or duplicate price. The release manifest records zero unresolved OCR coverage gaps. This does not mean all laptop identities or specification conflicts are resolved.

## Immutable data rules

1. Never edit the original screenshots, raw OCR register, raw OCR text or prior release files in place.
2. Keep OCR-observed price, current researched selling price, MRP, bank/card offer, exchange value, coupon price and EMI in separate fields.
3. A numeric token is not a price until its meaning is clear from the same listing context.
4. Never turn model-family evidence into an exact SKU assertion. RAM topology, panel, battery, ports, weight and warranty can vary by SKU.
5. Never copy a benchmark from a related CPU name. Require exact CPU identity and preserve the benchmark source/date.
6. Treat crosswalk links as navigation/review aids. Do not deduplicate or merge based on title similarity alone.
7. Preserve conflicts and blanks. Missing evidence is preferable to a fabricated specification.
8. Keep private datasets, screenshots, generated workbooks, databases, exports and credentials out of this public repository.

## Saved read-only workbench

The private 2026-11-02 delivery bundle contains a SQLite snapshot and a standard-library-only read-only CLI. The release manifest records SQLite `PRAGMA integrity_check=ok`, zero unresolved OCR coverage gaps, 195 OCR prices carried and zero researched prices. Extract the private bundle locally, enter the extracted folder, and run:

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

Keep the private source bundle in a local directory ignored by Git. Before extraction, create a SHA-256 manifest beside the original archive with `aiops hash-tree ./private-source ./private-source.manifest.json`; verify it with `aiops verify-manifest ./private-source ./private-source.manifest.json` after copying or restoring the archive. Place importer-compatible CSV exports in one input directory, then run:

```bash
# Validate the complete source directory without creating/changing a database:
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

The importer reports each expected file as imported or missing. Missing optional files are not treated as zero-record datasets. If both plain and enriched candidate-register exports are present, the enriched file is imported second and upserts the same candidate IDs; use it only when it contains the intended superset of source fields.

The importer preflights every present CSV before opening the target database for writes. It rejects missing key headers, blank/whitespace-padded keys, duplicate stable keys, duplicate headers and malformed row widths. Keyless tables report exact duplicate-content rows because hash-key imports would otherwise collapse identical rows. The importer requires at least one recognised CSV file and stops before database writes if any present file fails preflight. Import outcomes are reported per source filename, so the plain and enriched candidate CSVs cannot overwrite each other's report entries when both are present. When both candidate-register files are supplied, preflight also requires the enriched export to retain every raw-register column and exactly the same Candidate_ID set; otherwise import stops before any database writes. The full bundle is written inside one SQLite transaction, including source-index rows, and rolls back as a unit if a write fails.

Before any write import, create a verified backup of the working database with `aiops backup-db ./backups/laptop-before-import.sqlite --db ./data/laptop_research.sqlite`. Keep the original Library snapshot unchanged and use a separate working database as the write target. The backup command uses SQLite's online backup API and runs an integrity check before writing the destination.

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
- Candidate crosswalk counts are reported as matched, unmatched and ambiguous; links are never silently treated as unique-product identity.
- Preserve the 195-value OCR price register in the reconciled master/SQLite snapshot. Keep the 199-record expanded workbook register separate; do not replace either with current researched prices.
- Keep the 299 screenshot-level price-evidence rows as raw OCR evidence; do not assign sale/MRP/bank/exchange roles unless source context establishes them.
- Each future researched price has a separate source URL, observation date, price type, seller/marketplace and exact-SKU match status.
- Every manufacturer specification fact has its own source URL and scope (exact SKU, product family or generic platform).
- Benchmark rows preserve exact CPU name, score type, date and confidence.
- Confirm the last Tesseract tile remains linked to existing candidate `S4-348`; do not re-open it as an unresolved coverage gap absent new source evidence.
- Spreadsheet read-back validates sheet names, row counts, formulas/links and key columns; database QA validates dataset counts and source links.
- Final outputs have SHA-256 checksums. Keep the checksum manifest beside the private deliverables.

## Boundary between completed and pending deployment

The saved data delivery and SQLite snapshot exist in the user's Library. The platform source is maintained in this public repository, but device-local services are not thereby installed. Ollama models, MCP processes, Playwright browser binaries and n8n require a separate local installation and explicit start on the user's machine. Remote model access remains disabled by default; do not enable paid providers without an explicit decision.
