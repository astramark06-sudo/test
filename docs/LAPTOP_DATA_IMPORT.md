# Laptop research bundle import

The importer accepts the original source CSVs plus the derived OCR and manufacturer evidence exports. It stores each complete row as JSON in SQLite so source columns remain recoverable.

## Import

```bash
python scripts/ingest_research_bundle.py /path/to/private/laptop_research_bundle/csv \
  --db ./data/laptop_research.sqlite
```

The importer is idempotent for datasets with stable key fields. Files without a stable key use a deterministic row-content hash.

## Datasets

| Dataset | Key | Expected records in the 2026-11-01 bundle |
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

Counts are expected for this specific research-bundle version. New source bundles can have different counts.

## Evidence interpretation

- 348 candidate records are OCR observations, not 348 unique verified laptop models.
- The 220 older extracted listings are retained separately. The crosswalk uses text similarity for review only; it does not establish exact SKU identity.
- The 199 OCR prices remain estimates from the earlier listing extraction.
- The 299 screenshot price-evidence rows preserve raw amount tokens and nearby context. They are not assigned to listings automatically and are not live marketplace prices.
- Bank-offer values are captured separately only where OCR explicitly reads a nearby “Bank offer” label.
- Manufacturer specifications carry family/SKU scope caveats. Do not apply family facts to a listing without matching its exact SKU/configuration.

Keep the CSVs, screenshots, workbook and SQLite database in private/local storage. Do not commit these user research artifacts, images, databases or credentials to the public repository.
