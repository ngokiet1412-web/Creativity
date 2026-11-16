# -*- coding: utf-8 -*-
"""NXOpen Python journal - PC200-8 work-equipment CONCEPT assembly.

STATUS: SAFETY-REPAIRED DRAFT, NOT VERIFIED IN NX 12. Tested only by source review.
Original journal was authored by Claude without NX runtime access.
This version never overwrites existing CAD and stops on the first core feature failure.

Run (after the owner confirms a valid NX licence):
  NX > Menu > Tools > Journal > Play...  (select this file), or
  Use NX > Tools > Journal > Play for this .py after preflight.
Keep Claude\'s original pc2008_model.py next to this file. Output is isolated in
  ./nx_out_safe_runs/run_<timestamp>/ (never use the original ./nx_out).
  <part>.prt for every part, PC2008_WORK_EQUIPMENT_CONCEPT_ASSY_<pose>.prt
  for low / mid / high, PC2008_WORK_EQUIPMENT_CONCEPT_ASSY_mid.stp (AP214),
  4 viewport PNGs, nx_run_log.txt (every step and every exception).

What the journal does
  * one native feature per entry of pc2008_model.parts(): Extrude of a
    sketch-less line profile (prism) or Cylinder, united / subtracted in
    order, so the feature tree is editable and named
  * every PARAMS entry becomes an expression in each part (value + a
    comment with confidence and source id)
  * components are placed by computed position + rotation for each pose
KNOWN GAPS (do by hand in NX or extend the journal after the first run)
  * no assembly constraints / joints are created yet - components are only
    positioned; add Touch-Align on the pin axes (ids in joint_map.csv)
  * profiles are plain lines (arcs are polylines); no sketches, no blends
  * expressions are created but the extrude profiles are not driven by them
"""
import math
import os
import sys
import traceback
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
try:
    import pc2008_model as M  # noqa: E402
except Exception:
    raise RuntimeError(
        "Missing/invalid pc2008_model.py. Copy the ORIGINAL file created by Claude "
        "into the SAME directory as this journal, then run nx_preflight_pc2008.py."
    )

import NXOpen  # noqa: E402
import NXOpen.Features  # noqa: E402
import NXOpen.GeometricUtilities  # noqa: E402
import NXOpen.Assemblies  # noqa: E402
import NXOpen.UF  # noqa: E402

S = NXOpen.Session.GetSession()
# Never trust sys.argv in NX journal player and NEVER overwrite an existing .prt.
# Every execution gets its own entirely new directory.
ROOT = os.path.join(HERE, "nx_out_safe_runs")
if not os.path.isdir(ROOT):
    os.makedirs(ROOT)
OUT = os.path.join(ROOT, "run_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
os.makedirs(OUT)
LOG = open(os.path.join(OUT, "nx_run_log.txt"), "w")
LOG.write("SAFE RUN DIRECTORY: %s\n" % OUT)
LOG.flush()


def log(msg):
    LOG.write(msg + "\n")
    LOG.flush()
    try:
        S.ListingWindow.Open()
        S.ListingWindow.WriteLine(msg)
    except Exception:
        pass


def step(label, fn, *a):
    try:
        r = fn(*a)
        log("OK    " + label)
        return r
    except Exception:
        log("FAIL  " + label + "\n" + traceback.format_exc())
        raise


def new_part(name):
    path = os.path.join(OUT, name + ".prt")
    if os.path.exists(path):
        raise RuntimeError("Refusing to overwrite existing CAD file: " + path)
    S.Parts.NewDisplay(path, NXOpen.Part.Units.Millimeters)
    work = S.Parts.Work
    if work is None:
        raise RuntimeError("NX did not set a work part after NewDisplay: " + path)
    return work


def add_expressions(work):
    unit_mm = work.UnitCollection.FindObject("MilliMeter")
    for k, v in M.PARAMS.items():
        try:
            if v[1] == "mm":
                e = work.Expressions.CreateWithUnits("%s=%g" % (k, v[0]), unit_mm)
            else:
                e = work.Expressions.CreateExpression("Number", "%s=%g" % (k, v[0]))
            e.EditComment("%s | source %s | %s" % (v[2], v[3], v[4]))
        except Exception:
            log("  expression %s failed: %s" % (k, traceback.format_exc().splitlines()[-1]))


def boolean(builder_op, op, target):
    BT = NXOpen.GeometricUtilities.BooleanOperation.BooleanType
    if target is None:
        builder_op.Type = BT.Create
    else:
        builder_op.Type = BT.Unite if op == "add" else BT.Subtract
        builder_op.SetTargetBodies([target])


def first_body(work):
    bodies = [b for b in work.Bodies]
    return bodies[0] if bodies else None


def make_prism(work, f, target):
    pts = f["pts"]
    z0 = min(f["z0"], f["z1"])
    z1 = max(f["z0"], f["z1"])
    lines = []
    for i in range(len(pts)):
        a = pts[i]
        b = pts[(i + 1) % len(pts)]
        if math.hypot(a[0] - b[0], a[1] - b[1]) < 1e-3:
            continue
        lines.append(work.Curves.CreateLine(NXOpen.Point3d(a[0], a[1], 0.0), NXOpen.Point3d(b[0], b[1], 0.0)))
    eb = work.Features.CreateExtrudeBuilder(NXOpen.Features.Feature.Null)
    sec = work.Sections.CreateSection(0.0095, 0.01, 0.5)
    eb.Section = sec
    sec.SetAllowedEntityTypes(NXOpen.Section.AllowTypes.OnlyCurves)
    if not lines:
        raise RuntimeError("Empty/degenerate prism profile: %s" % f["name"])
    rule = work.ScRuleFactory.CreateRuleCurveDumb(lines)
    sec.AddToSection([rule], lines[0], NXOpen.NXObject.Null, NXOpen.NXObject.Null,
                     NXOpen.Point3d(pts[0][0], pts[0][1], 0.0), NXOpen.Section.Mode.Create, False)
    eb.Direction = work.Directions.CreateDirection(NXOpen.Point3d(0.0, 0.0, 0.0), NXOpen.Vector3d(0.0, 0.0, 1.0),
                                                   NXOpen.SmartObject.UpdateOption.WithinModeling)
    eb.Limits.StartExtend.Value.RightHandSide = "%.4f" % z0
    eb.Limits.EndExtend.Value.RightHandSide = "%.4f" % z1
    boolean(eb.BooleanOperation, f["op"], target)
    feat = eb.CommitFeature()
    eb.Destroy()
    feat.SetName(f["name"].upper())
    return feat


def make_cyl(work, f, target):
    cb = work.Features.CreateCylinderBuilder(NXOpen.Features.Feature.Null)
    cb.Type = NXOpen.Features.CylinderBuilder.Types.AxisDiameterAndHeight
    p = f["p"]
    ax = f["axis"]
    origin = NXOpen.Point3d(p[0], p[1], p[2])
    direction = work.Directions.CreateDirection(origin, NXOpen.Vector3d(float(ax[0]), float(ax[1]), float(ax[2])),
                                                NXOpen.SmartObject.UpdateOption.WithinModeling)
    point = work.Points.CreatePoint(origin)
    cb.Axis = work.Axes.CreateAxis(point, direction, NXOpen.SmartObject.UpdateOption.WithinModeling)
    cb.Diameter.RightHandSide = "%.4f" % f["d"]
    cb.Height.RightHandSide = "%.4f" % f["h"]
    boolean(cb.BooleanOption, f["op"], target)
    feat = cb.CommitFeature()
    cb.Destroy()
    feat.SetName(f["name"].upper())
    return feat


def build_part(name, feats, pin_len=None):
    work = new_part(name)
    step("%s: expressions" % name, add_expressions, work)
    for f in feats:
        if pin_len is not None and f["name"] == "pin":
            f = dict(f, h=pin_len)
        target = first_body(work)
        if target is None and f["op"] == "cut":
            log("SKIP  %s.%s (cut before any body)" % (name, f["name"]))
            continue
        fn = make_prism if f["kind"] == "prism" else make_cyl
        step("%s.%s [%s, %s]" % (name, f["name"], f["op"], f["conf"]), fn, work, f, target)
    step("%s: save" % name, work.Save, NXOpen.BasePart.SaveComponents.TrueValue, NXOpen.BasePart.CloseAfterSave.FalseValue)
    return work


def zrot(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    m = NXOpen.Matrix3x3()
    m.Xx, m.Xy, m.Xz = c, s, 0.0
    m.Yx, m.Yy, m.Yz = -s, c, 0.0
    m.Zx, m.Zy, m.Zz = 0.0, 0.0, 1.0
    return m


def build_assembly(pose_name, pose):
    assy = new_part("PC2008_WORK_EQUIPMENT_CONCEPT_ASSY_" + pose_name)
    inst, _ = M.instances(pose)
    for part, iname, org, deg, pin_len in inst:
        pname = part if pin_len is None else "pivot_pin_L%d" % int(round(pin_len))
        path = os.path.join(OUT, pname + ".prt")
        if not os.path.isfile(path):
            raise RuntimeError("Missing component part before assembly: " + path)
        step("assy %s: add %s" % (pose_name, iname), assy.ComponentAssembly.AddComponent, path, "MODEL", iname.upper(),
             NXOpen.Point3d(org[0], org[1], org[2]), zrot(deg), -1)
    step("assy %s: save" % pose_name, assy.Save, NXOpen.BasePart.SaveComponents.TrueValue, NXOpen.BasePart.CloseAfterSave.FalseValue)
    return assy


def export_step(assy_path, out_path):
    sc = S.DexManager.CreateStepCreator()
    sc.ExportAs = NXOpen.StepCreator.ExportAsOption.Ap214
    sc.InputFile = assy_path
    sc.OutputFile = out_path
    sc.FileSaveFlag = False
    sc.Commit()
    sc.Destroy()


def screenshot(name, view_name):
    work = S.Parts.Work
    lay = work.Layouts.Current
    lay.ReplaceView(work.ModelingViews.WorkView, work.ModelingViews.FindObject(view_name), True)
    work.ModelingViews.WorkView.Fit()
    uf = NXOpen.UF.UFSession.GetUFSession()
    uf.Disp.CreateImage(os.path.join(OUT, name + ".png"), NXOpen.UF.UFConstants.UF_DISP_PNG, NXOpen.UF.UFConstants.UF_DISP_ORIGINAL)


def optional_step(label, fn, *args):
    """Optional export/preview errors are logged but never hide geometry errors."""
    try:
        return step(label, fn, *args)
    except Exception:
        log("WARN optional step failed: " + label)
        return None


def main():
    log("PC200-8 concept journal - safe NX run")
    optional_step("NX release", lambda: S.GetEnvironmentVariableValue("UGII_FULL_VERSION"))
    for name in ("PARAMS", "parts", "poses", "instances"):
        if not hasattr(M, name):
            raise RuntimeError("pc2008_model.py missing required name: " + name)
    parts = M.parts()
    for name, feats in parts.items():
        if name == "pivot_pin":
            continue
        build_part(name, feats)
    poses = M.poses()
    lens = sorted(set(int(round(i[4])) for i in M.instances(poses[0][1])[0] if i[4] is not None))
    for L in lens:
        build_part("pivot_pin_L%d" % L, parts["pivot_pin"], float(L))
    for pose_name, pose in poses:
        build_assembly(pose_name, pose)
        optional_step("screenshot %s" % pose_name, screenshot, "NX_VIEW_%s_RIGHT" % pose_name, "Right")
        if pose_name == "mid":
            optional_step("screenshot mid trimetric", screenshot, "NX_VIEW_mid_TRIMETRIC", "Trimetric")
            optional_step("STEP AP214", export_step, os.path.join(OUT, "PC2008_WORK_EQUIPMENT_CONCEPT_ASSY_mid.prt"),
                 os.path.join(OUT, "PC2008_WORK_EQUIPMENT_CONCEPT_ASSY_mid.stp"))
    log("CORE COMPLETED. Inspect WARN lines and verify files in NX before acceptance.")
    log("Output: " + OUT)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log("ABORTED: " + traceback.format_exc())
        raise
    finally:
        LOG.close()