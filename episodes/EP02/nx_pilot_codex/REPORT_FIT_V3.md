# PC200-8 work equipment fit correction in NX 12

**DRAFT for Issue #13.** This journal builds a separate revision of the Argon V2 concept. It requires the owner-supplied `nx_pilot_v2_argon.py` and `geometry_v2_argon.py` from the V2 handoff.

## Geometry changes

The V2 boom lift brackets included nearly solid blocks around the rod ends. They intersected the rod and bore collars. V3 uses two tapered bridge plates and split, bored forks. The pin and cylinder axes for the two boom cylinders retain their V2 locations. Each boom rod eye has 8 mm of concept clearance per side.

The arm and bucket cylinder bodies also intersected the box covers in V2. The arm cylinder base pin rises 230 mm in the boom frame, and the bucket cylinder base pin rises 195 mm in the stick frame. The local X and Y coordinates stay the same. Both mounts use a center tongue inside the cylinder clevis. The boom covers end before the swing area of the stick horn.

The bucket four-bar has separate axial bands for the side links and H-link. The H-link retains a cross tube, the bucket torque tube moves clear of the links, and the recess at the bucket hinge clears the stick sleeve. Pin axes are retained as hidden display references. Updated centers and spans are in `joint_map.csv` and `pin_verification_v2.csv`.

Komatsu's brochure confirms the 5,700 mm boom and 2,925 mm arm option. It lists the following cylinder **bore × stroke × rod diameter**, in millimeters. [Komatsu CEN00049-08](https://d3is8fue1tbsks.cloudfront.net/PDF/Komatsu/PC200-8_PC200LC-8.pdf)

| Actuator | Count | Bore × stroke × rod diameter |
| --- | --- | --- |
| Boom | 2 | 120 × 1,334 × 85 |
| Arm | 1 | 135 × 1,490 × 95 |
| Bucket | 1 | 115 × 1,120 × 80 |

Pin coordinates, bracket profiles, closed pin-to-pin lengths, assembly clearances and transverse link stacks are `ASSUMED-PARAM`. The changes improve fit for the concept. OEM pivot locations and fit require a dimensioned assembly drawing or measurements of the corresponding PC200-8 configuration.

## Native verification

Siemens NX 12.0.0.27 built the parts and three assemblies. Each assembly reopened in NX with 27 occurrences, 11 constraints and all 13 named assembly reference objects hidden. The reach AP214 translation processed 169 solid bodies without translator errors.

The journal checked 26 component pairs with temporary solid Boolean intersections in each placed-solids part. It rolled back the Boolean after every comparison and closed the part without saving changes.

| Pose | Argon V2 body tests | V2 solid intersections | V3 body tests | V3 solid intersections |
| --- | ---: | ---: | ---: | ---: |
| Low | 2,617 | 63 | 2,081 | 0 |
| Reach | 2,617 | 67 | 2,081 | 0 |
| High | 2,617 | 62 | 2,081 | 0 |

The body counts differ because V3 replaced several individual features. There were no Boolean errors in either run. The nine pose-by-actuator rows also passed the analytic stroke, overlap, and four-bar closure checks in `pose_check.csv`. The supported review covers those three discrete poses and the selected pairs. A continuous sweep, pin hardware interference, weld details, hydraulic hose clearance, and structural strength remain unverified.

## Reproduce

In PowerShell, run from this journal's directory with a working Siemens NX 12 Modeling setup. `CAPY_ARGON_SOURCE` points to the owner-supplied dependencies. `CAPY_FIT_OUT` must be a new folder so the original handoff remains available for comparison.

```powershell
$env:CAPY_ARGON_SOURCE = (Get-Location).Path
$env:CAPY_FIT_OUT = Join-Path $env:TEMP ('NX_ARGON_V3_FIT_' + (Get-Date -Format yyyyMMdd_HHmmss))
$env:PYTHONDONTWRITEBYTECODE = '1'
$build = (Resolve-Path 'nx_fit_v3.py').Path
$check = (Resolve-Path 'nx_fit_check.py').Path
Push-Location "$env:UGII_BASE_DIR\NXBIN"
try {
  & .\run_journal.exe $build
  $env:CAPY_FIT_INPUT = $env:CAPY_FIT_OUT
  & .\run_journal.exe $check
} finally {
  Pop-Location
}
```

For a baseline comparison, set `CAPY_FIT_INPUT` to the V2 handoff folder and `CAPY_FIT_AUDIT_OUT` to a separate, existing folder. The audit writes new CSVs and rejects existing audit filenames.
