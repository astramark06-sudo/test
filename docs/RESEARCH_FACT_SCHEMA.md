# Research Fact and Price Evidence Schema

Use this convention for future laptop-spec and price enrichment. It is a documentation contract for new research rows; it does not imply that every historical row already contains every field.

## 1. Identity hierarchy

Record the strongest identity level supported by the evidence:

1. **Exact SKU / part number / MTM** — manufacturer part number, product number, service tag family, or Lenovo MTM tied to the listing.
2. **Exact model number** — model number is visible and maps to one hardware configuration.
3. **Model family** — e.g. Aspire 3, HP 15, IdeaPad Slim 3. Family-level facts must not be written into exact-SKU fields.
4. **Platform / processor only** — CPU or chipset identified but chassis/configuration remains unresolved.
5. **Unresolved** — insufficient evidence to identify the product.

Recommended fields:

| Field | Meaning |
|---|---|
| `Candidate_ID` | Stable OCR candidate key, when one exists |
| `Listing_Record_ID` | Stable detailed listing key, when one exists |
| `Brand` | Manufacturer/brand as evidenced |
| `Model_Family` | Family name; do not use as exact SKU |
| `Model_Number` | Printed model number, separate from family name |
| `SKU_Part_Number_MTM` | Manufacturer or seller SKU/part/MTM |
| `Identity_Level` | One of the five levels above |
| `Identity_Evidence` | Text/image location establishing identity |
| `Match_Status` | Exact, provisional, ambiguous, conflicting, unresolved |
| `Review_Required` | Boolean or explicit review status |

## 2. One row per independently sourced fact

Do not flatten conflicting sources into one cell. Store one fact per attribute per source, with enough information to compare evidence later.

| Field | Meaning |
|---|---|
| `Spec_Fact_ID` | Stable unique fact key |
| `Candidate_ID` / `Listing_Record_ID` | Link back to OCR/listing evidence |
| `Identity_Level` | Scope of the matched laptop identity |
| `Attribute` | CPU, GPU, RAM capacity, RAM type, RAM slots, display, brightness, gamut, storage, battery, weight, ports, OS, warranty, etc. |
| `Value_Raw` | Exact source wording/value |
| `Value_Normalized` | Comparable normalized value; blank if ambiguous |
| `Unit` | GB, Wh, kg, nit, MHz, inch, etc. |
| `Source_URL` | Direct URL for this fact |
| `Source_Title` | Page/document title |
| `Source_Type` | Manufacturer product page, datasheet, service manual, retailer listing, benchmark database, etc. |
| `Source_Scope` | Exact SKU, model number, family, or generic platform |
| `Retrieved_At` | Date/time checked, with timezone |
| `Match_Method` | Part-number lookup, exact model search, family inference, OCR text match, etc. |
| `Confidence` | High, medium, low, with a reason |
| `Conflict_Group` | Shared key for contradictory values |
| `Review_Status` | Pending, accepted, rejected, superseded, or conflict |
| `Notes` | Caveats and source limitations |

## 3. Price evidence is a separate record type

Never store a single generic `Price` field for all commercial amounts. A captured listing may contain an MRP, sale price, bank offer, coupon, exchange bonus, EMI, or unrelated number in the same OCR block.

Recommended fields:

| Field | Meaning |
|---|---|
| `Price_Evidence_ID` | Stable evidence key |
| `Candidate_ID` / `Listing_Record_ID` | Link to the source listing |
| `Price_Raw` | Exact OCR or page text |
| `Price_Amount` | Parsed numeric amount only when unambiguous |
| `Currency` | INR, etc. |
| `Price_Type` | MRP, sale/list price, bank/card offer, coupon, exchange, EMI, unknown |
| `Seller` | Named marketplace/seller |
| `Offer_Conditions` | Card, coupon, exchange, membership, quantity or tenure conditions |
| `Source_URL` | Direct listing URL for researched prices |
| `Observed_At` | Capture/check timestamp |
| `SKU_Match_Status` | Exact, family-only, ambiguous, unresolved |
| `Confidence` | Evidence-based confidence |
| `Review_Reason` | Why interpretation is uncertain |

Rules:

- Preserve the original OCR price cell and source context unchanged.
- A price token with ambiguous role stays in `Price_Raw`; leave `Price_Amount` blank.
- A researched live price must have a URL, seller, observation date and SKU-match status.
- Bank, exchange and coupon reductions are conditional amounts, never the base sale price.
- Do not compare prices across different configurations without making the RAM/storage/SKU difference explicit.
- Prices are time-sensitive. Recheck before presenting them as current.

## 4. CPU benchmark record requirements

Keep benchmark identity separate from laptop model identity. Require exact processor naming and preserve:

- CPU marketing name and exact suffix
- Benchmark source and direct URL
- Score type (multi-core/CPU Mark versus single-thread)
- Numeric score and units/scale
- Date checked or benchmark snapshot date
- Test version when supplied
- Confidence and any sample/variance caveat

No score inheritance from a similarly named CPU or from a different suffix/generation.

## 5. Conflict resolution

A conflict is not solved by picking the newest, highest, or most convenient number automatically.

1. Keep both source facts and URLs.
2. Compare identity scope first: an exact-SKU datasheet should not be conflated with a family-wide specification.
3. Check whether differences may represent separate SKUs, regional variants, panel options, memory layouts, seller substitutions, or revisions.
4. Record an adjudication row with the selected value, reason, reviewer/date and rejected alternatives.
5. If scope cannot be resolved, retain both facts and mark the attribute unresolved.

## 6. Spreadsheet / database implementation guidance

Use separate tabs or tables for candidates, detailed listings, crosswalk decisions, specification facts, price evidence, CPU benchmarks, sources, screenshots/regions, unresolved conflicts and data dictionary. Keep stable IDs across exports. Every derived value should retain a link to raw evidence and a provenance record.

For spreadsheet outputs, include a quality/coverage sheet with source counts, matched/unmatched/ambiguous totals, missing critical identity fields, duplicate keys, unverified price tokens and unresolved conflicts. Read the saved workbook back before delivery and compare row counts against its input registers.
