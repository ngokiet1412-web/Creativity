# EP01 audio-first workflow — CapCut visuals + independently approved speech

## Observation from owner-supplied test
The owner tested a 7-second 2D Capy BK cabin clip. Frame-to-frame character expression changes are promising, but the owner reports AI speech/audio quality issues; Codex makes attractive still images but does not supply the desired full-quality animation. File probe: 768×1366, 24fps, H.264 video; AAC stereo 32kHz audio. **Audio stream is present**, so do not label this as missing audio; perceptual TTS/lipsync diagnosis requires listening review. Do not upload the owner's video to this PUBLIC repo without checking rights/approval.

## Owner-approved division
- **Codex:** original consistent Capy reference sheets, stills/scene frames, shot-by-shot technical validation, subtitle timings, WAV conversion and loudness checks, asset nomenclature, export QA; no slideshow-style substitute animation.
- **CapCut AI / Seedance:** image-to-video visual motion and character acting in 5–8 sec clips. Prefer **video generation without baked-in AI dialogue**, because uneditable generated audio is problematic.
- **Voice:** record owner narration or create distinct high-quality Vietnamese TTS in a dedicated pass; keep separate WAV for every line and test expressive conversational voice (not newsreader). Never clone owner voice without consent.
- **CapCut Pro timeline:** import video **muted**, import selected voice WAV separately, synchronize visible mouth cues and/or manual mouth shapes, then add soft engine SFX and music, duck under voice; add human-reviewed subtitles.
- **Approval:** owner listens before approving 1 shot and only then batch-renders more AI animations.

## Recommended immediate A/B
1. Use the same 7-second CAB01 video image with original built-in sound -> baseline A.
2. Mute original audio. Add one clean separately generated WAV track from same dialogue -> B.
3. Compare natural Vietnamese pronunciation, prosody, loudness, sync, perceived robotic artifacts, editability.
4. If lipsync is off and cannot be fixed, trim mouth-speaking close-ups or use reaction + cutaway while narration continues; don't destroy character identity with dubious face-to-voice mapping.
5. Test final H.264/AAC master plays correctly on mobile with speech present, not just visual.

## Technical notes
- Upsampling from 32kHz AAC to 48kHz WAV does NOT restore detail; it only standardizes timeline compatibility. Source quality may need new TTS/recording.
- Don't change from original 24fps to 30fps by simply relabeling; explicitly conform during export if needed.
- Do not artificially claim successful lip sync, corrected audio, or completed TikTok without approval.

The first episode concept is **Capy discovers construction machinery**, not the older fuel-sensor scenario. Match current episodes/EP01/BRIEF.md.
