# EP02 — Siemens NX parametric CAD pilot (Codex)
**Owner objective:** Try a meaningful Siemens NX model, **not** generic blocks disguised as a finished PC200-8. Scope = work-equipment linkage only, 4 custom parts + cylinders/pins, with real assembly feature tree and reproducible NXOpen journal. Public source record: [CAD_SOURCE_REGISTER_PC2008.md](CAD_SOURCE_REGISTER_PC2008.md). Higher production objective: [V7 masterplan](V7_ENGINEERING_CINEMATIC_MASTERPLAN.md).

## Stage 0 — audit, no install
- Check whether licensed Siemens NX is actually installed; record exact version, valid license and if NXOpen Python journal works (interactively first). Do not ask owner to bypass licensing, do not download third-party tools or use MCP without review.
- Inspect accessible local `Creativity` workspace and existing V6/Claude/Blender assets; give exact paths/hashes, do not assume repo contains them.
- Preserve source V6; use an isolated output directory and feature branch, no overwrite/merge.
- When NX absent: STOP actual NX execution; create a clear journal prototype **unexecuted**, report what needs to be installed/licensed. Do not fabricate screenshots or run another CAD engine while calling it NX.

## Stage 1 — build a constrained 2D side-view skeleton within NX
- Choose **PC200-8, 5700-mm boom, 2925-mm arm** as the *brochure-supported example configuration*, **not** confirmed owner machine configuration.
- Define a right-handed coordinate system in **millimeters**, fixed frame at boom foot; establish 7–12 key pivot symbols/expressions (boom base, boom-stick, stick-bucket, bucket linkage, paired cylinder anchors).
- Mark each pin coordinate as **ASSUMED-PARAM** until backed by actual measured/dimensioned documentation. Do not label these as OEM dimensions.
- Cylinder attributes per brochure: two boom Ø120 bore / 1334 stroke / Ø85 rod; arm Ø135 /1490 /95; bucket Ø115 /1120 /80 for this chosen arm. Internal bore is hidden in simple solid barrel, but preserved as expressions/metadata.
- **Crucial:** closed pin-to-pin length UNKNOWN; define as a separately labeled adjustable parameter with an explicit design assumption and feasibility proof. Do not set closed length = stroke.

## Stage 2 — NX solid parts and assembly
Deliver editable native features for minimum `boom.prt`, `stick.prt`, `bucket.prt`, `boom_cylinder_barrel.prt`, `boom_rod.prt`, `arm_cylinder_barrel.prt`, `arm_rod.prt`, `bucket_cylinder_barrel.prt`, `bucket_rod.prt`, `pivot_pin.prt` and `PC2008_WORK_EQUIPMENT_CONCEPT_ASSY.prt`.
- Can use simplified but recognizable manufactured shapes, sheet/box-section booms with reasonable flange/taper, bucket with curved profile/teeth, clevis eyes, proper pin bores. **Not** arbitrary cubes/pipes presented as production quality.
- Build joints/mates at explicit reference points; rods as individual rigid parts sliding along cylinder axes, no scaling of solids.
- Use NXOpen Python journal under version-specific syntax; if journal API is unavailable in the installed edition, clearly document manual modeling steps and only then request approval for alternate workflow.

## Stage 3 — verification and Blender handoff
- Test at **minimum three** poses (low/reach/high) using only feasible joint geometry. Show max cylinder extension within [0, stroke] without pin detachment.
- Export `joint_map.csv` with {part, parent, joint_id, x_mm, y_mm, z_mm, confidence, source_id}; `assembly_params.csv` with source/confidence; `pose_check.csv` with angles, A/B pin distance, barrel length, rod extension and mechanical constraints.
- Export STEP AP214/AP242 if available (verified against current NX), plus part list / material placeholders. Separate visualization mesh for Blender in native supported format after verifying conversion; do not assert Blender reads STEP natively.
- Capture 4 viewport images (full linkage, closeup cylinder, exploded view, 3 poses) and a 3-pose QA sheet with pin overlays; QA against brochure silhouette (NOT manufacturing accuracy).
- No ANSYS until source dimensions, loads and material assumptions documented. No claim of safety rating.

## Acceptance gate: owner decides before adding photorealism or animation
Required: native editable .prt parts/assembly and feature tree screenshot, journal .py, run log/status, STEP/neutral exchange, 3 pose result tables and 4 preview images. Commit only permissibly authored scripts/parameters/documentation; store unverified or proprietary source CAD privately, list paths for owner. No full 8–12min video, no YouTube or TikTok publication.
**Failure is an acceptable result:** If NX can't be run due to missing installation/license, report specifically; do not invent success or silently substitute Blender.
