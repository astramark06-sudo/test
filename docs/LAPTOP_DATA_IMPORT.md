# Laptop research bundle import

> **Version scope — intermediate importer profile.** The table below documents an earlier CSV export profile from 2026-11-01, including an `ocr_prices` dataset of 199 rows and 299 raw screenshot price-evidence rows. The final Library delivery is a later 12-tab workbook that carries 195 OCR-observed price values. These are distinct artifact versions and row definitions; do not treat 199 and 195 as interchangeable or combine the exports. The exact final CSV-to-workbook reconciliation remains a next-session data-analysis check. For the authoritative saved release inventory and validation order, see [Laptop dataset runbook](LAPTOP_DATASET_RUNBOOK.md) and [Next analysis session checklist](NEXT_ANALYSIS_SESSION_CHECKLIST.md). Run the importer with `--dry-run` against a versioned copy of the intended CSV bundle before any database write.

The importer accepts the original source CSVs plus the derived OCR and manufacturer evidence exports. It stores each complete row as JSON in SQLite so source columns remain recoverable.

## Import

```bash
python scripts/ingest_research_bundle.py /path/to/private/laptop_research_bundle/csv \
  --db ./data/laptop_research.sqlite
```

The importer is idempotent for datasets with stable key fields. Files without a stable key use a deterministic row-content hash.

## Datasets — intermediate CSV export profile

| Dataset | Key | Expected records in that intermediate export |
|---|---|---:|
| laptop_candidates | Candidate_ID | 348 |
| extracted_listings | Listing_Record_ID | 220 |
| configurations | row-content hash | 89 |
| configurations_with_benchmarks | row-content hash | 89 |
| cpu_benchmarks | CPU | 39 |
| research_sources | URL | 27 |
| candidate_crosswalk | Candidate_ID | 348 |
| ocr_prices | Listing_Record_ID | 199 |
| manufacturer_spec_facts | Spec_Fact_ID | 9 |
| manufacturer_spec_sources | URL | 9 |
| screenshot_manifest | Screenshot_ID | 4 |
| screenshot_ocr_regions | Region_ID | 40 |
| ocr_price_evidence | Evidence_ID | 299 |
| verified_official_specs | Spec_Fact_ID | 4 |
| data_dictionary | row-content hash | 87 |

Counts are expected for this specific intermediate export profile. New source bundles can have different counts.

## Evidence interpretation

- 348 candidate records are OCR observations, not 348 unique verified laptop models.
- The 220 older extracted listings are retained separately. The crosswalk uses text similarity for review only; it does not establish exact SKU identity.
- The 199-row `ocr_prices` table is from the intermediate extraction profile. Do not substitute that row count for the final workbook's 195 carried OCR-observed price values.
- The 299 screenshot price-evidence rows preserve raw amount tokens and nearby context. They are not assigned to listings automatically and are not live marketplace prices.
- Bank-offer values are captured separately only where OCR explicitly reads a nearby “Bank offer” label.
- Manufacturer specifications carry family/SKU scope caveats. Do not apply family facts to a listing without matching its exact SKU/configuration.

Keep the CSVs, screenshots, workbook and SQLite database in private/local storage. Do not commit these user research artifacts, images, databases or credentials to the public repository.
