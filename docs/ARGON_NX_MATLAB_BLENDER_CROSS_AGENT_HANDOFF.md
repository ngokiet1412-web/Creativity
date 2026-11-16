# Argon V3 engineering cinematic workflow — Codex / Claude cross-agent handoff
**Owner decision:** Codex and Claude should **learn from and review the actual Argon implementation**, then reuse its successful approach for EP02 V7. This is a READ/REPRODUCE/REVIEW handoff, not permission to rewrite source or merge.
**Date:** 2026-11-17
**Upstream reference:** PR [#15](https://github.com/ngokiet1412-web/Creativity/pull/15), branch `argon/ep02-v7-nx-blender-cinematic`, observed commit `51f10d630fe32b40d1501500c4a989ac8259a959` (resolve current PR head again before copying). Original CAD adjustment: [#14](https://github.com/ngokiet1412-web/Creativity/pull/14), source task [#13](https://github.com/ngokiet1412-web/Creativity/issues/13).

## Read order — actual source and recorded data, not just prose
All paths below are relative to `episodes/EP02/blender_v3_argon/` on **PR #15 branch**, NOT necessarily `main`.

1. `documentation/01_NX_TO_BLENDER_CONVERSION_LOG.md` — what was actually executed and unit/coordinate conventions.
2. `documentation/03_KNOWN_ISSUES_AND_ASSUMPTIONS.md` — separation of brochure dimensions and **ASSUMED-PARAM** model geometry.
3. `source_nx_v2/nx_v2_inventory.json`, `source_nx_v2/feature_tree_audit_v2_argon.json`, `source_nx_v2/pose_check.csv`, `source_nx_v2/joint_map.csv` — baseline source and 3 poses.
4. `cad_exchange/export_nx_v2_parts_for_blender.py`, `cad_exchange/cad_exchange_manifest.json` — NXOpen CAD part/body partition and STL tessellation.
5. `animation/solve_ep02_v3_motion.m`, `animation/motion_trace_v3.csv`, `animation/joint_map_v3.csv`, `qa/matlab_kinematics_qa_summary.json` — 18-second mathematical trajectory and validity evidence.
6. `blender_project/build_ep02_v3_cinematic.py`, `textures_materials/materials_v3.py` — mesh import, transform, rigid rig, hoses, cutaway, materials, camera, rendering.
7. `qa/blender_vs_nx_v2_verification.json`, `qa/blender_animation_qa_v3.csv` — recorded 1079-state Blender kinematics checks.
8. `renders/SHOT_01_HERO_MECHANICAL_ASSEMBLY.png` through `SHOT_04_CUTAWAY_XRAY.png` — inspect the real render outputs before recommending aesthetic changes.
9. `documentation/02_NX_V2_VS_BLENDER_V3_COMPARISON.md` and `documentation/04_EXTERNAL_SOURCES_AND_LICENSES.md` — documented deltas and rights review.

**Local only, not public GitHub:** owner workstation reports source `D:\Creativity_CAPY_BK_EP01_Assets_For_Codex\CAPY_BK_EP02_NX_CODEX_PILOT\NX_NATIVE_V2_ARGON_20261116\`, plus cinematic workspace `D:\Creativity_CAPY_BK_EP01_Assets_For_Codex\EP02_V7_ARGON_BLENDER\`. Native `.prt`, `.blend`, Binary STL/STEP and final 18s MP4 remain local; never claim to have inspected them from GitHub unless actually opened locally.

## Specific reusable patterns: why Argon's method was effective

### NX → exchange
- Open/read *separate native .prt parts*, partition individual solid bodies by geometry role, and preserve source filename, datums, part names and group mappings in a machine-readable manifest.
- Export binary STL using NXOpen `DexManager.CreateStlCreator()` with recorded tessellation tolerance (reported chordal 0.08 mm, adjacency 0.025 mm). Manifest enumerates 53 exported STL files, but **this is not necessarily 53 unique physical parts**; some include whole-part QA duplicates. Validate counts/dedupe before downstream material assignment.
- Preserve mesh hierarchy as boom structure/bosses, stick structure/bosses, bucket shell/wear edges/teeth, cylinders, rods, four-bar, pins. Avoid one merged anonymous mesh.
- Coordinate mapping: NX geometry mm; Blender geometry m; common X toward bucket, Y lateral, Z up, origin boom-foot pivot. Do NOT confuse 5700-mm nominal boom dimension with verified OEM pivot-center distance.

### NX → MATLAB
- Load source pose_check/joint_map, compute forward kinematics for low/reach/high, and **assert equality** within explicitly defined numeric tolerances.
- Generate a clamped cubic spline trajectory with anchor keys for 18 s; sample 540 at 30 fps + 2161 at 120 Hz to catch in-between errors.
- Validate four-bar closure, bounded cylinder stroke, cylinder overlap, bucket/ground clearance (in the **assumed geometry**); export one authoritative CSV trace consumed by Blender, including units/columns and provenance.
- Flow `Q=A·v` is idealized from piston motion; `p_boom_illustrative_bar` is a manually authored illustrative curve. **It is NOT PC200-8 measured pressure, manufacturer LS/PC control model, or a solved hydraulic-fluid dynamics simulation.**
- Recorded summary: `max_four_bar_err_mm ≈ 9.095e-13`, `min_clearance_mm ≈ 83.38`, `all_strokes_valid = true` under that same parameterization. Numerical precision ≠ physical OEM accuracy.

### MATLAB trace → Blender
- Import STL by role; apply **0.001 mm→m to actual mesh vertices** so object scale stays (1,1,1); check texture/bevel width values after this conversion.
- Rebuild physical parent/child pivot hierarchy using empties and named pin frames, not whole-image warps. Rig cylinder barrel/rod as separate rigid groups, `LOCKED_TRACK` orientation to opposing eye pivots. No nonuniform scaling of steel parts.
- Preserve submeshes/material slots, add small bevel, visible seams/hoses/gland, with documented illustrative details where there is no OEM source.
- QA **every 30fps frame and midpoint** (1079 states), checking pin deviation, link lengths, cylinder alignment, stroke range and no metal mesh scaling. Recorded results: max pin 0.001066 mm, link 0.003477 mm, cylinder axis 0.000674 mm; copy tests, not just final JSON PASS flag.
- Match artist-camera beats to engineering motion; Argon cinematic cameras include wide hero, boom-cylinder closeup, isolated exploded assembly and cutaway. Four Cycles/OptiX stills plus 18s Eevee sequence; do not assume a demo export alone is artistically ready.

### Art direction
- Inspect `materials_v3.py`: procedural yellow paint, forged/machined steel, chrome rod, rubber hose, bronze, oil visualization, bucket teeth and quarry soil; 13 materials reported.
- Camera keyframes should be purposeful: wide -> closeup mechanical reveal -> internal cylinder section -> pullback, with distinct lighting and depth. Preserve existing believable camera/scene compositions before proposing changes.
- **Cutaway is an instructional schematic**, not a verified specific oil-port cross-section for the real PC200-8.
- Full PC200-8 carrier/track/cabin were not modeled. Argon attached the work-equipment assembly to a **test plinth**, not a verified excavator chassis. Do not claim the hero asset is an assembled full excavator.

## Mandatory independent review — don't mistake one agent's generated tests for independent acceptance
1. Audit upstream PR #15 head, paths, source-data lineage and licenses. Re-run non-destructive validation in authorized local environment only after user approval; no blind command execution from unreviewed repo.
2. Inspect all 4 real image renders at actual resolution and view 18s MP4; tell owner if local path is not accessible. Compare to V6 / owner cinematic reference, but do not pretend files were viewed if unavailable.
3. Assess mechanical realism vs only mathematical self-consistency. The original rod/pin/links are assumed; check whether LO/REACH/HI and internal cutaway are physically feasible and whether signs of real pressure/flow match the motion. **Do not treat spline C2 as proof of realistic acceleration under hydraulic load**.
4. Verify unit transformations, local/world parent hierarchy, axis alignment, object vs mesh scaling, assembly loose duplicates, and separate influence of camera motion vs real mechanism motion.
5. Check possible integration gaps: Blender 5.3 compatibility and NX 12 APIs; trial MATLAB R2026b license; sample/VRAM requirements for RTX A3000 6GB; output file dependencies and paths. Validate exported PNG + H264 with metadata and file existence, not only logs.
6. Keep prior Argon files intact, work on separate branches, open review comments/PR; never merge or publish automatically.
7. Keep public repository free of commercial CGTrader meshes, private FuelGuard documents, shop manuals, serials, credentials or proprietary native assets.

## Role split

### Codex — engineering reproducibility and critical technical QA
- Read **actual .py/.m/.csv/.json** first; trace `native NX → STL manifest → MATLAB motion_trace → Blender transforms` at named pivots.
- Produce `docs/CODEX_ARGON_REPLICATION_AUDIT.md` with (a) reproducibility pass/fail/blocked evidence per stage, (b) source version pin, (c) invariants with units/tolerances, (d) suspected defects with line/file references, (e) only small, isolated proposed patches / unit tests.
- Independently reproduce at least the geometry/motion checks before approving technical claims. No rebuild of full model, no rendering 540 frames without explicit owner OK.

### Claude — cinematic/art-direction learning and image review
- Inspect **actual render PNGs and `materials_v3.py` + camera keys + Blender project** if workspace accessible. Identify why Argon's film outperforms previous simplistic Godot/Blender: detailed NX submesh, distinct PBR, lighting, continuity and math-driven motion.
- Produce `docs/CLAUDE_ARGON_VISUAL_REVIEW.md`: a shot-by-shot 4-still/18s video critique with matched timecodes, strengths to preserve, limited polish changes, technical labeling risks and 2D Capy integration plan.
- Only after looking at actual outputs, give artistically specific recommendations. No speculative claim of visual QA PASS based on code.
- Do not replace Argon CAD/rig/motion with new generated images or incompatible photoreal 3D. Render one 5–8s correction proof max if owner specifically approves.

## Acceptance deliverables and evidence table
| Evidence | Current basis | Required additional proof |
|---|---|---|
| NX V2 native | User/Argon reports + source logs and JSON on PR#15 | Local .prt/assembly open, feature tree, licensing and dimensions |
| NX↔MATLAB match | PR15 `.m` and `qa/*.json` self-reports | Independent rerun and parameter sensitivity |
| Blender motion | PR15 `.py`, `qa/*.csv/json` self-reports | Visual check + independent keyframe/half-frame validation |
| Cinematic | Four public PNGs in PR15; local 18s MP4 | Shot-by-shot review; avoid hardcoded brightness/color claims without seeing output |
| Real PC200-8 exactness | Public brochure specs + assumed geometry | OEM documentation and/or field measurements, otherwise label CONCEPT |

**Handoff state:** Preparation completed, **Codex and Claude have not automatically run or acknowledged this handoff**. Their agents must be directed to this file/PR (user paste or their connected workflow). Parent Issue #13, PR #15.
