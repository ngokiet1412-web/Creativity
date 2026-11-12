@tool
extends Node2D
## PC200-8 side-view rig. Rigid painted layers rotate about pins; every
## hydraulic cylinder is solved from its two pin positions (L = |B - A|).
## Units: world px, 100 px = 1 m. Geometry is illustrative (see art/rig.json).

const INK := Color("#2a221c")
const PAINT := Color("#e7a82b")
const PAINT_DARK := Color("#a8701b")
const STEEL := Color("#4a4640")
const CHROME := Color("#d8dde0")

@export_range(-10.0, 60.0, 0.1) var boom_deg := 19.5: set = _set_boom
@export_range(20.0, 140.0, 0.1) var arm_rel := 99.9: set = _set_arm
@export_range(-60.0, 100.0, 0.1) var bucket_rel := 60.2: set = _set_bucket
@export_range(0.0, 1.0, 0.01) var cutaway := 0.0: set = _set_cutaway
@export_range(0.0, 1.0, 0.01) var housing_alpha := 1.0: set = _set_housing
@export var ink_style := true     # V4 2.5D illustration shader on painted layers

var rig: Dictionary
var ready_done := false
var tex := {}
var upper: Sprite2D
var tracks: Sprite2D
var boom_node: Node2D
var arm_node: Node2D
var bucket_node: Node2D
var layers := {}
var tip_local := Vector2.ZERO
var k_local := Vector2.ZERO
var mk := 1.0

func _ready() -> void:
	rig = JSON.parse_string(FileAccess.get_file_as_string("res://art/rig.json"))
	for name in ["upper", "undercarriage", "boom", "arm", "bucket"]:
		tex[name] = _load_tex("res://art/%s.png" % name)
	for c in get_children():
		if c.has_meta("gen"):
			c.free()
	upper = _sprite("Upper", tex.upper, _v(rig.upper.pin), rig.upper.scale, 1)
	tracks = _sprite("Undercarriage", tex.undercarriage, Vector2.ZERO, rig.undercarriage.scale, 2)
	tracks.position = Vector2(rig.undercarriage.x_left, rig.undercarriage.top_y)
	layers.far_ram = _layer("BoomRamFar", 0, _draw_far_ram)
	layers.frame = _layer("FrameNose", 3, _draw_frame)
	boom_node = _joint("Boom", self, 4)
	var bs: Dictionary = rig.boom_sprite
	var axis := _v(bs.tip) - _v(bs.foot)
	var s := _sprite("BoomPaint", tex.boom, _v(bs.foot), rig.boom_len / axis.length(), 4, boom_node)
	s.rotation = -axis.angle()
	layers.boom_extra = _layer("BoomLugs", 4, _draw_boom_extra, boom_node)
	layers.near_ram = _layer("BoomRamNear", 5, _draw_near_ram)
	layers.arm_ram = _layer("ArmRam", 6, _draw_arm_ram)
	arm_node = _joint("Arm", boom_node, 7)
	arm_node.position = Vector2(rig.boom_len, 0)
	var asp: Dictionary = rig.arm_sprite
	var aaxis := _v(asp.wrist) - _v(asp.elbow)
	var a := _sprite("ArmPaint", tex.arm, _v(asp.elbow), rig.arm_len / aaxis.length(), 7, arm_node)
	a.rotation = -aaxis.angle()
	layers.arm_extra = _layer("ArmBrackets", 7, _draw_arm_extra, arm_node)
	bucket_node = _joint("Bucket", arm_node, 8)
	bucket_node.position = Vector2(rig.arm_len, 0)
	var bk: Dictionary = rig.bucket_sprite
	mk = rig.bucket_tip_len / (_v(bk.tip) - _v(bk.hinge)).length()
	tip_local = (_v(bk.tip) - _v(bk.hinge)) * mk
	k_local = _v(bk.link_boss_offset_px) * mk
	_sprite("BucketPaint", tex.bucket, _v(bk.hinge), mk, 8, bucket_node)
	layers.bucket_extra = _layer("BucketBosses", 8, _draw_bucket_extra, bucket_node)
	layers.linkage = _layer("BucketLinkage", 9, _draw_linkage)
	ready_done = true
	_apply()

func _v(a) -> Vector2:
	return Vector2(a[0], a[1])

func _load_tex(path: String) -> Texture2D:
	var img := Image.load_from_file(ProjectSettings.globalize_path(path))
	img.generate_mipmaps()
	return ImageTexture.create_from_image(img)

func _joint(n: String, parent: Node, z: int) -> Node2D:
	var j := Node2D.new()
	j.name = n
	j.z_index = z
	j.z_as_relative = false
	j.set_meta("gen", true)
	parent.add_child(j)
	return j

func _sprite(n: String, t: Texture2D, pin: Vector2, sc: float, z: int, parent: Node = self) -> Sprite2D:
	var s := Sprite2D.new()
	s.name = n
	s.texture = t
	s.centered = false
	s.offset = -pin
	s.scale = Vector2.ONE * sc       # uniform scale only
	s.z_index = z
	s.z_as_relative = false
	s.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	if ink_style:
		var m := ShaderMaterial.new()
		m.shader = load("res://ink.gdshader")
		# ~2.4 screen px contour at wide framing whatever the layer's scale
		m.set_shader_parameter("outline_px", clampf(2.4 / sc, 1.5, 6.0))
		s.material = m
	s.set_meta("gen", true)
	parent.add_child(s)
	return s

func _layer(n: String, z: int, cb: Callable, parent: Node = self) -> Node2D:
	var l := Node2D.new()
	l.name = n
	l.z_index = z
	l.z_as_relative = false
	l.set_meta("gen", true)
	parent.add_child(l)
	l.draw.connect(cb.bind(l))
	return l

func _set_boom(v: float) -> void:
	boom_deg = v; _apply()
func _set_arm(v: float) -> void:
	arm_rel = v; _apply()
func _set_bucket(v: float) -> void:
	bucket_rel = v; _apply()
func _set_cutaway(v: float) -> void:
	cutaway = v; _apply()
func _set_housing(v: float) -> void:
	housing_alpha = v
	if ready_done:
		var g := Color(1, 1, 1, 1).lerp(Color(0.55, 0.72, 0.95, 0.30), 1.0 - v)
		if upper.material:
			upper.material.set_shader_parameter("ghost", g)
		else:
			upper.modulate = g

func _apply() -> void:
	if not ready_done:
		return
	boom_node.rotation = deg_to_rad(-boom_deg)
	arm_node.rotation = deg_to_rad(arm_rel)
	bucket_node.rotation = deg_to_rad(bucket_rel - 90.0)
	for l in layers.values():
		l.queue_redraw()

# ------------------------------------------------------------------ kinematics
## Pure forward kinematics (machine space). Mirrors tools/kinematics.py.
func fk(b: float, qa: float, qk: float) -> Dictionary:
	var ab := deg_to_rad(-b)
	var w1 := Vector2(rig.boom_len, 0).rotated(ab)
	var aa := ab + deg_to_rad(qa)
	var w2 := w1 + Vector2(rig.arm_len, 0).rotated(aa)
	var bk := aa + deg_to_rad(qk - 90.0)
	var bc: Dictionary = rig.boom_cyl
	var ac: Dictionary = rig.arm_cyl
	var kc: Dictionary = rig.bucket_cyl
	var c := w1 + _v(kc.base_arm).rotated(aa)
	var s := w1 + _v(kc.side_pivot_arm).rotated(aa)
	var k := w2 + k_local.rotated(bk)
	var j := _circle_meet(s, k, kc.side_len, kc.h_len)
	var out := {
		"W1": w1, "W2": w2, "T": w2 + tip_local.rotated(bk), "K": k, "S": s, "C": c, "J": j,
		"Bb": _v(bc.base_upper), "Eb": _v(bc.eye_boom).rotated(ab),
		"Ab": _v(ac.base_boom).rotated(ab), "Ea": w1 + _v(ac.eye_arm).rotated(aa),
		"ab": ab, "aa": aa, "bk": bk,
	}
	out.Lb = out.Bb.distance_to(out.Eb)
	out.La = out.Ab.distance_to(out.Ea)
	out.Lk = c.distance_to(j)
	out.link_ok = absf(kc.side_len - kc.h_len) < s.distance_to(k) and s.distance_to(k) < kc.side_len + kc.h_len
	return out

func current() -> Dictionary:
	return fk(boom_deg, arm_rel, bucket_rel)

func bucket_point(local_px: Vector2, f: Dictionary) -> Vector2:
	## sprite-pixel offset from the hinge -> machine space
	return f.W2 + (local_px * mk).rotated(f.bk)

func _circle_meet(s: Vector2, k: Vector2, a: float, b: float) -> Vector2:
	var d := s.distance_to(k)
	var x := (a * a - b * b + d * d) / (2.0 * d)
	var h := sqrt(maxf(a * a - x * x, 0.0))
	var u := (k - s) / d
	var v := Vector2(-u.y, u.x)
	return s + u * x - v * h

# --------------------------------------------------------------------- drawing
func pin(l: CanvasItem, p: Vector2, r: float) -> void:
	l.draw_circle(p, r + 1.6, INK, true, -1, true)
	l.draw_circle(p, r, Color("#8a8172"), true, -1, true)
	l.draw_circle(p - Vector2(0.6, 0.8), r * 0.62, Color("#c2b7a2"), true, -1, true)
	l.draw_circle(p + Vector2(0.5, 0.7), r * 0.3, Color("#5c574f"), true, -1, true)

func plate(l: CanvasItem, pts: PackedVector2Array, fill: Color, w := 2.0) -> void:
	l.draw_colored_polygon(pts, fill)
	var closed := pts.duplicate()
	closed.append(pts[0])
	l.draw_polyline(closed, INK, w, true)

## Telescoping cylinder between two pins. The barrel and rod keep fixed lengths;
## only the overlap changes. Returns piston position from the base pin.
func cylinder(l: CanvasItem, a: Vector2, b: Vector2, spec: Dictionary, shade := 1.0,
		cut := 0.0, chambers := Vector2.ZERO) -> float:
	var u := a.direction_to(b)
	var n := u.orthogonal()
	var length := a.distance_to(b)
	var closed: float = spec.closed
	var barrel := closed - 18.0
	var stroke_pos := clampf(length - closed, 0.0, spec.stroke)
	var piston := 22.0 + stroke_pos
	var bw: float = spec.barrel_w
	var rw: float = spec.rod_w
	var gland := a + u * barrel
	var paint := PAINT.darkened(1.0 - shade)
	var chrome := CHROME.darkened((1.0 - shade) * 1.2)
	# rod (drawn first, barrel covers the inner part)
	var rod_start := a + u * piston
	l.draw_line(rod_start, b, INK, rw + 3.2, true)
	l.draw_line(rod_start, b, chrome, rw, true)
	l.draw_line(rod_start - n * rw * 0.22, b - n * rw * 0.22, Color(1, 1, 1, 0.75 * shade), rw * 0.28, true)
	# barrel
	var body_alpha := 1.0 - 0.72 * cut
	l.draw_line(a - u * 4, gland, Color(INK, maxf(body_alpha, 0.9)), bw + 3.6, true)
	l.draw_line(a - u * 4, gland, Color(paint, body_alpha), bw, true)
	if cut > 0.01:
		var inner := bw - 5.0
		# chambers.x / .y: 1 = pressurised supply (red), 0 = return (blue)
		var bottom_col := Color("#d8432f") if chambers.x > 0.5 else Color("#3e8fd6")
		var rod_col := Color("#d8432f") if chambers.y > 0.5 else Color("#3e8fd6")
		l.draw_line(a + u * 6, a + u * piston, Color(bottom_col, cut * 0.95), inner, true)
		l.draw_line(a + u * (piston + 6), gland - u * 4, Color(rod_col, cut * 0.95), inner, true)
		l.draw_line(a + u * (piston + 6), gland, Color(chrome, cut), rw * 0.9, true)
		l.draw_line(a + u * piston, a + u * (piston + 7), Color("#6b6f73"), inner + 2, true)
		l.draw_line(a + u * (piston + 1), a + u * (piston + 6), Color("#b9bdc0"), inner - 1, true)
	l.draw_line(a + u * 8 - n * bw * 0.28, gland - u * 10 - n * bw * 0.28,
		Color(paint.lightened(0.35), body_alpha * 0.9), 2.4, true)
	l.draw_line(a + u * 8 + n * bw * 0.3, gland - u * 8 + n * bw * 0.3,
		Color(paint.darkened(0.3), body_alpha * 0.9), 2.4, true)
	# gland nut and base cap
	l.draw_line(gland - u * 9, gland + u * 2, INK, bw + 6.5, true)
	l.draw_line(gland - u * 7, gland, Color("#6d6457").darkened(1.0 - shade), bw + 3, true)
	l.draw_line(a - u * 4, a + u * 7, Color("#6d6457").darkened(1.0 - shade), bw + 2.5, true)
	# ports
	l.draw_circle(a + u * 14 - n * (bw * 0.5 + 1), 2.8, INK, true, -1, true)
	l.draw_circle(gland - u * 14 - n * (bw * 0.5 + 1), 2.8, INK, true, -1, true)
	pin(l, a, bw * 0.42)
	pin(l, b, rw * 0.62)
	return piston

func port_points(a: Vector2, b: Vector2, spec: Dictionary) -> Array:
	var u := a.direction_to(b)
	var n := u.orthogonal()
	var gland := a + u * (float(spec.closed) - 18.0)
	var bw: float = spec.barrel_w
	return [a + u * 14 - n * (bw * 0.5 + 1), gland - u * 14 - n * (bw * 0.5 + 1)]

func _draw_far_ram(l: Node2D) -> void:
	var f := current()
	var off := _v(rig.boom_cyl.far_offset)
	cylinder(l, f.Bb + off, f.Eb + off, rig.boom_cyl, 0.62)

func _draw_near_ram(l: Node2D) -> void:
	var f := current()
	cylinder(l, f.Bb, f.Eb, rig.boom_cyl, 1.0, cutaway, Vector2(1, 0))

func _draw_arm_ram(l: Node2D) -> void:
	var f := current()
	cylinder(l, f.Ab, f.Ea, rig.arm_cyl, 0.96)

func _draw_linkage(l: Node2D) -> void:
	var f := current()
	cylinder(l, f.C, f.J, rig.bucket_cyl, 0.98)
	# side link (arm -> J) and H-link (J -> bucket boss)
	l.draw_line(f.S, f.J, INK, 11, true)
	l.draw_line(f.S, f.J, Color("#5d544a"), 7.5, true)
	l.draw_line(f.J, f.K, INK, 13, true)
	l.draw_line(f.J, f.K, PAINT_DARK, 9.5, true)
	l.draw_line(f.J + (f.K - f.J).orthogonal().normalized() * 2.0, f.K, PAINT.lightened(0.25), 2.0, true)
	pin(l, f.S, 5.2)
	pin(l, f.K, 5.6)
	pin(l, f.J, 6.0)

func _draw_frame(l: Node2D) -> void:
	# revolving-frame nose carrying the boom cylinder foot pins
	var base := _v(rig.boom_cyl.base_upper)
	plate(l, PackedVector2Array([Vector2(-34, 36), Vector2(22, 36), Vector2(base.x + 16, base.y - 20),
		Vector2(base.x + 15, base.y + 9), Vector2(base.x - 8, base.y + 14), Vector2(-12, 64)]), Color("#3c3833"))
	l.draw_line(Vector2(-28, 41), Vector2(18, 41), Color("#6a645b"), 2.0, true)
	plate(l, PackedVector2Array([Vector2(-14, -14), Vector2(14, -14), Vector2(16, 20), Vector2(-16, 20)]), Color("#3c3833"))
	pin(l, Vector2.ZERO, 9.5)

func _draw_boom_extra(l: Node2D) -> void:
	var e := _v(rig.boom_cyl.eye_boom)
	plate(l, PackedVector2Array([Vector2(e.x - 22, -34), Vector2(e.x + 22, -34), Vector2(e.x + 12, e.y + 8),
		Vector2(e.x - 12, e.y + 8)]), PAINT_DARK)
	var tl := _v(rig.arm_cyl.base_boom)
	pin(l, tl, 7.5)
	# steel tubes feeding the arm and bucket circuits (decorative, static)
	for k in [0, 1]:
		var y0: float = -44.0 - k * 6.0
		var pts := PackedVector2Array([Vector2(36, -30 - k * 6), Vector2(150, y0 - 18), Vector2(330, y0 - 40),
			Vector2(500, y0 - 34), Vector2(560, y0 - 10)])
		l.draw_polyline(pts, INK, 5.0, true)
		l.draw_polyline(pts, Color("#5a5047"), 2.6, true)
	pin(l, Vector2.ZERO, 10.0)
	pin(l, Vector2(rig.boom_len, 0), 9.0)

func _draw_arm_extra(l: Node2D) -> void:
	var t := _v(rig.arm_cyl.eye_arm)
	plate(l, PackedVector2Array([Vector2(t.x - 17, -13), Vector2(t.x - 8, -22), Vector2(-6, -27),
		Vector2(20, -12), Vector2(20, 12), Vector2(-6, 26), Vector2(t.x - 8, 21), Vector2(t.x - 17, 12)]), PAINT)
	l.draw_line(Vector2(t.x - 4, -16), Vector2(-4, -21), PAINT.lightened(0.3), 2.0, true)
	pin(l, t, 7.0)
	var c := _v(rig.bucket_cyl.base_arm)
	plate(l, PackedVector2Array([Vector2(c.x - 16, -18), Vector2(c.x + 18, -18), Vector2(c.x + 10, c.y - 9),
		Vector2(c.x - 9, c.y - 9)]), PAINT_DARK)
	pin(l, c, 6.0)
	pin(l, Vector2.ZERO, 9.0)
	pin(l, Vector2(rig.arm_len, 0), 7.0)

func _draw_bucket_extra(l: Node2D) -> void:
	pin(l, k_local, 5.4)
	pin(l, Vector2.ZERO, 6.8)

# ------------------------------------------------------------------------ QA
## Returns an empty array when the pose obeys every rigid-body rule.
func verify(f: Dictionary) -> Array:
	var errs := []
	for pair in [["Lb", rig.boom_cyl], ["La", rig.arm_cyl], ["Lk", rig.bucket_cyl]]:
		var L: float = f[pair[0]]
		var spec: Dictionary = pair[1]
		if L < spec.closed - 0.01 or L > spec.closed + spec.stroke + 0.01:
			errs.append("%s=%.1f outside [%.0f, %.0f]" % [pair[0], L, spec.closed, spec.closed + spec.stroke])
	if not f.link_ok:
		errs.append("bucket four-bar cannot close")
	if absf(f.J.distance_to(f.S) - rig.bucket_cyl.side_len) > 0.05 or absf(f.J.distance_to(f.K) - rig.bucket_cyl.h_len) > 0.05:
		errs.append("link length drift")
	if ready_done:
		if bucket_node.global_position.distance_to(to_global(f.W2)) > 0.05:
			errs.append("bucket hinge detached")
		if arm_node.global_position.distance_to(to_global(f.W1)) > 0.05:
			errs.append("arm elbow detached")
		for n in [boom_node, arm_node, bucket_node]:
			if not n.global_scale.is_equal_approx(global_scale):
				errs.append("%s scaled" % n.name)
	return errs
