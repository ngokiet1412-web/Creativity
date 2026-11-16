# Independent review — Argon V7.1 Engineering Cinematic (EP02)
**Review date:** 2026-11-17 (Asia/Ho_Chi_Minh)  
**Reviewer:** ChatGPT coordination / engineering + visual quality  
**Target:** [PR #15](https://github.com/ngokiet1412-web/Creativity/pull/15), **pinned commit** `d6f6aae8e8e62ff6ffaa4b9aa9fa25765217a395`. Compare [Codex independent audit, PR #16](https://github.com/ngokiet1412-web/Creativity/pull/16) and CAD-fit work [PR #14](https://github.com/ngokiet1412-web/Creativity/pull/14).  
**Verdict:** **CHANGES REQUESTED BEFORE OWNER PRODUCTION APPROVAL**. **Accept** V7.1 as a **rendered technical CONCEPT demonstrator**, **not** as OEM-correct Komatsu PC200-8 or EP02 publish-ready insert. **Do not merge.**

## Evidence and scope
Read actual V7.1 scripts `blender_project/build_ep02_v7_1_cinematic.py`, `textures_materials/materials_v7_1.py`, `qa/run_v71_anim_with_telemetry.py`, `qa/make_v71_storyboards.py`, documentation `05/06/07`, geometry JSON, and GPU telemetry JSON from PR #15 head. **Visually inspected four actual 1920×1080 before/after image comparisons**, plus 4-timestamp timeline storyboard via GitHub connector:
- [SHOT 01 — Hero overview](https://github.com/ngokiet1412-web/Creativity/blob/d6f6aae8e8e62ff6ffaa4b9aa9fa25765217a395/episodes/EP02/blender_v3_argon/renders/COMPARE_SHOT_01_V7_0_VS_V7_1.png)
- [SHOT 02 — Cylinder close-up](https://github.com/ngokiet1412-web/Creativity/blob/d6f6aae8e8e62ff6ffaa4b9aa9fa25765217a395/episodes/EP02/blender_v3_argon/renders/COMPARE_SHOT_02_V7_0_VS_V7_1.png)
- [SHOT 03 — Exploded cylinder](https://github.com/ngokiet1412-web/Creativity/blob/d6f6aae8e8e62ff6ffaa4b9aa9fa25765217a395/episodes/EP02/blender_v3_argon/renders/COMPARE_SHOT_03_V7_0_VS_V7_1.png)
- [SHOT 04 — Cutaway](https://github.com/ngokiet1412-web/Creativity/blob/d6f6aae8e8e62ff6ffaa4b9aa9fa25765217a395/episodes/EP02/blender_v3_argon/renders/COMPARE_SHOT_04_V7_0_VS_V7_1.png)
- [Time-aligned V7.0/V7.1 storyboard](https://github.com/ngokiet1412-web/Creativity/blob/d6f6aae8e8e62ff6ffaa4b9aa9fa25765217a395/episodes/EP02/blender_v3_argon/renders/STORYBOARD_V7_0_VS_V7_1_TIMELINE.png)

Reviewed render/log metadata for MP4 but **did not independently play the complete V7.1 18s MP4 or open the native .blend/.prt on the owner's workstation** in this review. Rendering success, motion smoothness and full-frame compositing cannot be independently certified by static storyboard and producer self-logs alone. The earlier Codex PR #16 *did* independently inspect the original Argon V3 video and CAD/Blender scene; that audit is older than V7.1 and should not be misrepresented as V7.1 validation.

## Strong results to preserve
1. **Repeatable file-backed pipeline**: NX 12 solid groups → manifest/named STL submeshes → MATLAB 540-row motion trace → Blender rigid-part rig → animation frame output → FFmpeg; files/MP4/STL/STEP/.blend now actually included in PR #15. Keep module boundaries and source revisions pinned.
2. **V7.1 detail progression is visible, not just claimed**: SHOT 02 shows more convincing chrome rod, gland bolts, hoses/pipe routing and metal edge reflections; SHOT 01 shows a better industrial test-plinth and routing; SHOT 04 shows 2-chamber oil and readout concept. V7.1 improves on V7.0 especially for mechanical close-ups.
3. **Declared scope honesty**: source documentation acknowledges work-equipment **on a test plinth**; full chassis/cabin/tracks and serial-specific OEM structure are not modeled. Pressure is illustrative. Maintain this labeling, including in every export intended for public use.
4. **Reported GPU workflow fits the current scene**: V7.1 telemetry says **540/540** frames, 808.52 s, mean render GPU 78.98%, peak 99%; peak GPU temp **77°C** and peak VRAM **5618/6144 MiB** (only **526 MiB** remaining). No GPU failure evident in reported session. **Do not increase memory-heavy features or run parallel 3D applications casually**; peak VRAM margin is modest.
5. **Self-check coverage**: 1,079 states checked for pivot/axis/link metrics; retain invariant checks, but improve definitions below. An internal "PASS" does **not** equal independent OEM fit or complete collision-free assembly.

## BLOCKERS: must fix before publishing as verified engineering

### P0-01 — CAD source revision / actual solid intersections
Codex [PR #16 audit](https://github.com/ngokiet1412-web/Creativity/blob/462e89d27c787116d0336d5dc87447d8e920b345/docs/CODEX_ARGON_REPLICATION_AUDIT.md) independently reports NX Boolean solid intersections for selected *original NX V2* parts at REACH: boom ↔ boom rod, boom ↔ arm barrel, side link ↔ H-link. The V7.1 report explicitly says **same original NX V2 geometry and same motion trace** are preserved. Therefore, the 1079 pivot/axis self-check cannot close the interpenetration finding. PR #14 contains a distinct geometry-fit attempt; it is **not** implicitly integrated into V7.1.
**Required:** pick and hash one canonical CAD revision; compare changed `.prt` bodies/joints against V2; rerun targeted Boolean checks at LOW/REACH/HIGH and intermediate frames for affected pairs, with permissible-contact exemptions and plots/logs; only then replace affected STL meshes and synchronize all pin/length inputs across NX/MATLAB/Blender. No "all collision-free" claim until that audit passes. For demonstration-only release, visually isolate/label questionable geometry.

### P0-02 — Dynamics/volume claims still overreach current model
Codex PR #16 demonstrated:
- the clamped cubic spline meets zero **velocity** at 16.8s, but acceleration jumps at connection to final hold; overall trajectory is not C2 across that boundary;
- MATLAB cap/rod liquid-chamber geometry and Blender cutaway lengths differ (e.g. cap length previously differed by **272 mm**);
- illustrative pressure `p_boom_illustrative_bar` is not a hydraulic pump/valve/CLSS solution or field pressure.
V7.1 says MATLAB trace unchanged and cutaway is visually elaborated; these are **not fixed by lighting/extra material detail**.
**Required:** independent motion replay with a smooth stop including acceleration continuity; shared parameter dictionary for cutaway head/gland/piston/chamber volume; visible label **"Áp suất GIẢ ĐỊNH / MÔ HÌNH MINH HỌA"** (or hide numerical bar readings) in actual delivered frames. Recheck relative cylinder port flow direction if sign changes.

### P0-03 — QA metric names currently imply more than measured
The V7.1 JSON repeats V3's `max_pin_dev_mm=0.001066`, `max_link_len_err_mm=0.003477`, `max_cyl_axis_err_mm=0.000674`, `min_bucket_ground_clearance_mm=83.3801`. The older independent Codex audit established that (a) midpoint `pin_dev` wasn't evaluated against a reference, (b) ground-clearance figure comes from MATLAB CSV hull, not actual Blender bucket mesh, and (c) world-scale/mesh collision coverage differed from the original QA set. New V7.1 checks for hoses/soil are useful but don't automatically repair these definitions.
**Required:** produce named, per-metric sample counts, mark unmeasured values NULL instead of zero, separately report `MATLAB_hull_clearance` and `BLENDER_actual_mesh_clearance`, measure metal world scale and independently validate changed soft hoses + clod collisions/penetration at selected frames. PASS only on metrics actually measured.

## Visual QA: exact screenshots inspected

### P1-01 — SHOT 03 exploded cylinder is visually undersized (**HIGH PRIORITY**)
Actual [comparison](https://github.com/ngokiet1412-web/Creativity/blob/d6f6aae8e8e62ff6ffaa4b9aa9fa25765217a395/episodes/EP02/blender_v3_argon/renders/COMPARE_SHOT_03_V7_0_VS_V7_1.png): the exploded component chain occupies only a narrow band around the center/lower third of its image; most of the shot is unused empty studio/floor. Eight part annotations are squeezed into tiny single-/double-line text, illegible at mobile display scale. The new V7.1 "upgrade" is not an effective technical explainer at this camera distance.
**Required:** move camera substantially closer or compose in 2–3 progressive macro groupings (barrel/gland, piston/seals, rod/eye); use numbered 2D callouts at screen-safe 1080p size, do not anchor tiny 3D text to the far platform; confirm every component visible without occlusion. Render *one still* before a new animation.

### P1-02 — SHOT 04 HUD still too small; oil looks like neon bands
Actual [comparison](https://github.com/ngokiet1412-web/Creativity/blob/d6f6aae8e8e62ff6ffaa4b9aa9fa25765217a395/episodes/EP02/blender_v3_argon/renders/COMPARE_SHOT_04_V7_0_VS_V7_1.png): cylinder and red/blue chambers are more legible; however dark telemetry card has tiny and low-contrast text and must be enlarged for phone viewing. The red/blue glow may read as colored light beams rather than **oil occupying changing chamber volume**. Keep instructional arrows and A/B pin ring but show piston/chamber boundaries clearly.
**Required:** 2D compositor overlay with readable digits/units and hierarchy, large "minh họa" marking, 9:16 safe crop check. Reduce oil emission vs reflective/volumetric depiction; ensure chamber-length animation corresponds to shared model inputs.

### P1-03 — SHOT 01/02 mechanical improvements real; cinematic target not yet reached
Actual [SHOT 01](https://github.com/ngokiet1412-web/Creativity/blob/d6f6aae8e8e62ff6ffaa4b9aa9fa25765217a395/episodes/EP02/blender_v3_argon/renders/COMPARE_SHOT_01_V7_0_VS_V7_1.png) and [SHOT 02](https://github.com/ngokiet1412-web/Creativity/blob/d6f6aae8e8e62ff6ffaa4b9aa9fa25765217a395/episodes/EP02/blender_v3_argon/renders/COMPARE_SHOT_02_V7_0_VS_V7_1.png): structural geometry and metal highlights improved, but the overall machine surfaces remain very flat and uniform peach/orange with relatively low material wear texture; isolated rig/test plinth reads like a laboratory model rather than a Komatsu full-machine cinematic advertisement. **Do not fake a full PC200-8 body.** Aim for credible industrial testing cinematography and camera-selected detailed closeups rather than claiming full-machine realism. A bit more shape/texture/light variation is worthwhile; avoid hiding CAD with excessive grain.
**Required:** one art-directed shot focusing on machine scale and metal contact; compare same camera, same exposure and same frame to V7.0; preserve original validated rig.

### P1-04 — Motion and audio remain only partly reviewed
Comparison storyboard samples at t=2.0, 6.1, 11.0, 16.0 s establish continuity of visual subjects but **not** temporal smoothness, realistic inertial response, collision-free flexible hoses or subtitle-readability at every frame. MP4 reported silent.
**Required:** 18s playback with frame-accurate notes for 0–4, 4–8, 8–14, 14–18s; verify 30fps motion cadence, no shader pops/scene jumps, no floor penetration, hose lengths/radii and UI flicker; audio and captions are a separate gate with Claude.

## Security & provenance gate
Repo is public and latest commit now contains native `.blend`, STEP and STL concept geometry, so review ownership/sharing rights **before distributing/promoting** the assets; self-authored CAD is not necessarily proof of permission for embedded third-party content. Inspect that exports/metadata/logs do not include private FuelGuard data, customer machine serials, local secrets, proprietary manuals, or assets copied from restricted repositories. This review did not conduct a full binary-content security/IP audit; no approval for external redistribution is implied. PR must remain unmerged while source license/provenance is checked.

## Recommended minimal next acceptance sequence — avoid rerendering 540 frames again
**Gate A (Codex):** one canonical NX CAD geometry revision + targeted Boolean contact/intersection test and geometry/provenance table; motion end-stop + shared chamber dimensions; a 120Hz MATLAB verification and 30fps/half-frame Blender check, in isolated branch.  
**Gate B (Argon):** preview fix SHOT 03 composition and SHOT 04 HUD/oil with **two stills**; preserve SHOT 02 mechanical highlights and rerender only affected 4–8s or 8–14s subset if owner approves. No automatic full 18s render.  
**Gate C (Claude):** director's proof for 16:9/9:16 readability, 2-voice timing, Capy 2D and technical labels; **no fake telemetry**.  
**Gate D (Owner):** inspect genuine 18s video playback at full resolution and approve/decline before merge and EP02 integration.

## Decision log
- **Preserve** Argon V7.1 scene/materials/rig as *visual engineering prototype*.
- **Request changes** for P0 geometry/QA/data-integration; P1 exploded framing, HUD and cinematic communication.
- **No claim** this is an OEM-accurate complete Komatsu PC200-8; no ANSYS validation shown here.
- **No changes** made to Argon's PR #15 source/MP4; this is a read-only review and handoff.
