"""Build the Capy BK mechanical test with Blender's bundled Python and NumPy."""

import argparse
import csv
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector


GODOT = Path(__file__).resolve().parents[1] / "demo_v4"
ART = GODOT / "godot" / "art"
sys.path.insert(0, str(GODOT / "tools"))
from kinematics import MK, R, RIG, fk  # noqa: E402


FPS = 30
FRAMES = 270
UNIT = 1.0 / RIG["px_per_m"]
GRADE = RIG["ground_y"]
HULL = np.array(RIG["bucket_hull_px"]) * MK
TOL = 0.0001  # metres
TEST_SUBFRAMES = (0.0, 0.25, 0.5, 0.75)

# Angles are Godot's boom, relative stick and relative bucket coordinates.
# The source bucket has painted soil, so the shot starts after the bite.
POSES = (
    (0.00, (24.0, 95.0, 51.0)),
    (0.45, (24.0, 95.0, 51.0)),
    (2.15, (20.9, 101.0, 56.0)),
    (2.48, (20.9, 101.0, 56.0)),
    (4.12, (22.8, 106.0, 82.0)),
    (6.90, (41.0, 110.0, 78.0)),
    (7.85, (40.4, 109.2, 78.8)),
    (9.00, (40.4, 109.2, 78.8)),
)


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--preview", type=int, nargs="*", default=[])
    return parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])


def pose_at(t):
    for (a, start), (b, end) in zip(POSES, POSES[1:]):
        if t <= b:
            u = min(1.0, max(0.0, (t - a) / (b - a)))
            blend = u**3 * (10 - 15 * u + 6 * u**2)
            return tuple(x + (y - x) * blend for x, y in zip(start, end))
    return POSES[-1][1]


def world(point, depth=0.0):
    return Vector((point[0] * UNIT, depth, (GRADE - point[1]) * UNIT))


def local(point, depth=0.0):
    return Vector((point[0] * UNIT, depth, -point[1] * UNIT))


def link_object(obj, collection, parent=None):
    collection.objects.link(obj)
    obj.parent = parent
    return obj


def empty(name, collection, parent=None, location=(0, 0, 0), size=0.095):
    obj = link_object(bpy.data.objects.new(name, None), collection, parent)
    obj.location = location
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = size
    return obj


def mesh_object(name, vertices, faces, material, collection, parent=None):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = link_object(bpy.data.objects.new(name, mesh), collection, parent)
    obj.data.materials.append(material)
    return obj


def card(name, bounds, depth, material, collection, parent=None, rotation=0.0):
    x0, z0, x1, z1 = bounds
    vertices = []
    for x, z in ((x0, z0), (x1, z0), (x1, z1), (x0, z1)):
        vertices.append((x * math.cos(rotation) + z * math.sin(rotation), depth,
                         -x * math.sin(rotation) + z * math.cos(rotation)))
    obj = mesh_object(name, vertices, [(0, 1, 2, 3)], material, collection, parent)
    uv = obj.data.uv_layers.new()
    for i, point in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
        uv.data[i].uv = point
    return obj


def image_card(name, asset, pin, scale, depth, collection, parent=None, rotation=0.0):
    image = bpy.data.images.load(str(ART / (asset + ".png")), check_existing=True)
    image.pack()
    image.filepath = "//" + image.name
    material = bpy.data.materials.new(name + " | painted")
    material.surface_render_method = "DITHERED"
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    texture = nodes.new("ShaderNodeTexImage")
    texture.image = image
    texture.extension = "CLIP"
    emission = nodes.new("ShaderNodeEmission")
    links.new(texture.outputs["Color"], emission.inputs["Color"])
    if asset == "worksite":
        links.new(emission.outputs[0], output.inputs["Surface"])
    else:
        alpha = nodes.new("ShaderNodeMixShader")
        links.new(texture.outputs["Alpha"], alpha.inputs[0])
        links.new(nodes.new("ShaderNodeBsdfTransparent").outputs[0], alpha.inputs[1])
        links.new(emission.outputs[0], alpha.inputs[2])
        links.new(alpha.outputs[0], output.inputs["Surface"])
    w, h = image.size
    px, py = pin
    bounds = (-px * scale, (py - h) * scale, (w - px) * scale, py * scale)
    return card(name, bounds, depth, material, collection, parent, rotation)


def surface(name, srgb, roughness, metal=0.0):
    material = bpy.data.materials.new(name)
    shader = material.node_tree.nodes.get("Principled BSDF")
    rgb = tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055)**2.4 for v in srgb)
    shader.inputs["Base Color"].default_value = (*rgb, 1.0)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metal
    material.diffuse_color = (*rgb, 1.0)
    return material


def turned(name, radius, start, end, material, collection, parent):
    """A rigid cylinder along local Z in coordinates relative to its eye."""
    sides = 24
    vertices = [
        (radius * math.cos(a * math.tau / sides), radius * math.sin(a * math.tau / sides), z)
        for z in (start, end) for a in range(sides)
    ]
    faces = [
        (i, (i + 1) % sides, (i + 1) % sides + sides, i + sides)
        for i in range(sides)
    ]
    faces.extend([tuple(reversed(range(sides))), tuple(range(sides, 2 * sides))])
    obj = mesh_object(name, vertices, faces, material, collection, parent)
    for polygon in obj.data.polygons[:sides]:
        polygon.use_smooth = True
    bevel = obj.modifiers.new("Machined edges", "BEVEL")
    bevel.width = min(0.014, radius * 0.18)
    bevel.segments = 2
    return obj


def pin_cap(name, pin, radius, materials, collection):
    axis = empty(name, collection, pin)
    axis.rotation_euler.x = math.pi / 2
    turned(name + " | rim", radius, -0.025, 0.04, materials["dark"], collection, axis)
    turned(name + " | face", radius * 0.67, 0.035, 0.056, materials["pin"], collection, axis)


def bracket(name, profile, front, back, material, collection, parent):
    """Solid clevis gusset using the same pin coordinates as the painted layer."""
    count = len(profile)
    vertices = [(x * UNIT, depth, -y * UNIT) for depth in (front, back) for x, y in profile]
    faces = [tuple(reversed(range(count))), tuple(range(count, 2 * count))]
    faces += [(i, (i + 1) % count, (i + 1) % count + count, i + count) for i in range(count)]
    obj = mesh_object(name, vertices, faces, material, collection, parent)
    bevel = obj.modifiers.new("Rounded steel gusset", "BEVEL")
    bevel.width = 0.025
    bevel.segments = 3
    obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")


def aim(name, source, target, collection):
    obj = empty(name, collection, source)
    constraint = obj.constraints.new("DAMPED_TRACK")
    constraint.track_axis = "TRACK_Z"
    constraint.target = target
    return obj


def actuator(name, base, eye, spec, materials, collection):
    barrel = aim(name + " | fixed barrel axis", base, eye, collection)
    rod = aim(name + " | fixed rod axis", eye, base, collection)
    closed = spec["closed"] * UNIT
    stroke = spec["stroke"] * UNIT
    barrel_length = closed - 0.11
    rod_length = closed - 0.07
    if rod_length + barrel_length <= closed + stroke:
        raise ValueError(f"{name}: rod and barrel would separate at full stroke")
    radius = spec["barrel_w"] * UNIT * 0.65
    rod_radius = spec["rod_w"] * UNIT * 0.57
    turned(name + " | barrel", radius, 0.0, barrel_length, materials["paint"], collection, barrel)
    turned(name + " | cap", radius * 1.10, 0.055, 0.155, materials["dark"], collection, barrel)
    turned(name + " | gland", radius * 1.11, barrel_length - 0.09, barrel_length,
           materials["dark"], collection, barrel)
    turned(name + " | chrome rod", rod_radius, 0.0, rod_length, materials["chrome"], collection, rod)
    turned(name + " | rod end", rod_radius * 1.50, 0.0, 0.125, materials["dark"], collection, rod)
    pin_cap(name + " base eye", base, radius * 0.84, materials, collection)
    pin_cap(name + " rod eye", eye, radius * 0.73, materials, collection)
    return barrel, rod, barrel_length, rod_length


def shadow(name, width, height, x, z, opacity, depth, collection):
    material = bpy.data.materials.new(name)
    material.surface_render_method = "BLENDED"
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    coords = nodes.new("ShaderNodeTexCoord")
    distance = nodes.new("ShaderNodeVectorMath")
    distance.operation = "DISTANCE"
    distance.inputs[1].default_value = (0.5, 0.5, 0)
    links.new(coords.outputs["UV"], distance.inputs[0])
    falloff = nodes.new("ShaderNodeMapRange")
    falloff.interpolation_type = "SMOOTHERSTEP"
    falloff.inputs["From Min"].default_value = 0.03
    falloff.inputs["From Max"].default_value = 0.48
    falloff.inputs["To Min"].default_value = opacity
    falloff.inputs["To Max"].default_value = 0
    links.new(distance.outputs["Value"], falloff.inputs["Value"])
    mix = nodes.new("ShaderNodeMixShader")
    ink = nodes.new("ShaderNodeEmission")
    ink.inputs["Color"].default_value = (0.09, 0.047, 0.026, 1)
    links.new(falloff.outputs[0], mix.inputs[0])
    links.new(nodes.new("ShaderNodeBsdfTransparent").outputs[0], mix.inputs[1])
    links.new(ink.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], nodes.new("ShaderNodeOutputMaterial").inputs["Surface"])
    obj = card(name, (-width / 2, -height / 2, width / 2, height / 2), depth, material, collection)
    obj.location = (x, 0, z)
    return obj, falloff.inputs["To Min"]


def light(name, location, target, energy, color, size, collection):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.color = color
    data.shape = "DISK"
    data.size = size
    obj = link_object(bpy.data.objects.new(name, data), collection)
    obj.location = location
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def setup():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 16
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.fps = FPS
    scene.frame_start = 1
    scene.frame_end = FRAMES
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.view_transform = "Standard"
    scene.world = bpy.data.worlds.new("Subtle sky ambient")
    scene.world.color = (0.11, 0.13, 0.15)
    for frame, label in ((1, "Ready | loaded bucket"), (15, "Lower"), (75, "Curl"),
                         (125, "Lift"), (208, "Ease out"), (237, "Hold")):
        scene.timeline_markers.new(label, frame=frame)
    return scene


def collection(scene, name):
    out = bpy.data.collections.new(name)
    scene.collection.children.link(out)
    return out


def animate_and_verify(scene, hinges, linkage, casts, camera, shot_shadow, out):
    boom, arm, bucket = hinges
    j, side, boss = linkage
    shade, opacity = shot_shadow
    for frame in range(1, FRAMES + 1):
        t = (frame - 1) / FPS
        b, a, k = pose_at(t)
        boom.rotation_euler.y = math.radians(-b)
        arm.rotation_euler.y = math.radians(a)
        bucket.rotation_euler.y = math.radians(k - 90.0)
        for hinge in hinges:
            hinge.keyframe_insert(data_path="rotation_euler", index=1, frame=frame)
        solved = fk(b, a, k)
        j.location = world(solved["J"], j.location.y)
        j.keyframe_insert(data_path="location", frame=frame)
        height = (GRADE - solved["T"][1]) * UNIT
        shade.location.x = solved["T"][0] * UNIT + 0.3 + 0.34 * height
        shade.scale = (1.0 + height * 0.27, 1, 1.0 + height * 0.14)
        opacity.default_value = 0.24 / (1 + max(0, height) * 0.95)
        opacity.keyframe_insert(data_path="default_value", frame=frame)
        shade.keyframe_insert(data_path="location", index=0, frame=frame)
        shade.keyframe_insert(data_path="scale", frame=frame)
    for frame, x, z, width in ((1, 1.55, 2.38, 13.45), (FRAMES, 1.67, 2.52, 12.65)):
        camera.location = (x, -24, z)
        camera.data.ortho_scale = width
        camera.keyframe_insert(data_path="location", frame=frame)
        camera.data.keyframe_insert(data_path="ortho_scale", frame=frame)

    def point(obj):
        return obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation

    def axis(obj):
        matrix = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world
        return (matrix.to_3x3() @ Vector((0, 0, 1))).normalized()

    def check(error, label, frame, tolerance=TOL):
        if abs(error) > tolerance:
            raise ValueError(f"Frame {frame:g}: {label} ({error:.8f} m)")

    with (out / "geometry.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("frame", "subframe", "bucket_clearance_m", "boom_far_extension_m",
                         "boom_near_extension_m", "stick_extension_m", "bucket_extension_m",
                         "max_pin_error_m"))
        for frame in range(1, FRAMES + 1):
            for subframe in TEST_SUBFRAMES if frame < FRAMES else (0.0,):
                scene.frame_set(frame, subframe=subframe)
                values = tuple(math.degrees(h.rotation_euler.y) for h in hinges)
                solved = fk(-values[0], values[1], values[2] + 90)
                when = frame + subframe
                if not solved["reach_ok"]:
                    raise ValueError(f"Frame {when:g}: bucket four-bar cannot close")
                hull = HULL @ R(solved["bk"]).T + solved["W2"]
                clearance = (GRADE - hull[:, 1].max()) * UNIT
                check(min(0, clearance), "bucket penetrates the grade", when)
                check((point(arm) - point(boom)).length - RIG["boom_len"] * UNIT, "boom length", when)
                check((point(bucket) - point(arm)).length - RIG["arm_len"] * UNIT, "stick length", when)
                max_error = (point(j) - world(solved["J"], j.location.y)).length
                check((point(j) - point(side)).length - RIG["bucket_cyl"]["side_len"] * UNIT,
                      "bucket side-link length", when)
                check((point(j) - point(boss)).length - RIG["bucket_cyl"]["h_len"] * UNIT,
                      "bucket H-link length", when)
                lengths = []
                for base, eye, start, end, assembly, spec in casts:
                    a, b = point(base), point(eye)
                    barrel, rod, barrel_length, rod_length = assembly
                    length = (a - b).length
                    closed = spec["closed"] * UNIT
                    check(min(0, length - closed, closed + spec["stroke"] * UNIT - length),
                          base.name + " stroke", when)
                    overlap = barrel_length + rod_length - length
                    if not 0.0 < overlap < rod_length:
                        raise ValueError(f"Frame {when:g}: {base.name} lost barrel overlap")
                    error = max((a - world(solved[start], a.y)).length,
                                (b - world(solved[end], b.y)).length,
                                (point(barrel) - a).length, (point(rod) - b).length,
                                (a + axis(barrel) * length - b).length,
                                (b + axis(rod) * length - a).length)
                    check(error, base.name + " axis/anchor mismatch", when)
                    max_error = max(error, max_error)
                    lengths.append(length - closed)
                check(max_error, "four-bar and pin closure", when)
                writer.writerow((frame, subframe, f"{clearance:.6f}", *map(lambda x: f"{x:.6f}", lengths),
                                 f"{max_error:.9f}"))


def build(out):
    scene = setup()
    set_art = collection(scene, "01 • Worksite and painted shadows")
    machine = collection(scene, "02 • Original PC200-8 painted layers")
    controls = collection(scene, "03 • Hinges and measured pivots")
    hardware = collection(scene, "04 • Rigid hydraulic hardware")
    stage = collection(scene, "05 • Camera and daylight")
    materials = {
        "paint": surface("Ochre hydraulic paint", (0.65, 0.44, 0.19), 0.55, 0.20),
        "dark": surface("Dark oiled steel", (0.28, 0.245, 0.20), 0.56, 0.29),
        "chrome": surface("Satin plated rod", (0.76, 0.79, 0.79), 0.31, 0.29),
        "pin": surface("Machined pin cap", (0.47, 0.43, 0.36), 0.40, 0.24),
    }
    background = image_card("Original painted construction site", "worksite", (836, 470.5),
                            14.30 / 1672, 2.4, set_art)
    background.location = (1.54, 0, 2.36)
    shadow("Caterpillar | contact", 5.9, 0.48, -1.53, -0.05, 0.81, 1.3, set_art)
    shadow("Caterpillar | daylight penumbra", 7.0, 0.72, -1.02, -0.12, 0.44, 1.4, set_art)
    shot_shadow = shadow("Bucket | projected shadow", 2.85, 0.46, 4.9, -0.08, 0.49, 1.25, set_art)

    body = empty("PC200-8 | illustration coordinates", controls, location=world((0, 0)))
    upper = RIG["upper"]
    image_card("Upper body + cabin", "upper", upper["pin"], upper["scale"] * UNIT, 0.22, machine, body)
    tracks = RIG["undercarriage"]
    running_gear = image_card("Track frame", "undercarriage", (0, 0),
                              tracks["scale"] * UNIT, 0.05, machine, body)
    running_gear.location = local((tracks["x_left"], tracks["top_y"]))
    boom = empty("Boom hinge", controls, body)
    arm = empty("Stick hinge", controls, boom, local((RIG["boom_len"], 0)))
    bucket = empty("Bucket hinge", controls, arm, local((RIG["arm_len"], 0)))
    for asset, pivot, start, end, length, depth in (
        ("boom", boom, "foot", "tip", RIG["boom_len"], -0.14),
        ("arm", arm, "elbow", "wrist", RIG["arm_len"], -0.23),
        ("bucket", bucket, "hinge", "tip", RIG["bucket_tip_len"], -0.32),
    ):
        spec = RIG["arm_sprite" if asset == "arm" else asset + "_sprite"]
        x, y = np.subtract(spec[end], spec[start])
        rotation = 0.0 if asset == "bucket" else -math.atan2(y, x)
        image_card(asset.title(), asset, spec[start], length * UNIT / math.hypot(x, y),
                   depth, machine, pivot, rotation)
        pin_cap(asset.title() + " hinge cap", empty(asset + " face", controls, pivot,
                                                     (0, depth - 0.02, 0)), 0.085, materials, hardware)

    bc, ac, kc = (RIG[key] for key in ("boom_cyl", "arm_cyl", "bucket_cyl"))
    bracket("Revolving frame cylinder mount", [(-43, 28), (17, 34), (59, 65),
             (58, 89), (36, 99), (10, 76), (-29, 60)], -0.36, 0.45,
            materials["dark"], hardware, body)
    bracket("Boom lift cylinder lug", [(237, -45), (279, -42), (275, -16),
             (268, -9), (251, -10), (242, -19)], -0.41, 0.36,
            materials["paint"], hardware, boom)
    bracket("Stick cylinder head bracket", [(-77, -12), (-66, -21), (-13, -24),
             (18, -11), (18, 12), (-14, 24), (-67, 20), (-77, 12)],
            -0.34, -0.12, materials["paint"], hardware, arm)
    bracket("Bucket cylinder upper bracket", [(33, -14), (39, -37), (50, -50),
             (62, -41), (68, -15), (72, -5), (33, -4)],
            -0.49, -0.12, materials["paint"], hardware, arm)
    j = empty("Bucket linkage J | baked circle intersection", controls, location=(0, -0.53, 0))
    casts = []
    for name, base, eye, depth, spec in (
        ("Boom far", (body, bc["base_upper"], "Bb"), (boom, bc["eye_boom"], "Eb"), 0.43, bc),
        ("Boom near", (body, bc["base_upper"], "Bb"), (boom, bc["eye_boom"], "Eb"), -0.46, bc),
        ("Stick", (boom, ac["base_boom"], "Ab"), (arm, ac["eye_arm"], "Ea"), -0.37, ac),
        ("Bucket", (arm, kc["base_arm"], "C"), (None, None, "J"), -0.53, kc),
    ):
        base_obj = empty(name + " barrel pin", controls, base[0], local(base[1], depth))
        eye_obj = j if eye[0] is None else empty(name + " rod pin", controls, eye[0], local(eye[1], depth))
        assembly = actuator(name, base_obj, eye_obj, spec, materials, hardware)
        casts.append((base_obj, eye_obj, base[2], eye[2], assembly, spec))

    s = empty("Bucket linkage S", controls, arm, local(kc["side_pivot_arm"], -0.53))
    k = empty("Bucket linkage K", controls, bucket,
              local(np.array(RIG["bucket_sprite"]["link_boss_offset_px"]) * MK, -0.53))
    for name, pin, length, radius in (
        ("Side link", s, kc["side_len"], 0.062),
        ("H-link", k, kc["h_len"], 0.077),
    ):
        link = aim(name + " rotation", pin, j, controls)
        turned(name, radius, 0, length * UNIT, materials["paint"], hardware, link)
        pin_cap(name + " pin", pin, radius * 1.32, materials, hardware)

    camera_data = bpy.data.cameras.new("Side profile lens")
    camera_data.type = "ORTHO"
    camera = link_object(bpy.data.objects.new("Camera", camera_data), stage)
    camera.rotation_euler.x = math.pi / 2
    scene.camera = camera
    light("Warm afternoon key", (-4, -6, 9), (2, 0, 2), 2050, (1, 0.85, 0.68), 6.0, stage)
    light("Cool sky fill", (6, -4, 6), (2, 0, 2.5), 1250, (0.66, 0.82, 1.0), 8.0, stage)
    light("Soft rim", (3, 2, 8), (1, 0, 2), 1240, (1, 0.88, 0.72), 4.0, stage)

    animate_and_verify(scene, (boom, arm, bucket), (j, s, k), casts, camera, shot_shadow, out)
    scene.frame_set(132)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.region_3d.view_perspective = "CAMERA"
                area.spaces.active.overlay.show_overlays = False
                area.spaces.active.shading.type = "RENDERED"
    scene.render.filepath = "//frames/pc200_"
    bpy.ops.wm.save_as_mainfile(filepath=str(out / "EP02_PC200_BLENDER_DRAFT.blend"))
    print("Validated 270 frames and all quarter-frame samples.", flush=True)
    return scene


def main():
    args = arguments()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    scene = build(out)
    for frame in args.preview:
        scene.frame_set(frame)
        scene.render.filepath = str(out / f"preview_{frame:04}.png")
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
