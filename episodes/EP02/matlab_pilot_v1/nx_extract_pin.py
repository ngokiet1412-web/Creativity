"""NX 12 journal. Read-only source; selected load-bearing shank STEP export."""
import os, json, hashlib, re, time
from pathlib import Path
import NXOpen
import NXOpen.UF

src = Path(os.environ['CAPY_VALIDATION_CAD'])
out = Path(os.environ['CAPY_VALIDATION_OUT']) / 'ansys'
s = NXOpen.Session.GetSession()
uf = NXOpen.UF.UFSession.GetUFSession()
p, status = s.Parts.OpenBaseDisplay(str(src / 'pin_R42_L170.prt'))
assert status.NumberUnloadedParts == 0
status.Dispose()
assert p.PartUnits == NXOpen.BasePart.Units.Millimeters
bodies = []
for f in p.Features:
    if f.Name == 'Pin_shank':
        bodies.extend(f.GetBodies())
assert len(bodies) == 1, 'Require one exact named source feature'
box = list(uf.ModlGeneral.AskBoundingBox(bodies[0].Tag))
assert max(abs(a-b) for a,b in zip(box, [-42,-85,-42,42,85,42])) < .01
target = out / 'boom_rod_pin_shank.step'
assert not target.exists(), 'Refuse overwrite of exported evidence'
builder = s.DexManager.CreateStep214Creator()
try:
    builder.InputFile = str(src / 'pin_R42_L170.prt')
    builder.SettingsFile = str(Path(os.environ['UGII_BASE_DIR']) / 'STEP214UG' / 'ugstep214.def')
    builder.OutputFile = str(target)
    builder.FileSaveFlag = False
    builder.ExportFrom = NXOpen.Step214Creator.ExportFromOption.ExistingPart
    builder.ExportSelectionBlock.SelectionScope = NXOpen.ObjectSelector.Scope.SelectedObjects
    builder.ExportSelectionBlock.SelectionComp.Add(bodies[0])
    builder.ObjectTypes.Solids = True
    builder.LayerMask = '1-256'
    builder.Commit()
finally:
    builder.Destroy()
deadline = time.monotonic() + 30
while time.monotonic() < deadline:
    if target.is_file():
        step = target.read_bytes()
        if b'END-ISO-10303-21;' in step:
            assert step.count(b'MANIFOLD_SOLID_BREP(') == 1, 'Expected only the shank solid'
            assert re.search(rb'SI_UNIT\s*\(\s*\.MILLI\.\s*,\s*\.METRE\.\s*\)', step)
            break
    time.sleep(.25)
else:
    raise RuntimeError('NX STEP export incomplete')
record = dict(source_part=str(src/'pin_R42_L170.prt'), source_sha256=hashlib.sha256((src/'pin_R42_L170.prt').read_bytes()).hexdigest(),
              selected_owner_part=str(src/'PC2008_HIGH_PLACED_SOLIDS.prt'),
              selected_owner_sha256=hashlib.sha256((src/'PC2008_HIGH_PLACED_SOLIDS.prt').read_bytes()).hexdigest(),
              step_sha256=hashlib.sha256(step).hexdigest(), feature='Pin_shank',
              units='mm', bounding_box_mm=box, radius_mm=42, length_mm=170,
              defeaturing='Exclude overlapping end retainers and keeper tab; idealized load-bearing shank only',
              confidence='ASSUMED-PARAM concept; not OEM pin dimensions', step=str(target))
(out/'nx_pin_extraction.json').write_text(json.dumps(record,indent=2))
print('NX_PIN_EXTRACTION_DONE',box)
p.Close(NXOpen.BasePart.CloseWholeTree.TrueValue,NXOpen.BasePart.CloseModified.CloseModified,None)
