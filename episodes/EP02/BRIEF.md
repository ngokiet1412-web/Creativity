# KĨ SƯ ƠIII! / CAPY BK — EP02 BRIEF (DRAFT)

## Working title and creative promise
**"Ủa, tay máy đào lấy đâu ra sức mạnh dữ vậy?!"** — a ~2:00–2:10 TikTok episode about how an excavator hydraulic system moves the boom, stick, and bucket. Direct sequel to EP01's final question. Cute 2D cartoon, **NOT glossy 3D** or a slideshow. Capy has short stubby paws, cheery expressive face, original white/blue BK shirt; engineer mentor supports with a second natural Vietnamese voice. Preserve same approved dark-blue studio with BK mug, mic and laptop, and same stylized yellow excavator at construction site.

### Viewer takeaway
1. Diesel engine supplies mechanical power to **hydraulic pump**; pump delivers **flow**.
2. When oil meets load/restriction, **pressure develops**; **control valves** route pressurized oil to an actuator.
3. **Hydraulic cylinder** transforms fluid pressure and flow into linear force/motion; pin-jointed linkages move the boom, arm and bucket.
4. **Idealized** cylinder force F = p*A, speed v ≈ Q/A. Actual bucket lifting force is not equal to p*A due to linkage leverage, cylinder side and real losses.
5. No free energy, and no guarantee the excavator can lift any mass. Safety and pressure limits matter.

### Audience/format
- ~120–125 seconds, portrait 9:16 1080×1920 30fps; use recorded spoken track as timing authority. Draft until owner's approval.
- Separate later YouTube long-form ~10min deep dive, not the same short stretched.
- Tone: friendly, slightly cheeky Southern Vietnamese Capy + calm witty engineer; two voices fixed to EP01-approved voices and signature tag.
- First 5s: brand sonic logo "Kĩ Sư Ơiiii!" from owner-approved audio (rights handled locally, not stored in this public repo), then immediate comedic hook. Avoid reintroducing full biography from EP01.
- End with engineering teaser: what protects the system from excessive pressure? EP03 pressure relief valves.

### Scene plan
See SHOTLIST_AND_VOICE_V1.md for 12 production beats and VO dialogue. Aim 12–15 total AI/rendered shots with some clean 2D layer-rig repeats and B-roll inserts, not 28 totally isolated stills. Keep cuts motivated by story/action. Opening in studio with BK mug, match-cut to job site; avoid showing Capy near loaded buckets and never show any person under suspended load.

### Technical boundaries
Concept drawings are **generic hydraulic diagrams**. Do NOT assert a specific Komatsu PC200-8 or other real excavator circuit, exact system pressure, cylinder bore, lifting capacity, ECU layout or operating procedure without verified manual and model evidence. The simplified two-syringe experiment illustrates pressure transmission but not a complete excavator hydraulic circuit. Cylinder linkage must obey pin rotation and rod length geometry; no morphing of pistons/arms/tracks. Safety: no touching pressurized hydraulic lines, no machine control by untrained character while loaded.

### Sound and motion
- Keep **two VO stems per scene** with names CAPY / ENGINEER, WAV 48kHz preferable. Avoid eSpeak and overly fast TTS. Owner selects AI voice and approves brand tag. No forced lip-sync with model that corrupts character identity.
- Use 2D Godot/Codex layer rig for controlled character gestures and machine hinges, CapCut Pro for assembly, ducking, captions, SFX.
- Fixed background, separate moving cutouts, no mesh warps or non-uniform scaling. Track & wheel motion only when machine is actually driving. Cylinder rods remain attached, hydraulic hoses don't teleport.
- Give viewer enough time to watch piston move and fluid route; drawings are validated by reviewer before animation.

### Reference technical sources
- Bosch Rexroth: basic hydraulic circuitry, pump/motor/valves/cylinders and F = p*A, speed vs flow: https://www.btpco.com/download/training/Boschrexroth/1-Basic_Principles_and_Components_of_Fluid_Technolog.pdf
- Bosch Rexroth Academy reference book: https://dc-mkt-prod.cloud.bosch.tech/xrm/media/global/training_1/digital_media/reference_books/knowledge-in-detail-hydraulics-basic-principles.pdf
- Caterpillar: overview of fluid power/cylinders in loader equipment: https://www.cat.com/en_US/articles/for-owners/backhoe-loaders/backhoe-loader-hydraulic-flow-switch.html

### Roles + gates
- ChatGPT: story/dialogue, storyboard, scientific review, editorial QA.
- Codex: original 2D assets/rigging, verified diagrams, shot-manifest, SRT, export checks; branch + PR only; no merge without owner permission.
- Owner/CapCut Pro: approved VO/voice casting, timing, music, postproduction, preview approval and distribution.
- CapCut AI may be tried only in small reference-locked tests and **not** for fully remaking Capy; avoid credits wasted in prior trials.
- First acceptance: **two 6–8sec proof shots:** (a) Studio Capy turns from mug to camera and asks “Ủa?” (b) one hydraulic cylinder moves a mechanical link with fluid overlay, fixed machine geometry.
- Public repo: no actual unpublished FuelGuard data or machine/customer identities.
