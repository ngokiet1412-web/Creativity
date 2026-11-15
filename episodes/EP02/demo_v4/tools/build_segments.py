"""Write Godot scenes for EP02 script segments (godot/segments/scXX.tscn).
Each segment = one root director script + cutaway components + Camera2D +
AnimationPlayer "sequence". Keys are (time, value, transition); transition
-2 = ease in-out, 1 = linear, 0 = hold. Values are always written as floats.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from segment_timing import INSERTS, warp
from segment_timing import extra as extra_time
ROOT = os.path.join(os.path.dirname(__file__), "..", "godot")

def fmt(v):
    s = "%.6g" % v
    return s if any(ch in s for ch in ".e") else s + ".0"

def track(i, path, keys):
    keys = sorted(keys, key=lambda k: k[0])
    out, last = [], None
    for k in keys:
        t, v = k[0], k[1]
        tr = k[2] if len(k) > 2 else -2.0
        v = last if v is None else v
        out.append((t, v, tr)); last = v
    return (f'tracks/{i}/type = "value"\ntracks/{i}/imported = false\ntracks/{i}/enabled = true\n'
            f'tracks/{i}/path = NodePath("{path}")\ntracks/{i}/interp = 1\ntracks/{i}/loop_wrap = false\n'
            f'tracks/{i}/keys = {{\n"times": PackedFloat32Array({", ".join(fmt(k[0]) for k in out)}),\n'
            f'"transitions": PackedFloat32Array({", ".join(fmt(k[2]) for k in out)}),\n"update": 0,\n'
            f'"values": [{", ".join(fmt(k[1]) for k in out)}]\n}}\n')

def write(name, script, length, nodes, keys, props):
    keys = {p: [(warp(name, k[0]),) + tuple(k[1:]) for k in ks] for p, ks in keys.items()}
    length = length + extra_time(name)
    props = dict(props)
    ins = INSERTS.get(name, [])
    if ins:
        props["inserts"] = "PackedVector2Array(%s)" % ", ".join("%s, %s" % (fmt(a), fmt(d)) for a, d in ins)
    body = "".join(track(i, p, k) for i, (p, k) in enumerate(keys.items()))
    ext = [f'[ext_resource type="Script" path="res://segments/{script}" id="root"]']
    node_txt = []
    for j, (nname, nscript, extra) in enumerate(nodes):
        ext.append(f'[ext_resource type="Script" path="res://cutaway/{nscript}" id="c{j}"]')
        node_txt.append(f'[node name="{nname}" type="Node2D" parent="."]\nscript = ExtResource("c{j}")\n{extra}\n')
    prop_txt = "".join(f"{k} = {v}\n" for k, v in props.items())
    scene = (f'[gd_scene format=3]\n\n' + "\n".join(ext) + '\n\n'
             f'[sub_resource type="Animation" id="seq"]\nresource_name = "sequence"\nlength = {fmt(length)}\n{body}\n'
             f'[sub_resource type="AnimationLibrary" id="lib"]\n_data = {{\n&"sequence": SubResource("seq")\n}}\n\n'
             f'[node name="{name.upper()}" type="Node2D"]\nscript = ExtResource("root")\n{prop_txt}\n'
             + "\n".join(node_txt) +
             f'\n[node name="Camera" type="Camera2D" parent="."]\n\n'
             f'[node name="AnimationPlayer" type="AnimationPlayer" parent="."]\nlibraries = {{\n&"": SubResource("lib")\n}}\n')
    open(os.path.join(ROOT, "segments", f"{name}.tscn"), "w").write(scene)
    print("wrote", name, len(keys), "tracks")

# ===================================================================== SC03
L3 = 41.0
write("sc03", "sc03.gd", L3,
      [("Engine", "engine_cut.gd", "inset_pos = Vector2(1080, -290)\nz_index = 1"),
       ("Pump", "pump_cut.gd", "position = Vector2(1020, 0)")],
      {
        ".:rpm": [(0, 1.2), (24.6, 1.2), (26.0, 1.9), (31.5, 1.9), (33.0, 1.2), (L3, 1.2)],
        ".:swash_f": [(0, 0.35), (16.8, 0.35), (18.0, 0.06), (20.5, 0.06), (21.7, 1.0), (24.6, 1.0), (27.0, 0.56), (32.5, 0.56), (33.5, 0.35), (L3, 0.35)],
        ".:swash_r": [(0, 0.3), (24.6, 0.3), (27.0, 0.45), (32.5, 0.45), (33.5, 0.3), (L3, 0.3)],
        ".:meters": [(0, 0), (13.6, 0), (14.1, 1), (29.8, 1), (30.4, 0), (L3, 0)],
        ".:stroke_dim": [(0, 0, 0), (16.8, 1, 0), (24.6, 0, 0), (L3, 0)],
        ".:chips": [(0, 0), (31.4, 0, 1), (37.0, 1), (L3, 1)],
        ".:capy_in": [(0, 0), (24.8, 0), (25.4, 1), (29.8, 1), (30.4, 0), (L3, 0)],
        ".:capy_tilt": [(0, 0), (25.4, 0), (26.2, 4), (27.6, -2), (29.0, 3), (30.4, 0), (L3, 0)],
        ".:eng_in": [(0, 0), (29.8, 0), (30.4, 1), (L3, 1)],
        ".:legend": [(0, 1), (L3, 1)],
        "Engine:inset_alpha": [(0, 0), (1.5, 0), (2.3, 1), (5.6, 1), (6.4, 0), (L3, 0)],
        ".:cam_x": [(0, 450), (6.2, 470), (9.4, 900), (13.8, 1420), (24.6, 1270), (30.0, 1290), (32.0, 930), (L3, 950)],
        ".:cam_y": [(0, -120), (6.2, -125), (9.4, -60), (13.8, -40), (24.6, -60), (30.0, -55), (32.0, -40), (L3, -45)],
        ".:cam_zoom": [(0, 1.22), (6.2, 1.25), (9.4, 1.25), (13.8, 0.95), (15.2, 1.6), (24.6, 1.6), (30.0, 1.55), (32.0, 0.82), (L3, 0.85)],
      },
      {"scene_tag": '"SC03"', "scene_title": '"Động cơ và cụm bơm kép"'})

# ===================================================================== SC05
L5 = 29.0
write("sc05", "sc05.gd", L5,
      [("PPC", "ppc_cut.gd", "position = Vector2(300, 380)"),
       ("Spool", "spool_cut.gd", "position = Vector2(760, 300)"),
       ("Pump", "pump_cut.gd", "position = Vector2(420, 900)\nscale = Vector2(0.5, 0.5)\nshow_rear = false\nshow_valve_plate_inset = false")],
      {
        ".:lever": [(0, 0), (1.2, 0), (1.8, 0.12), (2.6, 0.0), (9.0, 0), (12.0, 0.5), (13.0, 0.5), (14.5, 1.0), (18.6, 1.0), (19.6, 0.0), (24.2, 0.0), (25.4, 0.7), (27.4, 0.7), (28.4, 0), (L5, 0)],
        ".:compare": [(0, 0), (19.8, 0), (20.4, 1), (23.2, 1), (23.8, 0), (L5, 0)],
        ".:capy_in": [(0, 0), (0.3, 0), (0.8, 1), (4.4, 1), (5.0, 0), (19.4, 0), (19.9, 1), (23.0, 1), (23.5, 0), (L5, 0)],
        ".:capy_tilt": [(0, 0), (1.0, 3), (2.6, -2), (4.0, 2), (19.9, 0), (21.0, 4), (22.6, 1), (L5, 0)],
        ".:eng_in": [(0, 0), (4.8, 0), (5.4, 1), (8.4, 1), (9.0, 0), (23.4, 0), (24.0, 1), (L5, 1)],
        ".:legend": [(0, 1), (L5, 1)],
        ".:cam_x": [(0, 330), (4.4, 340), (6.4, 910), (9.6, 760), (12.0, 880), (19.4, 930), (20.4, 930), (23.4, 1000), (25.0, 900), (L5, 905)],
        ".:cam_y": [(0, 230), (4.4, 235), (6.4, 250), (9.6, 300), (12.0, 260), (19.4, 245), (20.4, 245), (23.4, 180), (25.0, 330), (L5, 335)],
        ".:cam_zoom": [(0, 1.1), (4.4, 1.12), (6.4, 0.84), (9.6, 0.98), (12.0, 0.88), (19.4, 0.86), (20.4, 0.86), (23.4, 0.98), (25.0, 0.72), (L5, 0.73)],
      },
      {"scene_tag": '"SC05"', "scene_title": '"Từ tay điều khiển đến van chính"'})

# ===================================================================== SC04
L4 = 39.0
write("sc04", "sc04.gd", L4,
      [("Pump", "pump_cut.gd", "position = Vector2(60, 560)\nscale = Vector2(0.8, 0.8)\nshow_rear = false\nshow_valve_plate_inset = false"),
       ("ValveBoom", "spool_cut.gd", "position = Vector2(900, 150)\nscale = Vector2(0.55, 0.55)\ntag_text = \"Nhánh cần\""),
       ("ValveArm", "spool_cut.gd", "position = Vector2(900, 520)\nscale = Vector2(0.55, 0.55)\ntag_text = \"Nhánh tay gầu\"")],
      {
        ".:boom": [(0, 0), (10.0, 0), (11.2, 0.8), (31.0, 0.8), (36.0, 0.8), (37.2, 0), (L4, 0)],
        ".:arm": [(0, 0), (16.4, 0), (17.6, 0.7), (36.0, 0.7), (37.2, 0), (L4, 0)],
        ".:load_boom": [(0, 0.55), (31.0, 0.55), (32.4, 0.95), (36.0, 0.95), (37.0, 0.55), (L4, 0.55)],
        ".:load_arm": [(0, 0.3), (L4, 0.3)],
        ".:capy_in": [(0, 0), (0.3, 0), (0.8, 1), (3.6, 1), (4.1, 0), (24.2, 0), (24.7, 1), (30.0, 1), (30.5, 0), (L4, 0)],
        ".:capy_tilt": [(0, 0), (1.0, 4), (2.6, -1), (24.7, 0), (26.0, 5), (28.0, 1), (30.0, 3), (L4, 0)],
        ".:eng_in": [(0, 0), (3.8, 0), (4.4, 1), (7.0, 1), (7.5, 0), (30.4, 0), (31.0, 1), (L4, 1)],
        ".:legend": [(0, 1), (L4, 1)],
        ".:cam_x": [(0, 860), (3.8, 870), (6.4, 380), (9.6, 400), (12.0, 860), (16.2, 860), (17.8, 1150), (23.8, 1150), (25.0, 860), (30.6, 860), (31.6, 420), (36.8, 430), (38.0, 860), (L4, 860)],
        ".:cam_y": [(0, 320), (3.8, 320), (6.4, 200), (9.6, 200), (12.0, 320), (16.2, 320), (17.8, 300), (23.8, 300), (25.0, 320), (30.6, 320), (31.6, 180), (36.8, 180), (38.0, 320), (L4, 320)],
        ".:cam_zoom": [(0, 0.86), (3.8, 0.86), (6.4, 1.35), (9.6, 1.35), (12.0, 0.86), (16.2, 0.86), (17.8, 1.05), (23.8, 1.05), (25.0, 0.86), (30.6, 0.86), (31.6, 1.3), (36.8, 1.3), (38.0, 0.86), (L4, 0.86)],
      },
      {"scene_tag": '"SC04"', "scene_title": '"Điểm khó: cảm nhận tải CLSS"'})
