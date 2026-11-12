# EP02 SC03–SC05 — Visual Polish Pass V4.1
**Review date:** 2026-11-12. Source = user-uploaded previews `EP02_SC03_preview.mp4` (44.07s), `EP02_SC04_preview.mp4` (44.20s), `EP02_SC05_preview.mp4` (35.27s). Each H.264 1920×1080 30fps; video files are private conversation uploads, NOT part of this public repo.

## Owner decision
"Được á, chỉ cần chau chuốt hình ảnh đẹp hơn xíu nữa" = **approve the direction, make a focused visual polish pass; DO NOT restart production, switch mascot, change basic concept, or regenerate all images.** Claude V3 / later scene previews remain the working baseline. Re-render only affected shots with before/after comparison.

## Review notes grounded in uploaded clip frames
- **SC03** — machinery/build-up in a construction setting (e.g., at 12s a detailed excavator, at 24s engine/pump illustration, at 34s context-driven technical view): richer imaging works well; but the CG-rendered machine, dark blue blocks and bright cutaways need a **common illustrated 2.5D line/lighting language** with EP01 2D Capy. Retain realistic excavator details; don't replace with a simple icon. Improve contact shadows under tracks, cabin/boom edge clarity, material highlights, foreground/background separation, and transition matches from exterior to engine/pump.
- **SC04** — pressure/force explanation (e.g., at 22s engine/oil illustration and at 33s formula): diagrams are understandable but feel like separate slide templates. Use smoother technical transition, consistent type sizes, readable proper subscripts/units; animating pressure response should be tied to fluid flow and actual piston motion. Label idealized force relation rather than imply all p*A directly becomes bucket force. Keep enough reading hold for formulas while adding gentle mechanical activity.
- **SC05** — cylinder movement & cutaway (e.g., at 18s detailed external machinery/cylinder view, at 28s a very simplified schematic): currently the sharp change between rendered excavator and flat schematic is jarring. Give cutaway cylinder its own engineered visual identity: **barrel, piston, piston rod, rod guide/seals, ports, fixed pins**; keep diagram labeled "minh họa nguyên lý" unless model/serial-verified. Animate one continuous stroke and show the correct chamber inlet and return, rather than generic arrows unrelated to piston pose.

## Target art direction: 2.5D illustrated engineering cartoon
1. Keep owner-approved **Capy BK** and original blue studio, BK shirt/mug/logo intact. Main machine detailed and recognizable, still friendly 2D/2.5D; avoid extreme photorealism or plastic-toy simplification.
2. Unified palette: warm worksite yellow with cool dark-blue explanatory graphics, consistent 2–3 levels of shading and edge quality; background softer/less contrast than focal part.
3. Subtle shadows/occlusion: tracks-to-ground contact, pivot pins, boom overlap, chrome rod glint, hose attachment, cabin glass; no heavy motion blur obscuring mechanical parts.
4. Technical overlays share typography and stroke weights. Reserve lower-screen for dialogue captions, upper-corner for short component labels; don't bury details under fonts, logos or unnecessary arrows.
5. Smooth motivated camera: medium machine → same mechanical region close-up → controlled cutaway; no arbitrary scale jump. Don't change machine orientation/color/model between consecutive related frames.
6. Character motion: meaningful expression and hand gesture at a technical reveal, with actual lip-sync to owner-approved WAV; not a loop of repetitive nods.
7. Real kinematics: boom/stick/bucket connected at pins; cylinder rod slides along barrel axis with endpoints fixed to geometry. No rubber linkages. Tracks do NOT move while excavator is working stationary; when driving, sprocket and tread path must correlate with displacement.
8. Audio untouched in visual pass except tight handoff for lip-sync and SFX. Do not reuse eSpeak or replace approved ElevenLabs actor voices.

## Required lightweight QA (per shot)
- Save source + `*_before.jpg` vs `*_after.jpg` with same timestamp/timecode, no selective cropping.
- Test 5–8s per affected shot before batch regeneration. Confirm no spontaneous text/logo/geometry drift.
- Visual consistency of same machine across scenes (colors, glass, bucket, hydraulic hoses and PC200-8 silhouette).
- Mechanical check: pin coordinates overlay, rod length/angles for at least 3 key frames; verify engineering diagram arrow states against actuation.
- Output 1920×1080/30fps H.264, original clean audio stem isolated; don't globally sharpen/compress exported 1080p footage to invent details.
- Owner approves a **10–15s three-scene comparison reel (SC03 / SC04 / SC05)** before full YouTube long-form assembly.

## Handoff to Claude / Codex
**Claude:** visual polish, art consistency, scene render, shot-by-shot before/after; preserve original layers.
**Codex:** independent kinematics/technical overlay QA, export checks, audit of source artwork and filenames, no duplicate re-render.
**Owner + ChatGPT:** creative approval, technical caveats, voice/rights. Work in a branch; PR; no merge or publish without owner approval.

**Status:** review & specifications only; corrected V4.1 video not yet rendered.
