# Official Laptop Model Source Audit — 2026-11-02

This note records current manufacturer-source checks that can improve the existing family/configuration register. These are **source-scope updates**, not automatic assertions that an OCR listing is an exact SKU. No price values are captured here.

## 1. Acer Aspire Lite — Ryzen 3 7330U, 8GB, 512GB

**Official source:** Acer India Store, Aspire Lite AL15-41, product reference UN.31ZSI.05L  
https://store.acer.com/en-in/acer-aspire-lite-amd-ryzen-3-7330u-processor-8-gb-ram-512-gb-ssd-full-hd-ips-15-6-39-62-cm-windows-11-home-steel-gray-1-59-kg-al15-41-backlit-keyboard-thin-and-light-laptop-1

The official product result identifies Ryzen 3 7330U, 8GB RAM, 512GB SSD, 15.6-inch FHD IPS display, Windows 11 Home and 1.59kg for AL15-41 (UN.31ZSI.05L). It specifies 8GB dual-channel DDR4 memory, two SODIMM slots and support up to 32GB; 512GB PCIe Gen3 NVMe storage; and 36Wh battery.

**Cross-check:** Acer also lists AL15-42 variants with Ryzen 3 7330U and different weight/storage configurations. Do not transfer AL15-41 details to AL15-42 or use a family name alone to claim the exact SKU.

**Disposition:** The existing OCR/configuration entry “Acer Aspire Lite Metal / Ryzen 3 7330U / 8GB / 512GB” is strongly consistent with the AL15-41 configuration. Exact marketplace identity remains provisional because the OCR evidence does not provide the Acer part number. The source confirms a configuration; it does not prove the source listing is this exact Acer SKU.

## 2. HP 255R G10 — Ryzen 3 7335U, 8GB, 512GB

**Official source:** HP Support India, HP 255R G10 R3-7335U 15 8GB/512 PC, product number C8HS6AT  
https://support.hp.com/in-en/document/ish_13384261-13384288-16

HP's exact-product support record identifies Ryzen 3 7335U, 8GB DDR5-4800 memory, 512GB PCIe NVMe SSD, Radeon 660M graphics, 15.6-inch FHD 250-nit 45% NTSC display, 41Wh battery and starting weight of 1.66kg. The exact product record lists FreeDOS 3.0.

**Important conflict:** A retailer description for this part number has described Windows 11, while HP's exact-product page lists FreeDOS 3.0. The existing research family register includes Windows 11 for an HP 255R G10 configuration. Do not associate C8HS6AT with a Windows 11 OCR listing unless the operating-system identity is resolved. HP's family datasheet also warns that memory slots may be non-customer-accessible; don't label the RAM user-upgradeable based on the presence of two SODIMMs alone.

**Disposition:** CPU/RAM/storage/display evidence for C8HS6AT is strong for that HP part number. The user's OCR record is not proven to be C8HS6AT; operating-system mismatch is a review flag. Keep Windows/FreeDOS variants separate.

## 3. Dell 15 DC15255 — Ryzen 5 7520U, 8GB, 512GB

**Official source:** Dell India, Dell 15 Laptop DC15255  
https://www.dell.com/en-in/shop/shop-all-deals/dell-15-laptop/spd/dell-dc15255-laptop

Dell lists the Ryzen 5 7520U among supported DC15255 processor options. Its India product specification lists 8GB LPDDR5-5500 onboard memory for this processor option and 512GB M.2 PCIe NVMe SSD options. The family has more than one 15.6-inch FHD panel option, including differences in brightness, touch support and refresh rate.

**Disposition:** The OCR/configuration combination “Dell 15 / Ryzen 5 7520U / 8GB / 512GB” is consistent with the DC15255 family. The exact Dell model/part number and display option are not proven by a CPU/RAM/storage match alone. Do not describe the RAM as upgradeable; it is onboard LPDDR5 for the cited configuration.

## 4. ASUS ExpertBook P1 P1503 — Intel Core 3 100U

**Official sources:**
- ASUS India ExpertBook P1 P1503 technical specifications: https://www.asus.com/in/laptops/for-work/expertbook/expertbook-p1-p1503/techspec/
- ASUS India P1503 availability/model listing: https://www.asus.com/in/laptops/for-work/expertbook/expertbook-p1-p1503/wheretobuy/

ASUS lists Intel Core 3 100U (6 cores / 8 threads) as a P1503 processor option, with 8GB DDR5 SO-DIMM and 512GB M.2 NVMe options in the family specification. The family also includes multiple display and configuration choices. ASUS's India availability page lists Core 3 100U sub-models including P1503CVA-S72562WS and P1503CVA-S72563WS, but the OCR listing does not contain sufficient part-number evidence to select one.

**Disposition:** P1503 is a supported model-family candidate for an ExpertBook P1 Core 3 100U listing. Do not assert either sub-model as the exact OCR SKU until its memory, storage, OS and listing identifiers are matched.

## 5. Lenovo IdeaPad 1 15ALC7 — Ryzen 5 5500U

**Official source:** Lenovo PSREF, IdeaPad 1 15ALC7  
https://psref.lenovo.com/Product/IdeaPad/IdeaPad_1_15ALC7

Lenovo's PSREF model-family material includes Ryzen 5 5500U variants and multiple machine types/models. Component details vary by MTM.

**Disposition:** This establishes that the CPU/model-family combination exists, not that a particular OCR listing is an IdeaPad 1 15ALC7 or that the memory, display, battery or storage match a particular MTM. Require the Lenovo MTM before treating the listing as an exact configuration.

## Price handling

This audit does not capture current retail prices. The existing workbook's 195 OCR-observed price values remain historical OCR evidence, not validated selling prices. Future price research must record the exact listing URL, seller, timestamp, price type (base sale, MRP, bank/card offer, coupon, exchange or EMI), conditions and exact-SKU match status. Do not use a promotional amount from a family page as the researched price for a marketplace OCR record.

## Sources and checking method

Manufacturer product pages/support records and Lenovo PSREF are preferred over retailer aggregators. Dynamic pages may change by region and SKU. A manufacturer page can prove that a configuration exists while still not proving that an OCR row refers to that exact part number. The workbook should retain the distinction among exact SKU, model number, model family, platform-only and unresolved identities.
