# Laptop Dataset — Open Issues and Review Queue

This is the active review order for the saved private laptop research delivery. It is a process register, not a declaration that unresolved records have been fixed. Keep candidate/listing records and their raw evidence unchanged while review decisions are added.

## Priority 0 — prevent incorrect product claims

| Issue | Evidence | Required action | Do not do |
|---|---|---|---|
| HP 255R G10 R3-7335U / 8GB / 512GB | [HP exact part C8HS6AT](https://support.hp.com/in-en/product/product-specs/hp-255r-15.6-inch-g10-notebook-pc/model/2102647685?sku=C8HS6AT) lists FreeDOS 3.0; the family datasheet lists Windows 11 and FreeDOS as available OS options but does not tie Windows to C8HS6AT. | Find the actual part number or exact operating-system screenshot; separate FreeDOS and Windows variants | Assign C8HS6AT to a Windows listing based only on CPU/RAM/SSD |
| MSI Modern 14 R5-7430U / 8GB / 512GB | [India C7M-400IN sheet](https://storage-asset.msi.com/specSheet/in/bnp/Modern%2014%20C7M-400IN.pdf) is 16GB DDR4 onboard. MSI also publishes [Indonesia C7M-406ID](https://storage-asset.msi.com/specSheet/id/bnp/Modern%2014%20C7M-406ID.pdf) with the same R5-7430U/512GB and 8GB onboard, but that sheet is for a different country SKU. | Locate the seller's exact part number and country SKU; retain the 8GB-vs-16GB conflict until it is tied to the listing. | Change the OCR 8GB or label the listing C7M-400IN/C7M-406ID without exact evidence. |
| Acer Aspire Lite R3-7330U / 8GB / 512GB | [Acer India official store](https://store.acer.com/en-in/acerday-nongaming/total_ssd_capacity-512_gb) lists AL15-41 reference UN.31ZSI.06P (8GB DDR4, 512GB SSD, 1.59kg) and AL15-42 reference UN.378SI.00D (8GB DDR4, 512GB SSD, 1.65kg). The family codes and product references differ. | Match the actual part/reference number and preserve the AL15-41/AL15-42 distinction. | Copy weight, display or other chassis-specific details between variants. |
| Acer Aspire 3 R3-5300U vs R3-5400U | A325-42 appears in official Acer store records for both processors under different reference codes (UN.34QSI.018 vs UN.34QSI.00X / UN.34QSI.00Z) | Require the exact processor and Acer reference; preserve panel, memory and storage variant | Normalize 5300U and 5400U as the same model |
| Acer Aspire Lite AL15-41 R3-5400U vs R3-7330U | Official store indexes both CPU/storage combinations under different references | Confirm CPU and 256GB/512GB drive before selecting the part | Assume same AL15-41 implies same internals |
| Lenovo V15 G4 AMN R3-7320U / 8GB / 512GB | [Lenovo PSREF 83CQ000BIN](https://psref.lenovo.com/Detail/Lenovo_V15_G4_AMN?M=83CQ000BIN) and [PSREF 83CQ000NIN](https://psref.lenovo.com/Detail/Lenovo_V15_G4_AMN?M=83CQ000NIN) both specify 8GB soldered LPDDR5-5500, 512GB SSD, 38Wh and FHD TN 250-nit panel; BIN lists Windows 11 Pro, while NIN lists Windows 11 Home Single Language. | Obtain exact MTM from listing/label and use its PSREF page; preserve the OS/licence difference. | Apply one MTM's OS, display or service facts to all V15 G4 AMN units. |
| Motorola title fragment "Motobook 6" | Current Moto Book 60 and Moto Book 60 Pro product names exist, but the OCR title is truncated | Recover full title, CPU, RAM/storage and SKU from original screenshot/retailer listing | Infer Moto Book 60/Pro from the price or truncated title |
| Final OCR audit tile | Tesseract output contains clipped listing-like text without safe identity | Inspect the original crop and adjacent tile boundaries; create a record only if identity and context are visible | Attach a product or price to the clipped fragment |

## Priority 1 — complete the conservative reconciliation

Baseline counts from the saved release manifest:

- 348 OCR candidate IDs.
- 220 detailed listing extraction rows.
- 215 conservative links.
- 133 OCR candidates without a detailed-listing link.
- Five detailed listing rows without a candidate link.

Review steps:

1. Check exact candidate and listing identifiers first.
2. Inspect screenshot ID and top-pixel coordinate to distinguish adjacent product cards and overlapping OCR crops.
3. Compare brand, full processor suffix, RAM capacity and storage together.
4. Keep two records separate where offer/configuration context differs, even if their titles are nearly identical.
5. Add review status and evidence references to every decision.
6. Preserve ambiguous candidates and unpaired listing rows; do not optimize the unmatched count at the expense of false joins.

## Priority 2 — configuration and source conflicts

| Product family / candidate | Current evidence | Review action |
|---|---|---|
| Samsung Galaxy Book4 NP750XGJ-LG9IN | Samsung India page specifies i3-1315U, 8GB onboard LPDDR4x and 512GB NVMe | Use only when the candidate title/config matches; record onboard RAM limitation |
| Dell 15 DC15255 | Dell India lists R5-7520U, 8GB LPDDR5 onboard and 512GB M.2 2230 option; multiple display/OS options | Keep model family scoped unless exact part number and display/OS option appear |
| ASUS ExpertBook P1 P1503 | ASUS lists Core 3 100U, 8GB SO-DIMM and 512GB storage options; exact submodel may vary | Match the full P1503 part number before asserting complete configuration |
| ASUS Vivobook Go 15 E1504F | Ryzen 3 7320U / Ryzen 5 7520U and onboard memory variants exist; standard FHD and OLED options differ | Do not assume OLED from family name or processor alone |
| Neopticon EBook 11.6 | Manufacturer page states 128GB eMMC plus an M.2 expansion slot | Resolve OCR "SSD + eMMC" wording; expansion slot is not proof of a second preinstalled drive |
| Neopticon BrowseBook 14.1 | Manufacturer page/card variants show different RAM/storage; content also has repeated/inconsistent card fragments | Capture the exact selected variant and preserve source-page inconsistencies |
| Primebook WiFi vs 4G | Manufacturer brochure separates MT8183 WiFi from MT8788 4G; both are 4GB LPDDR4 PrimeOS systems | Keep cellular and WiFi variants separate |
| JioBook 11 | Secondary listing supports NB1112MMBLU / MT8788 / 4GB / 64GB / JioOS; Jio support page is software-focused | Retain listing as secondary evidence; exact part number must be visible for SKU match |
| Ultimus Apex Pro | Marketplace listing gives N4200, 4GB DDR3, 128GB SSD + 128GB eMMC, Windows 11, 14.1 HD and a part-number lead | Use as secondary listing-level evidence; require part-number match |
| Thomson NEO 3K / IN-K14C | N5100/QHD+ facts were found on a retailer-style page, not an authoritative manufacturer datasheet | Keep low confidence and seek official model/service documentation |

## Priority 3 — benchmark and price evidence

- The CPU benchmark register has 39 rows. Review missing scores and retain score type, source, date and confidence. Never carry a score across processor suffixes or generations.
- The source register has 27 rows. Add current official URLs and retrieval timestamps for any accepted fact updates.
- The saved workbook carries 195 OCR-observed price values. Preserve them as historical OCR evidence.
- Do not add current market prices unless separately requested. If added in a future task, record exact SKU match status, seller, observation date, amount type and offer conditions.
- A model's manufacturer page may prove a specification while showing no current sale price or no longer being sold online. Keep these concepts separate.

## Review completion criteria

An issue is resolved only when the evidence directly answers it, the exact identity scope is recorded, and source provenance is attached. Otherwise use a clear status such as `unresolved`, `family_only`, `conflicting_sources`, or `secondary_source_only`. The goal is defensible coverage, not a 100% filled spreadsheet.
