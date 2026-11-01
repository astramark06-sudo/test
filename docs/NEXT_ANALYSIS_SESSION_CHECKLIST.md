# Next Analysis Session — Laptop Research Completion Checklist

This checklist is deliberately written to prevent duplicate work. A completed private 12-tab workbook and a read-only SQLite workbench already exist in the user's Library. The next analysis session must verify and improve that delivery, not recreate a second workbook from scratch.

## 0. Starting state — already delivered

Private artifacts in the user's Library under `/AI Operations Platform Deliverables`:

- `laptop_inventory_reconciled_348.xlsx`
- `laptop-research-evidence-bundle.zip`
- `ocr_candidates_validated.jsonl`
- `tesseract_segment_audit_all_80_tiles.csv`
- `aiops-workbench-data-bundle.zip`
- `aiops_platform_workbench.sqlite3`
- `workbench_cli.py`
- `AI_OPS_WORKBENCH_README.md`
- `FINAL_DELIVERY_README.md`
- `AI_OPS_SHA256SUMS.txt` and `SHA256SUMS.txt`

The saved final manifest lists this SHA-256 for the 12-tab workbook:

`96d5d3b8a6145b0a193363e736f2de822976ca6ac1d6e5519bdfd4d9afd30e01`

Treat the saved files as the baseline release. Verify their bytes/hashes before changing anything. Do not regenerate them when the baseline is valid.

## 1. Restore and inspect source artifacts

1. Locate the existing Library files using Files listing/materialization; never infer a sandbox path from a Library filename.
2. Materialize the private evidence bundle, workbook and workbench bundle to a working directory.
3. Extract copies of the archives; retain the originals unchanged.
4. Read the saved SHA-256 manifests and compare actual file hashes. For new copied directories, use `aiops hash-tree ./private-source ./private-source.manifest.json` then `aiops verify-manifest ./private-source ./private-source.manifest.json`; keep manifest files outside the source tree.
5. Inventory archive contents and confirm screenshot filenames, CSV names, spreadsheet tabs and JSONL count.
6. Record a session manifest with input hashes, tool/runtime versions and date/time.
7. Never place private source artifacts under a Git-tracked path.

## 2. Workbook read-back validation

Use openpyxl for .xlsx read/write; do not use a PDF/document workflow or LibreOffice as the spreadsheet engine.

Expected baseline structure: 12 tabs:

1. All detected listings
2. Data quality & missing fields
3. Candidate Master (348)
4. OCR Candidate Register Raw
5. Unmatched Detailed Rows
6. Configuration Register
7. CPU Benchmark Register
8. Research Source Register
9. Source Image Inventory
10. QA Dashboard
11. Tesseract Sample Audit
12. Tesseract Coverage Gaps

Re-check these baseline relationships:

- Candidate Master: 348 rows and stable unique Candidate_ID values.
- Raw candidate register: 348 rows.
- Detailed listing extraction: 220 rows.
- Conservative crosswalk: 215 one-to-one links.
- Candidate records unmatched to a detailed listing: 133.
- Detailed rows unpaired: 5.
- OCR-observed price values copied from detailed extraction: 195.
- Configuration register: 89 rows.
- CPU benchmark register: 39 rows.
- Research source register: 27 rows.
- Source image inventory: four screenshots.
- Tesseract audit: 80 tiles, 16,044 recognized words, mean word confidence 79.91.
- One clipped final tile remains a coverage gap with no safe identity or assigned product price.

If any result differs, stop and investigate the discrepancy rather than silently updating the workbook's QA dashboard.

## 3. Reconcile without false joins

- Verify one-to-one key uniqueness on the crosswalk.
- Recheck the 215 links against candidate title, brand and processor evidence.
- Keep the 133 unmatched candidate records and five unpaired detailed listings visible.
- Review near-duplicates using screenshot ID, top-pixel coordinate, processor, RAM and storage together.
- Do not deduplicate separate offers/configurations simply because titles match.
- Do not infer a SKU from brand + product family + CPU alone.
- Preserve the source row and the reason for every match/rejection/adjudication.

## 4. Price controls

- Preserve all 195 source OCR price values unchanged.
- Never overwrite the OCR estimate with a retailer or manufacturer price.
- Keep MRP, base sale price, bank/card amount, coupon, exchange, cashback and EMI as separate price types.
- A token is not a price until the raw context establishes its role.
- Current researched price remains blank until there is a direct listing URL, named seller, observation timestamp, price type, offer conditions and adequate SKU match.
- User's earlier requirement was to retain the prices visible in OCR; do not add web prices to the workbook unless specifically requested in a later instruction.

## 5. Additive source enrichment

Use `docs/OFFICIAL_MODEL_SOURCE_AUDIT_2026-11-02.md` as a research lead sheet. It includes scoped manufacturer and secondary sources for Acer, HP, Dell, ASUS, Lenovo, Samsung, MSI, Neopticon, Primebook, JioBook, Ultimus, Motorola and Thomson.

For the new workbook revision:

- Add a separate `Spec_Facts` tab with one fact per source and attribute.
- Add `Price_Evidence` only if new price evidence is explicitly requested; otherwise preserve OCR price only.
- Add `Source_Audit` and `Conflict_Review` tabs with exact URL, source date, source type, identity scope and adjudication.
- Keep exact-SKU, model-number, family, platform-only and unresolved levels distinct.
- Record every fact's source scope; family information must not be promoted to SKU-level detail.
- Keep the MSI Ryzen 5 7430U / 8GB OCR vs C7M-400IN 16GB manufacturer discrepancy open.
- Keep HP 255R G10 C8HS6AT FreeDOS vs OCR/retailer Windows discrepancy open.
- Keep Acer AL15-41 versus AL15-42 part numbers separate.
- Keep Lenovo V15 G4 AMN machine-type/model suffixes separate.
- Keep Motorola "Motobook 6" title normalization unresolved pending exact title/CPU/SKU.
- Keep Thomson IN-K14C facts secondary-source-only until an official spec is found.
- For Neopticon, distinguish EBook's 128GB eMMC + expansion slot from a claim of a second preinstalled SSD; distinguish BrowseBook RAM/storage variants.
- For Primebook, distinguish MT8183 WiFi from MT8788 4G.
- Exact-match CPU benchmarks only; preserve missing scores.

## 6. SQLite update and migration safety

- Use a new database copy for the next import; do not mutate the only saved snapshot.
- Before import, create a verified backup using `aiops backup-db ./backups/laptop-before-import.sqlite --db ./data/laptop_research.sqlite`; use a separate working copy as the write target.
- Record hashes of the database, import CSVs and workbook before importing.
- Run importer mappings from `scripts/ingest_research_bundle.py` and save the import report.
- Do not place both plain and enriched candidate-register CSVs in the same batch unless enriched is intentionally the full superset; the later import upserts the same candidate IDs.
- Verify dataset counts, stable keys, source URLs and row payload retrieval after import.
- Run the importer in `--dry-run` mode first; review both the aggregate `datasets` summary and per-source-file report before importing.
- Confirm duplicate stable IDs and malformed row shapes are rejected, while keyless duplicate-content rows are reported.
- Run database integrity checks and restore-test on a separate copy.
- Keep the previous database as a recoverable baseline until all checks pass.

## 7. Release and publication

Only create a new version when it adds verified information or resolves a real quality issue. Use versioned filenames and preserve the baseline.

Release should contain:

- validated .xlsx workbook,
- private SQLite workbench snapshot plus read-only CLI,
- source/evidence bundle (or a manifest pointing to the original immutable source archive),
- data dictionary,
- QA and unresolved-conflict register,
- source manifest,
- SHA-256 checksums,
- concise release notes with changed row/sheet counts.

Do not commit any of these private data artifacts to the public GitHub repository. The repository may contain the software, schemas, tests, aggregate process documentation and non-sensitive public source audit links.

## 8. Final verification

- Read the saved workbook back and confirm the expected tabs, row counts, key columns and links.
- Compare row counts against each source register.
- Confirm there are no broken hyperlinks, external workbook links or stale formula values.
- Run the existing CLI `datasets`, `qa`, `prices`, `gaps` and `sources` commands against the final DB copy.
- Run `ruff check .` and `pytest -q` for any software changes.
- Verify GitHub Actions is green for the exact source commit.
- Verify the SHA-256 manifest against final release bytes.
- Mark unresolved conflicts as unresolved; never force a complete-looking dataset.
