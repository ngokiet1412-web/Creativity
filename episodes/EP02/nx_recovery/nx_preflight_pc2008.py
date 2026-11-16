# -*- coding: utf-8 -*-
"""Safe, non-destructive NXOpen PC200-8 preflight, compatible with basic Python 3.
Run via Siemens NX > Tools > Journal > Play. Does not create/delete parts.
Logs locally beside this file: nx_preflight_YYYYMMDD_HHMMSS.txt.
"""
import os
import sys
import csv
import traceback
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
LOG_PATH = os.path.join(HERE, "nx_preflight_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".txt")
FAILS = []

def note(s):
    print(s)
    with open(LOG_PATH, "a") as f:
        f.write(str(s) + "\n")
    try:
        if S is not None:
            S.ListingWindow.Open()
            S.ListingWindow.WriteLine(str(s))
    except Exception:
        pass

S = None
def main():
    global S
    note("NXOpen PRE-FLIGHT — NO CAD WILL BE CREATED OR DELETED")
    note("Python: " + sys.version.replace("\n", " "))
    note("Script directory: " + HERE)
    try:
        import NXOpen
        import NXOpen.Features
        import NXOpen.GeometricUtilities
        import NXOpen.Assemblies
        import NXOpen.UF
        S = NXOpen.Session.GetSession()
        note("PASS — NXOpen import and active NX session")
        note("NX session type: " + str(type(S)))
        for obj, desc in [
            (S.Parts, "Parts"),
            (S.DexManager, "DexManager")
        ]:
            note("PASS — has " + desc + ": " + str(obj is not None))
        note("NX Parts.NewDisplay: " + str(hasattr(S.Parts, "NewDisplay")))
        note("NX DexManager.CreateStepCreator: " + str(hasattr(S.DexManager, "CreateStepCreator")))
        work = S.Parts.Work
        note("Current work part: " + (str(getattr(work, "Name", "unnamed")) if work else "(none opened)"))
        if work:
            note("Extrude builder: " + str(hasattr(work.Features, "CreateExtrudeBuilder")))
            note("Cylinder builder: " + str(hasattr(work.Features, "CreateCylinderBuilder")))
            note("Curve rules: " + str(hasattr(work.ScRuleFactory, "CreateRuleCurveDumb")))
    except Exception:
        FAILS.append("NXOpen import/session/API failure")
        note("FAIL — NXOpen could not initialize:\n" + traceback.format_exc())

    model_path = os.path.join(HERE, "pc2008_model.py")
    if not os.path.isfile(model_path):
        FAILS.append("pc2008_model.py missing")
        note("FAIL — missing required model source: " + model_path)
    else:
        note("PASS — found model module at " + model_path)
        try:
            import pc2008_model as M
            for attr in ("PARAMS", "parts", "poses", "instances"):
                if not hasattr(M, attr):
                    FAILS.append("Model missing " + attr)
                    note("FAIL — model missing " + attr)
            if all(hasattr(M, x) for x in ("PARAMS", "parts", "poses")):
                parts = M.parts()
                poses = M.poses()
                nfeat = sum(len(v) for v in parts.values())
                note("Model parts: %d ; features: %d ; poses: %d ; parameters: %d"
                     % (len(parts), nfeat, len(poses), len(M.PARAMS)))
                if not parts or not poses:
                    FAILS.append("Model geometry/poses empty")
                for n, fs in parts.items():
                    for f in fs:
                        for k in ("kind", "name", "op"):
                            if k not in f:
                                FAILS.append("%s feature missing %s" % (n, k))
        except Exception:
            FAILS.append("Model import/geometry failure")
            note("FAIL — model import/geometry error:\n" + traceback.format_exc())

    csv_path = os.path.join(HERE, "pose_check.csv")
    if os.path.isfile(csv_path):
        try:
            with open(csv_path, "r") as f:
                poses = list(csv.DictReader(f))
            failures = [x for x in poses if x.get("within_stroke", "").lower() != "yes"
                        or x.get("fourbar_closes", "").lower() != "yes"
                        or float(x.get("rod_extension_mm", "0")) < 0
                        or float(x.get("rod_extension_mm", "0")) > float(x.get("stroke_mm", "0"))]
            note("Pose CSV: %d rows, rejected: %d" % (len(poses), len(failures)))
            if failures:
                FAILS.append("Pose CSV stroke/closure error")
        except Exception:
            FAILS.append("Pose CSV parse failure")
            note("FAIL — CSV error:\n" + traceback.format_exc())
    else:
        note("INFO — pose_check.csv not co-located; optional geometry-table check skipped")

    if FAILS:
        note("PRE-FLIGHT RESULT: FAIL — " + "; ".join(FAILS))
        note("Do NOT run the full NX journal yet.")
    else:
        note("PRE-FLIGHT RESULT: PASS for environment/model imports only.")
        note("This does NOT mean NX feature builders or STEP export have been tested.")
    note("Log saved to: " + LOG_PATH)

if __name__ == "__main__":
    main()
