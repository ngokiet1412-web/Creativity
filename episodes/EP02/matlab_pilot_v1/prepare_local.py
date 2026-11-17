"""Pin public baseline and owner-selected CAD without modifying either source."""
import hashlib, json, pathlib, subprocess, sys

out = pathlib.Path(sys.argv[1]).resolve()
cad = pathlib.Path(sys.argv[2]).resolve()
if not (cad / 'PC2008_HIGH_PLACED_SOLIDS.prt').is_file():
    raise FileNotFoundError('Select the owner-approved NX fit revision directory')
if (out / 'source_manifest.json').exists():
    raise FileExistsError('Use a new output directory for each run')
out.mkdir(parents=True, exist_ok=True)
sha = '51f10d630fe32b40d1501500c4a989ac8259a959'
root = 'episodes/EP02/blender_v3_argon/'
files = ['animation/solve_ep02_v3_motion.m', 'animation/motion_trace_v3.csv',
         'source_nx_v2/pose_check.csv', 'source_nx_v2/joint_map.csv',
         'qa/matlab_kinematics_qa_summary.json']
inventory = []
for rel in files:
    data = subprocess.check_output(['git', 'show', sha + ':' + root + rel])
    dst = out / 'baseline' / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)
    inventory.append(dict(path=rel, commit=sha, sha256=hashlib.sha256(data).hexdigest()))
    if rel == 'animation/motion_trace_v3.csv':
        (out/'baseline_reference.csv').write_bytes(data)
for p in sorted(cad.iterdir()):
    if p.suffix in ('.prt', '.csv', '.py'):
        inventory.append(dict(path=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(out / 'source_manifest.json').write_text(json.dumps(inventory, indent=2), encoding='utf8')
(out / 'ansys').mkdir(exist_ok=True)
(out / 'ansys' / 'license_probe.inp').write_text('/BATCH\n/TITLE,CAPY authorized solver execution probe\n/PREP7\nFINISH\n/EXIT,NOSAVE\n')
print('Prepared pinned baseline and hashed', len(inventory), 'files in', out)
