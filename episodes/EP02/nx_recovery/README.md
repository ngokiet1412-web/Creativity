# PC200-8 NX 12 — Claude journal recovery pack
**Status 2026-11-16:** code-level hardening only. NOT executed or certified in Siemens NX. No NX CAD or STEP file has been produced by ChatGPT.

## Existing evidence and missing required file
Owner supplied Claude's NX journal plus REPORT(1).md, assembly_params.csv, joint_map.csv, and pose_check.csv.
The report states: 12 concept parts/91 features were defined and tested in pure Python; NX journal was NOT run. The script imports a **separate pc2008_model.py** with parts(), poses(), instances(), and PARAMS. **That file was not uploaded and Claude's branch was not pushed to remote.** CSV tables are not a substitute for its feature geometry. Keep the ORIGINAL pc2008_model.py beside the journal files — do not make up OEM CAD geometry.

## New scripts
- [nx_preflight_pc2008.py](nx_preflight_pc2008.py): runs inside NX, checks NXOpen session and APIs, validates model import and optional pose_check.csv; generates only a local text log; never modifies CAD.
- [nx_build_pc2008_journal_safe.py](nx_build_pc2008_journal_safe.py): safe patched version of original journal. Does **not** delete old .prt files, isolates each run in nx_out_safe_runs/run_<timestamp>, fails fast when a geometry operation fails, verifies parts before assembling, and logs separate non-critical STEP/screenshot warnings. NX12-specific API calls are NOT yet runtime-verified.

## Place locally (do not upload unlicensed CAD)
Create D:/NX_Pilot_Safe/ and put files next to each other:
- pc2008_model.py — REQUIRED, original from Claude
- nx_preflight_pc2008.py
- nx_build_pc2008_journal_safe.py
- pose_check.csv — optional, recommended
- assembly_params.csv, joint_map.csv — source records

## Safe sequence
1. Save and back up all existing NX model files, especially Codex work. Do not overwrite or reuse its output directory.
2. In authorized/licensed Siemens NX: Tools > Journal > Play > nx_preflight_pc2008.py.
3. Locate nx_preflight_YYYYMMDD_HHMMSS.txt beside the .py. If FAIL, **do not run the full builder**; address the stated missing file/API issue.
4. After PASS, Tools > Journal > Play > nx_build_pc2008_journal_safe.py.
5. Inspect its new nx_out_safe_runs/run_<timestamp>/nx_run_log.txt. Core FAIL => stop and provide traceback. WARN optional STEP/screenshot => main assembly might be saved, but requires separate troubleshooting.
6. Open each resulting .prt in NX and verify Part Navigator, feature tree, dimensions and joint fit; do not assume STEP or PNG export is successful without inspection.

## Verified / Unverified distinction
- User-supplied CSV shows 9 low/mid/high pose rows marked within_stroke=yes, fourbar_closes=yes, with 0 reported link closure error. These are internally derived from assumed pin geometry, NOT Komatsu as-built validation.
- Still unverified: NX12 feature builder compatibility, the actual .prt, STEP and screenshots, true assembly mates, accurate OEM pin locations, and real hydraulic/cylinder structural feasibility.
- The journal still uses placed components rather than true NX assembly constraints, and expressions do not yet drive feature dimensions.
- Public repo contains only code/docs; never include copyrighted manuals, paid meshes, proprietary NX files or private FuelGuard data.

## What to send after first attempt
The **first FAIL block** in nx_run_log.txt (or the whole preflight text log), plus the actual NX version and original pc2008_model.py. This lets us fix NX-specific builder API calls without blind guessing.
