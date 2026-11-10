# CAPY BK assets — public-safe manifest

## Approved identity
| Asset | Purpose | Current location/status | Exact file |
|---|---|---|---|
| cheerful smiling Capy in studio | APPROVED visual & motion reference | Generated conversation file; still needs import to repo | cheerful_capybara_workspace_celebration.png (**actual GIF 89a despite .png**) |
| mascot original studio wave | earlier reference | Local only, not final identity | animated_bear_workshop_greeting.png (GIF despite extension) |
| avatar cropped from GIF | channel avatar | Local conversation file, awaiting upload | Capy_BK_avatar_vuong.png |
| animatic 32 sec | concept demo only | Local conversation file, awaiting upload | CAPY_BK_EP01_animatic_demo.mp4 |
| animatic builder | reproducible draft Python | Local conversation file, awaiting upload | build_capy_bk_ep01_animatic.py |
| animatic shotlist | prototype timings | Local conversation file, awaiting upload | CAPY_BK_EP01_animatic_shotlist.json |
| episode cover | draft thumbnail | Local conversation file, awaiting upload | CAPY_BK_EP01_cover.jpg |

**Do not mark any asset as present in repository until the binary is verified in GitHub.** Images and GIFs are not automatically transferred by writing this manifest; Codex/owner must import from approved local source on owner's computer.
Canonical mascot visual: very round cheerful chubby capybara with tiny arms, white-and-blue BK shirt; navy engineering studio; real BK-themed three-hexagon emblem on shirt, panel, and mug. No silent changes to character or logo.

## Filename handling
Some generated assets are GIF files with .png extensions. Detect MIME/magic bytes and rename *copies* to .gif before using in an automated pipeline. Keep original for provenance.
No machine footage, private user screenshots or licensed third-party stills may be pushed without explicit rights/safety check.

## Suggested binary asset layout (after owner import)
- assets/approved/capy_bk_master.gif
- assets/approved/capy_bk_avatar.png
- assets/prototypes/EP01_animatic_32s.mp4
- assets/prototypes/EP01_cover.jpg
- assets/prototypes/EP01_shotlist.json
- scripts/build_ep01_animatic.py

For each file, add sha256, original filename, owner approval date, license/permission and GitHub path here.
