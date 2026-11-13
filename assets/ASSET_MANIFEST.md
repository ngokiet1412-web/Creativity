# CAPY BK assets — public-safe manifest

## Cinematic V2 reference ledger

The [V2 ledger](APPROVED_SHA256_V2.json) records four original inputs, their byte counts, format, dimensions, SHA-256 and shot IDs. R01 is Capy beside the parked excavator, R02 is the uphill exterior and R03 is the cabin close-up. Use the original R03 file for CAB-01. R01 and R02 support continuity review and later shots.

1. Locate the original ChatGPT files by subject and recorded original filename. Use the approved package for the studio master.
2. Copy the bytes to the paths in the ledger. For future imports, compare the source SHA-256 before copying and stop if a destination has different bytes.
3. Run `python scripts/cab01.py verify-assets` from the checkout. Compare the GIF signature, PNG headers, dimensions, lengths and hashes.
4. Confirm approval and rights before using or distributing a new source. The BK mark requires release clearance. Keep legacy prototypes and generated CapCut takes out of the approved reference directory.

## Approved identity
| Asset | Purpose | Current location/status | Exact file |
|---|---|---|---|
| cheerful smiling Capy in studio | APPROVED visual & motion reference | `assets/approved/capy_bk_master.gif`, see V2 ledger | cheerful_capybara_workspace_celebration.png (**actual GIF 89a despite .png**) |
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
