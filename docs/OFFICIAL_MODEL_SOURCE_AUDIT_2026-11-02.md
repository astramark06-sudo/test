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


## 6. Samsung Galaxy Book4 — NP750XGJ-LG9IN

**Official source:** Samsung India, Galaxy Book4 15.6-inch, Core i3 / 8GB / 512GB  
https://www.samsung.com/in/computers/galaxy-book/galaxy-book4-15-6-inch-13th-i3-8gb-512gb-np750xgj-lg9in/

Samsung's India page identifies the exact product code NP750XGJ-LG9IN with Intel Core i3-1315U, 8GB onboard LPDDR4x, 512GB NVMe SSD, and a 15.6-inch FHD IPS anti-glare display.

**Disposition:** This is an exact manufacturer SKU/configuration reference. Match the OCR candidate to it only where the model name, CPU and 8GB/512GB configuration agree; retain the Samsung part code as the identifier. The memory is onboard, not a removable SO-DIMM.

## 7. ASUS Vivobook Go 15 — E1504F family, Ryzen 5 7520U / Ryzen 3 7320U

**Official source:** ASUS India technical specifications  
https://www.asus.com/in/laptops/for-home/vivobook/vivobook-go-15-oled-e1504f/techspec/

ASUS lists both Ryzen 5 7520U and Ryzen 3 7320U configurations in this family. The 8GB variants use onboard LPDDR5 with a maximum total system memory of 8GB; the page also lists 512GB M.2 NVMe PCIe 3.0 storage options. The family's display options include ordinary FHD anti-glare and materially different OLED options. Do not assign the OLED panel to an OCR record that only says FHD.

**Disposition:** This source can support the CPU/memory/storage/platform facts when the exact E1504F family and configuration are confirmed. It does not prove that a generic “Vivobook Go 15” screenshot is a specific part number or has the OLED option.

## 8. Lenovo V15 G4 AMN — Ryzen 3 7320U, 8GB / 512GB

**Official source:** Lenovo PSREF, V15 G4 AMN, machine type/model 83CQ000BIN  
https://psref.lenovo.com/Detail/Lenovo_V15_G4_AMN?M=83CQ000BIN

This exact PSREF record specifies Ryzen 3 7320U (4C/8T), integrated Radeon 610M, 8GB soldered LPDDR5-5500 dual-channel memory with no memory slots and no upgrade path, 512GB M.2 2242 PCIe 4.0x4 NVMe SSD, 15.6-inch FHD TN 250-nit anti-glare display, 38Wh battery and non-backlit keyboard.

**Suffix warning:** Another V15 G4 AMN MTM (for example, 83CQ000NIN) is a distinct part-number record and must be checked separately. Do not copy the 83CQ000BIN specification set to an OCR listing without the machine type/model.

## 9. MSI Modern 14 C7M — Ryzen 5 7430U, 16GB / 512GB

**Official source:** MSI India, Modern 14 C7X family specification comparison  
https://in.msi.com/Business-Productivity/Modern-14-C7X/Specification

MSI's own variant comparison lists Modern 14 C7M-400IN with Ryzen 5 7430U, 16GB DDR4-3200 onboard memory and 512GB NVMe PCIe Gen3 SSD. The same page lists other C7M SKUs with different CPUs and memory sizes, including 8GB variants for other CPU options.

**Disposition:** The existing research row that combines Ryzen 5 7430U with 8GB/512GB has an explicit manufacturer-spec conflict: C7M-400IN is 16GB. Do not silently change the OCR 8GB value or claim C7M-400IN is the exact listing. The CPU/family match is not enough; exact SKU or seller configuration evidence is required.


## 10. Neopticon EBook and BrowseBook — official brand pages

**Official sources:**
- EBook 11.6-inch: https://neopticon.com/ebook/
- BrowseBook 14.1-inch product page: https://neopticon.com/product/neopticon-browsebook-14-1-fhd-ips-laptop-intel-celeron-n4020-dual-core-up-to-2-8ghz-4gb-ram-256gb-ssd-intel-uhd-graphics-windows-11-home-38wh-1-3kg-grey/
- Current product-family listing: https://neopticon.com/product-specification/

The EBook 11.6 page describes Celeron N4020, 4GB DDR4, 128GB eMMC, an M.2 SSD expansion slot, 11.6-inch HD display, Windows 11 Home, 31Wh battery and 1.1kg. This differs from OCR wording that can be read as "128GB SSD + 128GB eMMC"; treat the M.2 slot as expansion capability, not evidence of a second preinstalled 128GB SSD.

The BrowseBook 14.1 page describes Celeron N4020, 4GB DDR4, 128GB SSD, FHD IPS display, Windows 11 Home and 1.3kg. The current family listing also shows 8GB RAM and 256GB SSD BrowseBook variants. The family page therefore supports multiple configurations, but the product page's 4GB configuration must not be substituted for an OCR listing that says 8GB.

**Disposition:** Manufacturer pages support the model families and available variant ranges. Match RAM/storage to the exact displayed option before updating the workbook. Source page content has some inconsistent repeated product-card fragments; keep each fact tied to the relevant product card and exact variant rather than treating the entire page as one SKU.

## 11. Primebook WiFi / 4G — MT8183 versus MT8788

**Manufacturer sources:**
- Primebook WiFi store listing: https://shop.primebook.in/products/primebook-wifi
- Primebook 4G/WiFi technical brochure (PDF): https://primeos.s3.ap-south-1.amazonaws.com/PrimebookProductPPT_V1.pdf
- Primebook FAQ: https://www.primebook.in/faq
- Primebook product comparison article: https://www.primebook.in/blog/best-laptops-for-students-under-inr-15000-primebook

The original Primebook brochure explicitly separates MT8183 on the WiFi model from MT8788 on the 4G model. It specifies 4GB LPDDR4, 64GB/128GB eMMC, 11.6-inch 720p IPS, PrimeOS 2.3 A11 (Android), and microSD expansion; the WiFi and 4G versions have different cellular capability. Do not merge the two chipset configurations. More recent Primebook Max models are a different hardware generation and must not be used to fill the older WiFi model.

**Disposition:** For an OCR row titled Primebook WiFi with MT8183 and 4GB/64GB, the family/variant is strongly supported. Preserve 64GB versus 128GB as separate variants; the original brochure is historical and should not be used to assert a current OS release or current battery life without a recent exact-product source.

## 12. JioBook 11 — model NB1112MMBLU / MT8788

**Sources:**
- JioBook official support: https://www.jio.com/jiobook/support/
- JioMart product listing: https://www.jiomart.com/product/jiobook-11-with-lifetime-officeandroid-4g-laptop-mediatek-8788-jioosoctacore4gb-ram64-emmc-storagethin-and-light-laptop-116-inch-990-gramsdual-band-wifi-simblue-mfqiog-7628646/
- Secondary listing with model/part number: https://www.flipkart.com/jio-jiobook-11-jioos-lifetime-office-mediatek-mt8788-4-gb-64-gb-emmc-storage-android-11-nb1112mmblu-thin-light-laptop-inbuilt-4g-lte/p/itm5e242fe9ed52d

The seller listings identify JioBook 11 / NB1112MMBLU with MediaTek MT8788, 4GB LPDDR4, 64GB eMMC, 11.6-inch 1366x768 display, JioOS/Android, built-in 4G LTE, microSD expansion and approximately 990g. Jio's official support page confirms the JioBook ecosystem, JioStore, JioSphere browser and SoftMaker Office suite, but is not a detailed hardware datasheet.

**Disposition:** The OCR row with MT8788 / 4GB / 64GB / JioOS is a strong family/configuration match. Use NB1112MMBLU only when the blue 4G variant/part number is visible or independently confirmed; retailer records should be identified as secondary sources, not manufacturer specifications.

## 13. Ultimus Apex Pro — N4200 exact listing lead

**Secondary source:** Flipkart listing for Ultimus Apex Pro, model NU14U8INC54LS-SG / part number NU14U8INB54LS-SG  
https://www.flipkart.com/ultimus-apex-pro-intel-pentium-quad-core-n4200-4-gb-128-gb-ssd-128-emmc-storage-windows-11-home-nu14u8inc54ls-sg-laptop/p/itm57488f91f02c8

The listing identifies Pentium N4200, 4GB DDR3, 128GB SSD plus 128GB eMMC, Windows 11 Home, and a 14.1-inch 1366x768 display. It names the model Apex Pro FU06.

**Disposition:** This is a strong listing-level lead for the OCR Apex Pro candidate because processor and storage wording are unusually specific. Since the source is a marketplace page rather than an official manufacturer support page, retain it as secondary evidence and require the model/part number match before treating it as exact-SKU verification.

## 14. Motorola "Motobook 6" — title normalization remains unresolved

**Official Motorola source for the current product family:**  
https://www.motorola.in/laptop-moto-book-60-pro-core-5/p

Motorola's current product navigation explicitly names Moto Book 60 Pro Core 5 and Core 7 as laptop models. Other launch-era coverage describes the distinct original Moto Book 60 with Core 5 210H / Core 7 240H, 16GB DDR5 and 512GB/1TB storage configurations.

**Disposition:** OCR text "Motorola Motobook 6" may be a clipped or truncated reference to "Moto Book 60", but that is only a title-normalization hypothesis. A detected price near ₹76,990 is not identity evidence. Do not assign either Moto Book 60 or Moto Book 60 Pro specifications to this candidate until the full title, processor, RAM/storage and SKU are visible. Keep the OCR row unresolved.

## 15. Thomson NEO 3K / IN-K14C — secondary-source-only lead

**Secondary source:**  
https://www.savekarloo.com/product/thomson-141-inch-3k-high-resolution-display-in-k14c-intel-celeron-b0dyvtlp29

A retailer-style product page associates model IN-K14C with Intel Celeron N5100, 8GB LPDDR4, 256GB SSD and a 14.1-inch 3000×2000 QHD+ display. No sufficiently authoritative current manufacturer datasheet was identified in this audit.

**Disposition:** This may be used as a low-confidence research lead only. The workbook's NEO 3K family row should retain OCR-sourced display/storage facts and clearly label every detail obtained from this secondary page. Do not elevate it to verified SKU status without a manufacturer model sheet or service manual.
