"""PC200-8-style pilot calculations in mm. No NX dependencies; Python 3.6+."""

import csv
import math
from pathlib import Path


SOURCE = "S01 CEN00049-08"
ASSUMED = "ASSUMED-PARAM"
PUBLIC = "VERIFIED-PUBLIC"
CONCEPT = "CONCEPT-V6-ADAPTATION"
BOOM_LENGTH = 5700.0
STICK_LENGTH = 2925.0
GROUND_Z = -1584.9
BOOM_HALF_Y = 520.0
ACTUATORS = {
    "boom": dict(bore=120., stroke=1334., rod=85., closed=2200., eye=42., qty=2),
    "arm": dict(bore=135., stroke=1490., rod=95., closed=1850., eye=44., qty=1),
    "bucket": dict(bore=115., stroke=1120., rod=80., closed=1700., eye=40., qty=1),
}
JOINTS = {
    "boom_base": ("boom", "carrier", (0., 0.)),
    "boom_tip": ("stick", "boom", (BOOM_LENGTH, 0.)),
    "stick_tip": ("bucket", "stick", (STICK_LENGTH, 0.)),
    "boom_cyl_A": ("boom_barrel", "carrier", (450., -850.)),
    "boom_cyl_B": ("boom_rod", "boom", (2600., 220.)),
    "arm_cyl_A": ("arm_barrel", "boom", (3565.7, 961.4)),
    "arm_cyl_B": ("arm_rod", "stick", (-600., 0.)),
    "bucket_cyl_A": ("bucket_barrel", "stick", (500., 400.)),
    "bucket_side": ("side_link", "stick", (2700., 150.)),
    "bucket_boss": ("h_link", "bucket", (188.6, -207.5)),
}
LINK_SIDE = 650.0
LINK_H = 750.0
POSES = {"low": (22.5, 101., 56.), "reach": (29., 86., 62.), "high": (42., 105., 76.)}

# Lateral sectional profiles in local X/Z. Extrusion directions and widths are
# selected in the NX journal; the walls represent a built-up steel concept.
BOOM_PROFILE = (
    (-240., -95.), (-125., -240.), (225., -285.), (1125., 130.),
    (2010., 540.), (3180., 640.), (4750., 270.), (5740., -110.),
    (5860., -40.), (5860., 95.), (5620., 220.), (4780., 570.),
    (3520., 1050.), (2480., 1080.), (1660., 890.), (820., 485.), (-125., 230.),
)
STICK_PROFILE = (
    (-770., -93.), (-690., -171.), (-375., -215.), (650., -234.),
    (1630., -210.), (2660., -115.), (2910., -120.), (3060., -61.),
    (3060., 82.), (2910., 180.), (2610., 202.), (1570., 268.),
    (575., 476.), (355., 458.), (135., 338.), (-310., 244.), (-720., 127.),
)
# Outer floor and cutting tips used to bound clearance. Arc extrema are also
# sampled by the journal profile; the conservative hull encloses those arcs.
BUCKET_HULL = ((-1400., -830.), (-1400., -690.), (-850., -1015.),
               (-250., -1080.), (300., -850.), (510., -535.),
               (560., -290.), (370., 140.), (90., 260.), (-120., 230.))
BUCKET_ARC = ((-1180., -755.), (-320., -990.), (473., -445.))
BUCKET_ARC_INNER = ((480., -333.), (-315., -913.), (-1170., -685.))


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def delta(a, b):
    return a[0] - b[0], a[1] - b[1]


def scale(a, k):
    return a[0] * k, a[1] * k


def length(p):
    return math.hypot(*p)


def rotate(p, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return c*p[0]-s*p[1], s*p[0]+c*p[1]


def direction(a, b):
    dx, dz = delta(b, a)
    return math.degrees(math.atan2(dz, dx))


def circle_joint(side, boss):
    line = delta(boss, side)
    d = length(line)
    if not abs(LINK_SIDE-LINK_H) < d < LINK_SIDE+LINK_H:
        raise ValueError("Bucket linkage has no two-circle intersection")
    u = scale(line, 1.0 / d)
    x = (LINK_SIDE**2-LINK_H**2+d*d) / (2*d)
    height = math.sqrt(LINK_SIDE**2-x*x)
    # Positive perpendicular here equals the previous V6 branch after Z reflection.
    return add(add(side, scale(u, x)), scale((-u[1], u[0]), height))


def evaluate(angles):
    boom, arm_rel, bucket_rel = angles
    arm = boom - arm_rel
    bucket = arm - bucket_rel + 90.
    b = rotate((BOOM_LENGTH, 0.), boom)
    c = add(b, rotate((STICK_LENGTH, 0.), arm))

    def anchor(name, origin, angle):
        return add(origin, rotate(JOINTS[name][2], angle))

    foot = (0., 0.)
    side = anchor("bucket_side", b, arm)
    boss = anchor("bucket_boss", c, bucket)
    j = circle_joint(side, boss)
    points = {
        "boom_base": foot, "boom_tip": b, "stick_tip": c, "bucket_side": side,
        "bucket_boss": boss, "bucket_cyl_B": j, "boom_cyl_A": JOINTS["boom_cyl_A"][2],
        "boom_cyl_B": anchor("boom_cyl_B", foot, boom),
        "arm_cyl_A": anchor("arm_cyl_A", foot, boom),
        "arm_cyl_B": anchor("arm_cyl_B", b, arm),
        "bucket_cyl_A": anchor("bucket_cyl_A", b, arm),
    }
    housings = {"boom": ("boom_cyl_A", "boom_cyl_B"),
                "arm": ("arm_cyl_A", "arm_cyl_B"), "bucket": ("bucket_cyl_A", "bucket_cyl_B")}
    rams = {}
    for key, (a, b) in housings.items():
        start, end = points[a], points[b]
        spec = ACTUATORS[key]
        pin_dist = length(delta(end, start))
        gland = spec["closed"] - 120.
        rod_span = spec["closed"] - 200.
        travel = pin_dist-spec["closed"]
        overlap = gland+rod_span-pin_dist
        if not 0 <= travel <= spec["stroke"] or overlap <= 0:
            raise ValueError("{} cylinder violates stroke or rod overlap at {}".format(key, angles))
        rams[key] = (start, end, pin_dist, gland, rod_span, travel, overlap)
    error = max(abs(length(delta(j,side))-LINK_SIDE), abs(length(delta(j,boss))-LINK_H))
    gap = min(add(c,rotate(point,bucket))[1] for point in BUCKET_HULL)-GROUND_Z
    if error > 0.001 or gap < 0:
        raise ValueError("Infeasible pose: closure {:.6g} mm, clearance {:.6g} mm".format(error,gap))
    return points, (boom,arm,bucket), rams, error, gap


def write_csv(path, header, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def write_tables(out):
    out.mkdir(parents=True, exist_ok=True)
    parameters = [
        ("boom_config", 5700, "mm", PUBLIC, SOURCE, "Published option; not a confirmed pin spacing"),
        ("stick_config", 2925, "mm", PUBLIC, SOURCE, "Published option"),
        ("boom_axis_spacing", BOOM_LENGTH, "mm", ASSUMED, CONCEPT, "Pilot pivot distance"),
        ("stick_axis_spacing", STICK_LENGTH, "mm", ASSUMED, CONCEPT, "Pilot pivot distance"),
        ("side_link_axis_spacing", LINK_SIDE, "mm", ASSUMED, CONCEPT, "Pilot closure"),
        ("h_link_axis_spacing", LINK_H, "mm", ASSUMED, CONCEPT, "Pilot closure"),
        ("boom_ram_lateral_offset", BOOM_HALF_Y, "mm", ASSUMED, CONCEPT, "Symmetric +/-"),
        ("ground_z", GROUND_Z, "mm", ASSUMED, CONCEPT, "Clearance reference only"),
    ]
    for name, spec in ACTUATORS.items():
        for key, value in sorted(spec.items()):
            assumed = key in ("closed", "eye")
            parameters.append((name+"_"+key, value, "count" if key=="qty" else "mm",
                               ASSUMED if assumed else PUBLIC, CONCEPT if assumed else SOURCE,
                               "Mounted pin distance at zero stroke" if key=="closed" else
                               "Pilot clevis hole radius" if key=="eye" else "Configuration-specific"))
    write_csv(out/"assembly_params.csv", ("parameter","value","unit","confidence","source","note"), parameters)
    pin_rows, state_rows = [], []
    for pose, angles in POSES.items():
        points, _, rams, error, gap = evaluate(angles)
        for name, (x,z) in points.items():
            part, parent = JOINTS[name][:2] if name in JOINTS else ("bucket_rod","four_bar")
            for y in (-BOOM_HALF_Y,BOOM_HALF_Y) if name.startswith("boom_cyl") else (0.,):
                pin_rows.append((pose,part,parent,name,round(x,6),y,round(z,6),ASSUMED,CONCEPT))
        for name, (_,_,dist,gland,span,ext,overlap) in rams.items():
            state_rows.append((pose,name,*angles,ACTUATORS[name]["qty"],
                               *(round(v,6) for v in (dist,gland,span,ext,ACTUATORS[name]["stroke"],
                                                     overlap,error,gap)), "ANALYTIC-PASS"))
    write_csv(out/"joint_map.csv", ("pose","part","parent","joint_id","x_mm","y_mm","z_mm",
                                    "confidence","source_id"), pin_rows)
    write_csv(out/"pose_check.csv", ("pose","actuator","boom_deg","arm_rel_deg","bucket_rel_deg","count",
        "pin_distance_mm","base_to_gland_mm","eye_to_rod_inner_mm","extension_mm","limit_mm",
        "overlap_mm","four_bar_closure_mm","bucket_ground_clearance_mm","check"), state_rows)


if __name__ == "__main__":
    import sys
    write_tables(Path(sys.argv[1]))
