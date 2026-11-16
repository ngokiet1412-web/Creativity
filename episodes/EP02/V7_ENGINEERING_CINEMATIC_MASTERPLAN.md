# KĨ SƯ ƠIII! — EP02 V7 ENGINEERING CINEMATIC MASTER PLAN
**Created:** 2026-11-16 | **Status:** PROPOSAL / PRE-PRODUCTION, NOT PRODUCTION APPROVAL
**Source of truth:** previous user-uploaded `EP02_FULL_V6_DRAFT.mp4` + `EP02_FULL_V6_vi.srt`; V6 audio subtitles cover 00:00–08:38. Source video was not successfully reopened for a full frame-by-frame review in the most recent inspection. Do not invent missing original frames. Repo has V2 full scripts and QA briefs, but no approved CAD/NX/ANSYS/Blender/Godot source artifacts in default branch.
**Goal:** Upgrade existing EP02 without discarding all V6 scenes. YouTube target 10–12 min **only if the added footage delivers real understanding**; an 8–9min strong episode is preferable to padded 12min. TikTok cut: 30–45 sec hook with its own voice/subtitles, not a speedup of the long form.

## Creative concept
A continuous, plausible **PC200-8-like** excavator as the single hero machine: cinematic front 3/4 view → animated transparent cutaway of power train/hydraulic circuit → cylinder barrel/piston closeup → physical joint motion → swing/travel via center swivel. Capy remains original owner-approved cute 2D mascot; engineer is a distinct calm voice. NO repetitive shouted long "Kĩ Sư Ơiiii!" intro. Instead immediate mechanical hook, logo in overlay or short sonic mark after the hook.

**Important claim control:** A public PC200-8 brochure or generic hydraulic schematic is not an as-built circuit for the owner's machine. An exact visual labeled Komatsu PC200-8 needs independently checked model reference dimensions, linkage mounting geometry, photos/manual/license rights and where needed serial-specific shop manual. Label unverifiable placements as "minh họa nguyên lý, không phải sơ đồ cổng dầu của máy cụ thể". Never fabricate manufacturer drawings or load capacity values.

## Tool responsibility and real data contract
| Tool | Role | Minimum output | Never infer |
| --- | --- | --- | --- |
| NX (if legal working installation and license available) | Concept CAD assembly: boom/stick/bucket/pins/cylinder points; dimensioned unit/coordinate convention, movable joints. May simplify cabin/body | `hero_machine_master.step` (or JT), `joint_map.csv`, image dimension/assumption register | Exact PC200-8 original part dimensions not present |
| MATLAB / Simulink (license check) | Kinematics and idealized hydraulic/power simulation: boom-stick-bucket angles, A/B cylinder endpoints, rod stroke, pressure/flow under stated assumptions. CLSS controls only if source-backed | `motion_trace.csv` + model .m/.slx + validation plots, `model_assumptions.md` | Hydraulic tuning/actual pressure for an unverified specific PC200 |
| ANSYS Mechanical (license check; OFF critical render path) | Selective FEA: one pin/boom lug bracket under stated illustrative load and contacts; mesh sensitivity; response visual | `FEA_report.pdf`, tabulated max deformation/von Mises with units, BC diagram, mesh convergence/sensitivity | Actual in-service strength/safety unless calibrated to real dimensions/materials/loads |
| Blender | Hero mesh via NX STEP → authorized neutral mesh converter (e.g., OBJ/GLB/FBX), retain object/pivot names and units. Rig mechanical hard parts, cinematic 2.5D technical art, lighting, cutaways, deterministic render | `EP02_hero.blend`, `render_scene.py`, render PNG/EXR sequences, clean MP4 previews | That prettier mesh implies mechanical correctness |
| Godot | Existing 2D Capy rig and reactions if proven working; optional, not required for mechanical hero | alpha character layers / character-scene exports | Auto-magically improved acting |
| CapCut Pro | Final edit, audio stems, subtitle delivery, SFX, mix, loudness, vertical crop | project, WAV stems, SRT, YouTube and TikTok exports | Curing broken kinematics with editing |
| Codex + Claude | Codex build/data/rig/QA; Claude visual direction/lighting/compositing/camera. Owner approves artistic and technical choices | branch, PR, per-shot QA, before/after matching timecodes | Missing install/license or assets exist |

**Data exchange:** `motion_trace.csv` sample at animation frame rate (e.g. 30fps): `t_s,boom_deg,stick_deg,bucket_deg,boom_cyl_length_mm,arm_cyl_length_mm,bucket_cyl_length_mm,p_boom_Pa,q_boom_m3s`; all columns optional until verified, never output fictional measurements as measured values. Separate simulated vs schematic data and explicitly document all assumptions. Mechanical kinematics constraint: rigid links rotate only on physical pivots; each rod end follows A/B and rod extension = distance(B,A) minus fixed barrel reference; no non-uniform scaling of metal. Surface force idealization F≈p*A for one chamber only after considering return-side pressure; force at teeth depends on geometry and load.

## V6 → V7 editorial replacement map (by SRT)
| Original V6 | V7 replacement |
| --- | --- |
| 00:00–00:38 branded intro + setup | **Cold open** 0–3s machine struggles/lifts heavy soil, 3–8s X-ray transition to cylinder, 8–15s Capy question + crisp technical claim. Brand appears as tasteful lower third after hook |
| 01:09–01:53 power plant + pump | NX/Blender exploded perspective + MATLAB pump swashplate concept. Show engine shaft powering two variable-displacement pump units; no unsupported as-built routing |
| 01:53–02:37 CLSS | Side-by-side one actuator vs simultaneous actuators, pressure/flow graph explicitly conceptual; engineer explains LS/PC limits |
| 02:38–03:13 joystick/pilot | Closeup control path joystick → pilot/main spool schematic with source flag |
| 03:14–04:24 cylinder and F=pA | **signature hero shot**: a single uninterrupted boom motion, rod physically slides, oil enters correct chamber and exits opposite; graphical pin overlay; explain force/geometry caveats |
| 04:28–05:38 swing/travel | Upper chassis rotates while tracks remain still; center swivel cutaway; two independently moving tracks ONLY during actual driving |
| 05:41–06:47 return/safety | Legible supply/return, filtering, cooler; relief/holding logic conceptual and checked |
| 06:51–07:56 controls/slow machine | Three-way symptom diagnostic **hypotheses**, no certainty and no hazardous hands-on procedures |
| 08:01–08:38 recap | Replace with 15–20s memorable looping full-system energy path and curiosity teaser |

V7 additions only if they raise technical depth: 20–40sec piston cross-sectional closeup, 30–45sec CLSS single vs compound motion, 20–30sec finite element example of pin under assumed load. Do not pad runtime with generic B-roll.

## Stage gates (hard stop after each stage until user approval)
**G0 — Asset / license / safety audit**: detect installed versions and license of NX, ANSYS, MATLAB; inventory V6 source scene projects, permissions and provenance of reference CAD/model/voice; no new model or MCP install without approval. Preserve original V6 with checksums. Decide fallback CAD in Blender if NX unavailable and generic force diagram if ANSYS unavailable.
**G1 — One locked hero asset**: PC200-8-like silhouette + separate real-joint meshes; maps of pins and dimensions, true provenance, texture/material style bible matched to Capy. Owner approves 4 still frames.
**G2 — Mechanical physics sanity**: MATLAB/Simulink simple motion model with 3 actuator stroke traces plus pressure/flow where defensible; require geometry constraints, positive feasible stroke, no rod/pivot disconnection, no boom/plastic bending, no ground penetration, no uncontrolled track roll. If external source lacks enough measurements, explicitly label illustrative geometry.
**G3 — ANSYS OPTIONAL mini-check**: only one isolated assembly when material, BC and loads documented. Review mesh sensitivity, solver residual and correct units; clearly mark educational illustrative stress image. Do not block creative prototype on a not-installed solver.
**G4 — Blender 12–20sec hero proof**: 0–3 action first frame; 3–8 cutaway, 8–14 coherent piston/boom motion, 14–20 Capy reaction. 1080p/30fps side-by-side *matching timecode* A/B with V6; separate non-split viewing version. Render frame sequences with Eevee first; Cycles only selectively on 6GB VRAM.
**G5 — Audio-first locked sequence**: choose two approved actor voices, no eSpeak, avoid excessive cartoon tags and drawn-out brand sting. Align the scene timing to exported WAV, then generate final 16:9 YouTube cut; captions outside mechanical focal region.
**G6 — Release QA**: check factual content vs shop manual, all visual sources and licensing, correct frame pacing and subtitle alignment, video loudness/limiter, copyright/rights, mobile 9:16 safe crop, 1–3sec TikTok hook. User approves before merge/publish.

## Visual style and workstation budget
**Machine:** credible detailed illustrated 2.5D with stylized edge lines, 3-tone shading, small realistic contact shadows, pins/hoses/steel rod specularity, visible dirt weight; Capy remains flat cute 2D original.
**Machine budget:** workstation Xeon, RTX A3000 Laptop 6GB VRAM, RAM 32GB. Use Eevee at 1080p for animation; 1K–2K textures with instancing, proxy meshes and texture consolidation. Higher quality Cycles render only for hero stills/shot where VRAM allows. No full fluid simulation or high-resolution FSI per frame; hydraulics shown as physically constrained engineering visualization, not CFD.
**Security/IP:** no untrusted Blender MCP/addons, no automatic downloads, no public upload of licensed CAD, proprietary shop manuals, FuelGuard telemetry, owner on-site photos or model weights. Public Creativity repo stores plans/scripts/generic diagrams; private binaries stay local or approved private storage.

## Deliverables and acceptance criteria
- Source `EP02_hero.blend`, render script, CAD neutral assembly + joint map, MATLAB trace+plots, optional ANSYS report, voice/caption stems, 15–20sec technical hero proof, 4-frame pin overlays, PR with diffs and QA.
- Mechanical motion: no geometry bending, pin endpoints match within model tolerance (specified in units), no cylinder stroke exceedances; visible movement during intended action; no 4–5sec unjustified frozen hold.
- Production: retain recognizable V6 scenes when valid, maintain SAME machine model across shots, stable character design and vocal identity, source-backed caveats and no interpolated physical measurements masquerading as field data.
- Owner acceptance must precede batch full EP02 render; do not automatically merge, publish or modify established project artifacts in-place.

## Source documentation (official)
- NX/Siemens CAD interoperability (STEP, JT, OBJ/STL): https://www.siemens.com/en-us/products/designcenter/cad-software/cad-interoperability/
- Blender 3D interchange and render CLI: https://www.blender.org/features/pipeline/ ; https://docs.blender.org/manual/en/latest/advanced/command_line/render.html
- MATLAB Simulink logging: https://www.mathworks.com/help/simulink/save-runtime-data-from-simulation.html
- ANSYS Mechanical data export: https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/wb_sim/ds_ExportingData.html
