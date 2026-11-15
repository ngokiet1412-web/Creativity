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

joint = {"boom_deg": [], "arm_rel": [], "bucket_rel": []}
def add_joint(t, b, a, k, tr=1.0):
    for name, v in zip(joint, (b, a, k)):
        joint[name].append((round(t, 4), round(v, 3), tr))

b0, a0, k0 = ik(tuple(tip_path(4.0)[:2]), tip_path(4.0)[2])
add_joint(0.0, b0, a0, k0, 1.0)
t = 4.0
while t <= WAYPOINTS[-1][0] + 1e-6:
    x, y, phi = tip_path(t)
    add_joint(t, *ik((x, y), phi))
    t += 1.0 / 15.0
bh, ah, kh = joint["boom_deg"][-1][1], joint["arm_rel"][-1][1], joint["bucket_rel"][-1][1]
add_joint(RAISE[0], bh, ah, kh, -1.8)
add_joint(RAISE[1], RAISE[2], ah, kh, 1.0)
# S6b: operator starts the next cycle (boom lowers; circuit not overlaid)
add_joint(37.4, RAISE[2], ah, kh, -1.8)
add_joint(41.9, 31.0, ah, kh, 1.0)
add_joint(LENGTH, 31.0, ah, kh, 1.0)

# ------------------------------------------------------------ authored keys
def hold(t, v):            # instant change (camera cut)
    return [(t - CUT, None, 0), (t, v, 1.0)]

def cuts(*shots):
    """shots: (t_start, value_start, t_end, value_end, transition)"""
    keys = []
    for i, (ts, vs, te, ve, tr) in enumerate(shots):
        keys.append((ts, vs, tr))
        last = i == len(shots) - 1
        keys.append((te if last else te - CUT, ve, 1.0 if last else 0.0))
    return keys

S2, S3, S4, S5A, S5B, S6A, S6B = 4.0, 9.6, 16.6, 23.4, 27.4, 30.8, 34.2
tracks = {
    "joystick": [(0, 0, 1), (20.2, 0, -2), (21.0, 1, 1), (30.1, 1, -2), (30.6, 0, 1)],
    "spool": [(0, 0, 1), (20.35, 0, -2), (21.15, 1, 1), (30.2, 1, -2), (30.75, 0, 1)],
    "intro": [(0, 1, 0), (S2, 0, 1)],
    "xray": [(0, 0, 1), (S3, 0, -2), (S3 + 0.9, 1, 1), (S5A - CUT, 1, 0), (S5A, 0.3, 1), (S5B - CUT, 0.3, 0),
             (S5B, 0, 1), (S6A - CUT, 0, 0), (S6A, 0.62, 1), (S6B - CUT, 0.62, 0), (S6B, 0, 1)],
    "cutaway": [(0, 0, 1), (S5A - CUT, 0, 0), (S5A, 1, 1), (S6B - CUT, 1, 0), (S6B, 0, 1)],
    "flow_overlay": [(0, 0, 1), (S5A - CUT, 0, 0), (S5A, 1, 1), (S6B - CUT, 1, 0), (S6B, 0, 1)],
    "legend": [(0, 0, 1), (S3 + 0.3, 0, -2), (S3 + 0.8, 1, 1), (S5B - CUT, 1, 0), (S5B, 0, 1), (S6A - CUT, 0, 0), (S6A, 1, 1), (S6B - CUT, 1, 0), (S6B, 0, 1)],
    "chain": [(0, 0, 1), (35.5, 0, -2), (35.8, 1, 1), (36.5, 1, -2), (36.8, 2, 1), (37.5, 2, -2), (37.8, 3, 1),
              (38.4, 3, -2), (38.7, 4, 1), (39.3, 4, -2), (39.6, 5, 1)],
    "cam_x": cuts((0, 110, S2, 110, 1), (S2, 110, S3, 150, -2), (S3, -282, S4, -238, -1.6), (S4, -238, 21.6, -118, -2), (21.6, -118, S5A, -10, -2),
                  (S5A, 0, S5B, 0, 1), (S5B, 150, S6A, 135, -2), (S6A, -40, S6B, -25, -2), (S6B, -235, LENGTH, -215, -2)),
    "cam_y": cuts((0, -131, S2, -131, 1), (S2, -131, S3, -122, -2), (S3, -14, S4, -10, -1.6), (S4, -10, 21.6, -6, -2), (21.6, -6, S5A, 30, -2),
                  (S5A, 0, S5B, 0, 1), (S5B, -175, S6A, -182, -2), (S6A, 12, S6B, 18, -2), (S6B, -40, LENGTH, -52, -2)),
    "cam_zoom": cuts((0, 1.0, S2, 1.0, 1), (S2, 1.0, S3, 1.05, -2), (S3, 3.7, S4, 3.55, -1.6), (S4, 3.55, 21.6, 3.3, -2), (21.6, 3.3, S5A, 1.75, -2),
                     (S5A, 2.7, S5B, 2.85, -2), (S5B, 0.98, S6A, 1.0, -2), (S6A, 1.9, S6B, 1.97, -2), (S6B, 1.2, LENGTH, 1.27, -2)),
    "cam_follow": [(0, 0, 1), (S5A - CUT, 0, 0), (S5A, 1, 1), (S5B - CUT, 1, 0), (S5B, 0, 1)],
    "capy_tilt": [(0, 0, 1), (S2, -1, -2), (4.7, 3.5, -2), (6.2, 4.5, -2), (8.4, 1.5, -2), (9.4, 0, 1),
                  (S5B, 0, -2), (30.4, -4.5, -2), (S6A, -4.5, 1), (S6B, -1, -2), (34.6, 2.5, -2), (34.85, 6, -2),
                  (35.25, 1.5, -2), (37.0, 3, -2), (39.0, -0.5, -2), (LENGTH, 1.5, 1)],
}
label_set = [(0, 0), (S3, 1), (S4, 2), (S5A, 3), (S5B, 4), (S6A, 5), (S6B, 6)]

# --------------------------------------------------------------- tscn writer
def fmt(v):
    return "%.6g" % v

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
json.dump({"waypoints": WAYPOINTS, "raise": RAISE, "joint_keys": {k: len(v) for k, v in joint.items()},
           "shots": {"S1": [0, S2], "S2": [S2, S3], "S3": [S3, S4], "S4": [S4, S5A], "S5A": [S5A, S5B],
                     "S5B": [S5B, S6A], "S6A": [S6A, S6B], "S6B": [S6B, LENGTH]}},
          open(os.path.join(ROOT, "godot", "art", "motion_plan.json"), "w"), indent=1)
print("tracks:", i + 1, "joint keys:", len(joint["boom_deg"]))
