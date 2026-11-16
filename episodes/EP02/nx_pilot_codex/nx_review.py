"""Reopen authored Siemens parts and verify saved geometry and datums."""

import csv
import math
import re
import sys
import traceback
from pathlib import Path

import NXOpen

sys.path.insert(0,str(Path(__file__).resolve().parent))
import nx_pilot


def recent_build(root):
    complete = [p for p in root.glob("NX_NATIVE_*")
                if re.fullmatch(r"NX_NATIVE_\d{8}_\d{6}",p.name)
                and (p/"nx_run.log").is_file()
                and (p/"PC2008_REACH_EXPLODED_VIEW.prt").is_file()]
    if not complete:
        raise FileNotFoundError("Run nx_pilot.py first")
    return max(complete, key=lambda p:p.name)


def open_part(session, path):
    part,status=session.Parts.OpenBaseDisplay(str(path))
    status.Dispose()
    return part


def inspect_pose(part, rows):
    datums = {}
    for feature in part.Features:
        if feature.Name.upper().startswith("J_"):
            entities = [entity for entity in feature.GetEntities() if isinstance(entity, NXOpen.Point)]
            if len(entities)!=1:
                raise ValueError("CAD datum {} does not expose one point".format(feature.Name))
            datums[feature.Name.upper()] = entities[0].Coordinates
    maximum = 0.
    for row in rows:
        name=row["joint_id"]
        y=float(row["y_mm"])
        suffix="_R" if y<0 else ("_L" if y>0 else "")
        actual=datums[("J_"+name+suffix).upper()]
        expected=[float(row[k]) for k in ("x_mm","y_mm","z_mm")]
        error=math.sqrt(sum((a-b)**2 for a,b in zip((actual.X,actual.Y,actual.Z),expected)))
        maximum=max(maximum,error)
    if maximum>0.01 or len(datums)!=len(rows):
        raise ValueError("Saved datum count or coordinates differ from joint_map.csv")
    return maximum


def main():
    session=NXOpen.Session.GetSession()
    root=Path(__file__).resolve().parent
    directory=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else recent_build(root)
    with (directory/"joint_map.csv").open(newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    log=directory/"native_reopen.log"
    with log.open("w",encoding="utf-8") as stream:
        def report(msg):
            stream.write(msg+"\n")
            stream.flush()
            print(msg)
        try:
            for name in ("LOW","HIGH","REACH","REACH_EXPLODED_VIEW"):
                stem="PC2008_"+name
                is_pose=name!="REACH_EXPLODED_VIEW"
                if is_pose:
                    stem+="_PLACED_SOLIDS"
                part=open_part(session,directory/(stem+".prt"))
                solids=sum(1 for body in part.Bodies if body.IsSolidBody)
                if solids!=76:
                    raise RuntimeError("{} reopened with {} solid bodies".format(stem,solids))
                error=inspect_pose(part,[r for r in rows if r["pose"]==name.lower()]) if is_pose else None
                report("{}: {} solids, datum discrepancy mm={}".format(stem,solids,error))
                nx_pilot.fit(part)
                if name=="REACH":
                    nx_pilot.optional(report,"STEP 76-solid handoff",nx_pilot.step_export,session,
                                      part,directory/"PC2008_REACH_AP214.step")
            bucket=open_part(session,directory/"bucket.prt")
            solids=sum(1 for body in bucket.Bodies if body.IsSolidBody)
            if solids!=11:
                raise RuntimeError("Bucket reopened without all eleven solid bodies")
            nx_pilot.fit(bucket)
            report("BUCKET: {} solids | NX_OPEN_VERIFY_OK".format(solids))
        except Exception:
            report(traceback.format_exc())
            raise


if __name__=="__main__":
    main()
