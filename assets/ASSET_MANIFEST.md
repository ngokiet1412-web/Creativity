# CAPY BK asset inventory

The [approved package manifest](ASSET_SHA256.json) records the original names, byte counts and SHA-256 digests for all eight files. It comes from the package identified in [Issue #2](https://github.com/ngokiet1412-web/Creativity/issues/2#issuecomment-6766938944).

| File in this checkout | Role and review status |
|---|---|
| `assets/approved/capy_bk_master.gif` | Owner-approved character and motion reference, including the shirt emblem, BK mug and illuminated panel. The original filename ended in `.png`. The bytes start with `GIF89a` and decode as nine frames at 478×354. |
| `assets/approved/capy_bk_avatar_square.png` | Owner-supplied avatar in approved package. |
| `assets/approved/capy_bk_still_from_gif.png` | Owner-supplied still for an identity reference in CapCut. |
| `assets/prototypes/EP01_animatic_32s.mp4` | DRAFT reference with a synthetic sound bed. |
| `assets/prototypes/EP01_cover.jpg` | DRAFT cover reference. |
| `assets/prototypes/EP01_contact_sheet.jpg` | DRAFT storyboard reference. |
| `assets/prototypes/source/build_capy_bk_ep01_animatic_PROTOTYPE.py` | Exact package copy of the historical builder. The repository's `scripts/` version already has a different output-path setting and remains the reference for the historical Git revision. |
| `episodes/EP01/prototype_shotlist.json` | DRAFT historical timings. Existing Git blob matches the package. |

The owner's package announcement is dated 2026-11-10. Use of the BK mark is subject to rights review for commercial release. Capy BK is an independent channel. The pilot's generated-media and voice provenance is recorded under `asset` in [pilot.json](../episodes/EP01/pilot.json).

From the repository root, verify the checkout with `pwsh -File scripts/import_approved_assets.ps1`. To ingest again from the supplied files, pass `-ExtractedPath <folder>` or `-ZipPath <file>`. The ZIP route verifies the archive hash before extraction. The extracted-folder route verifies the pinned manifest, all eight file sizes and hashes, and the canonical GIF signature before copying. An existing mismatched destination stops the import. The ZIP itself was outside the supplied workspace snapshot used for this import.
