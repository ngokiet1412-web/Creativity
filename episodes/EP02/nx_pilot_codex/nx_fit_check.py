"""Check selected component pairs with NX solid Boolean intersections in memory."""
import csv
import os
from pathlib import Path

import NXOpen
import NXOpen.Features as Features


PAIRS = (
    ("carrier", "boom"), ("carrier", "boom_barrel_r"), ("carrier", "boom_barrel_l"),
    ("boom", "boom_barrel_r"), ("boom", "boom_rod_r"), ("boom", "boom_rod_l"),
    ("boom", "arm_barrel"), ("boom", "arm_rod"), ("boom", "stick"),
    ("stick", "arm_barrel"), ("stick", "arm_rod"), ("stick", "bucket_barrel"),
    ("stick", "bucket_rod"), ("stick", "bucket"), ("stick", "side_link"),
    ("stick", "h_link"), ("bucket", "side_link"), ("bucket", "h_link"),
    ("bucket", "bucket_rod"), ("side_link", "h_link"),
    ("side_link", "bucket_rod"), ("h_link", "bucket_rod"),
    ("boom_barrel_r", "boom_rod_r"), ("boom_barrel_l", "boom_rod_l"),
    ("arm_barrel", "arm_rod"), ("bucket_barrel", "bucket_rod"),
)
RAMS = ("boom_r", "boom_l", "arm", "bucket")
POSES = ("LOW", "REACH", "HIGH")


def placed_solids(part):
    # The Argon placed-solids journal writes features in a fixed component order.
    groups = {}
    ram_index = -1
    link_index = -1
    group = None
    for feature in part.Features:
        name = feature.Name
        if name == "Pin_shank":
            break
        if name.startswith(("Carrier_", "Boom_", "Stick_", "Bucket_")):
            group = name.split("_", 1)[0].lower()
        elif name == "Barrel_annular_tube_with_brochure_bore":
            ram_index += 1
            actuator, _, side = RAMS[ram_index].partition("_")
            suffix = "_" + side if side else ""
            group = actuator + "_barrel" + suffix
        elif name == "Chrome_rigid_piston_rod":
            group = actuator + "_rod" + suffix
        elif name in ("Link_bored_strap_R", "Side_link_outer_strap_R", "H_link_inner_strap_R"):
            link_index += 1
            group = ("side_link", "h_link")[link_index]
        if group is None or not hasattr(feature, "GetBodies"):
            continue
        for body in feature.GetBodies():
            if body.IsSolidBody:
                groups.setdefault(group, []).append((name, body))
    missing = {key for pair in PAIRS for key in pair} - set(groups)
    if missing or ram_index != len(RAMS) - 1 or link_index != 1:
        raise RuntimeError("Unexpected placed-solids feature sequence: {}".format(sorted(missing)))
    return groups


def intersection(session, part, first, second):
    mark = session.SetUndoMark(NXOpen.Session.MarkVisibility.Invisible, "Temporary fit check")
    builder = None
    try:
        builder = part.Features.CreateBooleanBuilderUsingCollector(Features.BooleanFeature.Null)
        builder.Operation = Features.Feature.BooleanType.Intersect
        builder.Targets.Add(first)
        collector = part.ScCollectors.CreateCollector()
        collector.ReplaceRules([part.ScRuleFactory.CreateRuleBodyDumb([second])], False)
        builder.ToolBodyCollector = collector
        result = builder.CommitFeature()
        return ("OVERLAP" if any(body.IsSolidBody for body in result.GetBodies()) else "NO_SOLID", "")
    except NXOpen.NXException as error:
        if error.ErrorCode == 670030:  # NX 12: tool body completely outside target body.
            return "NO_SOLID", ""
        return "NX_ERROR", "{} {}".format(error.ErrorCode, str(error))
    finally:
        if builder is not None:
            builder.Destroy()
        session.UndoToMark(mark, None)
        session.DeleteUndoMark(mark, None)


def audit_pose(session, root, pose, detail, summary):
    path = root / ("PC2008_" + pose + "_PLACED_SOLIDS.prt")
    part, status = session.Parts.OpenBaseDisplay(str(path))
    status.Dispose()
    try:
        groups = placed_solids(part)
        for pair in PAIRS:
            left, right = pair
            checks = overlaps = errors = 0
            for name_a, body_a in groups[left]:
                for name_b, body_b in groups[right]:
                    result, reason = intersection(session, part, body_a, body_b)
                    checks += 1
                    overlaps += result == "OVERLAP"
                    errors += result == "NX_ERROR"
                    if result != "NO_SOLID":
                        detail.writerow((pose, left, right, name_a, name_b, result, reason))
            summary.writerow((pose, left, right, checks, overlaps, errors))
        print("CHECKED " + pose)
    finally:
        part.Close(NXOpen.BasePart.CloseWholeTree.FalseValue,
                   NXOpen.BasePart.CloseModified.CloseModified, None)


def main():
    root = Path(os.environ["CAPY_FIT_INPUT"]).resolve()
    output = Path(os.environ.get("CAPY_FIT_AUDIT_OUT", str(root))).resolve()
    session = NXOpen.Session.GetSession()
    with (output / "nx_solid_interference.csv").open("x", encoding="utf-8", newline="") as details, \
         (output / "nx_solid_interference_summary.csv").open("x", encoding="utf-8", newline="") as totals:
        detail, summary = csv.writer(details), csv.writer(totals)
        detail.writerow(("pose", "component_a", "component_b", "feature_a", "feature_b", "nx_result", "reason"))
        summary.writerow(("pose", "component_a", "component_b", "boolean_tests", "overlaps", "nx_errors"))
        for pose in POSES:
            audit_pose(session, root, pose, detail, summary)
            details.flush()
            totals.flush()


if __name__ == "__main__":
    main()
