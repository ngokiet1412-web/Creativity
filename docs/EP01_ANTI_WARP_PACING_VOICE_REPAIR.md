# EP01 Repair Pass — anti-warp 2D animation, pacing and natural voice

**Owner critique, 2026-11-10:** Original Codex stills are good, but 105-second animated draft feels jerky, some frames visibly bend/warp, movement is unconvincing, pacing too fast in parts. The ChatGPT offline TTS used in the earlier voice guide sounds unnatural. **Do not ship either draft as final.**

## Evidence and scope
Reviewed `Capy-BK-EP01-animation-draft.mp4` (owner-provided, not committed to public repo): 105 seconds, 720×1280, H.264 30fps, mono AAC 48kHz. Inspection shows many 0.4-second intervals with near-zero intra-shot character/object motion, while camera transforms change the composition. One can inspect samples around studio 0–20s, site arrival 25–45s, digging 48–55s, equipment montage 55–76s, ending 95–105s. This is an observational QC finding; exact cause of reported geometric warping is not yet proven and needs marked before/after frame comparison.

## Mandatory rendering rules
1. **NO** mesh-warp, perspective warp, optical-flow morph, elastic facial deformation, nonuniform X/Y scaling, or frame interpolation that invents pixels on the mascot, BK logos, mug, or hydraulic linkages.
2. Apply **uniform** scale + translation / rotation only on each independent raster cutout. Preserve aspect ratio. Crop to 9:16 instead of stretching.
3. Split each source shot into stable layers: backdrop, Capy torso/head, eyelids, 3–5 mouth states, hands/paws, mug/hat, machine chassis/boom/arm/bucket/cylinder/track or tire, foreground overlay. Establish hinge/pivot points per mechanical joint. Build alpha masks and inpaint exposed background; reject scenes with visible holes/halos.
4. Prefer 2D cutout/keyframe rig animation (CapCut layer+keyframes / Blender Grease Pencil / SVG/Lottie/Remotion) when clean layers exist. AI image-to-video is reserved for owner-approved shots after a 6–8s identity/geometry test; don't let AI redraw all 28 images in one batch.
5. A coherent motion cycle **must have causality**: Capy anticipates → moves paw/head → reacts → settles; excavator boom/stick/bucket pivot together at real joints, stick and bucket stay attached, cylinder extends consistently; tracked vehicles move at the ground contact. No face drifting / logo distortion / 'rubber' machine geometry.
6. Motion cadence: 30 fps export, smooth eased keyframes. No abrupt first/last-frame positional jump. Use slow camera pans sparingly; one physical action per shot.
7. Export QA should compare same static background edges across frames: stable straight lines, circular BK mug/logo unchanged, fixed proportions of machine links, no vertical/horizontal distortion. Flag segments where object regions change shape without a planned action.
8. Test clips and show the owner before rendering full sequence.

## Revised editorial pace
**Do not change speaking speed or globally slow the finished MP4.** Start from 105s draft, aim ~115–120s (+10–15%) by extending character *reactions*, reveal and natural pauses; don't stretch static panels endlessly. Recommend:
- 0–23s studio welcome + year-four automotive student intro;
- 23–39s HCMUT / linkage to engineering;
- 39–52s helmet transition and jobsite 'tiny shovel vs huge earth' gag;
- 52–97s machinery show-and-tell (excavator / dozer / loader / dump truck / roller / crane);
- 97–111s 'automotive engineering insight' (engine, controls and hydraulics);
- 111–120s teaser and cheerful sign-off.
Treat timestamps as editorial guides; timed spoken audio + reviewed scene timing rule.

## Voice fix
- Reject previous **eSpeak/offline robotic guide** as final. The earlier chat rendering used offline TTS, with speeds increased aggressively to make dialogue fit short shots; this explains unnatural speech pacing.
- Choose one youthful, warm, conversational Southern Vietnamese voice for Capy; owner may record own narrator. Generate separate voiced stems in real time, not sentence-compressed to fit visuals.
- Render dialogue FIRST, with expressive brief breaths, micro-pauses and sentence stresses. Then fit the animation duration to speech; do not aggressively force voice speed.
- Clean 48 kHz WAV per shot, normalized consistently; avoid clipping, add low music/SFX with ducking under voice. Caption SRT separately; never bake generated AI speech into the source animation during look-development.
- If CapCut video AI produces warped mouth movements, skip closeup lip-sync until a separately rigged mouth system is ready; play VO off-camera / over mechanically animated B-roll.

## First two acceptance clips (no expensive batch)
- **T01 Studio greeting** 6–8s from approved intro still: Capy blinks, small single-paw wave, smiles, light head tilt; background, logo, mug and microphone stay fixed; separate natural voice saying 'Hê lô mọi người! Chào mừng đến với Kĩ Sư Ơiii!'. Preserve Capy shape.
- **T02 Excavator** 6–8s from KF-06: only machine's boom, arm, bucket, cylinders move around mechanically correct joints; Capy stays safely behind railing. No warping of buckets or changing excavator body.
- Return original still, animation MP4, source layer/mask data, voice WAV, SRT, QA before/after contact sheet, notes on known limitations, and actual render characteristics.

## Distribution and security
Use exact owner-approved images and active EP01 PDF references. Public repo must not contain private FuelGuard source/field footage/telemetry or unapproved rights media. No posting/publishing, no merging without owner approval.
