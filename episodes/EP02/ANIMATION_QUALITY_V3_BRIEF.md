# CAPY BK EP02 — Animation quality upgrade / PC200-8 (V3 corrective brief)
Date: 2026-11-12. **Status: QA / corrective requirements**, NOT a claim that this animation has been fixed.

## Baseline from owner-supplied file
- Input: `CAPY-BK-EP02-PC200-8-demo.mp4`, owner shared in conversation; not committed or approved for public repo.
- Probe: H.264 1920×1080, 30 FPS, 42.00 sec, with AAC audio and subtitle stream.
- Sampled frames at t and t+0.25s every 0.5s after resizing to 320×180 grayscale: 34 of 82 comparisons showed mean absolute difference below 0.5/255. This does not diagnose every possible animation defect, but confirms much of the clip is visually static.
- Nearly identical frames around **17.5–21.5s and 35.5–40s**; inspect these clips for inactive prolonged holds vs missing animation. Scene cuts near 4, 10, 24 seconds show large changes, which should not be counted as convincing intra-shot motion.
- Key issue: source assets are diagram-like and some movement is whole-frame motion or sparse element movement. Current project is a technical motion-board, NOT a finished cinematic machine animation.

## Target style
**2D illustrated documentary with mechanical credibility:** preserve EP01's cute, warm hand-drawn capybara + white/blue BK shirt + BK mug/studio; excavator resembles a credible PC200-8 with consistent details, hydraulic lines, chassis and controls. Avoid glossy 3D or photorealistic generation. Depth via cutout layers/parallax, shading, overlap, and edited camera moves, not geometric warping.

## Rig architecture — source files must be independent layers
- Character: `capy_head, capy_torso, capy_paw_L, capy_paw_R, eyelids, brows, mouths_{closed,open,wide,smile}, hat`. Animate pivot, gaze, expression, blink, anticipation, secondary motion. Keep proportions exactly.
- Excavator (rigid hard parts): `undercarriage, upper_carriage, cab, boom, stick/arm, bucket, boom_cylinders_LR, arm_cylinder, bucket_cylinder, rod_each, piston_each, boom_pins, stick_pins, bucket_pins, hoses, track_sprocket, idler, track_links, dirt_particles, ground_shadow`.
- Separate Godot 4 `Node2D` parents at physical joints and use `AnimationPlayer` with easing curves. `Skeleton2D/Bone2D` optional for the softer Capy; DO NOT soft-deform rigid mechanical parts via Polygon2D skinning. Each rigid link rotates/translates; it must never bend.
- Cylinder rig: two *fixed mount pivots* A and B, compute target length `L=|B-A|`; barrel aims at B; rigid piston rod slides along barrel axis to match L (clamp to illustrated stroke). Do not stretch rod pixel art. Verify geometry across all poses.
- Bucket: wrist hinge rotation, teeth keep shape, scooped earth remains attached during lift; dumping rotates bucket, dirt follows downward gravity.
- Tracks: if driving, independent circulation of links and wheel/sprocket rotation proportional to travel; if stationary digging, tracks and ground stay fixed. No spinning whole track silhouette.

## Hydraulic / engineering correctness
- Generic teaching overlay: diesel engine shaft → variable-displacement pumps (flow) → main directional control valve → selected cylinder chambers → return/cooler/filter/tank, alongside pilot/control and simplified load-sensing feedback. Label as conceptual, NOT verified port-by-port circuit for particular PC200 serial.
- For a commanded extension: show oil entering the correct cylinder chamber, piston/rod extension, oil leaving the other chamber to return; no teleportation or disconnected hose ends. Show reverse flow for retract separately.
- Distinguish `F=p*A` (ideal piston force under differential pressure and correct effective area) from bucket digging/lifting capacity, which is governed by linkage lever ratios, friction, losses and stability. Flow and effective area determine speed ideally `v≈Q/A`; never show hydraulic oil as magically creating energy.
- Technical reference validation gate for PC200-8 not PC200-8M0, with source log for every model-specific claim.

## Acting/camera/visual polish
- Each mechanical 6–10s beat follows: settle/anticipate (0.4–0.8s) → spool/pressurize and move (2–4s) → bucket/soil reaction (0.5–1.5s) → rest/hold for comprehension (0.5–1s). **No arbitrary camera shake**; play environment reaction only when machine/soil impacts.
- Use dynamic camera across cuts: medium excavator overview → cylinder closeup → schematic cutaway → return to wide shot, all using scene-aware framing; not generic pan/zoom on a static slide.
- 2D visual polish: consistent 3-level shading, fine line weights, metal joints, hoses, piston chrome highlight, shadows under tracks, soil bits falling with gravity, occasional subtle dust and natural secondary hose motion.
- Capy reaction matches content (confused → curious → understands), avoids nonstop mechanical nodding. Engineer speaks while pointing at relevant component.
- Sound: keep EP01-approved signature and two ElevenLabs voices from owner locally; mix hydraulic whine, engine idle, bucket soil SFX at restrained levels; no stock robo eSpeak or rushed TTS; video re-timed to audio actual.

## QA test to pass BEFORE full 10–12min production
Create **one 12–18s proof** from existing source artwork:
1. 0–3s: full excavator on ground, Capy behind safety barrier, bucket parked, machine idles.
2. 3–9s: directional valve command → cylinder extends → boom and stick move through at least two distinct credible joint angles. One camera cut to high detail cylinder.
3. 9–13s: bucket curls and scoops soil, small soil reaction, return shot from 3/4 view.
4. 13–18s: Capy reacts naturally, hydraulic/sound diagram brief highlight, stable pause.
Return **editable Godot project**, exact input layers, animation curves/keyframes, MP4 1080p/30fps, 4–6 diagnostic keyframes overlaying pins, before/after visual comparison, and list of assumptions/unknown PC200-8 specifics. Commit in feature branch and PR. Do not merge or autopublish.

**Acceptance criteria:**
- For moving mechanical shots, identifiable physical movement every second except intentional 0.5–1s rests; no repeated 4–5s frozen screens.
- No image stretch/pixel mesh warp; pivot positions and joint lengths physically consistent.
- No unrealistic track/wheel animation; no hoses teleported, hydraulic path understandable.
- Shot pacing follows narration; animation fluid but not cartoon-fast. Any missing source layers identified as blocker instead of silently faking them with flat sprites.
