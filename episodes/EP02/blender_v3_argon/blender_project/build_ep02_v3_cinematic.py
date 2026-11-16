"""Blender 5.3 Cinematic Build, Mechanical Rigging, QA Verification, and Render Pipeline (EP02 V7 Argon V3).

Reads NX V2 tessellated binary STL sub-meshes from ../cad_exchange/stl/ and
MATLAB continuous motion trajectory from ../animation/motion_trace_v3.csv.
No external addons required. All paths resolved relative to workspace root.
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
from mathutils import Euler, Matrix, Vector

WS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WS_ROOT / "textures_materials"))
from materials_v3 import build_materials_library  # noqa: E402


FPS = 30
FRAMES = 540
UNIT = 0.001  # 1 mm -> 0.001 m (applied once on STL import)
GROUND_Z_M = -1.5849
GEOM_TOL_M = 0.00025  # 0.25 mm world invariant tolerance across all 1079 states

ACTUATOR_SPECS = {
    "boom": dict(closed=2.200, stroke=1.334, gland=2.080, rod_span=2.000, bore=0.120, rod=0.085),
    "arm": dict(closed=1.850, stroke=1.490, gland=1.730, rod_span=1.650, bore=0.135, rod=0.095),
    "bucket": dict(closed=1.700, stroke=1.120, gland=1.580, rod_span=1.500, bore=0.115, rod=0.080),
}
LINK_SIDE_M = 0.650
LINK_H_M = 0.750


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
            ang = e.link_faces[0].normal.angle(e.link_faces[1].normal, 0.0)
            e.smooth = (ang <= thresh)
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
    # Unlink from default scene collection if present
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


def create_box_mesh(name, x0, x1, y0, y1, z0, z1, material, coll, parent=None, bevel_m=0.004):
    bm = bmesh.new()
    v = [
        bm.verts.new((x0, y0, z0)), bm.verts.new((x1, y0, z0)),
        bm.verts.new((x1, y1, z0)), bm.verts.new((x0, y1, z0)),
        bm.verts.new((x0, y0, z1)), bm.verts.new((x1, y0, z1)),
        bm.verts.new((x1, y1, z1)), bm.verts.new((x0, y1, z1)),
    ]
    faces_idx = [
        (3, 2, 1, 0), (4, 5, 6, 7),
        (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
    ]
    for fi in faces_idx:
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


def create_cylinder_x(name, x0, x1, r_out, r_in, segments, material, coll, parent=None):
    """Create solid or annular cylinder along +X from x0 to x1 (unit length optional)."""
    bm = bmesh.new()
    verts_0_out = []
    verts_1_out = []
    for i in range(segments):
        a = i * math.tau / segments
        verts_0_out.append(bm.verts.new((x0, r_out * math.cos(a), r_out * math.sin(a))))
        verts_1_out.append(bm.verts.new((x1, r_out * math.cos(a), r_out * math.sin(a))))

    if r_in > 0.0:
        verts_0_in = []
        verts_1_in = []
        for i in range(segments):
            a = i * math.tau / segments
            verts_0_in.append(bm.verts.new((x0, r_in * math.cos(a), r_in * math.sin(a))))
            verts_1_in.append(bm.verts.new((x1, r_in * math.cos(a), r_in * math.sin(a))))
        for i in range(segments):
            j = (i + 1) % segments
            bm.faces.new((verts_0_out[i], verts_0_out[j], verts_1_out[j], verts_1_out[i]))
            bm.faces.new((verts_1_in[i], verts_1_in[j], verts_0_in[j], verts_0_in[i]))
            bm.faces.new((verts_0_in[i], verts_0_in[j], verts_0_out[j], verts_0_out[i]))
            bm.faces.new((verts_1_out[i], verts_1_out[j], verts_1_in[j], verts_1_in[i]))
    else:
        for i in range(segments):
            j = (i + 1) % segments
            bm.faces.new((verts_0_out[i], verts_0_out[j], verts_1_out[j], verts_1_out[i]))
        bm.faces.new(list(reversed(verts_0_out)))
        bm.faces.new(verts_1_out)

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


def create_cutaway_arc_shell_x(name, x0, x1, r_in, r_out, phi_start_deg, phi_end_deg,
                               mat_outer, mat_inner, mat_cut, coll, parent=None, segs=44):
    """Create a longitudinal sectioned annular cylinder along +X with 3 distinct material slots:
    0 = Outer Painted Shell, 1 = Honed Bore / Front-Back Rim, 2 = Section Cut Faces.
    Polar parameterization centered on -Y: y = -r * cos(phi), z = r * sin(phi).
    """
    bm = bmesh.new()
    angles = [
        math.radians(phi_start_deg + (phi_end_deg - phi_start_deg) * i / segs)
        for i in range(segs + 1)
    ]
    v_0_out = [bm.verts.new((x0, -r_out * math.cos(a), r_out * math.sin(a))) for a in angles]
    v_1_out = [bm.verts.new((x1, -r_out * math.cos(a), r_out * math.sin(a))) for a in angles]
    v_0_in = [bm.verts.new((x0, -r_in * math.cos(a), r_in * math.sin(a))) for a in angles]
    v_1_in = [bm.verts.new((x1, -r_in * math.cos(a), r_in * math.sin(a))) for a in angles]

    for i in range(segs):
        f_out = bm.faces.new((v_0_out[i], v_0_out[i + 1], v_1_out[i + 1], v_1_out[i]))
        f_out.material_index = 0
        f_out.smooth = True

        f_in = bm.faces.new((v_1_in[i], v_1_in[i + 1], v_0_in[i + 1], v_0_in[i]))
        f_in.material_index = 1
        f_in.smooth = True

        f_c0 = bm.faces.new((v_0_in[i], v_0_in[i + 1], v_0_out[i + 1], v_0_out[i]))
        f_c0.material_index = 2
        f_c0.smooth = False

        f_c1 = bm.faces.new((v_1_out[i], v_1_out[i + 1], v_1_in[i + 1], v_1_in[i]))
        f_c1.material_index = 2
        f_c1.smooth = False

    # The two longitudinal section faces (crimson-orange CAD cut faces)
    f_cut_a = bm.faces.new((v_0_out[0], v_1_out[0], v_1_in[0], v_0_in[0]))
    f_cut_a.material_index = 2
    f_cut_a.smooth = False

    f_cut_b = bm.faces.new((v_1_out[-1], v_0_out[-1], v_0_in[-1], v_1_in[-1]))
    f_cut_b.material_index = 2
    f_cut_b.smooth = False

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
    obj.data.materials.append(mat_outer)
    obj.data.materials.append(mat_inner)
    obj.data.materials.append(mat_cut)
    es = obj.modifiers.new("EdgeSplit", "EDGE_SPLIT")
    es.use_edge_angle = False
    es.use_edge_sharp = True
    return obj


def create_flow_arrow(name, length, shaft_r, head_r, mat, coll, parent=None, direction_z=-1.0):
    """Create crisp 3D engineering flow indicator arrow along Z."""
    bm = bmesh.new()
    segs = 18
    shaft_len = length * 0.62
    z0 = 0.0
    z1 = direction_z * shaft_len
    z2 = direction_z * length
    s0 = [bm.verts.new((shaft_r * math.cos(a * math.tau / segs), shaft_r * math.sin(a * math.tau / segs), z0)) for a in range(segs)]
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


def create_dynamic_hose(name, p_start_local, anchor_start, ctrl1_offset, ctrl2_offset,
                        p_end_local, anchor_end, radius, mat_hose, mat_ferrule, coll):
    """Create a true 3D curved hydraulic hose dynamically hooked to two moving rig anchors."""
    curve = bpy.data.curves.new(name + "_curve", "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = radius
    curve.bevel_resolution = 4
    curve.resolution_u = 20
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(1)

    mw_s = anchor_start.matrix_world
    mw_e = anchor_end.matrix_world
    ws = mw_s @ Vector(p_start_local)
    we = mw_e @ Vector(p_end_local)

    bp0, bp1 = spline.bezier_points[0], spline.bezier_points[1]
    bp0.co = ws
    bp0.handle_left_type = "FREE"
    bp0.handle_right_type = "FREE"
    bp0.handle_left = ws - Vector(ctrl1_offset) * 0.4
    bp0.handle_right = ws + Vector(ctrl1_offset)

    bp1.co = we
    bp1.handle_left_type = "FREE"
    bp1.handle_right_type = "FREE"
    bp1.handle_left = we + Vector(ctrl2_offset)
    bp1.handle_right = we - Vector(ctrl2_offset) * 0.4

    hose_obj = link_obj(bpy.data.objects.new(name, curve), coll)
    curve.materials.append(mat_hose)

    # Hook start vertices (point 0 + left/right handles -> index sequence: 0,1,2) & end (3,4,5)
    for hook_name, target_obj, indices in (
        ("HookStart", anchor_start, [0, 1, 2]),
        ("HookEnd", anchor_end, [3, 4, 5]),
    ):
        hm = hose_obj.modifiers.new(hook_name, "HOOK")
        hm.object = target_obj
        hm.vertex_indices_set(indices)

    # Add crimped steel ferrules rigidly mounted at start & end anchor ports
    for tag, anchor, loc in (("Start", anchor_start, p_start_local), ("End", anchor_end, p_end_local)):
        fer = create_cylinder_x(
            f"{name}_Ferrule_{tag}", -0.028, 0.028, radius * 1.48, 0.0, 16, mat_ferrule, coll, anchor
        )
        fer.location = loc
        fer.rotation_euler.y = math.pi * 0.5
    return hose_obj


def create_soil_mound(coll, parent_bucket, mat_soil):
    """Create irregular quarry soil payload resting cleanly inside bucket cavity (zero protruding)."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=0.38)
    for idx, v in enumerate(bm.verts):
        v.co.x *= 1.15
        v.co.y *= 1.05
        v.co.z *= 0.62
        # Deterministic natural gravel lump displacement
        n = 0.045 * math.sin(v.co.x * 11.3 + idx * 0.4) * math.cos(v.co.y * 9.7)
        v.co.x += n
        v.co.z += abs(n) * 0.8
    for f in bm.faces:
        f.smooth = True
    mesh = bpy.data.meshes.new("Bucket_Soil_Payload_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    obj = link_obj(bpy.data.objects.new("Bucket_Soil_Payload", mesh), coll, parent_bucket)
    obj.location = (-0.52, 0.0, -0.58)
    obj.data.materials.append(mat_soil)
    return obj


def build_stage_and_plinth(coll_stage, carrier_root, mats):
    """Build quarry testing ground at exact GROUND_Z and structural experimental stand under V2 Carrier."""
    # Large circular-blended industrial concrete/quarry ground plane at exact Z = -1.5849 m
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=24, y_segments=24, size=18.0)
    for v in bm.verts:
        # Gently slope up far backdrop cyclorama behind x < -5 or y > +6 so studio lighting sweeps clean
        dist = math.hypot(v.co.x - 2.0, v.co.y - 2.0)
        if v.co.y > 5.2:
            v.co.z += min(6.5, (v.co.y - 5.2) ** 1.7 * 0.14)
        elif dist > 11.5:
            v.co.z += (dist - 11.5) * 0.08
        v.co.z += GROUND_Z_M
    for f in bm.faces:
        f.smooth = True
    mesh = bpy.data.meshes.new("Industrial_Test_Bay_Floor")
    bm.to_mesh(mesh)
    bm.free()
    floor = link_obj(bpy.data.objects.new("Industrial_Test_Bay_Floor", mesh), coll_stage)
    floor.location = (2.5, 0.0, 0.0)
    floor.data.materials.append(mats["floor"])

    # Heavy structural test plinth supporting V2 carrier_mount_reference (which ends at z = -0.880 m)
    # Clearly represents a rigid test fixture anchoring the V2 attachment without inventing fake chassis!
    create_box_mesh("Test_Plinth_BasePlate", -1.15, 0.88, -0.78, 0.78, GROUND_Z_M, GROUND_Z_M + 0.075,
                    mats["test_stand"], coll_stage, carrier_root, bevel_m=0.008)
    for tag, y0, y1 in (("R", -0.56, -0.08), ("L", 0.08, 0.56)):
        create_box_mesh(f"Test_Plinth_Pedestal_{tag}", -0.44, 0.56, y0, y1, GROUND_Z_M + 0.075, -0.875,
                        mats["test_stand"], coll_stage, carrier_root, bevel_m=0.006)
    create_box_mesh("Test_Plinth_UpperDeck", -0.52, 0.62, -0.62, 0.62, -0.92, -0.875,
                    mats["dark_steel"], coll_stage, carrier_root, bevel_m=0.005)
    # Twin rear counterbalance block & hydraulic manifold header on test stand (clean visual counterweight!)
    create_box_mesh("Test_Plinth_Manifold_Block", -0.98, -0.45, -0.48, 0.48, GROUND_Z_M + 0.075, -0.42,
                    mats["test_stand"], coll_stage, carrier_root, bevel_m=0.012)
    create_box_mesh("Test_Plinth_Safety_Trim", -1.16, 0.89, -0.79, -0.75, GROUND_Z_M + 0.02, GROUND_Z_M + 0.068,
                    mats["yellow"], coll_stage, carrier_root, bevel_m=0.003)

    # Ground scale marker rail along X at ground grade (1 m graduations visually grounded)
    create_box_mesh("Grade_Reference_Rail", -0.50, 7.60, -1.35, -1.29, GROUND_Z_M, GROUND_Z_M + 0.018,
                    mats["machined_steel"], coll_stage, bevel_m=0.002)


def build_cutaway_and_exploded_assemblies(stl_dir: Path, mats, coll_cyl, coll_exploded,
                                          boom_cyl_r_barrel_axis, boom_cyl_r_rod_axis, boom_rod_piston_tpl):
    """Build precision sectioned cutaway shell + fluid columns on Boom_Cyl_R and coaxial Exploded Showcase."""
    spec = ACTUATOR_SPECS["boom"]
    cut_group = []

    # 1. Cutaway Shell for Boom_Cyl_R (window opens phi in [-48 deg, +56 deg] centered toward -Y!)
    shell = create_cutaway_arc_shell_x(
        "Boom_Cyl_R_Cutaway_Shell",
        0.140, spec["gland"], 0.060, 0.079, 56.0, 312.0,
        mats["yellow"], mats["machined_steel"], mats["cutaway_section"],
        coll_cyl, boom_cyl_r_barrel_axis
    )
    head_cut = create_cutaway_arc_shell_x(
        "Boom_Cyl_R_Cutaway_Head",
        0.113, 0.172, 0.001, 0.085, 56.0, 312.0,
        mats["dark_steel"], mats["machined_steel"], mats["cutaway_section"],
        coll_cyl, boom_cyl_r_barrel_axis
    )
    gland_cut = create_cutaway_arc_shell_x(
        "Boom_Cyl_R_Cutaway_Gland",
        spec["gland"] - 0.042, spec["gland"] + 0.028, 0.0439, 0.086, 56.0, 312.0,
        mats["dark_steel"], mats["machined_steel"], mats["cutaway_section"],
        coll_cyl, boom_cyl_r_barrel_axis
    )
    # Bronze piston wear band attached directly to Boom_Cyl_R_Rod_Axis matching NX Piston_land & wear ring
    piston_bronze = create_cylinder_x(
        "Boom_Cyl_R_Piston_BronzeGuide",
        spec["rod_span"] - 0.052, spec["rod_span"] - 0.041, 0.0592, 0.043, 36,
        mats["bronze_guide"], coll_cyl, boom_cyl_r_rod_axis
    )
    piston_seal = create_cylinder_x(
        "Boom_Cyl_R_Piston_VitonSeal",
        spec["rod_span"] - 0.082, spec["rod_span"] - 0.074, 0.0594, 0.043, 36,
        mats["rubber_hose"], coll_cyl, boom_cyl_r_rod_axis
    )

    # 2. Fluid Chambers inside Boom_Cyl_R_Barrel_Axis (unit-length cylinders scaled along X per frame!)
    # Cap chamber anchored at barrel inner closed head x = 0.172 m, extending in +X direction
    cap_oil = create_cylinder_x(
        "Boom_Cyl_R_CapOil_SupplyRed",
        0.0, 1.0, 0.0585, 0.0, 32,
        mats["oil_supply"], coll_cyl, boom_cyl_r_barrel_axis
    )
    cap_oil.location = (0.172, 0.0, 0.0)

    # Rod chamber anchored at barrel inner gland face x = 2.038 m, extending toward -X (scale.x along -1..0!)
    rod_oil = create_cylinder_x(
        "Boom_Cyl_R_RodOil_ReturnBlue",
        -1.0, 0.0, 0.0585, 0.0432, 32,
        mats["oil_return"], coll_cyl, boom_cyl_r_barrel_axis
    )
    rod_oil.location = (spec["gland"] - 0.042, 0.0, 0.0)

    # 3. 3D SAE Port Flow Arrows (Supply IN at base port x=0.255, Return OUT at gland port x=1.980)
    arr_in = create_flow_arrow(
        "Flow_Arrow_Supply_Red", 0.24, 0.011, 0.024, mats["oil_supply"],
        coll_cyl, boom_cyl_r_barrel_axis, direction_z=-1.0
    )
    arr_in.location = (0.255, 0.0, 0.37)

    arr_out = create_flow_arrow(
        "Flow_Arrow_Return_Blue", 0.24, 0.011, 0.024, mats["oil_return"],
        coll_cyl, boom_cyl_r_barrel_axis, direction_z=1.0
    )
    arr_out.location = (1.980, 0.0, 0.13)

    # 4. World-horizontal Technical Callout Banner tracking Boom_Cyl_R midpoint (placed in clean right open space)
    banner_anchor = make_empty("Cutaway_Banner_Anchor", coll_cyl, boom_cyl_r_barrel_axis, location=(1.10, 0.0, 0.0))
    banner = make_empty("Cutaway_Callout_Banner", coll_cyl, location=(1.25, -0.52, 0.45))
    c_loc = banner.constraints.new("COPY_LOCATION")
    c_loc.target = banner_anchor
    banner_text_holder = make_empty("Cutaway_Banner_Holder", coll_cyl, banner, location=(0.76, -0.12, -0.22))

    banner_card = create_box_mesh(
        "Cutaway_Banner_Glass", -0.05, 1.24, 0.02, 0.04, -0.17, 0.10,
        mats["hud_backing"], coll_cyl, banner_text_holder, bevel_m=0.004
    )

    font_data_h = bpy.data.curves.new("Cutaway_Header_Font", "FONT")
    font_data_h.body = "MẶT CẮT MINH HỌA · XI LANH NÂNG CẦN"
    font_data_h.size = 0.052
    font_data_h.align_x = "LEFT"
    hdr_obj = link_obj(bpy.data.objects.new("Cutaway_Header_Text", font_data_h), coll_cyl, banner_text_holder)
    hdr_obj.location = (0.0, -0.005, 0.025)
    hdr_obj.rotation_euler.x = math.pi * 0.5
    font_data_h.materials.append(mats["hud_gold"])

    font_data_s = bpy.data.curves.new("Cutaway_Sub_Font", "FONT")
    font_data_s.body = "ĐỎ: Dầu cấp khoang đáy (đẩy piston)\nXANH: Dầu hồi khoang ty (ra cửa trên)"
    font_data_s.size = 0.038
    font_data_s.align_x = "LEFT"
    sub_obj = link_obj(bpy.data.objects.new("Cutaway_Sub_Text", font_data_s), coll_cyl, banner_text_holder)
    sub_obj.location = (0.0, -0.005, -0.045)
    sub_obj.rotation_euler.x = math.pi * 0.5
    font_data_s.materials.append(mats["hud_white"])

    cut_group.extend([shell, head_cut, gland_cut, cap_oil, rod_oil, arr_in, arr_out, banner_card, hdr_obj, sub_obj])

    # --- Isolated Coaxial Exploded Cylinder Showcase for SHOT 03 (clean studio bay at Y = +28.0 m) ---
    exp_origin = make_empty("Exploded_Showcase_Origin", coll_exploded, location=(0.0, 28.0, 0.0))
    create_box_mesh("Exploded_Studio_Floor", -4.0, 9.5, -6.0, 6.0, -0.60, -0.34,
                    mats["floor"], coll_exploded, exp_origin, bevel_m=0.0)
    create_box_mesh("Exploded_Display_Bench", -0.80, 6.30, -0.72, 0.72, -0.34, -0.24,
                    mats["test_stand"], coll_exploded, exp_origin, bevel_m=0.008)
    create_cylinder_x("Exploded_Centerline_Axis", -0.58, 6.08, 0.004, 0.0, 12,
                      mats["hud_gold"], coll_exploded, exp_origin)

    # Components exploded coaxially left -> right in true assembly mating sequence
    exp_pin_a = import_stl_part(stl_dir, "pin_R42_L184.stl", "Exploded_01_Pin_Base_A",
                                mats["machined_steel"], coll_exploded, exp_origin)
    exp_pin_a.location = (-0.35, 0.0, 0.0)

    exp_barrel = import_stl_part(stl_dir, "boom_cylinder_barrel_body.stl", "Exploded_02_Barrel_Tube",
                                 mats["yellow"], coll_exploded, exp_origin)
    exp_barrel.location = (0.0, 0.0, 0.0)

    exp_ports = import_stl_part(stl_dir, "boom_cylinder_barrel_ports.stl", "Exploded_03_SAE_Ports_FeedLine",
                                mats["machined_steel"], coll_exploded, exp_origin)
    exp_ports.location = (0.0, 0.0, 0.28)  # Offset cleanly upward to expose port seating

    # Piston enters barrel first (world 2.38..2.46 m), followed by Gland Collar (2.82..2.89 m), then Chrome Rod
    exp_piston = instance_stl_mesh(boom_rod_piston_tpl, "Exploded_04_Piston_Head",
                                   mats["machined_steel"], coll_exploded, exp_origin)
    exp_piston.rotation_euler.z = math.pi
    exp_piston.location = (4.38, 0.0, 0.0)  # Local piston 1.92..2.00 rotated -> world 2.38..2.46 m
    create_cylinder_x("Exploded_04_Bronze_Wear_Band", spec["rod_span"] - 0.052, spec["rod_span"] - 0.041,
                      0.0596, 0.043, 36, mats["bronze_guide"], coll_exploded, exp_piston)

    exp_gland = import_stl_part(stl_dir, "boom_cylinder_barrel_gland.stl", "Exploded_05_Gland_Seal_Collar",
                                mats["dark_steel"], coll_exploded, exp_origin)
    exp_gland.location = (0.78, 0.0, 0.0)  # Gland local X ~ 2.04..2.11 -> sits cleanly at 2.82..2.89 m

    exp_chrome = import_stl_part(stl_dir, "boom_rod_chrome.stl", "Exploded_06_Chrome_Piston_Rod",
                                 mats["chrome"], coll_exploded, exp_origin)
    exp_chrome.rotation_euler.z = math.pi
    exp_chrome.location = (5.22, 0.0, 0.0)  # Local shaft 0.10..2.00 rotated -> world 3.22..5.12 m

    exp_eye = import_stl_part(stl_dir, "boom_rod_eye.stl", "Exploded_07_Forged_Rod_Eye",
                              mats["dark_steel"], coll_exploded, exp_origin)
    exp_eye.rotation_euler.z = math.pi
    exp_eye.location = (5.45, 0.0, 0.0)    # Eye sits cleanly at 5.31..5.52 m

    exp_pin_b = import_stl_part(stl_dir, "pin_R42_L170.stl", "Exploded_08_Pin_Rod_B",
                                mats["machined_steel"], coll_exploded, exp_origin)
    exp_pin_b.location = (5.82, 0.0, 0.0)

    return cut_group, cap_oil, rod_oil, exp_origin


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


def setup_cinematic_lighting_and_world(coll_stage, scene):
    world = bpy.data.worlds.new("Industrial_Proving_Sky")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 0.85

    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.045, 0.055, 0.072, 1.0)
    e_mid = ramp.color_ramp.elements.new(0.49)
    e_mid.color = (0.16, 0.19, 0.24, 1.0)
    ramp.color_ramp.elements[2].position = 0.72
    ramp.color_ramp.elements[2].color = (0.28, 0.34, 0.42, 1.0)
    nt.links.new(tc.outputs["Generated"], sep.inputs["Vector"])
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

    def add_area(name, loc, target, energy, color, size, size_y=None):
        ld = bpy.data.lights.new(name, "AREA")
        ld.energy = energy
        ld.color = color
        if size_y is not None:
            ld.shape = "RECTANGLE"
            ld.size = size
            ld.size_y = size_y
        else:
            ld.shape = "DISK"
            ld.size = size
        lo = link_obj(bpy.data.objects.new(name, ld), coll_stage)
        lo.location = loc
        lo.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        return lo

    # Three-point cinematic lighting for hero excavator work attachment
    add_area("Key_Warm_Sunlight", (-2.5, -8.8, 7.6), (3.4, 0.0, 0.6), 4600.0, (1.0, 0.88, 0.74), 4.2)
    add_area("Fill_Cool_SkyBay", (9.2, -7.2, 3.2), (3.6, 0.0, 0.8), 1850.0, (0.68, 0.82, 1.0), 7.5)
    add_area("Rim_Steel_EdgeLight", (4.5, 6.2, 6.4), (3.0, 0.0, 1.2), 3400.0, (1.0, 0.94, 0.86), 5.5)
    add_area("Undercarriage_Fill", (5.5, -4.5, -1.2), (4.8, 0.0, 0.1), 520.0, (0.78, 0.86, 0.96), 4.0)

    # Dedicated clean gallery lighting over Exploded View bench at Y = +28.0 m
    add_area("Exploded_Key", (1.2, 23.5, 3.6), (2.0, 28.0, 0.0), 1400.0, (1.0, 0.94, 0.88), 3.8)
    add_area("Exploded_Fill", (5.2, 24.5, 2.2), (2.0, 28.0, 0.0), 650.0, (0.72, 0.84, 1.0), 4.0)
    add_area("Exploded_Rim", (2.2, 31.8, 3.2), (2.0, 28.0, 0.0), 1100.0, (0.85, 0.92, 1.0), 4.2)


def make_camera(name, loc, target, lens_mm, coll, clip_end=120.0):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens_mm
    cd.clip_start = 0.05
    cd.clip_end = clip_end
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
        raise ValueError(f"Expected {FRAMES} motion rows, found {len(rows)}")
    return rows


def animate_and_verify(scene, rows, refs, cap_oil, rod_oil, intact_r_objs, cutaway_r_objs, qa_dir: Path):
    boom_pv = refs["boom_pv"]
    stick_pv = refs["stick_pv"]
    bucket_pv = refs["bucket_pv"]
    knee_j = refs["knee_j"]

    for obj in (boom_pv, stick_pv, bucket_pv, knee_j, cap_oil, rod_oil):
        obj.animation_data_clear()

    # Animate every single frame cleanly from MATLAB trace
    for frame, row in enumerate(rows, 1):
        boom_pv.rotation_euler.y = -math.radians(row["boom_abs_deg"])
        stick_pv.rotation_euler.y = math.radians(row["arm_rel_deg"])
        bucket_pv.rotation_euler.y = math.radians(row["bucket_rel_deg"] - 90.0)

        boom_pv.keyframe_insert(data_path="rotation_euler", index=1, frame=frame)
        stick_pv.keyframe_insert(data_path="rotation_euler", index=1, frame=frame)
        bucket_pv.keyframe_insert(data_path="rotation_euler", index=1, frame=frame)

        knee_j.location = (row["bucket_cyl_B_x_mm"] * UNIT, 0.0, row["bucket_cyl_B_z_mm"] * UNIT)
        knee_j.keyframe_insert(data_path="location", frame=frame)

        # Update cutaway oil column X lengths identically to NX chamber walls (never stretch metal!)
        L_m = row["boom_cyl_length_mm"] * UNIT
        cap_len = L_m - 2.172
        rod_len = 3.956 - L_m
        cap_oil.scale = (max(0.05, cap_len), 1.0, 1.0)
        rod_oil.scale = (max(0.05, rod_len), 1.0, 1.0)
        cap_oil.keyframe_insert(data_path="scale", index=0, frame=frame)
        rod_oil.keyframe_insert(data_path="scale", index=0, frame=frame)

    # Toggle cutaway visibility cleanly for 8-14s segment (Frames 240 .. 420)
    set_cutaway_visibility(intact_r_objs, cutaway_r_objs, show_cutaway=False, frame=1)
    set_cutaway_visibility(intact_r_objs, cutaway_r_objs, show_cutaway=False, frame=239)
    set_cutaway_visibility(intact_r_objs, cutaway_r_objs, show_cutaway=True, frame=240)
    set_cutaway_visibility(intact_r_objs, cutaway_r_objs, show_cutaway=True, frame=420)
    set_cutaway_visibility(intact_r_objs, cutaway_r_objs, show_cutaway=False, frame=421)

    # Full 1079-state mechanical QA audit (540 frames + 539 subframes)
    def wpos(obj):
        deps = bpy.context.evaluated_depsgraph_get()
        return obj.evaluated_get(deps).matrix_world.translation

    def wxaxis(obj):
        deps = bpy.context.evaluated_depsgraph_get()
        return (obj.evaluated_get(deps).matrix_world.to_3x3() @ Vector((1.0, 0.0, 0.0))).normalized()

    max_pin_err_mm = 0.0
    max_axis_err_mm = 0.0
    max_link_err_mm = 0.0
    min_clear_mm = 9e9

    qa_rows = []
    for i, row in enumerate(rows):
        frame = i + 1
        for sub in ((0.0, 0.5) if i < len(rows) - 1 else (0.0,)):
            scene.frame_set(frame, subframe=sub)
            pb = wpos(boom_pv)
            ps = wpos(stick_pv)
            pk = wpos(bucket_pv)
            pj = wpos(knee_j)
            pside = wpos(refs["side_pv"])
            pboss = wpos(refs["boss_pv"])

            e_boom_len = abs((ps - pb).length - 5.700)
            e_stick_len = abs((pk - ps).length - 2.925)
            e_side = abs((pj - pside).length - LINK_SIDE_M)
            e_h = abs((pj - pboss).length - LINK_H_M)
            link_err = max(e_boom_len, e_stick_len, e_side, e_h)
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
                    raise ValueError(f"Frame {frame}+{sub}: {cname} stroke out of bounds ({ext:.4f} m)")
                ae1 = (pa + wxaxis(b_ax) * dist - peye).length
                ae2 = (peye + wxaxis(r_ax) * dist - pa).length
                axis_err = max(axis_err, ae1, ae2)
                # Ensure zero metal stretch
                for o in refs["metal_objs"]:
                    if (Vector(o.scale) - Vector((1.0, 1.0, 1.0))).length > 1e-6:
                        raise ValueError(f"Non-unit metal scale detected on {o.name}: {o.scale}")
            max_axis_err_mm = max(max_axis_err_mm, axis_err * 1000.0)

            if max(link_err, axis_err, pin_err) > GEOM_TOL_M:
                raise ValueError(
                    f"QA tolerance exceeded at frame {frame}+{sub}: link={link_err*1000:.4f} axis={axis_err*1000:.4f} pin={pin_err*1000:.4f} mm"
                )
            qa_rows.append((frame, sub, round(pin_err * 1000, 6), round(link_err * 1000, 6), round(axis_err * 1000, 6)))

    qa_csv = qa_dir / "blender_animation_qa_v3.csv"
    with qa_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(("frame", "subframe", "pin_dev_mm", "link_len_err_mm", "cyl_axis_err_mm"))
        w.writerows(qa_rows)

    summary = {
        "states_checked": len(qa_rows),
        "max_pin_dev_mm": round(max_pin_err_mm, 6),
        "max_link_len_err_mm": round(max_link_err_mm, 6),
        "max_cyl_axis_err_mm": round(max_axis_err_mm, 6),
        "min_bucket_ground_clearance_mm": round(min_clear_mm, 4),
        "zero_metal_scaling_verified": True,
        "status": "BLENDER_KINEMATICS_QA_PASS",
    }
    (qa_dir / "blender_vs_nx_v2_verification.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("BLENDER_QA_PASS:", summary)


def setup_animated_demo_camera(cam, target_empty):
    """Animate cinematic camera + aim target smoothly through 0-4s -> 4-8s -> 8-14s -> 14-18s."""
    cam.animation_data_clear()
    cam.data.animation_data_clear()
    target_empty.animation_data_clear()

    c = cam.constraints.new("TRACK_TO")
    c.target = target_empty
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"

    # (frame, cam_loc, target_loc, lens_mm)
    beats = (
        (1,   (2.90, -12.40, 1.85), (3.15, 0.0, 0.72), 38.0),   # 0s: Full wide hero 3/4 establishing
        (115, (2.85, -11.40, 1.95), (3.10, 0.0, 0.90), 40.0),   # ~4s: End establishing before push
        (185, (2.55, -4.60, 1.25),  (1.55, -0.52, 0.65), 44.0),  # ~6s: Pushing onto Boom_Cyl_R & gland/ports
        (240, (2.10, -5.30, 0.48),  (1.25, -0.52, 0.32), 35.0),  # 8s: Full-cylinder Cutaway framing (both chambers!)
        (420, (2.00, -5.30, 0.65),  (1.18, -0.52, 0.48), 35.0),  # 14s: Tracks upward lift cleanly in Cutaway
        (504, (2.95, -12.60, 2.35), (3.10, 0.0, 1.35), 38.0),   # 16.8s: Smooth pull back for finale HIGH
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

    mats = build_materials_library()
    stl_dir = WS_ROOT / "cad_exchange" / "stl"

    # --- 1. Carrier Mount & Industrial Test Stand ---
    carrier_pv = make_empty("Carrier_Mount_Origin", coll_stage, location=(0.0, 0.0, 0.0))
    import_stl_part(stl_dir, "carrier_mount_reference.stl", "Carrier_Turret_Mount",
                    mats["dark_steel"], coll_stage, carrier_pv)
    build_stage_and_plinth(coll_stage, carrier_pv, mats)

    # --- 2. Main Linkage Empties & Sub-Meshes ---
    boom_pv = make_empty("Pivot_BoomBase", coll_boom, carrier_pv, location=(0.0, 0.0, 0.0))
    m_boom_s = import_stl_part(stl_dir, "boom_structure.stl", "Boom_Structure", mats["yellow"], coll_boom, boom_pv)
    m_boom_b = import_stl_part(stl_dir, "boom_bosses.stl", "Boom_Machined_Bosses", mats["machined_steel"], coll_boom, boom_pv)
    # Side hydraulic steel pipes & bolted clamps along Boom spine (y = -0.222 m facing camera cleanly)
    pipe_pts = [(0.55, -0.222, 0.34), (1.66, -0.222, 0.88), (2.48, -0.222, 1.07), (3.18, -0.222, 1.05)]
    for line_idx, dz in enumerate((-0.025, 0.025), 1):
        pcurve = bpy.data.curves.new(f"Boom_Steel_Line_{line_idx}_crv", "CURVE")
        pcurve.dimensions = "3D"
        pcurve.bevel_depth = 0.013
        pcurve.bevel_resolution = 4
        sp = pcurve.splines.new("POLY")
        sp.points.add(len(pipe_pts) - 1)
        for pt, coord in zip(sp.points, pipe_pts):
            pt.co = (coord[0], coord[1], coord[2] + dz, 1.0)
        pobj = link_obj(bpy.data.objects.new(f"Boom_Steel_Line_{line_idx}", pcurve), coll_boom, boom_pv)
        pcurve.materials.append(mats["machined_steel"])
    for idx, (cx, cz) in enumerate(((0.85, 0.49), (1.66, 0.88), (2.48, 1.07), (3.12, 1.05)), 1):
        create_box_mesh(f"Boom_Pipe_Clamp_{idx}", cx - 0.028, cx + 0.028, -0.242, -0.205, cz - 0.055, cz + 0.055,
                        mats["dark_steel"], coll_boom, boom_pv, bevel_m=0.002)

    stick_pv = make_empty("Pivot_BoomTip", coll_stick, boom_pv, location=(5.700, 0.0, 0.0))
    m_stick_s = import_stl_part(stl_dir, "stick_structure.stl", "Stick_Structure", mats["yellow"], coll_stick, stick_pv)
    m_stick_b = import_stl_part(stl_dir, "stick_bosses.stl", "Stick_Machined_Bosses", mats["machined_steel"], coll_stick, stick_pv)

    bucket_pv = make_empty("Pivot_StickTip", coll_bucket, stick_pv, location=(2.925, 0.0, 0.0))
    m_bkt_s = import_stl_part(stl_dir, "bucket_shell.stl", "Bucket_Shell", mats["bucket_steel"], coll_bucket, bucket_pv)
    m_bkt_w = import_stl_part(stl_dir, "bucket_wear_edges.stl", "Bucket_Wear_Edges", mats["dark_steel"], coll_bucket, bucket_pv)
    m_bkt_t = import_stl_part(stl_dir, "bucket_teeth.stl", "Bucket_Forged_Teeth", mats["forged_teeth"], coll_bucket, bucket_pv)
    create_soil_mound(coll_bucket, bucket_pv, mats["soil"])

    # --- 3. Four-Bar Bucket Linkage ---
    knee_j = make_empty("FourBar_Knee_J", coll_link, carrier_pv, location=(0.0, 0.0, 0.0))
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

    # --- 4. All 4 Hydraulic Cylinders ---
    # Import templates once then instance for twin Boom cylinders cleanly
    def build_cyl_pair(cname, spec_key, y_val, base_parent, base_loc, eye_parent, eye_loc, is_cutaway_target=False):
        b_pv = make_empty(f"{cname}_BasePivot", coll_cyl, base_parent, location=(base_loc[0], y_val, base_loc[1]))
        if eye_parent is None:
            e_pv = knee_j
        else:
            e_pv = make_empty(f"{cname}_RodEyePivot", coll_cyl, eye_parent, location=(eye_loc[0], y_val, eye_loc[1]))
        b_ax = make_empty(f"{cname}_BarrelAxis", coll_cyl, b_pv)
        add_locked_track(b_ax, e_pv, "TRACK_X", "LOCK_Y")
        r_ax = make_empty(f"{cname}_RodAxis", coll_cyl, e_pv)
        add_locked_track(r_ax, b_pv, "TRACK_X", "LOCK_Y")

        b_body = import_stl_part(stl_dir, f"{spec_key}_cylinder_barrel_body.stl", f"{cname}_Barrel_Body",
                                 mats["yellow"], coll_cyl, b_ax)
        b_gland = import_stl_part(stl_dir, f"{spec_key}_cylinder_barrel_gland.stl", f"{cname}_Barrel_Gland",
                                  mats["dark_steel"], coll_cyl, b_ax)
        b_ports = import_stl_part(stl_dir, f"{spec_key}_cylinder_barrel_ports.stl", f"{cname}_Barrel_Ports",
                                  mats["machined_steel"], coll_cyl, b_ax)
        r_chr = import_stl_part(stl_dir, f"{spec_key}_rod_chrome.stl", f"{cname}_Rod_Chrome",
                                mats["chrome"], coll_cyl, r_ax)
        r_pis = import_stl_part(stl_dir, f"{spec_key}_rod_piston.stl", f"{cname}_Rod_Piston",
                                mats["machined_steel"], coll_cyl, r_ax)
        r_eye = import_stl_part(stl_dir, f"{spec_key}_rod_eye.stl", f"{cname}_Rod_Eye",
                                mats["dark_steel"], coll_cyl, r_ax)
        return b_pv, e_pv, b_ax, r_ax, [b_body, b_gland], r_pis, [b_body, b_gland, b_ports, r_chr, r_pis, r_eye]

    cyl_l_base, cyl_l_eye, cyl_l_bax, cyl_l_rax, _, _, cyl_l_objs = build_cyl_pair(
        "Boom_Cyl_L", "boom", +0.520, carrier_pv, (0.450, -0.850), boom_pv, (2.600, 0.220)
    )
    cyl_r_base, cyl_r_eye, cyl_r_bax, cyl_r_rax, intact_r_objs, r_pis_tpl, cyl_r_objs = build_cyl_pair(
        "Boom_Cyl_R", "boom", -0.520, carrier_pv, (0.450, -0.850), boom_pv, (2.600, 0.220), is_cutaway_target=True
    )
    arm_base, arm_eye, arm_bax, arm_rax, _, _, arm_objs = build_cyl_pair(
        "Arm_Cyl", "arm", 0.0, boom_pv, (3.5657, 0.9614), stick_pv, (-0.600, 0.0)
    )
    bkt_base, bkt_eye, bkt_bax, bkt_rax, _, _, bkt_objs = build_cyl_pair(
        "Bucket_Cyl", "bucket", 0.0, stick_pv, (0.500, 0.400), None, (0.0, 0.0)
    )

    # --- 5. All 13 Physical Pivot Pins mounted cleanly onto Joint Pivots ---
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
    pin_objs = [import_stl_part(stl_dir, fname, pid, mats["machined_steel"], coll_pins, pv) for pid, fname, pv in pin_specs]

    # --- 6. Dynamic Flexible Hydraulic Hoses ---
    # Set frame pose at REACH temporarily before adding hooks so hook bind transforms sit nicely mid-stroke
    rows = read_motion_trace(WS_ROOT / "animation" / "motion_trace_v3.csv")
    reach_row = min(rows, key=lambda r: abs(r["boom_deg"] - 29.0) + abs(r["arm_rel_deg"] - 86.0))
    boom_pv.rotation_euler.y = -math.radians(reach_row["boom_abs_deg"])
    stick_pv.rotation_euler.y = math.radians(reach_row["arm_rel_deg"])
    bucket_pv.rotation_euler.y = math.radians(reach_row["bucket_rel_deg"] - 90.0)
    knee_j.location = (reach_row["bucket_cyl_B_x_mm"] * UNIT, 0.0, reach_row["bucket_cyl_B_z_mm"] * UNIT)
    bpy.context.view_layer.update()

    create_dynamic_hose(
        "Hose_Boom_R_Supply", (-0.45, -0.32, -0.56), carrier_pv, (0.35, -0.10, 0.25), (-0.28, 0.0, 0.22),
        (0.255, 0.0, 0.110), cyl_r_bax, 0.014, mats["rubber_hose"], mats["machined_steel"], coll_boom
    )
    create_dynamic_hose(
        "Hose_Boom_L_Supply", (-0.45, 0.32, -0.56), carrier_pv, (0.35, 0.10, 0.25), (-0.28, 0.0, 0.22),
        (0.255, 0.0, 0.110), cyl_l_bax, 0.014, mats["rubber_hose"], mats["machined_steel"], coll_boom
    )
    create_dynamic_hose(
        "Hose_Arm_Cyl_Jump", (3.18, -0.222, 1.075), boom_pv, (0.20, 0.05, 0.22), (-0.20, -0.05, 0.24),
        (0.255, 0.0, 0.118), arm_bax, 0.013, mats["rubber_hose"], mats["machined_steel"], coll_boom
    )
    create_dynamic_hose(
        "Hose_Bucket_Cyl_Jump", (0.18, -0.08, 0.36), stick_pv, (0.14, 0.02, 0.20), (-0.16, -0.04, 0.18),
        (0.255, 0.0, 0.108), bkt_bax, 0.012, mats["rubber_hose"], mats["machined_steel"], coll_stick
    )

    # --- 7. Cutaway Housing & Exploded Cylinder Showcase ---
    cutaway_r_objs, cap_oil, rod_oil, exp_origin = build_cutaway_and_exploded_assemblies(
        stl_dir, mats, coll_cyl, coll_exp, cyl_r_bax, cyl_r_rax, r_pis_tpl
    )

    # --- 8. Lighting & Cameras ---
    setup_cinematic_lighting_and_world(coll_stage, scene)
    cam_shot1 = make_camera("CAM_SHOT01_HERO", (2.95, -12.60, 1.95), (3.15, 0.0, 0.85), 38.0, coll_stage)
    cam_shot2 = make_camera("CAM_SHOT02_CLOSEUP", (2.75, -3.45, 1.48), (1.75, -0.52, 0.92), 46.0, coll_stage)
    cam_shot3 = make_camera("CAM_SHOT03_EXPLODED", (2.75, 19.60, 1.85), (2.75, 28.0, 0.05), 34.0, coll_exp)
    cam_shot4 = make_camera("CAM_SHOT04_CUTAWAY", (2.10, -5.30, 0.50), (1.25, -0.52, 0.35), 35.0, coll_stage)
    cam_target = make_empty("CAM_ANIM_TARGET", coll_stage, location=(3.15, 0.0, 0.72))
    cam_anim = make_camera("CAM_ANIM_DEMO", (2.90, -12.40, 1.85), (3.15, 0.0, 0.72), 38.0, coll_stage)
    setup_animated_demo_camera(cam_anim, cam_target)

    # --- 9. Apply Motion & Execute Strict 1079-State Kinematics Verification ---
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
    animate_and_verify(scene, rows, refs, cap_oil, rod_oil, intact_r_objs, cutaway_r_objs, WS_ROOT / "qa")

    return scene, {
        "shot1": cam_shot1,
        "shot2": cam_shot2,
        "shot3": cam_shot3,
        "shot4": cam_shot4,
        "anim": cam_anim,
        "intact_r": intact_r_objs,
        "cutaway_r": cutaway_r_objs,
        "coll_exp": coll_exp,
        "rows": rows,
    }


def render_four_hero_stills(scene, ctx, samples):
    out_dir = WS_ROOT / "renders"
    out_dir.mkdir(parents=True, exist_ok=True)
    configure_render_engine(scene, engine="CYCLES", samples=samples)

    # Hide cutaway initially, frame 175 = exact REACH pose (~5.8s)
    ctx["coll_exp"].hide_render = True
    ctx["coll_exp"].hide_viewport = True

    def snap(cam, frame_num, show_cut, filename):
        scene.camera = cam
        scene.frame_set(frame_num)
        set_cutaway_visibility(ctx["intact_r"], ctx["cutaway_r"], show_cutaway=show_cut)
        t0 = time.monotonic()
        scene.render.filepath = str(out_dir / filename)
        bpy.ops.render.render(write_still=True)
        print(f"RENDERED_STILL {filename} in {time.monotonic() - t0:.2f} s", flush=True)

    # SHOT 01: Hero 3/4 at REACH pose (frame 175)
    snap(ctx["shot1"], 175, False, "SHOT_01_HERO_MECHANICAL_ASSEMBLY.png")
    # SHOT 02: Hydraulic Cylinder Close-up at REACH pose (frame 175)
    snap(ctx["shot2"], 175, False, "SHOT_02_HYDRAULIC_CYLINDER_CLOSEUP.png")
    # SHOT 03: Exploded Engineering View (isolated showcase bench)
    ctx["coll_exp"].hide_render = False
    ctx["coll_exp"].hide_viewport = False
    snap(ctx["shot3"], 175, False, "SHOT_03_EXPLODED_ENGINEERING_VIEW.png")
    ctx["coll_exp"].hide_render = True
    ctx["coll_exp"].hide_viewport = True
    # SHOT 04: Cutaway / X-Ray mid-lift (frame 331, t=11.0s)
    snap(ctx["shot4"], 331, True, "SHOT_04_CUTAWAY_XRAY.png")


def configure_clean_gui_viewport(scene):
    """Configure saved Layout/3D Viewports so opening .blend in GUI shows clean camera view without light gizmo clutter."""
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type != "VIEW_3D":
                continue
            for space in area.spaces:
                if space.type != "VIEW_3D":
                    continue
                if hasattr(space, "shading"):
                    space.shading.type = "RENDERED"
                    if hasattr(space.shading, "use_scene_lights"):
                        space.shading.use_scene_lights = True
                    if hasattr(space.shading, "use_scene_world"):
                        space.shading.use_scene_world = True
                if hasattr(space, "overlay"):
                    for attr, val in (
                        ("show_extras", False),
                        ("show_relationship_lines", False),
                        ("show_cursor", False),
                        ("show_object_origins", False),
                        ("show_floor", False),
                        ("show_axis_x", False),
                        ("show_axis_y", False),
                    ):
                        if hasattr(space.overlay, attr):
                            setattr(space.overlay, attr, val)
                if hasattr(space, "region_3d") and space.region_3d is not None:
                    space.region_3d.view_location = Vector((3.15, 0.0, 0.85))
                    space.region_3d.view_distance = 8.2
                    space.region_3d.view_rotation = Euler((math.radians(74.0), 0.0, math.radians(16.0))).to_quaternion()
                    space.region_3d.view_perspective = "CAMERA"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("stills", "animate", "full", "build_only"), default="stills")
    parser.add_argument("--still-samples", type=int, default=64)
    parser.add_argument("--anim-engine", choices=("CYCLES", "BLENDER_EEVEE"), default="BLENDER_EEVEE")
    parser.add_argument("--anim-samples", type=int, default=24)
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    args = parser.parse_args(argv)

    scene, ctx = build_scene(args)

    blend_path = WS_ROOT / "blender_project" / "EP02_PC2008_V3_CINEMATIC.blend"
    clean_blend_path = WS_ROOT / "blender_project" / "EP02_PC2008_V3_CLEAN_VIEW.blend"

    def save_clean_blends():
        ctx["coll_exp"].hide_render = True
        ctx["coll_exp"].hide_viewport = True
        configure_render_engine(scene, engine=args.anim_engine, samples=args.anim_samples)
        scene.camera = ctx["anim"]
        scene.frame_set(175)
        bpy.ops.object.select_all(action="DESELECT")
        configure_clean_gui_viewport(scene)
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
        bpy.ops.wm.save_as_mainfile(filepath=str(clean_blend_path))

    save_clean_blends()
    print("SAVED_BLEND:", blend_path, "AND", clean_blend_path, flush=True)

    if args.mode in ("stills", "full"):
        render_four_hero_stills(scene, ctx, samples=args.still_samples)

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
        frames_dir = WS_ROOT / "renders" / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)
        scene.render.filepath = str(frames_dir / "ep02_v3_")
        t0 = time.monotonic()
        bpy.ops.render.render(animation=True)
        print(f"RENDERED_ANIMATION_540_FRAMES in {time.monotonic() - t0:.2f} s", flush=True)
        save_clean_blends()


if __name__ == "__main__":
    main()
