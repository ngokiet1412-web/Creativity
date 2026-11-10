> **WORKFLOW UPDATE (2026-11-10):** Owner-approved **cinematic animation v2** is authoritative for the current EP01 production. Read [docs/WORKFLOW_V2_CINEMATIC.md](docs/WORKFLOW_V2_CINEMATIC.md) first. Replace all earlier flat infographic/storyboard/card-based style goals with Capy acting inside an excavator, conversational voice, and CapCut AI-generated motion. The v2 **first milestone is an 8-second spoken cabin clip**; target short is roughly 75–100 seconds initially (extend toward 120 seconds only after timing/owner review). YouTube ~10min remains a later distinct format. **GitHub cannot automatically control owner's CapCut Pro desktop.**

# CAPY BK — Agent contract (public repository)

Read README.md, docs/CREATIVE_BIBLE.md, docs/PRODUCTION_PIPELINE.md, episodes/EP01/BRIEF.md and issue #1 before acting.

## Canonical decision
- Brand: **Capy BK**; keep approved source mascot, not a newly invented character. Face joyful, fat/squat, arms tiny. White polo with accurate BK TP.HCM-inspired three-hexagon logo. Background: dark blue engineering studio, mic, laptop, logo on mug and backlit panel. Verify rights before commercial release.
- EP01 theme: indicated fuel level changes on an inclined excavator vs actual fuel volume, engine consumption, and genuinely unexplained loss.
- Outputs: TikTok **~120 seconds 9:16 1080×1920 30 fps**; YouTube **~600 seconds 16:9 1920×1080 30 fps**. Separate narrative edit and VO for each.
- Owner **has CapCut Pro**; it is the finishing editor. CapCut Video Studio/Seedance AI is operator-driven and may require credits. No agent may claim it opened the owner's desktop app unless confirmed.
- Prototype 32-s animatic has **sound bed, no intelligible speech, no lip sync**, 540×960 16 FPS: reference ONLY.

## Lanes and review
| Lane | Owner | Output |
|---|---|---|
| C0/Creative | ChatGPT/creative agent | scripts, timed storyboards, thumbnails, captions |
| C1/Engineering | Codex | reproducible assets pipeline, ffmpeg scripts, tests, folder layout, manifests |
| C2/Animation | CapCut Pro AI or animation agent | character clips, background plates, B-roll, lip sync tests |
| C3/Audio | voice/editor agent + owner | approved voice casting, clean WAV stems, music/SFX licensed |
| C4/Technical QA | independent reviewer | facts, assumptions, citation/source log, diagram correctness |
| C5/Owner approval | owner | freeze script, select voice, publish gate |

All agents: work in branches, open PRs, link issue IDs, provide example output/QA note; do NOT force-push or merge without owner approval.

## Safety/public boundary
This repository is **PUBLIC**. Do not copy from any other private FuelGuard project, commercial customer/owner data, machine IDs, raw fleet/ECU telemetry, private engineering secrets, unpublished NCKH experimental results, financing material or credentials. Use schematic/conceptual synthetic illustrations. Public episodes cannot claim FuelGuard's detection system is independently proven.
Respect copyright: creator-owned/original media or licensed resources only. Don't mimic a YouTube channel scene-for-scene or reuse original music/characters.
Mark school logo usage as subject to rights review; do not claim HCMUT officially endorses project.

## Technical rules
- Every image/clip: record input, prompt, model, date, intended shot, source license, and approval state in an asset manifest.
- Visualize *fuel level* separately from *fuel volume*; explicit tank geometry and sensor location assumptions for diagrams.
- Slope/slosh can affect sensor readings, but avoid blanket statements about every fuel sensor design.
- Explain that IMU angle alone cannot distinguish theft; multimodal inference requires calibration, synchronization and validation.
- Clips should stand alone with safe-area design and readable captions; no final TikTok/YouTube uploading without owner review.
- Keep all generated results labeled DRAFT and do not overwrite approved mascot assets.
