# Creativity — CAPY BK 🐻🎬

A creator-production workspace for **Capy BK**, an independent animated education channel about automotive engineering, construction machinery, applied AI, HCMUT student life, and carefully approved public-friendly R&D concepts.

> **Status (2026-11-10):** Project kickoff / EP01 pre-production. The earlier 32-second animatic is a **silent narration placeholder**, not a releasable episode. New target: two editorially distinct cuts, **TikTok ~2 min (9:16)** and **YouTube ~10 min (16:9)**, with narration, expressive mascot animation, and scientifically reviewed diagrams.

## EP01: Máy xúc nghiêng dốc — dầu thật sự mất hay cảm biến đọc sai?

**Story premise:** Capy wrongly accuses someone of stealing fuel because the indicated tank level changed on a slope. The explanation distinguishes *level reading*, *actual fuel volume*, *engine consumption* and *unexplained loss*. Never label theft based on a single level change.

**Channel identity:** Original chubby, short-armed, friendly Capy BK mascot; white/blue school-inspired polo, cheerful facial expressions; studio contains laptop, microphone, BK-themed mug, and technical construction machinery visualizations. This is **not an official university channel**. Verify rights before publishing third-party artwork, marks, sound, or stock assets.

**Toolchain:** Research/script/technical review → asset sheets + animation → narration/TTS → reproducible assembly by Codex where possible → **CapCut Pro** editorial finishing → owner review → platform upload. Do not assume CapCut private project formats are supported for automated editing; exchange standard media assets and timed subtitles.

**Who owns what?**
- **Owner:** creative approvals, brand decisions, publication, final technical sign-off.
- **ChatGPT (Editor/Technical reviewer):** script treatment, scientific assumptions, storyboards, quality checklist.
- **Codex (Pipeline engineer):** reusable build scripts, asset inventory, 9:16 & 16:9 exports, audio and subtitle alignment, CI checks.
- **Animation/Visual agent:** mascot consistency, scene creation, character motion and compositing assets.
- **Voice/Editing agent:** voice casting and speech stems, CapCut Pro finishing, sound design.
- **Independent reviewer (e.g. Claude/Gemini):** check technical correctness, claim/evidence and editorial clarity.

## Repo rules

1. **No unpublished/private FuelGuard docs, customer data, machine IDs, pricing, source telemetry, financial workbooks, or restricted engineering/IP assets** in this public repo. Represent public-safe technical concepts using illustrative or synthetic data only.
2. All drafts should be identified as **DRAFT / UNVERIFIED** until accepted. A demo is not a deliverable.
3. Preserve the **approved mascot source**. Do not regenerate or silently change its silhouette, shirt emblem, studio mug, or face. The authoritative source must be added only after rights/source are approved.
4. Technical review is mandatory for fuel sensing, tilt compensation, CAN/ECU and construction equipment claims.
5. Agents develop in branches, propose PRs, attach previews/evidence, and do **not** merge or publish autonomously.

## Project docs
- `docs/CREATIVE_BIBLE.md` — brand and character continuity.
- `docs/PRODUCTION_PIPELINE.md` — multi-agent production, deliverables and CapCut Pro workflow.
- `episodes/EP01/BRIEF.md` — 2-minute and 10-minute treatment and storyboard.
- `episodes/EP01/VOICE_SCRIPT.md` — narration and dialogue direction.
- `docs/AGENT_HANDOFF.md` — scoped agent work packages, acceptance criteria.

Use GitHub Issues for ownership and PRs for actual artifacts. First goal: **one 15–25 second polished, voice-enabled proof-of-style segment**, approved before producing both complete cuts.
