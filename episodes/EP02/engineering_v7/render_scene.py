"""Read the MATLAB trace into the existing Blender rig and build Hydraulic Reveal."""

import argparse
import csv
import math
import re
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "blender_pc200"))
import build_shot as proof

FPS = 30
FRAMES = 510
GEOM_TOL_M = 0.0001
PIN_MAP = {
    "boom_pivot": "Boom hinge",
    "stick_pivot": "Stick hinge",
    "bucket_pivot": "Bucket hinge",
    "boom_a": "Boom near barrel pin",
    "boom_b": "Boom near rod pin",
    "stick_a": "Stick barrel pin",
    "stick_b": "Stick rod pin",
    "bucket_a": "Bucket barrel pin",
    "bucket_b": "Bucket linkage J | baked circle intersection",
    "bucket_side": "Bucket linkage S",
    "bucket_boss": "Bucket linkage K",
}
CYLINDERS = {
    "Boom near": ("boom_a", "boom_b", "boom_cyl_length_mm", "boom_cyl"),
    "Boom far": ("boom_a", "boom_b", "boom_cyl_length_mm", "boom_cyl"),
    "Stick": ("stick_a", "stick_b", "arm_cyl_length_mm", "arm_cyl"),
    "Bucket": ("bucket_a", "bucket_b", "bucket_cyl_length_mm", "bucket_cyl"),
}


def read_trace(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = [{k: float(v) for k, v in row.items()} for row in csv.DictReader(f)]
    if len(rows) != FRAMES:
        raise ValueError(f"Expected {FRAMES} trace rows; received {len(rows)}")
    for i, row in enumerate(rows):
        if not all(math.isfinite(x) for x in row.values()) or abs(row["t_s"]-i/FPS) > 1e-7:
            raise ValueError(f"Invalid timestamp or nonfinite values at sample {i}")
    return rows


def sample_point(row, name, depth):
    return Vector((row[name + "_x_mm"] / 1000, depth, row[name + "_z_mm"] / 1000))


def keyed_translation(obj, frame, x, z):
    obj.location.x, obj.location.z = x, z
    obj.keyframe_insert(data_path="location", frame=frame)


def animate_machine(scene, rows, out):
    objects = bpy.data.objects
    pins = {name: objects[obj] for name, obj in PIN_MAP.items()}
    hinge_ids = ("boom_pivot", "stick_pivot", "bucket_pivot")
    hinges = [pins[n] for n in hinge_ids]
    knuckle = pins["bucket_b"]
    root_shadow = objects["Bucket | projected shadow"]
    shadow_nodes = root_shadow.data.materials[0].node_tree
    shadow_opacity = next(n for n in shadow_nodes.nodes if n.type == "MAP_RANGE").inputs["To Min"]
    for obj in (*hinges, knuckle, root_shadow, shadow_nodes, scene.camera, scene.camera.data):
        obj.animation_data_clear()
    for frame, row in enumerate(rows, 1):
        for hinge, field in zip(hinges, ("boom_deg", "stick_deg", "bucket_deg")):
            hinge.rotation_euler.y = math.radians(row[field])
            hinge.keyframe_insert(data_path="rotation_euler", index=1, frame=frame)
        knuckle.location = sample_point(row, "bucket_b", knuckle.location.y)
        knuckle.keyframe_insert(data_path="location", frame=frame)
        tooth = sample_point(row, "tooth", 0)
        root_shadow.location.x = tooth.x + 0.3 + 0.34 * tooth.z
        root_shadow.scale = (1 + 0.27 * tooth.z, 1, 1 + 0.14 * tooth.z)
        shadow_opacity.default_value = 0.24 / (1 + max(0, tooth.z) * 0.95)
        root_shadow.keyframe_insert(data_path="location", index=0, frame=frame)
        root_shadow.keyframe_insert(data_path="scale", frame=frame)
        shadow_opacity.keyframe_insert(data_path="default_value", frame=frame)

    for marker in list(scene.timeline_markers):
        scene.timeline_markers.remove(marker)
    for frame, name in ((1, "01 Loaded boom"), (88, "02 Reveal cylinder"),
                        (112, "03 Raise under load"), (411, "04 Capy reaction")):
        scene.timeline_markers.new(name, frame=frame)
    for frame, x, z, width in ((1, 1.53, 2.45, 13.55), (88, 1.55, 2.49, 13.3),
                               (FRAMES, 1.62, 2.51, 13.3)):
        keyed_translation(scene.camera, frame, x, z)
        scene.camera.data.ortho_scale = width
        scene.camera.data.keyframe_insert(data_path="ortho_scale", frame=frame)
    scene.frame_end = FRAMES

    with (out / "blender_geometry.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(("frame", "subframe", "pin_deviation_mm", "axis_deviation_mm",
                         "bucket_ground_clearance_mm"))
        for i, row in enumerate(rows):
            for offset in (0.0, 0.5) if i < len(rows)-1 else (0.0,):
                scene.frame_set(i+1, subframe=offset)
                deps = bpy.context.evaluated_depsgraph_get()

                def matrix(obj):
                    return obj.evaluated_get(deps).matrix_world

                p = {name: matrix(obj).translation for name, obj in pins.items()}
                if offset:
                    expected = proof.fk(-math.degrees(hinges[0].rotation_euler.y),
                                        math.degrees(hinges[1].rotation_euler.y),
                                        math.degrees(hinges[2].rotation_euler.y)+90)
                    maximum = (p["bucket_b"]-proof.world(expected["J"], p["bucket_b"].y)).length
                else:
                    maximum = max((point-sample_point(row, name, point.y)).length
                                  for name, point in p.items())
                maximum = max(maximum,
                              abs((p["boom_pivot"]-p["stick_pivot"]).length-5.7),
                              abs((p["stick_pivot"]-p["bucket_pivot"]).length-2.925),
                              abs((p["bucket_b"]-p["bucket_side"]).length-0.65),
                              abs((p["bucket_b"]-p["bucket_boss"]).length-0.75))
                align = 0.0
                for label, (start, end, field, spec) in CYLINDERS.items():
                    barrel = matrix(objects[label + " | fixed barrel axis"])
                    rod = matrix(objects[label + " | fixed rod axis"])
                    a, b = barrel.translation, rod.translation
                    distance = (b-a).length
                    reach = proof.RIG[spec]
                    stroke = distance - reach["closed"] * proof.UNIT
                    if not -GEOM_TOL_M <= stroke <= reach["stroke"]*proof.UNIT+GEOM_TOL_M:
                        raise ValueError(f"Frame {i+1}: {label} stroke {stroke}")
                    if not offset:
                        maximum = max(maximum, abs(distance-row[field]/1000),
                                      (a-sample_point(row, start, a.y)).length,
                                      (b-sample_point(row, end, b.y)).length)
                    else:
                        maximum = max(maximum,
                                      (a-Vector((p[start].x, a.y, p[start].z))).length,
                                      (b-Vector((p[end].x, b.y, p[end].z))).length)
                    align = max(align, (a+barrel.to_3x3().col[2].normalized()*distance-b).length,
                                (b+rod.to_3x3().col[2].normalized()*distance-a).length)
                matrix_bucket = matrix(hinges[2])
                clearance = min((matrix_bucket @ proof.local(point)).z for point in proof.HULL)
                if not offset:
                    maximum = max(maximum, abs(clearance-row["ground_clearance_mm"]/1000))
                if max(maximum, align) > GEOM_TOL_M or clearance < 0:
                    raise ValueError(f"Frame {i+1}+{offset}: {maximum=} {align=} {clearance=}")
                writer.writerow((i+1, offset, maximum*1000, align*1000, clearance*1000))


def flat(name, color):
    material = bpy.data.materials.new(name)
    tree = material.node_tree
    tree.nodes.clear()
    glow = tree.nodes.new("ShaderNodeEmission")
    glow.inputs["Color"].default_value = (*color, 1)
    tree.links.new(glow.outputs[0], tree.nodes.new("ShaderNodeOutputMaterial").inputs[0])
    return material


def label(name, body, x, z, size, font, material, coll, parent):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body, curve.size, curve.font = body, size, font
    obj = proof.link_object(bpy.data.objects.new(name, curve), coll, parent)
    obj.location = (x, -0.13, z)
    obj.rotation_euler.x = math.pi/2
    curve.materials.append(material)
    return obj


def outline(name, points, radius, mat, coll, parent, closed=False):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = radius
    curve.bevel_resolution = 2
    spline = curve.splines.new("POLY")
    spline.points.add(len(points)-1)
    for p, (x, y, z) in zip(spline.points, points):
        p.co = (x, y, z, 1)
    spline.use_cyclic_u = closed
    obj = proof.link_object(bpy.data.objects.new(name, curve), coll, parent)
    curve.materials.append(mat)
    return obj


def lift_overlay(root, start, stop, z):
    for frame, height in ((max(1, start-1), 10), (start+10, z),
                          (stop-10, z), (stop, 10)):
        keyed_translation(root, frame, root.location.x, height)


def reveal_graphics(scene, rows, capy_path, font_path, bold_path):
    coll = proof.collection(scene, "06 • Hydraulic reveal and Capy")
    regular, bold = (bpy.data.fonts.load(str(p), check_existing=True) for p in (font_path, bold_path))
    navy = flat("Reveal | blue-black", (0.013,0.028,0.050))
    cavity = flat("Reveal | cavity", (0.030,0.064,0.088))
    ink = flat("Reveal | light", (0.82,0.89,0.93))
    metal = flat("Reveal | steel", (0.42,0.56,0.62))
    white = flat("Reveal | chrome", (0.70,0.79,0.80))
    gold = flat("Reveal | warm", (0.96,0.55,0.13))
    supply = flat("Reveal | oil supply", (0.64,0.095,0.045))
    return_oil = flat("Reveal | oil return", (0.026,0.26,0.46))
    aqua = flat("Reveal | return accent", (0.16,0.59,0.80))

    panel = proof.empty("Cylinder teaching insert", coll, location=(-4.74,-5.0,6.05))
    proof.card("Cylinder insert backing", (0,-2.13,5.22,0), 0, navy, coll, panel)
    proof.card("Accent", (0,-0.045,5.22,0), -0.03, gold, coll, panel)
    label("Chapter marker", "THỦY LỰC  /  01", 0.23,-0.29,0.15,bold,gold,coll,panel)
    label("Heading", "Bên trong xi lanh nâng cần",0.23,-0.60,0.28,bold,ink,coll,panel)
    label("Pressure inlet", "Dầu cấp  ·  Khoang đáy",0.48,-0.89,0.15,regular,gold,coll,panel)
    label("Return outlet", "Khoang ty  ·  Dầu hồi",3.02,-0.89,0.15,regular,aqua,coll,panel)
    label("Schematic disclosure", "Mặt cắt nguyên lý  ·  Ty và cần dùng chung dữ liệu chuyển động",
          0.23,-1.98,0.125,regular,ink,coll,panel)
    low, high, left, right = -1.59, -1.10, 0.69, 4.01
    proof.card("Cylinder section casing", (left-0.065,low-0.07,right+0.104,high+0.07),
               -0.045,metal,coll,panel)
    proof.card("Cylinder section cavity", (left,low,right,high),-0.06,cavity,coll,panel)
    cap_volume = proof.card("Variable cap chamber", (0,low,1,high),-0.07,supply,coll,panel)
    cap_volume.location.x = left
    rod_volume = proof.card("Variable rod chamber", (0,low,1,high),-0.07,return_oil,coll,panel)
    crosshead = proof.empty("Section piston",coll,panel)
    proof.card("Piston", (-0.053,low,0.053,high),-0.095,white,coll,crosshead)
    proof.card("Rigid section rod", (0.05,-1.407,2.14,-1.285),-0.092,white,coll,crosshead)
    proof.card("Gland", (right-0.04,low-0.04,right+0.10,high+0.04),-0.085,metal,coll,panel)
    arrows = proof.empty("Flow arrows | only while extending",coll,panel)
    for name, x, direction, color in (("Supply into cap",0.96,-1,gold),
                                      ("Rod out to return",3.81,1,aqua)):
        z = -1.016 if direction<0 else -0.94
        tail = z+0.16 if direction<0 else z-0.17
        outline(name, [(x,-0.1,tail),(x,-0.1,z)],0.012,color,coll,arrows)
        outline(name + " arrow", [(x-0.067,-0.1,z-0.08*direction),(x,-0.1,z),
                                  (x+0.067,-0.1,z-0.08*direction)],0.012,color,coll,arrows)
    start = next(i for i,r in enumerate(rows,1) if r["t_s"] >= 3.72)
    stop = next(i for i,r in enumerate(rows,1) if r["t_s"] >= 11.72)
    for frame, height in ((1,10),(start,10),(start+2,0),(stop,0),(stop+2,10)):
        keyed_translation(arrows, frame, 0, height)
    for frame, row in enumerate(rows,1):
        piston = left+0.38+row["boom_stroke_mm"]*0.00188
        crosshead.location.x = piston
        cap_volume.scale.x = piston-left
        rod_volume.location.x = piston
        rod_volume.scale.x = right-piston
        crosshead.keyframe_insert(data_path="location",index=0,frame=frame)
        cap_volume.keyframe_insert(data_path="scale",index=0,frame=frame)
        rod_volume.keyframe_insert(data_path="location",index=0,frame=frame)
        rod_volume.keyframe_insert(data_path="scale",index=0,frame=frame)
    lift_overlay(panel, 88, 409, 6.05)

    for name, radius in (("Boom hinge",0.14),("Stick hinge",0.122),("Bucket hinge",0.103),
                         ("Boom near barrel pin",0.10),("Boom near rod pin",0.10)):
        circle = [(radius*math.cos(a*math.tau/48),-0.78,radius*math.sin(a*math.tau/48))
                  for a in range(48)]
        ring = outline(name + " | highlight",circle,0.012,aqua,coll,bpy.data.objects[name],True)
        for frame, off in ((1, True),(92,False),(405,False),(412,True)):
            ring.hide_render = off
            ring.keyframe_insert(data_path="hide_render",frame=frame)

    field = proof.empty("Capy reaction | approved local source",coll,location=(-4.73,-5,6.01))
    proof.card("Reaction backing", (0,-1.39,5.14,0), 0, navy,coll,field)
    proof.card("Reaction accent", (0,-0.045,5.14,0), -0.03, gold,coll,field)
    label("Capy speaker", "CAPY BK",1.49,-0.40,0.17,bold,gold,coll,field)
    label("Capy reaction", "À! Ty đẩy, cần quay quanh chốt.",1.49,-0.79,0.214,bold,ink,coll,field)
    label("Mechanics takeaway", "Sơ đồ nguyên lý  ·  máy dáng PC200-8",1.49,-1.08,0.135,regular,ink,coll,field)
    image = bpy.data.images.load(str(capy_path),check_existing=True)
    texmat = flat("Original Capy artwork",(1,1,1))
    tree = texmat.node_tree
    image_node = tree.nodes.new("ShaderNodeTexImage")
    image_node.image = image
    glow = next(n for n in tree.nodes if n.type=="EMISSION")
    mix = tree.nodes.new("ShaderNodeMixShader")
    tree.links.new(image_node.outputs["Color"],glow.inputs["Color"])
    tree.links.new(image_node.outputs["Alpha"],mix.inputs[0])
    tree.links.new(tree.nodes.new("ShaderNodeBsdfTransparent").outputs[0],mix.inputs[1])
    tree.links.new(glow.outputs[0],mix.inputs[2])
    tree.links.new(mix.outputs[0],next(n for n in tree.nodes if n.type=="OUTPUT_MATERIAL").inputs[0])
    actor = proof.empty("Capy anticipation and settle",coll,field,location=(0.76,-0.11,-0.75))
    w,h = image.size
    proof.card("Approved Capy cel", (-0.59,-0.59*h/w,0.59,0.59*h/w),0,texmat,coll,actor)
    for frame, rot in ((411,-3),(427,5),(439,-2),(456,0)):
        actor.rotation_euler.y = math.radians(rot)
        actor.keyframe_insert(data_path="rotation_euler",index=1,frame=frame)
    for frame, z in ((1,10),(410,10),(425,6.01),(510,6.01)):
        keyed_translation(field,frame,field.location.x,z)
    bpy.ops.file.pack_all()
    image.filepath = "//" + image.name


def verify_nx(stl, step, joint_map, out):
    """Use native STL import to measure an NX-exported, asymmetric reference part."""
    contents = step.read_text(encoding="latin-1")
    if not re.search(r"SI_UNIT\s*\(\s*\.MILLI\.\s*,\s*\.METRE\.\s*\)", contents, re.I):
        raise ValueError("STEP does not declare millimetres")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.stl_import(filepath=str(stl),global_scale=0.001,forward_axis="Y",up_axis="Z")
    obj = bpy.context.selected_objects[0]
    points = np.array([tuple(obj.matrix_world @ v.co) for v in obj.data.vertices])
    with joint_map.open(newline="",encoding="utf-8-sig") as f:
        refs = {row["joint"]:np.array([float(row[k]) for k in ("x_mm","y_mm","z_mm")])*0.001
                for row in csv.DictReader(f)}
    gauge_max = np.array([1.0, 0.2, 0.3])
    gauge = points[((points >= -GEOM_TOL_M) & (points <= gauge_max+GEOM_TOL_M)).all(axis=1)]
    if len(np.unique(gauge, axis=0)) != 8:
        raise ValueError("Could not locate all eight gauge corners")
    tests = [np.max(np.abs(gauge.min(axis=0))),
             np.max(np.abs(gauge.max(axis=0)-gauge_max))]
    for axis in ("boom_pivot","stick_pivot","bucket_pivot"):
        tests.append(np.min(np.linalg.norm(points-refs[axis],axis=1)))
    if max(tests)>GEOM_TOL_M:
        raise ValueError(f"NX import unit, orientation or datum mismatch: {tests}")
    out.write_text(f"STEP declares mm, STL mm→m verified. Gauge 1.000 x 0.200 x 0.300 m. "
                   f"Three NX joint datum corners checked; max error {max(tests)*1000:.6f} mm.\n",
                   encoding="utf-8")


def set_camera_review_view(scene):
    scene.frame_set(272)
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            view = area.spaces.active
            if view.region_3d is None:
                continue
            view.region_3d.view_perspective = "CAMERA"
            view.region_3d.view_camera_zoom = 20
            view.region_3d.view_camera_offset = (0, 0)
            view.lock_camera = False
            view.overlay.show_overlays = False
            # Blender 5.3 reopens a saved Rendered viewport as Solid.
            view.shading.type = "MATERIAL"
            view.shading.use_scene_lights = True
            view.shading.use_scene_world = True
        elif area.ui_type == "TIMELINE":
            region = next(r for r in area.regions if r.type == "WINDOW")
            with bpy.context.temp_override(area=area, region=region):
                bpy.ops.action.view_all()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--capy",type=Path)
    parser.add_argument("--nx-units",action="store_true")
    parser.add_argument("--camera-copy",action="store_true",
                        help="Save a new viewing copy of the currently open hero scene.")
    parser.add_argument("--preview",type=int,nargs="*",default=[])
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    out = args.out.resolve()
    if args.nx_units:
        verify_nx(out/"nx/calibration.stl",out/"nx/calibration.step",out/"joint_map.csv",out/"nx_units.txt")
        return
    scene = bpy.context.scene
    if args.camera_copy:
        set_camera_review_view(scene)
        bpy.ops.wm.save_as_mainfile(filepath=str(out/"EP02_hero_CAMERA.blend"), copy=True)
        return
    rows = read_trace(out/"motion_trace.csv")
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1
    animate_machine(scene,rows,out)
    reveal_graphics(scene,rows,args.capy,Path("C:/Windows/Fonts/segoeui.ttf"),
                    Path("C:/Windows/Fonts/segoeuib.ttf"))
    scene.eevee.taa_render_samples = 12
    scene.render.image_settings.compression = 4
    scene.render.filepath = "//frames/hr_"
    set_camera_review_view(scene)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/"EP02_hero.blend"))
    print("HYDRAULIC_REVEAL_OK 510 frames + 509 half-frame checks",flush=True)
    for frame in args.preview:
        scene.frame_set(frame)
        scene.render.filepath = str(out/f"preview_{frame:04}.png")
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
