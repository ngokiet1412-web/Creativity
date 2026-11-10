> **CANONICAL EP01 CONTENT CHANGE (2026-11-10):** The FIRST episode is now **Capy BK khám phá xe/máy công trình: là gì, vì sao có, từng loại dùng làm gì?** with a cinematic worksite tour. **Do not build the old fuel-level reading / theft assumption as EP01.** That previous pitch is preserved at [episodes/BACKLOG/FUEL_LEVEL_ORIGINAL_BRIEF.md](../episodes/BACKLOG/FUEL_LEVEL_ORIGINAL_BRIEF.md). New EP01: [brief](../episodes/EP01/BRIEF.md), [TikTok script](../episodes/EP01/SCRIPT_TIKTOK_V1_CONG_TRUONG.md), [CapCut AI scene prompts](../episodes/EP01/CAPCUT_EP01_DISCOVERY_SHOTS.md). The **first visual proof** is SC01 Capy arriving at the site carrying a tiny shovel, not CAB-01 fuel gauge alert. This update overrides old EP01 scene content while retaining the general Codex/CapCut tool division.

# CAPY BK — WORKFLOW V2 / Cinematic animation production
**Decision date:** 2026-11-10. **Status:** authoritative working workflow for EP01, subject to owner approval. Links: issue #1 (master), #2 (Codex), #3 (CapCut AI), #4 (technical QA), #5 (writing).

## 0. Creative reset: NO slides posing as a film
Previous 8-card infographic storyboard and 32s animatic are learning prototypes, NOT a style target. Visual priority: **story → character acting → interesting excavator action → visually accurate explanation**, not sequential static posters.
Owner-approved reference style: 3 cinematic vertical stills from chat (not in GitHub yet): **R01** cheerful Capy BK standing beside high-quality yellow crawler excavator in warm sunlit outdoor construction setting; **R02** same Capy seated in detailed crawler excavator climbing an earthy slope; **R03** front-facing Capy in excavator cab with twin joysticks and fuel gauge. Don't recreate an inconsistent new mascot. These 3 stills must be imported separately by owner/Codex from approved files before batch production.

**Character canon:** tan, round, cute, very chubby short-limbed capybara, happy human-like expressions, blue/white polo with BK-inspired mark, yellow/black hair accessory; keep same character and same vehicle between shots. Keep logo/mug fidelity; apply canonical logo as overlay when video AI distorts tiny lettering. Do not imply official HCMUT endorsement.

## 1. Success criteria
- First proof: **6–8s cabin acting with audible natural Vietnamese line + character turning/reacting + stable excavator controls**; separate voice stem and render.
- Second proof: **15–25s cinematic edit** of R02 hill + R03 cab + one validated explanatory tank cutaway; coherent movement, voices, subtitles.
- EP01 short: **75–100s initial editorial target** (can extend toward ~120s after retention/read-aloud assessment); TikTok 9:16 1080×1920, 30fps.
- EP01 long: **YouTube ~10min** independently written 16:9 1920×1080, 30fps; later milestone, not short video looped or stretched.
- Publish-ready means human VO audible, Capy voice character consistent, motion smooth, licensed SFX/music, visually reviewed physics, no absurd machine controls. Not automatic publishing.

## 2. Role ownership — precise boundaries
| Stage | Lead | Inputs → concrete outputs | Gate |
|---|---|---|---|
| Direction/story | ChatGPT + owner | clear narrative arc, dialogue, beat sheet, per-shot prompts | owner script approval |
| Asset & continuity | Codex | import/verify original GIF and R01–R03, SHA256 ledger, named shot references, filenames, asset provenance | no unknown/unlicensed images |
| Layout / diagrams | Codex + engineering reviewer | generic cross-section, labels, tank geometry, machine states, diagrams/synthetic plots | engineering review before animation |
| Cinematic movement | CapCut Pro AI / Seedance **operated by owner** | 5–8s image-to-video shot clips for driving, shock, studio talk, walkaround, camera reaction | visual identity and machinery QA |
| Character audio | CapCut text-to-speech / owner | 2–3 Vietnamese voice trials, separate WAV clips, agreed recording, lip-sync test where supported | owner voice selection |
| Precompositing | Codex | clip list, subtitle timing/SRT, file inspection, clean voices/SFX layers, H.264 previews, edit-ready sequence folder | no silent export |
| Editorial finish | CapCut Pro timeline, owner | stitched timing, sound design, music ducking, nuanced cuts, karaoke captions, original thumbnail, polished MP4 | owner watches start-to-end |
| Technical approval | ChatGPT + reviewer + owner | claim-to-source table, correct sensor/tank visuals, no private R&D leak | explicit publish authorization |

**Not Codex:** inventing artistic motion from stills as a substitute for a video model; silently changing mascot; treating a rough edit as final; operating CapCut Pro's desktop UI without a supported connected capability.
**Not CapCut AI:** independently deriving fuel physics, deciding sensor positions, writing definitive technical facts, assuming private GitHub read access, or making the entire long-form video from one prompt.
**No automatic cross-tool sync:** Codex/GitHub and CapCut desktop exchange local files. ChatGPT can update GitHub, but cannot assume CapCut has consumed the updates.

## 3. Exact scene assembly (cinematic, not cards)
1. **CAB-01 (6–8s):** use R03. Capy happily pilots with twin levers, glimpses dashboard fuel gauge, freezes, surprised eyes, turns to camera. Animate subtle cabin vibration; no extra limbs, no steering wheel.
2. **HILL-01 (5–8s):** use R02. Beautiful crawler excavator climbs a modest dirt slope, believable crawler travel and arm constraints. Exterior shot, background parallax.
3. **HOST-01 (5–8s):** R01 or approved studio GIF. Capy addresses viewer: informal short dialogue; camera pans/pushes smoothly.
4. **TANK-01 (~6s):** mechanically reviewed generic transparent fuel tank. Fixed fuel volume; while tank tilts, relative fluid depth at an assumed sensor may change. Diagram overlaid by editor, no hand-wavy impossible geometry.
5. **REACTION-01 (5–8s):** close-up Capy embarrassed, scratch/head tilt, comic gesture and eye contact.
6. **ROAD-01 (5–8s):** original excavator drives over small bumps to motivate slosh and filtering, not reckless operation.
7. **DATA-01 (~6s):** original QA-reviewed technical overlays (level / IMU / operating state / time), briefly over actual action; **not full-screen dashboard card sequences**.
8. **FINALE-01 (5–8s):** Capy stands by machine/studio with cheerful natural sign-off; teaser about CAN bus.

Reuse short clip IDs for shots, not long AI generations. The exact shots and durations come from approved voice script and editor, not generated text. Example short lines:
- CAPY (surprised, southern-conversational): "Ê ê, khoan! Sao mới leo cái dốc mà đồng hồ dầu tụt dữ vậy trời?!"
- NARRATOR (calm, plain-spoken): "Khoan kết luận. Máy nghiêng là cảm biến có thể đọc khác, chứ chưa chắc dầu bị mất."
- CAPY (embarrassed): "Ủa... vậy nãy giờ tui la oan hả trời?"
Keep language natural, not stiff textbook narration. Pause/laugh/reaction timing follows performance.

## 4. CapCut AI use instructions
- In CapCut Video Studio/Seedance, import original *approved still* for each shot (R03 for CAB-01). Use image-to-video with motion prompts; if Director/Standard offers multiple modes, test small first and log cost.
- For CAB-01 prompt: "Animate exactly this uploaded capybara inside an excavator cabin. The tracked excavator travels gently uphill; subtle cabin vibration. Capy smiles while holding twin joysticks, notices its dashboard fuel gauge, freezes in surprise, opens mouth, and turns toward camera. Cinematic 3D feature-animation acting, natural timing, keep same short arms and polo logo, no steering wheel, no extra limbs, no new dashboard components, no distorted digits or logos, portrait 9:16, 6–8 seconds, no captions baked in."
- Prefer audio-first: lock the script + record/generate the voice before trying AI dialogue lip sync. Generate TTS track separately if AI video has no direct audio support. Include lively inflection; test Vietnamese phonemes, e.g. "Ê ê, khoan! Sao mới leo cái dốc mà đồng hồ dầu tụt dữ vậy trời?!".
- AI model might make text/logos/gauges inconsistent. Fix labels, logo and gauge via CapCut graphic overlays/compositing instead of regenerating entire shot.
- Provide to Codex: `CAB-01_v01.mp4`, `CAB-01_voice_v01.wav`, `CAB-01_prompt_v01.txt`, runtime/credits/artifacts note. CapCut export is human-mediated; no connector to CapCut app currently verified.
- Human checks: paws remain short, lever geometry stable, excavator remains on tracks, no magically changing bucket/cab, no incoherent mouth expression, machine's actual fuel change not asserted as measured case.

## 5. Codex input/output interface
**Codex inputs:** github repo branch, script vN, `assets/approved/` mascot and R01–R03 files imported by owner, `shots/<shot_id>/` CapCut AI exports and voice stems.
**Codex outputs:**
```
episodes/EP01/
  scripts/short_vi.md, long_vi.md
  shot_manifest.csv
  source_review.md
  shots/CAB-01/{reference.png,clip.mp4,voice.wav,prompt.txt,qa.md}
  shots/HILL-01/...
  subtitles/short_vi.srt, long_vi.srt
  capcut_handoff/{clips/,audio/,subtitles/,READ_ME.md}
  preview/{style_test.mp4,short_rough.mp4}
```
Keep source files & licenses/hashes. Test clips with ffprobe; verify H.264 30fps / 1080x1920 (or upscale after AI export), 48kHz voice when practical, synchronized dialogue and caption safe zones. Never claim CapCut-native .capcut project generated until verified. Keep large video binaries out of GitHub unless user approves LFS/storage policy.

## 6. Approval gates / task sequence
- **G0 references**: owner supplies rights-cleared R01–R03 and approved mascot GIF; Codex imports and hashes.
- **G1 8s sample**: owner/CapCut outputs spoken CAB-01; ChatGPT+owner review face/voice/controls/logos/movement.
- **G2 20s proof**: 2–3 action shots + narrator + accurate cutaway + sound; no cards.
- **G3 short v1**: ~75–100s fully voiced 9:16 rough cut; owner approves improvements.
- **G4 final short**: subtitled, mixed, QA reviewed, MP4.
- **G5 YouTube**: distinct ~10min script, fully researched diagrams & narration, long-form export after short production lessons.
Nothing is published automatically. No merge/deploy of repo code without owner approval.

## 7. GitHub source & security constraints
This is a PUBLIC repo. Do not upload internal FuelGuard repository data, real field telemetry, unpublished research findings, finance/customer info, equipment identifiers or private images; use illustrations and synthetic demonstration values. A readout change on a slope is NOT proof of theft. Candidate sensor/IMU fusion is research, not a validated performance claim. All school-themed logos and third-party media require rights clearance.
