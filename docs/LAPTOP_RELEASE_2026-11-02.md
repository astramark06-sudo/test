# Private Laptop Research Release — 2026-11-02

This release note describes the current private laptop OCR/research deliverables. The workbooks, screenshots, SQLite database and evidence files remain in the user's private Library; they must not be committed to this public repository.

## Release files

| Artifact | Private Library filename | SHA-256 |
|---|---|---|
| Expanded research report (19 tabs) | `laptop_research_consolidated_2026-11-02_spec_audit_enriched_v2.xlsx` | `ec5245061b25f42613c754e503140d5536febb52f33bf3062014c1e3d930911a` |
| Reconciled master workbook (12 tabs) | `laptop_inventory_reconciled_348_reconciled_2026-11-02.xlsx` | `cfbb8fe619162c9ff865fc41bae6ef92981bdcf010fc03be5bf94f9df93d1d56` |
| Private SQLite workbench bundle | `aiops-workbench-data-bundle_reconciled_2026-11-02.zip` | `4356764bba60af8f83b1c59b25d44e9a1222f96931838949d79b56c8f4f8067f` |

The matching manifest is `OCR_RELEASE_MANIFEST_2026-11-02.txt`. The three artifact hashes were checked against that manifest on 2026-11-03.

## Workbook contents and quality metrics

### Reconciled master workbook — 12 tabs

- 348 candidate observations, retained as OCR records rather than asserted unique SKUs.
- 220 detailed listing rows.
- 215 conservative candidate/listing links.
- 133 unmatched candidate observations and five unpaired detailed listings.
- 195 OCR-observed price values carried from the detailed extraction.
- 89 configuration records, 39 CPU benchmark records and 27 research-source records.
- Four source screenshots and an 80-tile Tesseract audit (16,044 recognized words; mean confidence 79.91).

### Expanded research report — 19 tabs

The report includes the candidate register, detailed listings, configuration/benchmark records, crosswalk review, screenshot manifest and OCR regions, price evidence, manufacturer/specification research, source audit, conflict review and data dictionary.

- 348 OCR candidate rows; repeated titles are preserved as separate OCR observations.
- 220 listing rows and 199 OCR price-estimate records in the expanded price register.
- 299 screenshot-level price-evidence rows. 285 have nearby OCR text explicitly containing “Bank offer”; the numeric tokens remain raw evidence and are not automatically assigned a price role.
- 30 manufacturer/model-variant source-audit entries, nine manufacturer fact records, nine additional specification-source records and four focused official-spec cross-check profiles.
- 16 conflict-review records retained with their own evidence, status and required-resolution fields.
- 40 screenshot OCR regions from four screenshots.

The expanded workbook's 199 price-estimate records are a separate register from the 195 OCR price values carried in the reconciled master and private SQLite snapshot. Do not combine these counts or assume they are interchangeable.

## SQLite and coverage verification

The private bundle contains `aiops_platform_workbench.sqlite3`, `workbench_cli.py` and its README. The database passed SQLite `PRAGMA integrity_check` with result `ok`. The release manifest records zero unresolved OCR coverage gaps, 195 OCR prices carried into the database and zero internet-researched prices.

The final Tesseract tile was linked to existing candidate `S4-348`; it did not create a new candidate or duplicate price. This closes the previously documented OCR coverage gap. It does not resolve any laptop SKU/specification conflicts.

## Interpretation and safety rules

1. OCR prices are evidence from the screenshots, not verified current market prices.
2. Screenshot price tokens do not automatically mean sale price, MRP, card/bank offer, exchange value or EMI.
3. Candidate/listing crosswalk links are navigation/review aids, not proof of exact SKU identity.
4. Keep exact-SKU, model-family and secondary-source facts distinct.
5. Preserve unresolved conflicts and missing values. Do not infer OS, panel, RAM topology, storage, upgradeability or part number from a partial family match.
6. No internet-researched prices were added to this release.
7. Keep all private screenshots, workbooks, raw OCR, CSV exports and SQLite snapshots outside Git.

## Follow-up work

The report is delivered and its release files have passed checksum verification. Further research should focus on the 16 conflict-review records and the 133 unmatched candidate observations, without rebuilding extraction or overwriting OCR source data. Only add a specification fact when its source scope and exact model/SKU applicability are recorded. Add live prices only when explicitly requested and only in a separate researched-price field.
