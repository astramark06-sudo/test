# Next Analysis Session — Laptop Research Post-Release Checklist

This checklist starts from the verified private release dated 2026-11-02. Do not rebuild OCR extraction or recreate the report from scratch. Improve only where new source evidence, a corrected data defect or a reproducible software issue justifies a new version.

## 1. Current delivered state

Private Library artifacts:

- `laptop_research_consolidated_2026-11-02_spec_audit_enriched_v2.xlsx` — primary enriched report, 19 tabs.
- `laptop_inventory_reconciled_348_reconciled_2026-11-02.xlsx` — reconciled master, 12 tabs.
- `aiops-workbench-data-bundle_reconciled_2026-11-02.zip` — SQLite snapshot, read-only CLI and bundle README.
- `OCR_RELEASE_MANIFEST_2026-11-02.txt` — SHA-256 release manifest.

See [Laptop release notes](LAPTOP_RELEASE_2026-11-02.md) and [Laptop dataset runbook](LAPTOP_DATASET_RUNBOOK.md) for full counts, structure and verification rules.

The report and bundle hashes match the release manifest. The SQLite database returns `ok` from `PRAGMA integrity_check`. The release manifest records zero unresolved OCR coverage gaps, 195 OCR prices carried to SQLite and zero researched prices.

## 2. Canonical counts — keep the registers distinct

- 348 OCR candidate observations.
- 220 detailed listing rows.
- 215 conservative candidate/listing links.
- 133 candidate observations without a detailed-listing link.
- Five detailed listing rows without a candidate link.
- 195 OCR-observed price values in the reconciled master/SQLite snapshot.
- 199 OCR price-estimate records in the expanded workbook's separate register.
- 299 screenshot-level OCR price-evidence rows, including 285 with nearby explicit “Bank offer” text. These are raw evidence tokens, not classified offer amounts.
- 89 configuration research rows; 39 CPU benchmark rows; 27 research sources.
- Four source screenshots; 40 OCR regions; 80 Tesseract audit tiles and 16,044 recognized words.
- 30 manufacturer/model-variant source-audit entries; nine manufacturer fact records; nine additional specification-source records; four focused official-spec cross-check profiles.
- 16 conflict-review records.

Do not sum or substitute similarly named price registers. Their counts represent different stages and scopes. OCR-estimated prices are not verified current prices.

## 3. Resolved OCR coverage item

The final Tesseract tile is linked to existing candidate `S4-348`. It did not create another candidate or duplicate price. The 2026-11-02 release reports zero unresolved coverage gaps. Do not re-open the clipped-tile issue unless new source pixels contradict this resolution.

## 4. Next data work

Prioritize the 16 conflict-review records and 133 unmatched candidate observations. Preserve all original IDs and evidence.

For every new specification fact:

- Record one fact per attribute/source.
- Preserve the source URL, retrieval date, source type and identity scope.
- Distinguish exact SKU, manufacturer part number, model family, platform-only and secondary-source evidence.
- Do not transfer OS, RAM topology, panel, storage, weight, ports, battery or upgradeability across variants without direct evidence.
- Require exact processor identity for benchmark joins; preserve missing scores.

The current priority conflicts include HP 255R G10 C8HS6AT FreeDOS vs retailer/Windows descriptions; MSI Modern 14 R5-7430U OCR 8GB vs India SKU C7M-400IN 16GB; Acer AL15-41 vs AL15-42; Lenovo V15 G4 AMN MTM suffix/OS differences; truncated Motorola “Motobook 6”; Neopticon EBook expansion-slot vs installed SSD wording; Primebook WiFi MT8183 vs 4G MT8788; and secondary-source-only variants.

Do not add live/current prices unless explicitly requested. If authorised later, put them in a separate researched-price field with exact seller URL, retrieval timestamp, amount type, offer conditions and exact-SKU match status. Never overwrite OCR price evidence.

## 5. SQLite and importer safety

- Treat the 2026-11-02 database as a read-only baseline.
- Create a separate working copy before testing an import or migration.
- Run the importer in `--dry-run` mode first.
- Review per-file import reports, dataset counts, stable IDs, source links and row payload retrieval before writing.
- Use the SQLite backup command before import and verify the backup with an integrity check.
- Never overwrite the only saved database snapshot.
- Preserve input batch hashes and prior database versions.

## 6. Repository, CI and security

- Keep user screenshots, OCR exports, workbooks, private SQLite snapshots and evidence archives out of this public repository.
- Keep software, schema, tests, runbooks and non-sensitive public source links in Git.
- Run `ruff check .` and `pytest -q` for software changes.
- Verify GitHub Actions against the exact commit intended for merge.
- PR #10 (Dependency Review) is not merge-ready as of 2026-11-03: the latest Dependency Review run reports that the repository's Dependency Graph must be enabled, and the PR base predates current `main`. Enable Settings → Security & analysis → Dependency graph, then rebase/recreate the PR against current `main` and rerun checks. Do not merge until both the repository prerequisite and CI are green.

## 7. Release criteria

Create a new version only when it adds verified information or fixes a real quality defect. Preserve the 2026-11-02 files as an immutable baseline. A future release must include a versioned workbook, versioned database/bundle, source manifest, SHA-256 checksums, import report and concise change log. Validate the workbook read-back, database integrity, row counts, key uniqueness and exact commit CI before marking it complete.
