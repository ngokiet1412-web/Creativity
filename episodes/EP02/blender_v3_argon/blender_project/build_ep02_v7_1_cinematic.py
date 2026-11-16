"""Blender 5.3 V7.1 Cinematic Quality Upgrade: Micro-details, EEVEE/Cycles AO PBR, Secondary Motion,
Cutaway Flow Pulses & Dynamic Telemetry, Depth of Field, Compositor, and Strict 1079-State QA.

Preserves all NX V2 STL meshes and MATLAB motion_trace_v3.csv trajectory untouched.
"""

import argparse
import csv
import json
import math
import sys
import time
from pathlib import Path

import bmesh
import bpy
from bpy.app.handlers import persistent
from mathutils import Euler, Matrix, Vector

WS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WS_ROOT / "textures_materials"))
from materials_v7_1 import build_v71_materials  # noqa: E402


FPS = 30
FRAMES = 540
UNIT = 0.001
GROUND_Z_M = -1.5849
GEOM_TOL_M = 0.00025

ACTUATOR_SPECS = {
    "boom": dict(closed=2.200, stroke=1.334, gland=2.080, rod_span=2.000, bore=0.120, rod=0.085),
    "arm": dict(closed=1.850, stroke=1.490, gland=1.730, rod_span=1.650, bore=0.135, rod=0.095),
    "bucket": dict(closed=1.700, stroke=1.120, gland=1.580, rod_span=1.500, bore=0.115, rod=0.080),
}
LINK_SIDE_M = 0.650
LINK_H_M = 0.750

# Module-level trace cache for @persistent live HUD readout during rendering
_TRACE_ROWS = []
_TELEMETRY_FONT = None


@persistent
def _update_telemetry_text(scene, depsgraph=None):
    global _TELEMETRY_FONT
    font_curve = bpy.data.curves.get("V71_Telemetry_Live_Font") or _TELEMETRY_FONT
    if font_curve is None or not _TRACE_ROWS:
        return
    idx = max(0, min(len(_TRACE_ROWS) - 1, scene.frame_current - 1))
    row = _TRACE_ROWS[idx]
    ab = int(round(row["boom_cyl_length_mm"]))
    ext = int(round(row["boom_stroke_mm"]))
    vel = row["boom_vel_mms"]
    p_bar = int(round(row["p_boom_illustrative_bar"]))
    font_curve.body = (
        f"A-B: {ab:,} mm  |  Ty đi ra: {ext:,} / 1,334 mm\n"
        f"Tốc độ đẩy ty: {vel:.1f} mm/s  |  Áp suất minh họa: ~{p_bar} bar"
    )
    font_curve.update_tag()
    txt_obj = bpy.data.objects.get("V71_Telemetry_Live_Text")
    if txt_obj is not None:
        txt_obj.update_tag()


def ensure_collection(parent_coll, name):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        parent_coll.children.link(coll)
    return coll


def link_obj(obj, coll, parent=None):
    if obj.name not in coll.objects:
        coll.objects.link(obj)
    if parent is not None:
        obj.parent = parent
    return obj


def make_empty(name, coll, parent=None, location=(0.0, 0.0, 0.0), size=0.015):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = size
    obj.location = location
    return link_obj(obj, coll, parent)


def polish_imported_mesh(obj, angle_deg=32.0, bevel_m=0.002):
    mesh = obj.data
    mesh.transform(Matrix.Scale(UNIT, 4))
    obj.scale = (1.0, 1.0, 1.0)

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    thresh = math.radians(angle_deg)
    for e in bm.edges:
        if len(e.link_faces) == 2:
            e.smooth = (e.link_faces[0].normal.angle(e.link_faces[1].normal, 0.0) <= thresh)
        else:
            e.smooth = False
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    if bevel_m > 0.0:
        bev = obj.modifiers.new("CAD_Chamfer", "BEVEL")
        bev.width = bevel_m
        bev.segments = 2
        bev.limit_method = "ANGLE"
        bev.angle_limit = math.radians(angle_deg + 2.0)
        bev.harden_normals = False

    es = obj.modifiers.new("CAD_SharpSplit", "EDGE_SPLIT")
    es.use_edge_angle = False
    es.use_edge_sharp = True


def import_stl_part(stl_dir: Path, filename: str, name: str, material, coll, parent=None,
                    angle_deg=32.0, bevel_m=0.002):
    path = stl_dir / filename
    if not path.is_file():
        raise FileNotFoundError(f"Missing STL file: {path}")
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.stl_import(filepath=str(path), global_scale=1.0, forward_axis="Y", up_axis="Z")
    obj = bpy.context.selected_objects[0]
    obj.name = name
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    polish_imported_mesh(obj, angle_deg=angle_deg, bevel_m=bevel_m)
    obj.data.materials.append(material)
    return link_obj(obj, coll, parent)


def instance_stl_mesh(template_obj, name: str, material, coll, parent=None):
    obj = bpy.data.objects.new(name, template_obj.data.copy())
    obj.data.materials.clear()
    obj.data.materials.append(material)
    for mod in template_obj.modifiers:
        m = obj.modifiers.new(mod.name, mod.type)
        if mod.type == "BEVEL":
            m.width = mod.width
            m.segments = mod.segments
            m.limit_method = mod.limit_method
            m.angle_limit = mod.angle_limit
            m.harden_normals = mod.harden_normals
        elif mod.type == "EDGE_SPLIT":
            m.use_edge_angle = mod.use_edge_angle
            m.use_edge_sharp = mod.use_edge_sharp
    return link_obj(obj, coll, parent)


def add_locked_track(obj, target, track="TRACK_X", lock="LOCK_Y"):
    c = obj.constraints.new("LOCKED_TRACK")
    c.target = target
    c.track_axis = track
    c.lock_axis = lock
    return c


def create_box_mesh(name, x0, x1, y0, y1, z0, z1, material, coll, parent=None, bevel_m=0.003):
    bm = bmesh.new()
    v = [
        bm.verts.new((x0, y0, z0)), bm.verts.new((x1, y0, z0)),
        bm.verts.new((x1, y1, z0)), bm.verts.new((x0, y1, z0)),
        bm.verts.new((x0, y0, z1)), bm.verts.new((x1, y0, z1)),
        bm.verts.new((x1, y1, z1)), bm.verts.new((x0, y1, z1)),
    ]
    for fi in ((3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([v[i] for i in fi])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = link_obj(bpy.data.objects.new(name, mesh), coll, parent)
    obj.data.materials.append(material)
    if bevel_m > 0.0:
        b = obj.modifiers.new("Chamfer", "BEVEL")
        b.width = bevel_m
        b.segments = 2
    return obj


def create_prism_xz(name, poly_xz, y0, y1, material, coll, parent=None, bevel_m=0.003):
    bm = bmesh.new()
    n = len(poly_xz)
    v0 = [bm.verts.new((x, y0, z)) for x, z in poly_xz]
    v1 = [bm.verts.new((x, y1, z)) for x, z in poly_xz]
    bm.faces.new(list(reversed(v0)))
    bm.faces.new(v1)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((v0[i], v0[j], v1[j], v1[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = link_obj(bpy.data.objects.new(name, mesh), coll, parent)
    obj.data.materials.append(material)
    if bevel_m > 0.0:
        b = obj.modifiers.new("Chamfer", "BEVEL")
        b.width = bevel_m
        b.segments = 2
    return obj


def create_cylinder_x(name, x0, x1, r_out, r_in, segments, material, coll, parent=None):
    bm = bmesh.new()
    v0o = [bm.verts.new((x0, r_out * math.cos(i * math.tau / segments), r_out * math.sin(i * math.tau / segments))) for i in range(segments)]
    v1o = [bm.verts.new((x1, r_out * math.cos(i * math.tau / segments), r_out * math.sin(i * math.tau / segments))) for i in range(segments)]
    if r_in > 0.0:
        v0i = [bm.verts.new((x0, r_in * math.cos(i * math.tau / segments), r_in * math.sin(i * math.tau / segments))) for i in range(segments)]
        v1i = [bm.verts.new((x1, r_in * math.cos(i * math.tau / segments), r_in * math.sin(i * math.tau / segments))) for i in range(segments)]
        for i in range(segments):
            j = (i + 1) % segments
            bm.faces.new((v0o[i], v0o[j], v1o[j], v1o[i]))
            bm.faces.new((v1i[i], v1i[j], v0i[j], v0i[i]))
            bm.faces.new((v0i[i], v0i[j], v0o[j], v0o[i]))
            bm.faces.new((v1o[i], v1o[j], v1i[j], v1i[i]))
    else:
        for i in range(segments):
            j = (i + 1) % segments
            bm.faces.new((v0o[i], v0o[j], v1o[j], v1o[i]))
        bm.faces.new(list(reversed(v0o)))
        bm.faces.new(v1o)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    for e in bm.edges:
        if len(e.link_faces) == 2:
            e.smooth = (e.link_faces[0].normal.angle(e.link_faces[1].normal, 0.0) < math.radians(32.0))
        else:
            e.smooth = False
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = link_obj(bpy.data.objects.new(name, mesh), coll, parent)
    obj.data.materials.append(material)
    es = obj.modifiers.new("EdgeSplit", "EDGE_SPLIT")
    es.use_edge_angle = False
    es.use_edge_sharp = True
    return obj


def make_shared_hex_bolt_mesh(radius=0.011, height=0.010, axis="Y"):
    bm = bmesh.new()
    verts0, verts1 = [], []
    for i in range(6):
        a = i * math.tau / 6.0
        c, s = radius * math.cos(a), radius * math.sin(a)
        if axis == "Y":
            verts0.append(bm.verts.new((c, 0.0, s)))
            verts1.append(bm.verts.new((c, height, s)))
        elif axis == "X":
            verts0.append(bm.verts.new((0.0, c, s)))
            verts1.append(bm.verts.new((height, c, s)))
        else:
            verts0.append(bm.verts.new((c, s, 0.0)))
            verts1.append(bm.verts.new((c, s, height)))
    bm.faces.new(list(reversed(verts0)))
    bm.faces.new(verts1)
    for i in range(6):
        j = (i + 1) % 6
        bm.faces.new((verts0[i], verts0[j], verts1[j], verts1[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"Shared_HexBolt_{axis}")
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def add_bolt_ring(prefix, bolt_mesh, material, coll, parent, center, ring_r, count, axis="Y", sign=1.0):
    cx, cy, cz = center
    for i in range(count):
        a = i * math.tau / count
        obj = link_obj(bpy.data.objects.new(f"{prefix}_Bolt_{i + 1}", bolt_mesh), coll, parent)
        if not obj.data.materials:
            obj.data.materials.append(material)
        if axis == "Y":
            obj.location = (cx + ring_r * math.cos(a), cy, cz + ring_r * math.sin(a))
            if sign < 0:
                obj.rotation_euler.z = math.pi
        elif axis == "X":
            obj.location = (cx, cy + ring_r * math.cos(a), cz + ring_r * math.sin(a))
            if sign < 0:
                obj.rotation_euler.z = math.pi
        else:
            obj.location = (cx + ring_r * math.cos(a), cy + ring_r * math.sin(a), cz)
            if sign < 0:
                obj.rotation_euler.x = math.pi


def create_cutaway_arc_shell_x(name, x0, x1, r_in, r_out, phi_start_deg, phi_end_deg,
                               mat_outer, mat_inner, mat_cut, coll, parent=None, segs=48):
    bm = bmesh.new()
    angles = [math.radians(phi_start_deg + (phi_end_deg - phi_start_deg) * i / segs) for i in range(segs + 1)]
    v_0_out = [bm.verts.new((x0, -r_out * math.cos(a), r_out * math.sin(a))) for a in angles]
    v_1_out = [bm.verts.new((x1, -r_out * math.cos(a), r_out * math.sin(a))) for a in angles]
    v_0_in = [bm.verts.new((x0, -r_in * math.cos(a), r_in * math.sin(a))) for a in angles]
    v_1_in = [bm.verts.new((x1, -r_in * math.cos(a), r_in * math.sin(a))) for a in angles]

    for i in range(segs):
        for f, m_idx, sm in (
            (bm.faces.new((v_0_out[i], v_0_out[i + 1], v_1_out[i + 1], v_1_out[i])), 0, True),
            (bm.faces.new((v_1_in[i], v_1_in[i + 1], v_0_in[i + 1], v_0_in[i])), 1, True),
            (bm.faces.new((v_0_in[i], v_0_in[i + 1], v_0_out[i + 1], v_0_out[i])), 2, False),
            (bm.faces.new((v_1_out[i], v_1_out[i + 1], v_1_in[i + 1], v_1_in[i])), 2, False),
        ):
            f.material_index = m_idx
            f.smooth = sm

    for verts in ((v_0_out[0], v_1_out[0], v_1_in[0], v_0_in[0]), (v_1_out[-1], v_0_out[-1], v_0_in[-1], v_1_in[-1])):
        f = bm.faces.new(verts)
        f.material_index = 2
        f.smooth = False

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for e in bm.edges:
        if len(e.link_faces) == 2:
            e.smooth = (e.link_faces[0].normal.angle(e.link_faces[1].normal, 0.0) < math.radians(32.0))
        else:
            e.smooth = False

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = link_obj(bpy.data.objects.new(name, mesh), coll, parent)
    for m in (mat_outer, mat_inner, mat_cut):
        obj.data.materials.append(m)
    es = obj.modifiers.new("EdgeSplit", "EDGE_SPLIT")
    es.use_edge_angle = False
    es.use_edge_sharp = True
    return obj


def create_flow_arrow(name, length, shaft_r, head_r, mat, coll, parent=None, direction_z=-1.0):
    bm = bmesh.new()
    segs = 20
    shaft_len = length * 0.60
    z1, z2 = direction_z * shaft_len, direction_z * length
    s0 = [bm.verts.new((shaft_r * math.cos(a * math.tau / segs), shaft_r * math.sin(a * math.tau / segs), 0.0)) for a in range(segs)]
    s1 = [bm.verts.new((shaft_r * math.cos(a * math.tau / segs), shaft_r * math.sin(a * math.tau / segs), z1)) for a in range(segs)]
    h0 = [bm.verts.new((head_r * math.cos(a * math.tau / segs), head_r * math.sin(a * math.tau / segs), z1)) for a in range(segs)]
    tip = bm.verts.new((0.0, 0.0, z2))
    bm.faces.new(list(reversed(s0)) if direction_z > 0 else s0)
    for i in range(segs):
        j = (i + 1) % segs
        bm.faces.new((s0[i], s0[j], s1[j], s1[i]))
        bm.faces.new((s1[i], s1[j], h0[j], h0[i]))
        bm.faces.new((h0[i], h0[j], tip))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = link_obj(bpy.data.objects.new(name, mesh), coll, parent)
    obj.data.materials.append(mat)
    return obj


def create_reticle_ring(name, r_outer, r_inner, mat, coll, parent):
    """Create thin camera-facing XZ target reticle ring at joint pin."""
    bm = bmesh.new()
    segs = 36
    y0, y1 = -0.145, -0.155
    vo = [bm.verts.new((r_outer * math.cos(i * math.tau / segs), y0, r_outer * math.sin(i * math.tau / segs))) for i in range(segs)]
    vi = [bm.verts.new((r_inner * math.cos(i * math.tau / segs), y0, r_inner * math.sin(i * math.tau / segs))) for i in range(segs)]
    vo2 = [bm.verts.new((r_outer * math.cos(i * math.tau / segs), y1, r_outer * math.sin(i * math.tau / segs))) for i in range(segs)]
    vi2 = [bm.verts.new((r_inner * math.cos(i * math.tau / segs), y1, r_inner * math.sin(i * math.tau / segs))) for i in range(segs)]
    for i in range(segs):
        j = (i + 1) % segs
        bm.faces.new((vi[i], vo[i], vo[j], vi[j]))
        bm.faces.new((vi2[j], vo2[j], vo2[i], vi2[i]))
        bm.faces.new((vo[i], vo2[i], vo2[j], vo[j]))
        bm.faces.new((vi2[i], vi[i], vi[j], vi2[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = link_obj(bpy.data.objects.new(name, mesh), coll, parent)
    obj.data.materials.append(mat)
    return obj


def create_catenary_hose(name, p_start_local, anchor_start, ctrl_start, sag_world_mid,
                         ctrl_end, p_end_local, anchor_end, radius, mat_hose, mat_ferrule, coll):
    """Three-point Bezier hydraulic hose directly keyframed per frame in World space (zero Hook offset drift)."""
    curve = bpy.data.curves.new(name + "_curve", "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = radius
    curve.bevel_resolution = 4
    curve.resolution_u = 18
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(2)

    ws = anchor_start.matrix_world @ Vector(p_start_local)
    we = anchor_end.matrix_world @ Vector(p_end_local)
    ts = anchor_start.matrix_world.to_3x3() @ Vector(ctrl_start)
    te = anchor_end.matrix_world.to_3x3() @ Vector(ctrl_end)
    wmid = 0.5 * (ws + we) + Vector(sag_world_mid)
    tmid = (we - ws) * 0.24

    bp0, bp1, bp2 = spline.bezier_points
    for bp in (bp0, bp1, bp2):
        bp.handle_left_type = "FREE"
        bp.handle_right_type = "FREE"

    bp0.co = ws
    bp0.handle_left = ws - ts * 0.4
    bp0.handle_right = ws + ts

    bp1.co = wmid
    bp1.handle_left = wmid - tmid
    bp1.handle_right = wmid + tmid

    bp2.co = we
    bp2.handle_left = we + te
    bp2.handle_right = we - te * 0.4

    hose_obj = link_obj(bpy.data.objects.new(name, curve), coll)
    curve.materials.append(mat_hose)

    for tag, anchor, loc in (("Start", anchor_start, p_start_local), ("End", anchor_end, p_end_local)):
        fer = create_cylinder_x(f"{name}_Ferrule_{tag}", -0.028, 0.028, radius * 1.48, 0.0, 16, mat_ferrule, coll, anchor)
        fer.location = loc
        fer.rotation_euler.y = math.pi * 0.5
    return (hose_obj, anchor_start, p_start_local, ctrl_start, anchor_end, p_end_local, ctrl_end, Vector(sag_world_mid))


def create_soil_mound_and_clods(coll, parent_bucket, coll_stage, mats):
    """Create excavated gravel load inside bucket + 14 secondary ballistic falling clods during 0.5-3.4s."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=0.39)
    for idx, v in enumerate(bm.verts):
        v.co.x *= 1.18
        v.co.y *= 1.06
        v.co.z *= 0.64
        n = 0.052 * math.sin(v.co.x * 11.7 + idx * 0.45) * math.cos(v.co.y * 9.3)
        v.co.x += n
        v.co.z += abs(n) * 0.9
    for f in bm.faces:
        f.smooth = True
    mesh = bpy.data.meshes.new("Bucket_Soil_Payload_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    mound = link_obj(bpy.data.objects.new("Bucket_Soil_Payload", mesh), coll, parent_bucket)
    mound.location = (-0.54, 0.0, -0.58)
    mound.data.materials.append(mats["soil"])

    # Shared icosphere clod mesh for lightweight instancing
    cbm = bmesh.new()
    bmesh.ops.create_icosphere(cbm, subdivisions=2, radius=0.042)
    for i, v in enumerate(cbm.verts):
        v.co.x *= 1.25 + 0.25 * math.sin(i * 1.7)
        v.co.z *= 0.78
    for f in cbm.faces:
        f.smooth = True
    clod_mesh = bpy.data.meshes.new("Soil_Clod_SharedMesh")
    cbm.to_mesh(clod_mesh)
    cbm.free()
    clod_mesh.materials.append(mats["soil"])

    clods = []
    for k in range(14):
        cobj = link_obj(bpy.data.objects.new(f"Falling_Soil_Clod_{k + 1:02d}", clod_mesh), coll_stage)
        clods.append(cobj)
    return clods


def build_industrial_stage_and_ibeam_plinth(coll_stage, carrier_root, mats, bolt_mesh_y, bolt_mesh_z):
    """Build detailed structural I-Beam test stand, hydraulic supply manifold, bay rails, and background arches."""
    # Ground plane at exact GROUND_Z = -1.5849 m + smooth rear bay slope
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=28, y_segments=28, size=20.0)
    for v in bm.verts:
        dist = math.hypot(v.co.x - 2.5, v.co.y - 2.0)
        if v.co.y > 6.8:
            v.co.z += min(6.5, (v.co.y - 6.8) ** 1.6 * 0.11)
        elif dist > 13.0:
            v.co.z += (dist - 13.0) * 0.06
        v.co.z += GROUND_Z_M
    for f in bm.faces:
        f.smooth = True
    fmesh = bpy.data.meshes.new("Industrial_Test_Bay_Floor")
    bm.to_mesh(fmesh)
    bm.free()
    floor = link_obj(bpy.data.objects.new("Industrial_Test_Bay_Floor", fmesh), coll_stage)
    floor.location = (2.5, 0.0, 0.0)
    floor.data.materials.append(mats["floor"])

    # Heavy I-Beam structural test plinth under V2 carrier_mount_reference (z = -1.5849 .. -0.875 m)
    # 1. Machined base sole plate + safety amber trim + M36 anchor bolts
    create_box_mesh("Plinth_SolePlate", -1.25, 0.98, -0.86, 0.86, GROUND_Z_M, GROUND_Z_M + 0.055,
                    mats["test_stand"], coll_stage, carrier_root, bevel_m=0.006)
    create_box_mesh("Plinth_Hazard_Trim", -1.26, 0.99, -0.87, -0.83, GROUND_Z_M + 0.012, GROUND_Z_M + 0.048,
                    mats["yellow"], coll_stage, carrier_root, bevel_m=0.002)
    for ax in (-1.15, -0.45, 0.25, 0.88):
        for ay in (-0.76, 0.76):
            bolt = link_obj(bpy.data.objects.new(f"AnchorBolt_{ax:.2f}_{ay:.2f}", bolt_mesh_z), coll_stage, carrier_root)
            bolt.scale = (2.2, 2.2, 2.5)
            bolt.location = (ax, ay, GROUND_Z_M + 0.055)
            if not bolt.data.materials:
                bolt.data.materials.append(mats["machined_steel"])

    # 2. Longitudinal Structural I-Beams (Left & Right web + flanges + diagonal stiffener gussets)
    z_bot_flange = GROUND_Z_M + 0.055
    z_top_flange = -0.925
    for tag, yc in (("R", -0.38), ("L", 0.38)):
        create_box_mesh(f"Plinth_IBeam_BotFlange_{tag}", -0.58, 0.68, yc - 0.16, yc + 0.16,
                        z_bot_flange, z_bot_flange + 0.045, mats["test_stand"], coll_stage, carrier_root)
        create_box_mesh(f"Plinth_IBeam_Web_{tag}", -0.52, 0.62, yc - 0.032, yc + 0.032,
                        z_bot_flange + 0.045, z_top_flange, mats["dark_steel"], coll_stage, carrier_root)
        # Welded vertical stiffener ribs inside I-beam channel (facing camera!)
        for rx in (-0.42, -0.08, 0.24, 0.54):
            create_box_mesh(f"Plinth_IBeam_Rib_{tag}_{rx:.2f}", rx - 0.018, rx + 0.018,
                            yc - 0.15, yc + 0.15, z_bot_flange + 0.045, z_top_flange,
                            mats["test_stand"], coll_stage, carrier_root, bevel_m=0.002)

    # Diagonal outer gusset braces
    for rx_pair in (((-0.96, GROUND_Z_M + 0.055), (-0.54, GROUND_Z_M + 0.055), (-0.54, -0.88), (-0.64, -0.88)),
                    ((0.86, GROUND_Z_M + 0.055), (0.60, GROUND_Z_M + 0.055), (0.60, -0.88), (0.70, -0.88))):
        create_prism_xz(f"Plinth_GussetBrace_{rx_pair[0][0]:.1f}", rx_pair, -0.44, -0.36,
                        mats["test_stand"], coll_stage, carrier_root)
        create_prism_xz(f"Plinth_GussetBraceL_{rx_pair[0][0]:.1f}", rx_pair, 0.36, 0.44,
                        mats["test_stand"], coll_stage, carrier_root)

    create_box_mesh("Plinth_Upper_TurretDeck", -0.60, 0.68, -0.66, 0.66, -0.925, -0.875,
                    mats["dark_steel"], coll_stage, carrier_root, bevel_m=0.005)

    # 3. Rear Hydraulic Test Pump & Distribution Manifold Chest
    create_box_mesh("Test_Pump_Housing", -1.16, -0.56, -0.54, 0.54, z_bot_flange, -0.38,
                    mats["test_stand"], coll_stage, carrier_root, bevel_m=0.010)
    create_box_mesh("Test_Valve_Manifold", -0.64, -0.44, -0.42, 0.42, -0.68, -0.44,
                    mats["machined_steel"], coll_stage, carrier_root, bevel_m=0.005)
    # Recessed Floor Track Rails (Clean studio floor framing without overhead gantry beams)
    create_box_mesh("Grade_Scale_Rail_Front", -1.00, 7.80, -1.32, -1.26, GROUND_Z_M, GROUND_Z_M + 0.022,
                    mats["machined_steel"], coll_stage, bevel_m=0.002)


def add_cinematic_bolt_and_pipe_details(coll_boom, coll_stick, coll_pins, boom_pv, stick_pv,
                                        pin_map, cyl_axes, mats, bolt_mesh_y, bolt_mesh_x):
    """Attach machined M20 hex bolt circles onto pivot caps/glands + rigid steel lines & boom ribs."""
    # Boom side welded stiffener rib & junction manifold
    rib_poly = [(0.75, 0.20), (1.72, 0.68), (2.46, 0.85), (3.12, 0.82),
                (3.12, 0.77), (2.46, 0.80), (1.74, 0.63), (0.77, 0.15)]
    create_prism_xz("Boom_Side_Reinforcement_Rib", rib_poly, -0.214, -0.206,
                    mats["yellow"], coll_boom, boom_pv, bevel_m=0.002)
    create_box_mesh("Boom_Hydraulic_JunctionBox", 0.56, 0.76, -0.255, -0.209, 0.25, 0.41,
                    mats["dark_steel"], coll_boom, boom_pv, bevel_m=0.003)

    # Four parallel rigid hydraulic steel pipes along Boom -Y spine with bolted clamps
    pipe_pts = [(0.72, -0.228, 0.34), (1.66, -0.228, 0.88), (2.48, -0.228, 1.07), (3.18, -0.228, 1.05)]
    for line_idx, (dz, pmat) in enumerate(((-0.036, mats["machined_steel"]), (-0.012, mats["machined_steel"]),
                                           (0.012, mats["dark_steel"]), (0.036, mats["dark_steel"])), 1):
        pcurve = bpy.data.curves.new(f"Boom_Steel_Line_{line_idx}_crv", "CURVE")
        pcurve.dimensions = "3D"
        pcurve.bevel_depth = 0.010
        pcurve.bevel_resolution = 4
        sp = pcurve.splines.new("POLY")
        sp.points.add(len(pipe_pts) - 1)
        for pt, coord in zip(sp.points, pipe_pts):
            pt.co = (coord[0], coord[1], coord[2] + dz, 1.0)
        link_obj(bpy.data.objects.new(f"Boom_Steel_Line_{line_idx}", pcurve), coll_boom, boom_pv)
        pcurve.materials.append(pmat)
    for idx, (cx, cz) in enumerate(((0.92, 0.45), (1.52, 0.80), (2.10, 0.98), (2.68, 1.06), (3.12, 1.05)), 1):
        create_box_mesh(f"Boom_Pipe_Clamp_{idx}", cx - 0.025, cx + 0.025, -0.246, -0.208, cz - 0.056, cz + 0.056,
                        mats["dark_steel"], coll_boom, boom_pv, bevel_m=0.002)

    # Stick twin steel lines along upper flange
    spipe_pts = [(0.22, -0.165, 0.31), (0.62, -0.165, 0.45), (1.58, -0.165, 0.25), (2.45, -0.165, 0.19)]
    for lidx, dz in enumerate((-0.016, 0.016), 1):
        scurve = bpy.data.curves.new(f"Stick_Steel_Line_{lidx}_crv", "CURVE")
        scurve.dimensions = "3D"
        scurve.bevel_depth = 0.009
        scurve.bevel_resolution = 4
        sp = scurve.splines.new("POLY")
        sp.points.add(len(spipe_pts) - 1)
        for pt, coord in zip(sp.points, spipe_pts):
            pt.co = (coord[0], coord[1], coord[2] + dz, 1.0)
        link_obj(bpy.data.objects.new(f"Stick_Steel_Line_{lidx}", scurve), coll_stick, stick_pv)
        scurve.materials.append(mats["machined_steel"])
    for idx, (sx, sz) in enumerate(((0.62, 0.45), (1.58, 0.25), (2.35, 0.19)), 1):
        create_box_mesh(f"Stick_Pipe_Clamp_{idx}", sx - 0.020, sx + 0.020, -0.182, -0.150, sz - 0.036, sz + 0.036,
                        mats["dark_steel"], coll_stick, stick_pv, bevel_m=0.002)

    # Machined Hex Bolt Circles on major retaining caps (Y facing camera) and cylinder glands (X axis)
    for pid, y_loc, ring_r, count in (
        ("PIN_BOOM_BASE", -0.371, 0.064, 6),
        ("PIN_BOOM_TIP", -0.264, 0.060, 6),
        ("PIN_STICK_TIP", -0.254, 0.054, 4),
        ("PIN_ARM_CYL_A", -0.144, 0.044, 4),
    ):
        add_bolt_ring(pid, bolt_mesh_y, mats["machined_steel"], coll_pins, pin_map[pid], (0.0, y_loc, 0.0), ring_r, count, axis="Y", sign=-1.0)

    for cname, gland_x, ring_r in (("boom_r", 2.108, 0.068), ("boom_l", 2.108, 0.068),
                                   ("arm", 1.758, 0.076), ("bucket", 1.608, 0.065)):
        add_bolt_ring(f"{cname}_gland", bolt_mesh_x, mats["machined_steel"], coll_pins, cyl_axes[cname],
                      (gland_x, 0.0, 0.0), ring_r, 6, axis="X", sign=1.0)


def build_v71_cutaway_and_exploded(stl_dir: Path, mats, coll_cyl, coll_exp,
                                   cyl_r_base, cyl_r_eye, cyl_r_bax, cyl_r_rax, boom_rod_piston_tpl,
                                   bolt_mesh_x=None):
    """Build upgraded V7.1 Cutaway (dual seals, animated fluid waves, pin reticles, leader lines & live HUD)
    plus V7.1 Coaxial Exploded View showcase.
    """
    global _TELEMETRY_FONT
    spec = ACTUATOR_SPECS["boom"]
    cut_group = []

    # 1. Cutaway Shell, Head, Gland facing camera (-Y)
    shell = create_cutaway_arc_shell_x(
        "Boom_Cyl_R_Cutaway_Shell", 0.140, spec["gland"], 0.060, 0.079, 56.0, 312.0,
        mats["yellow"], mats["machined_steel"], mats["cutaway_section"], coll_cyl, cyl_r_bax
    )
    head_cut = create_cutaway_arc_shell_x(
        "Boom_Cyl_R_Cutaway_Head", 0.113, 0.172, 0.001, 0.085, 56.0, 312.0,
        mats["dark_steel"], mats["machined_steel"], mats["cutaway_section"], coll_cyl, cyl_r_bax
    )
    gland_cut = create_cutaway_arc_shell_x(
        "Boom_Cyl_R_Cutaway_Gland", spec["gland"] - 0.042, spec["gland"] + 0.028, 0.0439, 0.086, 56.0, 312.0,
        mats["dark_steel"], mats["machined_steel"], mats["cutaway_section"], coll_cyl, cyl_r_bax
    )

    # Upgraded multi-part internal piston on Rod_Axis (bronze guides, central PTFE pressure seal, lock nut)
    piston_bronze_f = create_cylinder_x(
        "Boom_Cyl_R_Piston_BronzeFront", spec["rod_span"] - 0.048, spec["rod_span"] - 0.036, 0.0593, 0.043, 36,
        mats["bronze_guide"], coll_cyl, cyl_r_rax
    )
    piston_ptfe = create_cylinder_x(
        "Boom_Cyl_R_Piston_PTFE_Seal", spec["rod_span"] - 0.066, spec["rod_span"] - 0.050, 0.0596, 0.043, 36,
        mats["ptfe_seal"], coll_cyl, cyl_r_rax
    )
    piston_bronze_r = create_cylinder_x(
        "Boom_Cyl_R_Piston_BronzeRear", spec["rod_span"] - 0.082, spec["rod_span"] - 0.070, 0.0593, 0.043, 36,
        mats["bronze_guide"], coll_cyl, cyl_r_rax
    )
    piston_nut = create_cylinder_x(
        "Boom_Cyl_R_Piston_LockNut", spec["rod_span"], spec["rod_span"] + 0.026, 0.032, 0.0, 6,
        mats["machined_steel"], coll_cyl, cyl_r_rax
    )

    # 2. Animated Hydraulic Oil Columns (TexCoord Object bound directly to cyl_r_bax -> wave bands never stretch!)
    mats["oil_supply_tc"].object = cyl_r_bax
    mats["oil_return_tc"].object = cyl_r_bax

    cap_oil = create_cylinder_x("Boom_Cyl_R_CapOil_SupplyRed", 0.0, 1.0, 0.0585, 0.0, 32,
                                mats["oil_supply"], coll_cyl, cyl_r_bax)
    cap_oil.location = (0.172, 0.0, 0.0)

    rod_oil = create_cylinder_x("Boom_Cyl_R_RodOil_ReturnBlue", -1.0, 0.0, 0.0585, 0.0432, 32,
                                mats["oil_return"], coll_cyl, cyl_r_bax)
    rod_oil.location = (spec["gland"] - 0.042, 0.0, 0.0)

    # 3. 3D SAE Flow Arrows + Dual Pin Target Reticles
    arr_in = create_flow_arrow("Flow_Arrow_Supply_Red", 0.24, 0.011, 0.024, mats["arrow_red"],
                               coll_cyl, cyl_r_bax, direction_z=-1.0)
    arr_in.location = (0.255, 0.0, 0.37)

    arr_out = create_flow_arrow("Flow_Arrow_Return_Blue", 0.24, 0.011, 0.024, mats["arrow_blue"],
                                coll_cyl, cyl_r_bax, direction_z=1.0)
    arr_out.location = (1.980, 0.0, 0.13)

    ret_a = create_reticle_ring("Pin_Reticle_A", 0.125, 0.108, mats["reticle_cyan"], coll_cyl, cyl_r_base)
    ret_b = create_reticle_ring("Pin_Reticle_B", 0.125, 0.108, mats["reticle_cyan"], coll_cyl, cyl_r_eye)

    # 4. World-Horizontal Dynamic Telemetry Panel & Engineering Leader Lines (Right Open Zone)
    banner_anchor = make_empty("Cutaway_Banner_Anchor", coll_cyl, cyl_r_bax, location=(1.10, 0.0, 0.0))
    banner = make_empty("Cutaway_Callout_Banner", coll_cyl, location=(1.25, -0.52, 0.45))
    c_loc = banner.constraints.new("COPY_LOCATION")
    c_loc.target = banner_anchor

    holder = make_empty("Cutaway_Banner_Holder", coll_cyl, banner, location=(0.76, -0.12, -0.10))

    # Main telemetry readout card (upper right)
    panel_bg = create_box_mesh("Cutaway_Telemetry_Card", -0.05, 1.38, 0.02, 0.04, -0.27, 0.19,
                               mats["hud_backing"], coll_cyl, holder, bevel_m=0.004)

    fh = bpy.data.curves.new("V71_Header_Font", "FONT")
    fh.body = "MẶT CẮT MINH HỌA · XI LANH NÂNG CẦN (PC200-8 CONCEPT)"
    fh.size = 0.040
    fh.align_x = "LEFT"
    hdr_obj = link_obj(bpy.data.objects.new("V71_Header_Text", fh), coll_cyl, holder)
    hdr_obj.location = (0.0, -0.005, 0.105)
    hdr_obj.rotation_euler.x = math.pi * 0.5
    fh.materials.append(mats["hud_gold"])

    # Live dynamic numbers updated per frame via _update_telemetry_text
    flive = bpy.data.curves.new("V71_Telemetry_Live_Font", "FONT")
    flive.body = "A-B: 2,925 mm  |  Ty đi ra: 725 / 1,334 mm\nTốc độ đẩy ty: 21.5 mm/s  |  Áp suất minh họa: ~185 bar"
    flive.size = 0.033
    flive.align_x = "LEFT"
    _TELEMETRY_FONT = flive
    live_obj = link_obj(bpy.data.objects.new("V71_Telemetry_Live_Text", flive), coll_cyl, holder)
    live_obj.location = (0.0, -0.005, 0.035)
    live_obj.rotation_euler.x = math.pi * 0.5
    flive.materials.append(mats["hud_white"])

    # Physical progress gauge bar (scales deterministically with boom_stroke_mm / 1334.0)
    gauge_track = create_box_mesh("Telemetry_Stroke_Track", 0.0, 1.24, -0.008, 0.008, -0.095, -0.068,
                                  mats["dark_steel"], coll_cyl, holder, bevel_m=0.001)
    gauge_fill = create_box_mesh("Telemetry_Stroke_Fill", 0.0, 1.0, -0.012, 0.006, -0.093, -0.070,
                                 mats["hud_gold"], coll_cyl, holder, bevel_m=0.001)
    gauge_fill.location = (0.0, 0.0, 0.0)
    gauge_fill.scale = (1.24 * 0.54, 1.0, 1.0)

    flgd = bpy.data.curves.new("V71_Legend_Font", "FONT")
    flgd.body = "ĐỎ: Dầu cấp khoang đáy (đẩy piston)   |   XANH: Dầu hồi khoang ty -> về thùng"
    flgd.size = 0.029
    flgd.align_x = "LEFT"
    lgd_obj = link_obj(bpy.data.objects.new("V71_Legend_Text", flgd), coll_cyl, holder)
    lgd_obj.location = (0.0, -0.005, -0.175)
    lgd_obj.rotation_euler.x = math.pi * 0.5
    flgd.materials.append(mats["hud_white"])

    fdisc = bpy.data.curves.new("V71_Disclaimer_Font", "FONT")
    fdisc.body = "*Hành trình theo brochure CEN00049-08; cổng dầu & áp suất minh họa nguyên lý"
    fdisc.size = 0.023
    fdisc.align_x = "LEFT"
    disc_obj = link_obj(bpy.data.objects.new("V71_Disclaimer_Text", fdisc), coll_cyl, holder)
    disc_obj.location = (0.0, -0.005, -0.235)
    disc_obj.rotation_euler.x = math.pi * 0.5
    fdisc.materials.append(mats["reticle_cyan"])

    # Clean Horizontal Leader Lines pointing cleanly from Panel Left Edge toward Blue/Red Chambers
    leader_rod = create_box_mesh("Leader_To_RodChamber", -0.58, -0.05, -0.01, 0.01, -0.004, 0.004,
                                 mats["arrow_blue"], coll_cyl, holder, bevel_m=0.0)
    leader_rod.location = (0.0, -0.01, 0.14)
    leader_cap = create_box_mesh("Leader_To_CapChamber", -0.82, -0.05, -0.01, 0.01, -0.004, 0.004,
                                 mats["arrow_red"], coll_cyl, holder, bevel_m=0.0)
    leader_cap.location = (0.0, -0.01, -0.16)

    cut_group.extend([
        shell, head_cut, gland_cut, piston_bronze_f, piston_ptfe, piston_bronze_r, piston_nut,
        cap_oil, rod_oil, arr_in, arr_out, ret_a, ret_b,
        panel_bg, hdr_obj, live_obj, gauge_track, gauge_fill, lgd_obj, disc_obj, leader_rod, leader_cap
    ])

    # --- Isolated Coaxial Exploded Cylinder Showcase at Y = +28.0 m ---
    exp_origin = make_empty("Exploded_Showcase_Origin", coll_exp, location=(0.0, 28.0, 0.0))
    create_box_mesh("Exploded_Studio_Floor", -4.0, 9.5, -6.0, 6.0, -0.60, -0.34,
                    mats["floor"], coll_exp, exp_origin, bevel_m=0.0)
    create_box_mesh("Exploded_Display_Bench", -0.80, 6.30, -0.72, 0.72, -0.34, -0.24,
                    mats["test_stand"], coll_exp, exp_origin, bevel_m=0.008)
    create_cylinder_x("Exploded_Centerline_Axis", -0.58, 6.08, 0.004, 0.0, 12,
                      mats["hud_gold"], coll_exp, exp_origin)

    exp_pin_a = import_stl_part(stl_dir, "pin_R42_L184.stl", "Exploded_01_Pin_Base_A",
                                mats["machined_steel"], coll_exp, exp_origin)
    exp_pin_a.location = (-0.35, 0.0, 0.0)
    exp_barrel = import_stl_part(stl_dir, "boom_cylinder_barrel_body.stl", "Exploded_02_Barrel_Tube",
                                 mats["yellow"], coll_exp, exp_origin)
    exp_ports = import_stl_part(stl_dir, "boom_cylinder_barrel_ports.stl", "Exploded_03_SAE_Ports_FeedLine",
                                mats["machined_steel"], coll_exp, exp_origin)
    exp_ports.location = (0.0, 0.0, 0.28)

    exp_piston = instance_stl_mesh(boom_rod_piston_tpl, "Exploded_04_Piston_Head",
                                   mats["machined_steel"], coll_exp, exp_origin)
    exp_piston.rotation_euler.z = math.pi
    exp_piston.location = (4.38, 0.0, 0.0)
    create_cylinder_x("Exploded_04_Bronze_WearBand", spec["rod_span"] - 0.048, spec["rod_span"] - 0.036,
                      0.0596, 0.043, 36, mats["bronze_guide"], coll_exp, exp_piston)
    create_cylinder_x("Exploded_04_PTFE_Seal", spec["rod_span"] - 0.066, spec["rod_span"] - 0.050,
                      0.0598, 0.043, 36, mats["ptfe_seal"], coll_exp, exp_piston)

    exp_gland = import_stl_part(stl_dir, "boom_cylinder_barrel_gland.stl", "Exploded_05_Gland_Seal_Collar",
                                mats["dark_steel"], coll_exp, exp_origin)
    exp_gland.location = (0.78, 0.0, 0.0)
    if bolt_mesh_x is not None:
        add_bolt_ring("Exploded_Gland", bolt_mesh_x, mats["machined_steel"], coll_exp, exp_gland,
                      (2.108, 0.0, 0.0), 0.068, 6, axis="X", sign=1.0)
    exp_chrome = import_stl_part(stl_dir, "boom_rod_chrome.stl", "Exploded_06_Chrome_Piston_Rod",
                                 mats["chrome"], coll_exp, exp_origin)
    exp_chrome.rotation_euler.z = math.pi
    exp_chrome.location = (5.22, 0.0, 0.0)
    exp_eye = import_stl_part(stl_dir, "boom_rod_eye.stl", "Exploded_07_Forged_Rod_Eye",
                              mats["dark_steel"], coll_exp, exp_origin)
    exp_eye.rotation_euler.z = math.pi
    exp_eye.location = (5.45, 0.0, 0.0)
    exp_pin_b = import_stl_part(stl_dir, "pin_R42_L170.stl", "Exploded_08_Pin_Rod_B",
                                mats["machined_steel"], coll_exp, exp_origin)
    exp_pin_b.location = (5.82, 0.0, 0.0)

    # Clean technical label strip along front edge of Exploded_Display_Bench (zero clutter)
    plaque = make_empty("Exploded_Label_Plaque", coll_exp, exp_origin, location=(2.75, -0.82, -0.22))
    plaque.rotation_euler.x = math.radians(72.0)
    create_box_mesh("Exploded_Label_Backdrop", -3.48, 3.48, -0.145, 0.145, -0.024, 0.0,
                    mats["hud_backing"], coll_exp, plaque, bevel_m=0.004)
    for l_idx, (y_off, body_txt, l_mat) in enumerate((
        (0.032, "[01] Chốt đáy Pin A   |   [02] Vỏ xi lanh   |   [03] Tuy ô dầu SAE   |   [04] Piston & Phớt Đồng/PTFE", mats["hud_gold"]),
        (-0.075, "[05] Cổ bít Gland   |   [06] Ty mạ Chrome   |   [07] Đầu mắt ty   |   [08] Chốt cần Pin B", mats["hud_white"]),
    ), 1):
        fc = bpy.data.curves.new(f"Exploded_Legend_Row{l_idx}_Font", "FONT")
        fc.body = body_txt
        fc.size = 0.095
        fc.align_x = "CENTER"
        fo = link_obj(bpy.data.objects.new(f"Exploded_Legend_Row{l_idx}", fc), coll_exp, plaque)
        fo.location = (0.0, y_off, 0.004)
        fc.materials.append(l_mat)

    return cut_group, cap_oil, rod_oil, gauge_fill


def set_cutaway_visibility(intact_objs, cutaway_objs, show_cutaway: bool, frame=None):
    for obj in intact_objs:
        obj.hide_render = show_cutaway
        obj.hide_viewport = show_cutaway
        if frame is not None:
            obj.keyframe_insert(data_path="hide_render", frame=frame)
            obj.keyframe_insert(data_path="hide_viewport", frame=frame)
    for obj in cutaway_objs:
        obj.hide_render = not show_cutaway
        obj.hide_viewport = not show_cutaway
        if frame is not None:
            obj.keyframe_insert(data_path="hide_render", frame=frame)
            obj.keyframe_insert(data_path="hide_viewport", frame=frame)


def setup_cinematic_lighting_dof_and_compositor(coll_stage, scene, cam_target):
    world = bpy.data.worlds.new("Industrial_Proving_Sky_V71")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 0.90

    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.035, 0.044, 0.060, 1.0)
    e_mid = ramp.color_ramp.elements.new(0.49)
    e_mid.color = (0.14, 0.175, 0.225, 1.0)
    ramp.color_ramp.elements[2].position = 0.72
    ramp.color_ramp.elements[2].color = (0.28, 0.35, 0.44, 1.0)
    nt.links.new(tc.outputs["Generated"], sep.inputs["Vector"])
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

    def add_area(name, loc, target, energy, color, size):
        ld = bpy.data.lights.new(name, "AREA")
        ld.energy = energy
        ld.color = color
        ld.shape = "DISK"
        ld.size = size
        lo = link_obj(bpy.data.objects.new(name, ld), coll_stage)
        lo.location = loc
        lo.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        return lo

    # Balanced industrial studio 5-light rig (soft 180-deg falloff matching V7.0 rich saturation)
    add_area("Key_Warm_Sunlight_V71", (-2.2, -9.2, 8.0), (3.4, 0.0, 0.6), 4500.0, (1.0, 0.88, 0.74), 4.2)
    add_area("Fill_Cool_SkyBay_V71", (9.6, -7.8, 3.0), (3.6, 0.0, 0.8), 1750.0, (0.68, 0.82, 1.0), 7.5)
    add_area("Rim_Steel_Highlight_V71", (4.5, 6.4, 6.8), (3.0, 0.0, 1.2), 3500.0, (1.0, 0.94, 0.86), 5.5)
    add_area("Chrome_Specular_Strip_V71", (1.2, -5.5, 5.5), (1.4, -0.52, 0.4), 550.0, (0.95, 0.97, 1.0), 2.4)
    add_area("Undercarriage_Fill_V71", (5.5, -4.5, -1.2), (4.8, 0.0, 0.1), 500.0, (0.78, 0.86, 0.96), 4.0)

    # Exploded gallery bay lights at Y = +28 m
    add_area("Exploded_Key_V71", (1.2, 23.2, 3.8), (2.7, 28.0, 0.0), 1450.0, (1.0, 0.94, 0.88), 3.8)
    add_area("Exploded_Fill_V71", (5.5, 24.5, 2.2), (2.7, 28.0, 0.0), 680.0, (0.72, 0.84, 1.0), 4.0)
    add_area("Exploded_Rim_V71", (2.5, 31.8, 3.2), (2.7, 28.0, 0.0), 1150.0, (0.85, 0.92, 1.0), 4.2)

    # Setup Blender 5.3 Compositor with subtle Fog Glow for metallic & fluid highlights
    scene.use_nodes = True
    ng = bpy.data.node_groups.new("V71_Cinematic_Compositor", "CompositorNodeTree")
    ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    scene.compositing_node_group = ng
    rl = ng.nodes.new("CompositorNodeRLayers")
    glare = ng.nodes.new("CompositorNodeGlare")
    glare.inputs["Type"].default_value = "Fog Glow"
    glare.inputs["Threshold"].default_value = 1.65
    glare.inputs["Size"].default_value = 6
    glare.inputs["Strength"].default_value = 0.20
    out_n = ng.nodes.new("NodeGroupOutput")
    ng.links.new(rl.outputs["Image"], glare.inputs["Image"])
    ng.links.new(glare.outputs["Image"], out_n.inputs["Image"])


def make_camera(name, loc, target, lens_mm, coll, dof_target=None, fstop=3.4):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens_mm
    cd.clip_start = 0.05
    cd.clip_end = 120.0
    if dof_target is not None:
        cd.dof.use_dof = True
        cd.dof.focus_object = dof_target
        cd.dof.aperture_fstop = fstop
    co = link_obj(bpy.data.objects.new(name, cd), coll)
    co.location = loc
    co.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return co


def configure_render_engine(scene, engine="CYCLES", samples=96):
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.fps = FPS
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.view_transform = "AgX"
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0

    if engine == "CYCLES":
        scene.render.engine = "CYCLES"
        prefs = bpy.context.preferences.addons["cycles"].preferences
        try:
            prefs.compute_device_type = "OPTIX"
            prefs.get_devices()
            for d in prefs.devices:
                d.use = (d.type == "OPTIX")
        except Exception:
            prefs.compute_device_type = "CUDA"
            prefs.get_devices()
            for d in prefs.devices:
                d.use = (d.type == "CUDA")
        scene.cycles.device = "GPU"
        scene.cycles.samples = samples
        scene.cycles.use_adaptive_sampling = True
        scene.cycles.adaptive_threshold = 0.015
        scene.cycles.use_denoising = True
        scene.cycles.max_bounces = 8
        scene.cycles.glossy_bounces = 4
        scene.cycles.transmission_bounces = 6
    else:
        scene.render.engine = "BLENDER_EEVEE"
        scene.eevee.taa_render_samples = max(24, samples)
        scene.eevee.use_raytracing = True


def read_motion_trace(csv_path: Path):
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        rows = [{k: float(v) for k, v in r.items()} for r in csv.DictReader(f)]
    if len(rows) != FRAMES:
        raise ValueError(f"Expected {FRAMES} rows, found {len(rows)}")
    return rows


def animate_secondary_effects_and_verify(scene, rows, refs, cap_oil, rod_oil, gauge_fill,
                                         intact_r, cutaway_r, mats, hoses_info, clods, qa_dir: Path):
    boom_pv = refs["boom_pv"]
    stick_pv = refs["stick_pv"]
    bucket_pv = refs["bucket_pv"]
    knee_j = refs["knee_j"]

    for obj in (boom_pv, stick_pv, bucket_pv, knee_j, cap_oil, rod_oil, gauge_fill):
        obj.animation_data_clear()

    base_stroke = rows[0]["boom_stroke_mm"]

    for frame, row in enumerate(rows, 1):
        t = row["t_s"]
        boom_pv.rotation_euler.y = -math.radians(row["boom_abs_deg"])
        stick_pv.rotation_euler.y = math.radians(row["arm_rel_deg"])
        bucket_pv.rotation_euler.y = math.radians(row["bucket_rel_deg"] - 90.0)

        boom_pv.keyframe_insert(data_path="rotation_euler", index=1, frame=frame)
        stick_pv.keyframe_insert(data_path="rotation_euler", index=1, frame=frame)
        bucket_pv.keyframe_insert(data_path="rotation_euler", index=1, frame=frame)

        knee_j.location = (row["bucket_cyl_B_x_mm"] * UNIT, 0.0, row["bucket_cyl_B_z_mm"] * UNIT)
        knee_j.keyframe_insert(data_path="location", frame=frame)

        # Update cutaway chambers (fixed cylinder axis, strictly incompressible fluid volume fit)
        L_m = row["boom_cyl_length_mm"] * UNIT
        cap_oil.scale = (max(0.05, L_m - 2.172), 1.0, 1.0)
        rod_oil.scale = (max(0.05, 3.956 - L_m), 1.0, 1.0)
        cap_oil.keyframe_insert(data_path="scale", index=0, frame=frame)
        rod_oil.keyframe_insert(data_path="scale", index=0, frame=frame)

        # Progress bar X scale
        gauge_fill.scale = (1.24 * max(0.02, row["boom_stroke_mm"] / 1334.0), 1.0, 1.0)
        gauge_fill.keyframe_insert(data_path="scale", index=0, frame=frame)

        # Animate hydraulic wave pulses flowing steadily upward through Cap & Rod chambers
        delta_ext_m = (row["boom_stroke_mm"] - base_stroke) * UNIT
        phase = delta_ext_m * 10.5  # clear multi-cycle steady wave motion
        mats["oil_supply_phase"].outputs[0].default_value = phase
        mats["oil_supply_phase"].outputs[0].keyframe_insert(data_path="default_value", frame=frame)
        mats["oil_return_phase"].outputs[0].default_value = phase * 1.35
        mats["oil_return_phase"].outputs[0].keyframe_insert(data_path="default_value", frame=frame)

    # Secondary motion 1: Directly keyframe all 3 Bezier points of all 6 catenary hoses in World coords (0.00 mm drift)
    bpy.context.view_layer.update()
    for frame, row in enumerate(rows, 1):
        scene.frame_set(frame)
        deps = bpy.context.evaluated_depsgraph_get()
        t = row["t_s"]
        vel_norm = row["boom_vel_mms"] / 22.0
        for hose_obj, anchor_s, loc_s, ctrl_s, anchor_e, loc_e, ctrl_e, base_sag in hoses_info:
            mw_s = anchor_s.evaluated_get(deps).matrix_world
            mw_e = anchor_e.evaluated_get(deps).matrix_world
            ws = mw_s @ Vector(loc_s)
            we = mw_e @ Vector(loc_e)
            ts = mw_s.to_3x3() @ Vector(ctrl_s)
            te = mw_e.to_3x3() @ Vector(ctrl_e)
            bounce = Vector((0.0, 0.0, -0.028 * vel_norm + 0.012 * math.sin(t * 2.8) * vel_norm))
            wmid = 0.5 * (ws + we) + base_sag + bounce
            tmid = (we - ws) * 0.24

            bp0, bp1, bp2 = hose_obj.data.splines[0].bezier_points
            bp0.co = ws
            bp0.handle_left = ws - ts * 0.4
            bp0.handle_right = ws + ts
            bp1.co = wmid
            bp1.handle_left = wmid - tmid
            bp1.handle_right = wmid + tmid
            bp2.co = we
            bp2.handle_left = we + te
            bp2.handle_right = we - te * 0.4

            for bp in (bp0, bp1, bp2):
                bp.keyframe_insert(data_path="co", frame=frame)
                bp.keyframe_insert(data_path="handle_left", frame=frame)
                bp.keyframe_insert(data_path="handle_right", frame=frame)

    # Secondary motion 2: Ballistic gravel/soil clods shedding from curled bucket rim during heavy initial lift (0.4s-3.5s)
    for idx, cobj in enumerate(clods):
        t_start = 0.35 + (idx * 0.21)
        f_start = max(1, int(round(t_start * FPS)) + 1)
        scene.frame_set(f_start)
        deps = bpy.context.evaluated_depsgraph_get()
        bkt_mw = bucket_pv.evaluated_get(deps).matrix_world
        origin_w = bkt_mw @ Vector((-0.88 - 0.06 * (idx % 4), -0.32 + 0.11 * (idx % 7), -0.58))
        vx = -0.18 + 0.07 * (idx % 5)
        vy = -0.06 + 0.03 * (idx % 5)
        vz0 = -0.15

        cobj.hide_render = True
        cobj.hide_viewport = True
        cobj.keyframe_insert(data_path="hide_render", frame=1)
        cobj.keyframe_insert(data_path="hide_viewport", frame=1)

        for frame in range(f_start, FRAMES + 1):
            dt = (frame - 1) / FPS - t_start
            if dt < 0.0:
                continue
            if frame == f_start:
                cobj.hide_render = False
                cobj.hide_viewport = False
                cobj.keyframe_insert(data_path="hide_render", frame=frame)
                cobj.keyframe_insert(data_path="hide_viewport", frame=frame)
            z_pos = origin_w.z + vz0 * dt - 0.5 * 9.81 * (dt * dt)
            z_floor = GROUND_Z_M + 0.028
            if z_pos <= z_floor:
                t_hit = (-vz0 + math.sqrt(max(0.0, vz0 * vz0 + 2.0 * 9.81 * (origin_w.z - z_floor)))) / 9.81
                cobj.location = (origin_w.x + vx * t_hit, origin_w.y + vy * t_hit, z_floor)
                cobj.keyframe_insert(data_path="location", frame=frame)
                break
            cobj.location = (origin_w.x + vx * dt, origin_w.y + vy * dt, z_pos)
            cobj.rotation_euler = (dt * 3.2, dt * 2.1, dt * 1.4)
            cobj.keyframe_insert(data_path="location", frame=frame)
            cobj.keyframe_insert(data_path="rotation_euler", frame=frame)

    # Keyframe cutaway reveal strictly for 8-14s (Frames 240..420)
    set_cutaway_visibility(intact_r, cutaway_r, show_cutaway=False, frame=1)
    set_cutaway_visibility(intact_r, cutaway_r, show_cutaway=False, frame=239)
    set_cutaway_visibility(intact_r, cutaway_r, show_cutaway=True, frame=240)
    set_cutaway_visibility(intact_r, cutaway_r, show_cutaway=True, frame=420)
    set_cutaway_visibility(intact_r, cutaway_r, show_cutaway=False, frame=421)

    # Full 1079-state mechanical QA verification
    def wpos(o):
        return o.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation

    def wxaxis(o):
        return (o.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.to_3x3() @ Vector((1.0, 0.0, 0.0))).normalized()

    max_pin_err_mm = max_axis_err_mm = max_link_err_mm = 0.0
    min_clear_mm = 9e9
    qa_rows = []
    for i, row in enumerate(rows):
        frame = i + 1
        for sub in ((0.0, 0.5) if i < len(rows) - 1 else (0.0,)):
            scene.frame_set(frame, subframe=sub)
            pb, ps, pk, pj = wpos(boom_pv), wpos(stick_pv), wpos(bucket_pv), wpos(knee_j)
            pside, pboss = wpos(refs["side_pv"]), wpos(refs["boss_pv"])

            link_err = max(
                abs((ps - pb).length - 5.700), abs((pk - ps).length - 2.925),
                abs((pj - pside).length - LINK_SIDE_M), abs((pj - pboss).length - LINK_H_M),
            )
            max_link_err_mm = max(max_link_err_mm, link_err * 1000.0)

            pin_err = 0.0
            if sub == 0.0:
                pin_err = max(
                    (Vector((ps.x, ps.z)) - Vector((row["boom_tip_x_mm"] * UNIT, row["boom_tip_z_mm"] * UNIT))).length,
                    (Vector((pk.x, pk.z)) - Vector((row["stick_tip_x_mm"] * UNIT, row["stick_tip_z_mm"] * UNIT))).length,
                    (Vector((pside.x, pside.z)) - Vector((row["bucket_side_x_mm"] * UNIT, row["bucket_side_z_mm"] * UNIT))).length,
                    (Vector((pboss.x, pboss.z)) - Vector((row["bucket_boss_x_mm"] * UNIT, row["bucket_boss_z_mm"] * UNIT))).length,
                )
                max_pin_err_mm = max(max_pin_err_mm, pin_err * 1000.0)
                min_clear_mm = min(min_clear_mm, row["bucket_clearance_mm"])

            axis_err = 0.0
            for cname, (base_p, eye_p, b_ax, r_ax, spec_k) in refs["cyl_checks"].items():
                pa, peye = wpos(base_p), wpos(eye_p)
                dist = (peye - pa).length
                sp = ACTUATOR_SPECS[spec_k]
                ext = dist - sp["closed"]
                if not (-GEOM_TOL_M <= ext <= sp["stroke"] + GEOM_TOL_M):
                    raise ValueError(f"Frame {frame}+{sub}: {cname} stroke violated ({ext:.4f} m)")
                axis_err = max(axis_err, (pa + wxaxis(b_ax) * dist - peye).length, (peye + wxaxis(r_ax) * dist - pa).length)
            for o in refs["metal_objs"]:
                if (Vector(o.scale) - Vector((1.0, 1.0, 1.0))).length > 1e-6:
                    raise ValueError(f"Metal stretch detected on {o.name}: {o.scale}")
            max_axis_err_mm = max(max_axis_err_mm, axis_err * 1000.0)
            if max(link_err, axis_err, pin_err) > GEOM_TOL_M:
                raise ValueError(f"QA fail at {frame}+{sub}: {link_err*1000:.4f} / {axis_err*1000:.4f} / {pin_err*1000:.4f}")
            qa_rows.append((frame, sub, round(pin_err * 1000, 6), round(link_err * 1000, 6), round(axis_err * 1000, 6)))

    with (qa_dir / "blender_animation_qa_v7_1.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(("frame", "subframe", "pin_dev_mm", "link_len_err_mm", "cyl_axis_err_mm"))
        w.writerows(qa_rows)

    summary = {
        "version": "V7.1",
        "states_checked": len(qa_rows),
        "max_pin_dev_mm": round(max_pin_err_mm, 6),
        "max_link_len_err_mm": round(max_link_err_mm, 6),
        "max_cyl_axis_err_mm": round(max_axis_err_mm, 6),
        "min_bucket_ground_clearance_mm": round(min_clear_mm, 4),
        "zero_metal_scaling_verified": True,
        "status": "BLENDER_V71_KINEMATICS_QA_PASS",
    }
    (qa_dir / "blender_vs_nx_v2_verification_v7_1.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("BLENDER_V71_QA_PASS:", summary)


def setup_animated_demo_camera(cam, target_empty):
    cam.animation_data_clear()
    cam.data.animation_data_clear()
    target_empty.animation_data_clear()

    c = cam.constraints.new("TRACK_TO")
    c.target = target_empty
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"

    # Match V7.0 frame pacing cleanly while refining angle/framing & DOF focus target
    beats = (
        (1,   (2.90, -12.40, 1.85), (3.15, 0.0, 0.72), 38.0),   # 0s: Wide hero 3/4 with I-beam plinth & falling soil
        (115, (2.85, -11.40, 1.95), (3.10, 0.0, 0.90), 40.0),   # ~4s: End establishing, ready for push
        (185, (2.55, -4.60, 1.25),  (1.55, -0.52, 0.65), 44.0),  # ~6s: Push onto twin chrome rods, bolts & gland
        (240, (2.10, -5.30, 0.48),  (1.25, -0.52, 0.32), 35.0),  # 8s: Full-cylinder Cutaway framing (Chốt A/B + Panel)
        (420, (2.00, -5.30, 0.65),  (1.18, -0.52, 0.48), 35.0),  # 14s: Smooth vertical track during powered lift
        (504, (2.95, -12.60, 2.35), (3.10, 0.0, 1.35), 38.0),   # 16.8s: Majestic return to wide hero HIGH
        (540, (3.00, -12.70, 2.38), (3.10, 0.0, 1.38), 38.0),   # 18s: Gentle hold settle
    )
    for frame, cloc, tloc, lens in beats:
        cam.location = cloc
        cam.keyframe_insert(data_path="location", frame=frame)
        cam.data.lens = lens
        cam.data.keyframe_insert(data_path="lens", frame=frame)
        target_empty.location = tloc
        target_empty.keyframe_insert(data_path="location", frame=frame)


def build_scene(args):
    global _TRACE_ROWS
    bpy.ops.wm.read_factory_settings(use_empty=False)
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)
    for blk in (bpy.data.meshes, bpy.data.cameras, bpy.data.lights, bpy.data.materials):
        for item in list(blk):
            if item.users == 0:
                blk.remove(item)

    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = FRAMES

    root_coll = scene.collection
    coll_stage = ensure_collection(root_coll, "01_Carrier_And_Stage")
    coll_boom = ensure_collection(root_coll, "02_Boom_Group")
    coll_stick = ensure_collection(root_coll, "03_Stick_Group")
    coll_bucket = ensure_collection(root_coll, "04_Bucket_Group")
    coll_cyl = ensure_collection(root_coll, "05_Hydraulic_Cylinders")
    coll_link = ensure_collection(root_coll, "06_FourBar_Linkage")
    coll_pins = ensure_collection(root_coll, "07_Pivot_Pins_13")
    coll_exp = ensure_collection(root_coll, "08_Exploded_Cylinder_Showcase")

    mats = build_v71_materials()
    stl_dir = WS_ROOT / "cad_exchange" / "stl"
    bolt_mesh_y = make_shared_hex_bolt_mesh(radius=0.011, height=0.010, axis="Y")
    bolt_mesh_x = make_shared_hex_bolt_mesh(radius=0.009, height=0.009, axis="X")
    bolt_mesh_z = make_shared_hex_bolt_mesh(radius=0.014, height=0.012, axis="Z")

    # 1. Carrier Mount & Industrial I-Beam Test Stand
    carrier_pv = make_empty("Carrier_Mount_Origin", coll_stage, location=(0.0, 0.0, 0.0))
    import_stl_part(stl_dir, "carrier_mount_reference.stl", "Carrier_Turret_Mount",
                    mats["dark_steel"], coll_stage, carrier_pv)
    build_industrial_stage_and_ibeam_plinth(coll_stage, carrier_pv, mats, bolt_mesh_y, bolt_mesh_z)

    # 2. Boom, Stick, Bucket + Secondary Payload Clods
    boom_pv = make_empty("Pivot_BoomBase", coll_boom, carrier_pv)
    m_boom_s = import_stl_part(stl_dir, "boom_structure.stl", "Boom_Structure", mats["yellow"], coll_boom, boom_pv)
    m_boom_b = import_stl_part(stl_dir, "boom_bosses.stl", "Boom_Machined_Bosses", mats["machined_steel"], coll_boom, boom_pv)

    stick_pv = make_empty("Pivot_BoomTip", coll_stick, boom_pv, location=(5.700, 0.0, 0.0))
    m_stick_s = import_stl_part(stl_dir, "stick_structure.stl", "Stick_Structure", mats["yellow"], coll_stick, stick_pv)
    m_stick_b = import_stl_part(stl_dir, "stick_bosses.stl", "Stick_Machined_Bosses", mats["machined_steel"], coll_stick, stick_pv)

    bucket_pv = make_empty("Pivot_StickTip", coll_bucket, stick_pv, location=(2.925, 0.0, 0.0))
    m_bkt_s = import_stl_part(stl_dir, "bucket_shell.stl", "Bucket_Shell", mats["bucket_steel"], coll_bucket, bucket_pv)
    m_bkt_w = import_stl_part(stl_dir, "bucket_wear_edges.stl", "Bucket_Wear_Edges", mats["dark_steel"], coll_bucket, bucket_pv)
    m_bkt_t = import_stl_part(stl_dir, "bucket_teeth.stl", "Bucket_Forged_Teeth", mats["forged_teeth"], coll_bucket, bucket_pv)
    clods = create_soil_mound_and_clods(coll_bucket, bucket_pv, coll_stage, mats)

    # 3. Four-Bar Bucket Linkage
    knee_j = make_empty("FourBar_Knee_J", coll_link, carrier_pv)
    side_pv = make_empty("FourBar_Side_Pivot", coll_link, stick_pv, location=(2.700, 0.0, 0.150))
    side_axis = make_empty("FourBar_Side_Axis", coll_link, side_pv)
    add_locked_track(side_axis, knee_j, "TRACK_X", "LOCK_Y")
    import_stl_part(stl_dir, "side_link_body.stl", "Side_Link_Straps", mats["yellow"], coll_link, side_axis)
    import_stl_part(stl_dir, "side_link_bosses.stl", "Side_Link_Bosses", mats["machined_steel"], coll_link, side_axis)

    boss_pv = make_empty("FourBar_Boss_Pivot", coll_link, bucket_pv, location=(0.1886, 0.0, -0.2075))
    h_axis = make_empty("FourBar_H_Axis", coll_link, boss_pv)
    add_locked_track(h_axis, knee_j, "TRACK_X", "LOCK_Y")
    import_stl_part(stl_dir, "h_link_body.stl", "H_Link_Body", mats["yellow"], coll_link, h_axis)
    import_stl_part(stl_dir, "h_link_bosses.stl", "H_Link_Bosses", mats["machined_steel"], coll_link, h_axis)

    # 4. Hydraulic Cylinders
    def build_cyl_pair(cname, spec_key, y_val, base_parent, base_loc, eye_parent, eye_loc):
        b_pv = make_empty(f"{cname}_BasePivot", coll_cyl, base_parent, location=(base_loc[0], y_val, base_loc[1]))
        e_pv = knee_j if eye_parent is None else make_empty(f"{cname}_RodEyePivot", coll_cyl, eye_parent, location=(eye_loc[0], y_val, eye_loc[1]))
        b_ax = make_empty(f"{cname}_BarrelAxis", coll_cyl, b_pv)
        add_locked_track(b_ax, e_pv, "TRACK_X", "LOCK_Y")
        r_ax = make_empty(f"{cname}_RodAxis", coll_cyl, e_pv)
        add_locked_track(r_ax, b_pv, "TRACK_X", "LOCK_Y")

        b_body = import_stl_part(stl_dir, f"{spec_key}_cylinder_barrel_body.stl", f"{cname}_Barrel_Body", mats["yellow"], coll_cyl, b_ax)
        b_gland = import_stl_part(stl_dir, f"{spec_key}_cylinder_barrel_gland.stl", f"{cname}_Barrel_Gland", mats["dark_steel"], coll_cyl, b_ax)
        b_ports = import_stl_part(stl_dir, f"{spec_key}_cylinder_barrel_ports.stl", f"{cname}_Barrel_Ports", mats["machined_steel"], coll_cyl, b_ax)
        r_chr = import_stl_part(stl_dir, f"{spec_key}_rod_chrome.stl", f"{cname}_Rod_Chrome", mats["chrome"], coll_cyl, r_ax)
        r_pis = import_stl_part(stl_dir, f"{spec_key}_rod_piston.stl", f"{cname}_Rod_Piston", mats["machined_steel"], coll_cyl, r_ax)
        r_eye = import_stl_part(stl_dir, f"{spec_key}_rod_eye.stl", f"{cname}_Rod_Eye", mats["dark_steel"], coll_cyl, r_ax)
        return b_pv, e_pv, b_ax, r_ax, [b_body, b_gland], r_pis, [b_body, b_gland, b_ports, r_chr, r_pis, r_eye]

    cyl_l_base, cyl_l_eye, cyl_l_bax, cyl_l_rax, _, _, cyl_l_objs = build_cyl_pair(
        "Boom_Cyl_L", "boom", +0.520, carrier_pv, (0.450, -0.850), boom_pv, (2.600, 0.220)
    )
    cyl_r_base, cyl_r_eye, cyl_r_bax, cyl_r_rax, intact_r_objs, r_pis_tpl, cyl_r_objs = build_cyl_pair(
        "Boom_Cyl_R", "boom", -0.520, carrier_pv, (0.450, -0.850), boom_pv, (2.600, 0.220)
    )
    arm_base, arm_eye, arm_bax, arm_rax, _, _, arm_objs = build_cyl_pair(
        "Arm_Cyl", "arm", 0.0, boom_pv, (3.5657, 0.9614), stick_pv, (-0.600, 0.0)
    )
    bkt_base, bkt_eye, bkt_bax, bkt_rax, _, _, bkt_objs = build_cyl_pair(
        "Bucket_Cyl", "bucket", 0.0, stick_pv, (0.500, 0.400), None, (0.0, 0.0)
    )

    # 5. All 13 Pivot Pins + Mechanical Bolt & Pipe Additions
    pin_specs = [
        ("PIN_BOOM_BASE", "pin_R64_L710.stl", boom_pv),
        ("PIN_BOOM_TIP", "pin_R60_L496.stl", stick_pv),
        ("PIN_STICK_TIP", "pin_R54_L476.stl", bucket_pv),
        ("PIN_BOOM_CYL_A_L", "pin_R42_L184.stl", cyl_l_base),
        ("PIN_BOOM_CYL_A_R", "pin_R42_L184.stl", cyl_r_base),
        ("PIN_BOOM_CYL_B_L", "pin_R42_L170.stl", cyl_l_eye),
        ("PIN_BOOM_CYL_B_R", "pin_R42_L170.stl", cyl_r_eye),
        ("PIN_ARM_CYL_A", "pin_R44_L256.stl", arm_base),
        ("PIN_ARM_CYL_B", "pin_R44_L344.stl", arm_eye),
        ("PIN_BUCKET_CYL_A", "pin_R40_L204.stl", bkt_base),
        ("PIN_BUCKET_SIDE", "pin_R38_L320.stl", side_pv),
        ("PIN_BUCKET_CYL_B", "pin_R38_L264.stl", knee_j),
        ("PIN_BUCKET_BOSS", "pin_R38_L470.stl", boss_pv),
    ]
    pin_map = {}
    pin_objs = []
    for pid, fname, pv in pin_specs:
        po = import_stl_part(stl_dir, fname, pid, mats["machined_steel"], coll_pins, pv)
        pin_map[pid] = po
        pin_objs.append(po)

    add_cinematic_bolt_and_pipe_details(
        coll_boom, coll_stick, coll_pins, boom_pv, stick_pv, pin_map,
        {"boom_r": cyl_r_bax, "boom_l": cyl_l_bax, "arm": arm_bax, "bucket": bkt_bax},
        mats, bolt_mesh_y, bolt_mesh_x
    )

    # 6. Load Trajectory & Set REACH pose cleanly to bind 3-Point Catenary Hoses
    rows = read_motion_trace(WS_ROOT / "animation" / "motion_trace_v3.csv")
    _TRACE_ROWS = rows
    reach_row = min(rows, key=lambda r: abs(r["boom_deg"] - 29.0) + abs(r["arm_rel_deg"] - 86.0))
    boom_pv.rotation_euler.y = -math.radians(reach_row["boom_abs_deg"])
    stick_pv.rotation_euler.y = math.radians(reach_row["arm_rel_deg"])
    bucket_pv.rotation_euler.y = math.radians(reach_row["bucket_rel_deg"] - 90.0)
    knee_j.location = (reach_row["bucket_cyl_B_x_mm"] * UNIT, 0.0, reach_row["bucket_cyl_B_z_mm"] * UNIT)
    bpy.context.view_layer.update()

    hose_specs = [
        ("Hose_BoomR_Supply", (-0.44, -0.34, -0.50), carrier_pv, (0.28, -0.08, 0.14), (0.04, -0.10, -0.18), (-0.18, 0.0, 0.14), (0.255, 0.0, 0.110), cyl_r_bax, 0.013, coll_boom),
        ("Hose_BoomR_Return", (-0.44, -0.26, -0.56), carrier_pv, (0.24, -0.06, 0.12), (0.04, -0.08, -0.15), (-0.16, 0.0, 0.12), (0.285, 0.04, 0.105), cyl_r_bax, 0.011, coll_boom),
        ("Hose_BoomL_Supply", (-0.44, 0.34, -0.50), carrier_pv, (0.28, 0.08, 0.14), (0.04, 0.10, -0.18), (-0.18, 0.0, 0.14), (0.255, 0.0, 0.110), cyl_l_bax, 0.013, coll_boom),
        ("Hose_Arm_Supply",   (3.18, -0.228, 1.07), boom_pv, (0.18, 0.05, 0.14), (0.0, -0.02, 0.11), (-0.16, -0.04, 0.14), (0.255, 0.0, 0.118), arm_bax, 0.012, coll_boom),
        ("Hose_Arm_Return",   (3.18, -0.228, 1.02), boom_pv, (0.16, 0.04, 0.11), (0.0, -0.01, 0.08), (-0.14, -0.03, 0.11), (0.295, 0.03, 0.114), arm_bax, 0.011, coll_boom),
        ("Hose_Bucket_Jump",  (0.22, -0.165, 0.31), stick_pv, (0.12, 0.02, 0.14), (0.06, -0.04, 0.06), (-0.12, -0.03, 0.12), (0.255, 0.0, 0.108), bkt_bax, 0.011, coll_stick),
    ]
    hoses_info = []
    for hname, p_s, a_s, c1, sag, c2, p_e, a_e, rad, col_h in hose_specs:
        h_tuple = create_catenary_hose(
            hname, p_s, a_s, c1, sag, c2, p_e, a_e, rad, mats["rubber_hose"], mats["machined_steel"], col_h
        )
        hoses_info.append(h_tuple)

    # 7. Cutaway Upgrade & Exploded Showcase
    cutaway_r_objs, cap_oil, rod_oil, gauge_fill = build_v71_cutaway_and_exploded(
        stl_dir, mats, coll_cyl, coll_exp, cyl_r_base, cyl_r_eye, cyl_r_bax, cyl_r_rax, r_pis_tpl,
        bolt_mesh_x=bolt_mesh_x
    )

    # Register live telemetry text handler cleanly
    bpy.app.handlers.frame_change_pre[:] = [h for h in bpy.app.handlers.frame_change_pre if h.__name__ != "_update_telemetry_text"]
    bpy.app.handlers.frame_change_pre.append(_update_telemetry_text)

    # 8. Lighting, DOF, Compositor & Cameras
    cam_target = make_empty("CAM_ANIM_TARGET", coll_stage, location=(3.15, 0.0, 0.72))
    setup_cinematic_lighting_dof_and_compositor(coll_stage, scene, cam_target)

    shot1_focus = make_empty("Focus_Shot1", coll_stage, location=(3.10, 0.0, 0.85))
    shot2_focus = make_empty("Focus_Shot2", coll_stage, location=(1.75, -0.52, 0.92))
    shot3_focus = make_empty("Focus_Shot3", coll_exp, location=(2.75, 28.0, 0.05))
    shot4_focus = make_empty("Focus_Shot4", coll_stage, location=(1.25, -0.52, 0.35))

    cam_shot1 = make_camera("CAM_SHOT01_HERO", (2.95, -12.60, 1.95), (3.15, 0.0, 0.85), 38.0, coll_stage, shot1_focus, fstop=5.6)
    cam_shot2 = make_camera("CAM_SHOT02_CLOSEUP", (2.75, -3.45, 1.48), (1.75, -0.52, 0.92), 46.0, coll_stage, shot2_focus, fstop=3.5)
    cam_shot3 = make_camera("CAM_SHOT03_EXPLODED", (2.75, 19.60, 1.85), (2.75, 28.0, 0.05), 34.0, coll_exp, shot3_focus, fstop=4.5)
    cam_shot4 = make_camera("CAM_SHOT04_CUTAWAY", (2.10, -5.30, 0.50), (1.25, -0.52, 0.35), 35.0, coll_stage, shot4_focus, fstop=4.0)
    cam_anim = make_camera("CAM_ANIM_DEMO", (2.90, -12.40, 1.85), (3.15, 0.0, 0.72), 38.0, coll_stage, cam_target, fstop=4.2)
    setup_animated_demo_camera(cam_anim, cam_target)

    # 9. Animate & Execute Strict 1079-State Verification
    metal_objs = [m_boom_s, m_boom_b, m_stick_s, m_stick_b, m_bkt_s, m_bkt_w, m_bkt_t]
    metal_objs.extend(cyl_l_objs + cyl_r_objs + arm_objs + bkt_objs + pin_objs)
    refs = {
        "boom_pv": boom_pv,
        "stick_pv": stick_pv,
        "bucket_pv": bucket_pv,
        "knee_j": knee_j,
        "side_pv": side_pv,
        "boss_pv": boss_pv,
        "metal_objs": metal_objs,
        "cyl_checks": {
            "boom_l": (cyl_l_base, cyl_l_eye, cyl_l_bax, cyl_l_rax, "boom"),
            "boom_r": (cyl_r_base, cyl_r_eye, cyl_r_bax, cyl_r_rax, "boom"),
            "arm":    (arm_base, arm_eye, arm_bax, arm_rax, "arm"),
            "bucket": (bkt_base, bkt_eye, bkt_bax, bkt_rax, "bucket"),
        },
    }
    animate_secondary_effects_and_verify(
        scene, rows, refs, cap_oil, rod_oil, gauge_fill, intact_r_objs, cutaway_r_objs,
        mats, hoses_info, clods, WS_ROOT / "qa"
    )

    return scene, {
        "shot1": cam_shot1, "shot2": cam_shot2, "shot3": cam_shot3, "shot4": cam_shot4,
        "anim": cam_anim, "intact_r": intact_r_objs, "cutaway_r": cutaway_r_objs, "coll_exp": coll_exp,
    }


def configure_clean_gui_viewport(scene):
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type != "VIEW_3D":
                continue
            for space in area.spaces:
                if space.type != "VIEW_3D":
                    continue
                if hasattr(space, "shading"):
                    space.shading.type = "MATERIAL"
                    if hasattr(space.shading, "use_scene_lights"):
                        space.shading.use_scene_lights = True
                    if hasattr(space.shading, "use_scene_world"):
                        space.shading.use_scene_world = True
                if hasattr(space, "overlay"):
                    for attr, val in (
                        ("show_extras", False), ("show_relationship_lines", False),
                        ("show_cursor", False), ("show_object_origins", False),
                        ("show_floor", False), ("show_axis_x", False), ("show_axis_y", False),
                    ):
                        if hasattr(space.overlay, attr):
                            setattr(space.overlay, attr, val)
                if hasattr(space, "region_3d") and space.region_3d is not None:
                    space.region_3d.view_location = Vector((3.15, 0.0, 0.85))
                    space.region_3d.view_distance = 8.2
                    space.region_3d.view_rotation = Euler((math.radians(74.0), 0.0, math.radians(16.0))).to_quaternion()
                    space.region_3d.view_perspective = "CAMERA"


def render_four_v71_stills(scene, ctx, samples):
    out_dir = WS_ROOT / "renders"
    out_dir.mkdir(parents=True, exist_ok=True)
    configure_render_engine(scene, engine="CYCLES", samples=samples)
    ctx["coll_exp"].hide_render = True
    ctx["coll_exp"].hide_viewport = True

    def snap(cam, frame_num, show_cut, filename):
        scene.camera = cam
        scene.frame_set(frame_num)
        _update_telemetry_text(scene)
        set_cutaway_visibility(ctx["intact_r"], ctx["cutaway_r"], show_cutaway=show_cut)
        t0 = time.monotonic()
        scene.render.filepath = str(out_dir / filename)
        bpy.ops.render.render(write_still=True)
        print(f"RENDERED_V71_STILL {filename} in {time.monotonic() - t0:.2f} s", flush=True)

    snap(ctx["shot1"], 175, False, "SHOT_01_V7_1.png")
    snap(ctx["shot2"], 175, False, "SHOT_02_V7_1.png")
    ctx["coll_exp"].hide_render = False
    ctx["coll_exp"].hide_viewport = False
    snap(ctx["shot3"], 175, False, "SHOT_03_V7_1.png")
    ctx["coll_exp"].hide_render = True
    ctx["coll_exp"].hide_viewport = True
    snap(ctx["shot4"], 331, True, "SHOT_04_V7_1.png")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("stills", "animate", "full", "build_only"), default="stills")
    parser.add_argument("--still-samples", type=int, default=72)
    parser.add_argument("--anim-engine", choices=("CYCLES", "BLENDER_EEVEE"), default="BLENDER_EEVEE")
    parser.add_argument("--anim-samples", type=int, default=24)
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    args = parser.parse_args(argv)

    scene, ctx = build_scene(args)
    blend_path = WS_ROOT / "blender_project" / "EP02_PC2008_V7_1_CINEMATIC.blend"

    def save_clean():
        ctx["coll_exp"].hide_render = True
        ctx["coll_exp"].hide_viewport = True
        configure_render_engine(scene, engine=args.anim_engine, samples=args.anim_samples)
        scene.camera = ctx["anim"]
        scene.frame_set(175)
        _update_telemetry_text(scene)
        bpy.ops.object.select_all(action="DESELECT")
        configure_clean_gui_viewport(scene)
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    save_clean()
    print("SAVED_V71_BLEND:", blend_path, flush=True)

    if args.mode in ("stills", "full"):
        render_four_v71_stills(scene, ctx, samples=args.still_samples)

    if args.mode in ("animate", "full"):
        ctx["coll_exp"].hide_render = True
        ctx["coll_exp"].hide_viewport = True
        set_cutaway_visibility(ctx["intact_r"], ctx["cutaway_r"], show_cutaway=False, frame=1)
        set_cutaway_visibility(ctx["intact_r"], ctx["cutaway_r"], show_cutaway=False, frame=239)
        set_cutaway_visibility(ctx["intact_r"], ctx["cutaway_r"], show_cutaway=True, frame=240)
        set_cutaway_visibility(ctx["intact_r"], ctx["cutaway_r"], show_cutaway=True, frame=420)
        set_cutaway_visibility(ctx["intact_r"], ctx["cutaway_r"], show_cutaway=False, frame=421)

        configure_render_engine(scene, engine=args.anim_engine, samples=args.anim_samples)
        scene.camera = ctx["anim"]
        frames_dir = WS_ROOT / "renders" / "frames_v7_1"
        frames_dir.mkdir(parents=True, exist_ok=True)
        scene.render.filepath = str(frames_dir / "ep02_v71_")
        t0 = time.monotonic()
        bpy.ops.render.render(animation=True)
        print(f"RENDERED_V71_ANIMATION_540_FRAMES in {time.monotonic() - t0:.2f} s", flush=True)
        save_clean()


if __name__ == "__main__":
    main()
