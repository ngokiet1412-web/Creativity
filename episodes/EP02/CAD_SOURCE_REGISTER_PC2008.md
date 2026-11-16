# CAPY BK / EP02 — PC200-8 CAD source register
**Date checked:** 2026-11-16
**Status:** LINKS + VERIFIED PUBLICLY PUBLISHED DIMENSIONS ONLY. No CAD asset purchased, no STEP/PRT uploaded, no licensed manual or model copied. This does **NOT** certify an exact PC200-8 assembly. Source of dimensions: specific PC200-8/PC200LC-8 brochure rather than -8M0.

## S01 — KOMATSU brochure (PRIMARY for product dimensions)
- URL: https://d3is8fue1tbsks.cloudfront.net/PDF/Komatsu/PC200-8_PC200LC-8.pdf
- Title: Komatsu PC200-8/PC200LC-8, brochure code CEN00049-08, printed 2012-05. Cross-check actual machine generation/config/serial.
- Page **10–11 printed**, PDF spread page index **5 zero-based**: major dimensions, standard hydraulic cylinder bore/stroke/rod dimensions, working envelope. Original source is a **brochure**, not a manufacturing drawing.
- **Boom:** standard 5700 mm as listed in brochure optional equipment (page front); this is NOT pin-center distance.
- **Arm options:** 1840, 2410, 2925 mm (configuration must be chosen).
- **Boom cylinder:** 2 units, bore 120 mm / stroke 1334 mm / rod 85 mm.
- **Arm cylinder:** 1 unit, bore 135 mm / stroke 1490 mm / rod 95 mm.
- **Bucket cylinder** for 2410/2925 mm arm: 1 unit, bore 115 mm / stroke 1120 mm / rod 80 mm; **1840 mm arm has DIFFERENT cylinder** (125 x 1110 x 85 mm).
- **Main hydraulic pump:** variable displacement piston type, maximum flow 439 L/min stated as system reference, not cylinder motion measurement.
- **Dimensions available**: machine overall and operating envelope. See page graphic; use as silhouette/scale constraints, **not** as complete joint geometry.
- **Unknown:** coordinates of boom base, boom-stick joint, bucket linkage, cylinder anchor pins, rod assembly closed length, boom web profile, individual bucket linkage lengths and offsets. NEVER infer these as measured OEM dimensions.
- **DO NOT:** upload brochure PDF to public repo; store only link and independently derived limited factual values with source note.

## S02 — TraceParts catalog (GENERIC component shapes, NOT PC200 OEM)
- URL: https://www.traceparts.com/en/search/traceparts-classification-hydraulics-hydraulic-cylinders?CatalogPath=TRACEPARTS%3ATP07002
- Purpose: reference for generic hydraulic cylinder construction, CAD modeling strategy and optional legally licensed STEP geometry. Model listings and licenses must be checked per specific component before use.
- No verified matching Komatsu PC200-8 OEM STEP is available from this link. Do not claim it matches source cylinder or that any downloaded generic STEP is a Komatsu replacement.

## S03 — GrabCAD Community (DISCOVERY ONLY)
- URL: https://grabcad.com/library
- Terms: https://help.grabcad.com/article/246-how-can-models-be-used-and-shared
- User CAD models are generally for private use. Commercial public use requires explicit permission from original creator and attribution. For this YouTube/TikTok channel with potential monetization, **do not import/publish without a per-file license clearance**.
- Do NOT mirror/download community files into this public repo by default. No specific PC200-8 model or authentic construction has been accepted.

## S04 — CGTrader exterior render mesh (PAID, NOT ACQUIRED)
- Listing: https://www.cgtrader.com/3d-models/industrial/industrial-machine/komatsu-pc200-8-excavator-pbr
- Seller: docamb, listed at **USD 57** when checked 2026-11-16 (may change).
- Seller claims 443,637 polygons, Blender/FBX/OBJ formats, 4K PBR maps; **not rigged** and no CAD/NX feature tree. It is a *visual mesh*, not an OEM dimensional CAD source.
- Listing states “two parts main body and interior ... can separate any part”. That is not proof every pin and cylinder can be rigged correctly. Verify license and actual separation after authorized purchase.
- Licensing reference: https://help.cgtrader.com/hc/en-us/articles/360015124437-Royalty-Free-License ; terms allow rendered imagery under RF model rules but prohibit redistributing underlying mesh. Check exact listing's rights, including any editorial/AI exclusions, before purchase.
- **No purchase approved. DO NOT download, redistribute, or treat as an NX CAD source.**

## S05 — NXOpen / journal workflow (RUNTIME ONLY AFTER LICENSE CHECK)
- Siemens community reference for Python NXOpen journals (version-dependent): https://siemens-en-sandbox-community.insided.com/designcenter-open-43/how-to-execute-or-run-nx-custom-tool-developed-using-python-nxopen-api-208895
- Use NX's built-in Python Journal (menu varies) or `run_journal.exe` only after verifying local Siemens NX installation/version/license. No third-party NX MCP/server required for initial proof.
- Do not install unreviewed “NX agent skill” or scripts from external repos just because available; use documentation to guide locally authored journal source.

## Provenance / confidence grades
- **VERIFIED-PUBLIC:** claimed by source brochure, checked on exact PC200-8 document; still configuration-specific.
- **GENERIC-CONCEPT:** reasonable teaching model; not matched to Komatsu.
- **ASSUMED-PARAM:** explicit temporary parameter for feasibility demo; no claim of OEM truth.
- **UNVERIFIED:** source/rights/dimensions unconfirmed and cannot be used as authoritative.

## Non-negotiable warnings
1. Do not mix PC200-8 and PC200-8M0 or PC200LC-8 dimensions without explicit identity mapping.
2. A cylinder stroke is NOT the full pin-to-pin length; do not set mounted length equal to stroke.
3. No complete joint coordinate diagram is currently verified. Codex can build **NX parametric concept assembly** with tagged assumptions, not accurate OEM reconstruction.
4. No actual FuelGuard private vehicle photos, serials, customer info, shop-manual binaries or paid model assets in public Creativity repository.
5. Repository files are text source register/tasking only, not a bundled CAD data pack.
