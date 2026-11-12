# EP02 A/B QA — Gemini Argon vs Claude V3 (2026-11-12)
**Owner source:** `CAPY-BK-EP02-PC200-8-demo(1).mp4` (owner: Gemini Argon) and `CAPY-BK-EP02-V3-PC200-8-demo.mp4` (owner: Claude Opus). Both were user-supplied in ChatGPT; no source binary was uploaded to this public repo. Owner prefers Claude V3; **adopt Claude V3 as visual/motion baseline but do not mark finished**.

## Technical comparison
- Argon: H.264 1920x1080, 30fps, 42.00sec, AAC mono 48kHz, ~61MB.
- Claude: H.264 1920x1080, 30fps, 42.00sec, AAC stereo 48kHz, ~45MB.
- Comparative 4fps low-resolution frame-difference analysis (320×180 grayscale): median frame-pair mean absolute delta ~3.26/255 (Argon) vs ~8.13/255 (Claude). Argon has more uniform lower-amplitude visual changes; Claude has pronounced dynamic visual changes but ~8% sampled steps near-static, especially intro and near end. **Frame differences are not mechanical realism scores.** 
- Visual review: Argon resembles schematic/cartoon infographic, machine/arm oversimplified; Claude shows better-detailed excavator, more cinematic close-ups, hydraulic internal visuals and labels. Claude changes style to heavily 3D-rendered / near-photorealistic, conflicting with approved cute 2D Capy BK look.
- Neither sample establishes serial-accurate PC200-8 circuits, accurate hydraulic fittings, or force/flow correctness by itself; requires source evidence, transparent schematic layer and technical review.

## V4 target — NOT a fresh rewrite
Preserve Claude's stronger machine visuals, composition, transitions and active shot design. **Do not throw away working scenes or switch back to Argon flat cards.** Bring look into warm 2D/2.5D illustrated technical documentary: outlined/shaded machinery, 2D Capy as recurring host, consistent yellow machine and studio BK identity. Keep rich mechanical details, reduce generic photorealistic stock-3D look.

### Must fix in order
1. **Mechanics & kinematics**: proper boom/stick/bucket pivots, rod/barrel mounting points, length constraint vs joint angles, no rigid part bending, realistic tracked undercarriage anchored when digging. Add QA pin overlay across representative moving frames.
2. **Hydraulics**: animated signal/flow cutaway distinguishes engine shaft, variable-displacement pumps, directional valve, selected cylinder chambers, return, simplified load-sense feedback; synchronize indicated oil flow with actual extension/retraction, avoid pump 'creating fixed pressure' misconception. Label conceptual vs verified PC200-8 circuits.
3. **2D Capy integration**: return approved studio and white BK mug in first seconds; Capy reacts to machine, watches crossection, asks the engineer; no unapproved new mascot/species.
4. **Shot timing**: replace awkward empty static holds with e.g. smooth machine action, engineering close-up or purposeful Capy reactions; don't animate everything unnecessarily. Use narratively meaningful ~0.4-1s hold for comprehension.
5. **Audio**: preserve EP01 approved Capy/engineer voice IDs and brand sting, clean stems separately; no eSpeak and no making up VO; measure dialogue timing then cut animation. Mix separately in CapCut Pro.
6. **Technical QA**: source-check model-specific details from PC200-8 correct manuals, not automatically PC200-8M0; no real owner machine claims from this demo.

### Acceptance test (12–18 seconds)
- 0–3s: cinematic studio Capy question / existing original branding.
- 3–7s: detailed illustrated PC200-8-like excavator stationary, jointed boom cylinder begins extension.
- 7–12s: camera transition to visually detailed cutaway cylinder / valve, flow enters chamber; physical piston and boom pose evolve consistently.
- 12–18s: return full machine with bucket curl and small soil reaction; Capy reacts, technical overlay labels limited to source-confirmed concepts.
Submit H.264 1920×1080 30fps, silent/voice stem versions as needed, Godot/Blender/2D source project, layers and pin-coordinate plot, assumed hydraulic schematic with refs, QA notes, and a before/after frame-pair comparison. Seek owner approval BEFORE full 10–12min production.

**Status:** QA review+recommendations; no Claude V4 has been rendered or uploaded. No merge or auto publication. Public repo must not include private FuelGuard telemetry, shop manual under copyright, or private machine owner identifiers.
