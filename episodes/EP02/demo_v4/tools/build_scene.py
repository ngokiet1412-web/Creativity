"""Write godot/main.tscn: node tree + one AnimationPlayer clip ("sequence").

The scoop is planned as a bucket-tip path (task space) and baked to joint
keyframes with inverse kinematics (tools/kinematics.py), 15 keys per second.
Every other track is authored here as (time, value, transition) keys and can be
edited afterwards in the Godot AnimationPlayer.

Godot transition values: 1 linear, -2 ease in-out, 0 = hold (used for cuts).
"""
import json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from kinematics import RIG, ik, fk

ROOT = os.path.join(os.path.dirname(__file__), "..")
G = RIG["ground_y"]
LENGTH = 42.0
CUT = 0.001

# --------------------------------------------------------------- scoop path
WAYPOINTS = [  # time, bucket tooth tip (machine px), tooth direction (deg, screen)
    (4.0, (668, G - 38), 110), (5.6, (602, G - 44), 128),
    (7.0, (532, G - 42), 150), (8.1, (482, G - 98), 195), (9.1, (468, G - 140), 200)]
RAISE = (22.6, 30.5, 40.0)    # start, stop, final boom elevation (deg)

def catmull(p0, p1, p2, p3, u):
    return 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)

def tip_path(t):
    ts = [w[0] for w in WAYPOINTS]
    P = [np.array([*w[1], w[2]], float) for w in WAYPOINTS]
    for i in range(len(ts) - 1):
        if ts[i] <= t <= ts[i + 1]:
            u = (t - ts[i]) / (ts[i + 1] - ts[i])
            if i in (0, len(ts) - 2):
                u = u * u * (3 - 2 * u)
            return catmull(P[max(i - 1, 0)], P[i], P[i + 1], P[min(i + 2, len(P) - 1)], u)
    return P[-1] if t > ts[-1] else P[0]


# ================================================================ V4 PROOF
LENGTH = 16.0
x, y, phi = tip_path(WAYPOINTS[-1][0])
B0, QA, _ = ik((x, y), phi)                # loaded pose at the end of the V3 scoop
QK0, QK1 = 38.0, 64.0                       # bucket curls at the end of the proof
B1 = 40.0
joint = {"boom_deg": [], "arm_rel": [], "bucket_rel": []}

def smooth(u):
    u = min(max(u, 0.0), 1.0); return u * u * u * (u * (6 * u - 15) + 10)   # min-jerk

def boom_profile(t):
    """Loaded boom raise: valve opens, load transfers (tiny sag), min-jerk
    acceleration, steady stroke, deceleration, then a damped settle from oil
    compliance under load. Degrees of boom elevation."""
    dip = 0.12
    t_sag0, t_go, t_acc, t_dec, t_stop = 4.05, 4.35, 5.35, 11.65, 12.55
    if t <= t_sag0:
        return B0
    if t <= t_go:
        return B0 - dip * smooth((t - t_sag0) / (t_go - t_sag0))
    start = B0 - dip
    span = B1 - start
    # trapezoid-like speed with smooth ramps: integrate numerically
    def speed(s):
        if s < t_go or s > t_stop: return 0.0
        if s < t_acc: return smooth((s - t_go) / (t_acc - t_go))
        if s > t_dec: return 1.0 - smooth((s - t_dec) / (t_stop - t_dec))
        return 1.0
    import numpy as _np
    grid = _np.linspace(t_go, t_stop, 2001)
    sp = _np.array([speed(g) for g in grid])
    cum = _np.concatenate([[0], _np.cumsum((sp[1:] + sp[:-1]) * 0.5 * _np.diff(grid))])
    if t <= t_stop:
        # flow-controlled: the ROD moves with the min-jerk speed profile
        # (constant pump flow -> constant rod speed), the boom angle follows
        # from the pin geometry.
        L0 = fk(start, QA, QK0)["Lb"]; L1 = fk(B1, QA, QK0)["Lb"]
        target = L0 + (L1 - L0) * _np.interp(t, grid, cum) / cum[-1]
        lo, hi = start - 1.0, B1 + 1.0
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if fk(mid, QA, QK0)["Lb"] < target: lo = mid
            else: hi = mid
        return 0.5 * (lo + hi)
    tau = t - t_stop
    return B1 - 0.28 * (1 - math.cos(2 * math.pi * min(tau, 1.4) / 0.7)) * 0.5 * math.exp(-tau / 0.55)

def bucket_profile(t):
    if t <= 12.9: return QK0
    if t <= 14.3: return QK0 + (QK1 + 0.8 - QK0) * smooth((t - 12.9) / 1.4)
    return QK1 + 0.8 * (1 - smooth((t - 14.3) / 0.45))

t = 0.0
while t <= LENGTH + 1e-6:
    dense = 3.9 <= t <= 14.9
    if dense or abs(t - round(t)) < 1e-6:
        for name, v in (("boom_deg", boom_profile(t)), ("arm_rel", QA), ("bucket_rel", bucket_profile(t))):
            joint[name].append((round(t, 4), round(v, 4), 1.0))
    t = round(t + 1.0 / 15.0, 6)

S1, S2, XR, CYL, OUT, END = 3.0, 6.4, 7.7, 9.6, 12.8, LENGTH
tracks = {
    "joystick": [(0, 0, 1), (3.6, 0, -2), (4.05, 1, 1), (11.45, 1, -2), (12.35, 0, 1)],
    "spool": [(0, 0, 1), (3.75, 0, -2), (4.2, 1, 1), (11.6, 1, -2), (12.5, 0, 1)],
    "intro": [(0, 1, 0), (S1, 0, 1)],
    "xray": [(0, 0, 1), (6.7, 0, -2), (XR, 1, 1), (11.9, 1, -2), (12.7, 0, 1)],
    "cutaway": [(0, 0, 1), (8.6, 0, -2), (9.2, 1, 1), (12.2, 1, -2), (12.8, 0, 1)],
    "flow_overlay": [(0, 0, 1), (4.0, 0, -2), (4.3, 1, 1), (12.9, 1, -2), (13.4, 0, 1)],
    "legend": [(0, 0, 1), (4.2, 0, -2), (4.6, 1, 1), (15.6, 1, 1)],
    "chain": [(0, 0, 1)],
    "cam_x": [(0, 150, 1), (S1, 150, -2), (S2, 165, -2.2), (XR, -215, -2), (8.7, -70, -2), (CYL, 60, 1), (11.9, 60, -2.2), (OUT, 165, -2), (END, 150, 1)],
    "cam_y": [(0, -165, 1), (S1, -165, -2), (S2, -172, -2.2), (XR, -12, -2), (8.7, 4, -2), (CYL, 0, 1), (11.9, 0, -2.2), (OUT, -178, -2), (END, -165, 1)],
    "cam_zoom": [(0, 1.0, 1), (S1, 1.0, -2), (S2, 1.04, -2.2), (XR, 3.3, -2), (8.7, 3.2, -2), (CYL, 2.75, 1), (11.9, 2.95, -2.2), (OUT, 1.06, -2), (END, 1.12, 1)],
    "cam_follow": [(0, 0, 1), (8.7, 0, -2), (CYL, 1, 1), (11.9, 1, -2.2), (OUT, 0, 1)],
    "capy_tilt": [(0, 0, 1), (S1, 0, -2), (3.4, 3, -2), (4.6, -1.5, -2), (6.5, -3.2, -2), (OUT, -3.2, -2), (13.4, 2, -2),
                  (14.55, 6, -2), (14.85, 1, -2), (END, 2.5, 1)],
}
label_set = [(0, 0), (4.2, 10), (7.2, 11), (9.3, 12), (12.1, 0), (12.9, 13)]
# --------------------------------------------------------------- tscn writer
def fmt(v):
    # always write a float literal: Godot parses "1" as int and int tracks
    # interpolate in whole steps (this made V3 fades/joystick/head tilts step)
    s = "%.6g" % v
    return s if any(ch in s for ch in ".e") else s + ".0"

def value_track(i, prop, keys):
    # resolve None (= previous value) for hold keys
    out, last = [], None
    for t, v, tr in sorted(keys, key=lambda k: k[0]):
        v = last if v is None else v
        out.append((max(t, 0.0), v, tr)); last = v
    times = ", ".join(fmt(k[0]) for k in out)
    trans = ", ".join(fmt(k[2]) for k in out)
    vals = ", ".join(fmt(k[1]) for k in out)
    return (f'tracks/{i}/type = "value"\ntracks/{i}/imported = false\ntracks/{i}/enabled = true\n'
            f'tracks/{i}/path = NodePath(".:{prop}")\ntracks/{i}/interp = 1\ntracks/{i}/loop_wrap = false\n'
            f'tracks/{i}/keys = {{\n"times": PackedFloat32Array({times}),\n"transitions": PackedFloat32Array({trans}),\n'
            f'"update": 0,\n"values": [{vals}]\n}}\n')

def discrete_track(i, prop, keys):
    times = ", ".join(fmt(k[0]) for k in keys)
    vals = ", ".join(str(int(k[1])) for k in keys)
    trans = ", ".join("1" for _ in keys)
    return (f'tracks/{i}/type = "value"\ntracks/{i}/imported = false\ntracks/{i}/enabled = true\n'
            f'tracks/{i}/path = NodePath(".:{prop}")\ntracks/{i}/interp = 0\ntracks/{i}/loop_wrap = false\n'
            f'tracks/{i}/keys = {{\n"times": PackedFloat32Array({times}),\n"transitions": PackedFloat32Array({trans}),\n'
            f'"update": 1,\n"values": [{vals}]\n}}\n')

body = []
i = 0
for prop, keys in list(joint.items()) + list(tracks.items()):
    body.append(value_track(i, prop, keys)); i += 1
body.append(discrete_track(i, "label_set", label_set))

scene = f'''[gd_scene load_steps=12 format=3]

[ext_resource type="Script" path="res://director.gd" id="1"]
[ext_resource type="Script" path="res://env.gd" id="2"]
[ext_resource type="Script" path="res://rig.gd" id="3"]
[ext_resource type="Script" path="res://hydraulics.gd" id="4"]
[ext_resource type="Script" path="res://crew.gd" id="5"]
[ext_resource type="Script" path="res://hud.gd" id="6"]
[ext_resource type="Script" path="res://intro.gd" id="7"]

[sub_resource type="Animation" id="Animation_reset"]
resource_name = "RESET"
length = 0.001

[sub_resource type="Animation" id="Animation_sequence"]
resource_name = "sequence"
length = {LENGTH}
{"".join(body)}
[sub_resource type="AnimationLibrary" id="AnimationLibrary_main"]
_data = {{
&"RESET": SubResource("Animation_reset"),
&"sequence": SubResource("Animation_sequence")
}}

[node name="Main" type="Node2D"]
script = ExtResource("1")
tremor_px = 0.45
pitch_gain = 0.025
bake_mound = true
cel_offset = 0.36
capy_blinks = [3.9, 6.2, 9.0, 13.1, 15.3]
eng_blinks = [4.6, 10.5, 14.1]
crumb_bursts = [[4.5, 6.2, 6], [5.0, 9.0, 3], [12.9, 14.5, 10]]
moving_threshold = 2.0

[node name="World" type="Node2D" parent="."]

[node name="Env" type="Node2D" parent="World"]
script = ExtResource("2")

[node name="Front" type="Node2D" parent="World/Env"]

[node name="Machine" type="Node2D" parent="World"]
script = ExtResource("3")

[node name="Hydraulics" type="Node2D" parent="World/Machine"]
script = ExtResource("4")

[node name="Crew" type="Node2D" parent="World"]
script = ExtResource("5")

[node name="Camera" type="Camera2D" parent="."]
position = Vector2(110, -131)

[node name="HUD" type="CanvasLayer" parent="."]

[node name="Overlay" type="Node2D" parent="HUD"]
script = ExtResource("6")

[node name="Intro" type="CanvasLayer" parent="."]
layer = 5

[node name="Card" type="Node2D" parent="Intro"]
script = ExtResource("7")

[node name="AnimationPlayer" type="AnimationPlayer" parent="."]
libraries = {{
&"": SubResource("AnimationLibrary_main")
}}
'''
open(os.path.join(ROOT, "godot", "main.tscn"), "w").write(scene)
json.dump({"version": "V4 proof 16 s", "start_pose": [B0, QA, QK0], "boom_end": B1, "bucket_end": QK1, "joint_keys": {k: len(v) for k, v in joint.items()},
           "shots": {"studio": [0, S1], "wide_raise": [S1, S2], "dolly_xray": [S2, XR], "valve_to_cylinder": [XR, CYL], "cylinder_cutaway": [CYL, 11.9], "pull_out": [11.9, OUT], "bucket_curl": [OUT, END]}},
          open(os.path.join(ROOT, "godot", "art", "motion_plan.json"), "w"), indent=1)
print("tracks:", i + 1, "joint keys:", len(joint["boom_deg"]))
