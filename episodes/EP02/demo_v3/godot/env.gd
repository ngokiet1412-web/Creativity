@tool
extends Node2D
## Background plate, ground shadow, x-ray dimming (behind the machine) and a
## front layer with the soil mound, falling soil and exhaust. All effects are
## pure functions of time so frames can be rendered in any order.

const SOIL := Color("#b8743d")
const SOIL_DARK := Color("#7d4a24")
const SOIL_LIGHT := Color("#d79a5c")
const GRAVITY := 981.0      # px/s^2 at 100 px = 1 m

var plate: Texture2D
var front: Node2D
var director: Node
var rig_cfg: Dictionary
var ground := 158.49
var _bite_cache := {}

func _ready() -> void:
	director = get_parent().get_parent()
	rig_cfg = JSON.parse_string(FileAccess.get_file_as_string("res://art/rig.json"))
	ground = rig_cfg.ground_y
	var img = Image.load_from_file(ProjectSettings.globalize_path("res://art/worksite.png"))
	img.generate_mipmaps()
	plate = ImageTexture.create_from_image(img)
	z_index = -10
	z_as_relative = false
	texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	front = get_node_or_null("Front")
	if front == null:
		front = Node2D.new()
		front.name = "Front"
		add_child(front)
	front.z_index = 12
	front.z_as_relative = false
	front.draw.connect(_draw_front)
	front.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR

func _process(_d: float) -> void:
	front.queue_redraw()

func _draw() -> void:
	# painted plate, uniform scale 1.5, anchored so its dirt yard carries the tracks
	draw_texture_rect(plate, Rect2(Vector2(-1200, -735), plate.get_size() * 1.5), false)
	var m = _machine_x()
	draw_set_transform(Vector2(m - 170, ground + 2), 0.0, Vector2(1.0, 0.16))
	draw_circle(Vector2.ZERO, 270.0, Color(0.15, 0.08, 0.03, 0.22), true, -1, true)
	draw_set_transform(Vector2.ZERO)
	var xr: float = director.xray if director else 0.0
	var dim = maxf(xr * 0.72, director.cutaway * 0.45 if director and director.cam_zoom > 1.5 else 0.0)
	if dim > 0.0:
		draw_rect(Rect2(-4000, -3000, 8000, 6000), Color(0.03, 0.06, 0.12, dim))

func _machine_x() -> float:
	return 0.0

# ------------------------------------------------------------------- mound
func mound_profile(t: float) -> PackedVector2Array:
	var md: Dictionary = rig_cfg.mound
	var pts = PackedVector2Array()
	var bite = _bite(t)
	var x: float = md.x0
	var i = 0
	while x <= md.x1 + 0.1:
		var u: float = (x - md.peak_x) / ((md.x1 - md.x0) * 0.5)
		var h: float = md.peak_h * pow(maxf(0.0, 1.0 - u * u), 1.2)
		h += 3.0 * sin(x * 0.11) * maxf(0.0, 1.0 - absf(u))
		var y = ground - h
		y = maxf(y, bite[i] if i < bite.size() else y)
		y = minf(y, ground - 1.5)
		pts.append(Vector2(x, y))
		x += 5.0
		i += 1
	return pts

func _bite(t: float) -> PackedFloat32Array:
	## lowest surface reached by the bucket teeth so far (carves the mound)
	var md: Dictionary = rig_cfg.mound
	var n = int((md.x1 - md.x0) / 5.0) + 2
	var key = snappedf(minf(t, 9.4), 1.0 / 30.0)
	if _bite_cache.has(key):
		return _bite_cache[key]
	var out = PackedFloat32Array()
	out.resize(n)
	out.fill(-1e9)
	var s = 4.0
	var rig = director.rig
	while s <= key:
		var f: Dictionary = director.pose_at(s)
		for lp in [Vector2(-330, 195), Vector2(-300, 215), Vector2(-250, 230), Vector2(-150, 250)]:
			var p: Vector2 = rig.bucket_point(lp, f)
			var k = int(round((p.x - md.x0) / 5.0))
			for dk in range(-3, 4):
				var j = k + dk
				if j >= 0 and j < n:
					out[j] = maxf(out[j], p.y + absf(dk) * 2.5)
		s += 1.0 / 15.0
	_bite_cache[key] = out
	return out

# ------------------------------------------------------------- front layer
func _draw_front() -> void:
	var c = front
	if director == null:
		return
	var t: float = director.t
	var shade = 1.0 - 0.6 * maxf(director.xray, director.cutaway * 0.7)
	var prof = mound_profile(t)
	var md: Dictionary = rig_cfg.mound
	var poly = PackedVector2Array([Vector2(md.x0 - 30, ground + 2)])
	poly.append_array(prof)
	poly.append(Vector2(md.x1 + 30, ground + 2))
	# occluder below grade (feathered) keeps buried teeth hidden
	c.draw_colored_polygon(PackedVector2Array([Vector2(md.x0 - 10, ground - 2), Vector2(md.x1 + 10, ground - 2),
		Vector2(md.x1 - 10, ground + 40), Vector2(md.x0 + 10, ground + 40)]), Color(SOIL.darkened(0.12), shade))
	for k in 6:
		var y = ground + 40 + k * 3.0
		c.draw_line(Vector2(md.x0 + 10 + k * 3, y), Vector2(md.x1 - 10 - k * 3, y), Color(SOIL.darkened(0.12), shade * (1.0 - k / 6.0)), 3.0)
	c.draw_colored_polygon(poly, Color(SOIL, shade).darkened(0.05))
	# lighter crest + clods + outline
	var crest = PackedVector2Array()
	for p in prof:
		crest.append(p + Vector2(0, 5))
	c.draw_polyline(crest, Color(SOIL_LIGHT, 0.75 * shade), 4.0, true)
	c.draw_polyline(prof, Color(SOIL_DARK.darkened(0.2), shade), 2.6, true)
	var rng = RandomNumberGenerator.new()
	rng.seed = 7
	for i in 26:
		var x = rng.randf_range(md.x0 + 12, md.x1 - 12)
		var top = _surface_at(prof, x)
		var y = rng.randf_range(top + 8, ground + 10)
		var r = rng.randf_range(2.5, 5.5)
		c.draw_circle(Vector2(x, y), r, Color(SOIL_DARK, 0.55 * shade), true, -1, true)
		c.draw_circle(Vector2(x - 0.8, y - 0.8), r * 0.5, Color(SOIL_LIGHT, 0.5 * shade), true, -1, true)
	_draw_crumbs(c, t, shade)
	_draw_exhaust(c, t, shade)

func _surface_at(prof: PackedVector2Array, x: float) -> float:
	for i in prof.size() - 1:
		if prof[i].x <= x and x <= prof[i + 1].x:
			return lerpf(prof[i].y, prof[i + 1].y, (x - prof[i].x) / (prof[i + 1].x - prof[i].x))
	return ground

## Soil clods leave the bucket lip with the lip's velocity, then fall under
## gravity and settle on the ground.
func _draw_crumbs(c, t: float, shade: float) -> void:
	var rng = RandomNumberGenerator.new()
	rng.seed = 2026
	var rig = director.rig
	var bursts = [[8.2, 9.7, 16], [23.6, 26.5, 4], [27.6, 30.2, 5], [31.0, 33.5, 2]]
	for burst in bursts:
		for i in int(burst[2]):
			var te: float = rng.randf_range(burst[0], burst[1])
			var lp = Vector2(rng.randf_range(-320, -210), rng.randf_range(140, 190))
			var r = rng.randf_range(2.2, 4.8)
			var jx = rng.randf_range(-25, 25)
			if t < te:
				continue
			var f0: Dictionary = director.pose_at(te)
			var f1: Dictionary = director.pose_at(te + 1.0 / 30.0)
			var p0: Vector2 = rig.bucket_point(lp, f0)
			var v0: Vector2 = (rig.bucket_point(lp, f1) - p0) * 30.0 + Vector2(jx, -10)
			var dt = t - te
			var floor_y = ground + 4.0 - r
			# time to land: solve p0.y + v0.y dt + g/2 dt^2 = floor
			var a = 0.5 * GRAVITY
			var disc = v0.y * v0.y - 4.0 * a * (p0.y - floor_y)
			var t_land = (-v0.y + sqrt(maxf(disc, 0.0))) / (2.0 * a)
			var p: Vector2
			var alpha = shade
			if dt < t_land:
				p = p0 + v0 * dt + Vector2(0, a * dt * dt)
			else:
				p = p0 + v0 * t_land + Vector2(0, a * t_land * t_land)
				p.y = floor_y
				alpha *= clampf(1.0 - (dt - t_land - 1.5) / 1.0, 0.0, 1.0)
			if alpha <= 0.0:
				continue
			c.draw_circle(p, r + 0.9, Color(SOIL_DARK.darkened(0.3), alpha), true, -1, true)
			c.draw_circle(p, r, Color(SOIL, alpha), true, -1, true)
			c.draw_circle(p - Vector2(0.7, 0.9), r * 0.45, Color(SOIL_LIGHT, alpha), true, -1, true)

## Exhaust puffs from the stack; denser while the pump is loaded.
func _draw_exhaust(c, t: float, shade: float) -> void:
	if t < 4.0:
		return
	var stack = Vector2(-247, -86)
	for i in 14:
		var period = 0.42
		var born = floor(t / period) * period - i * period
		var age = t - born
		if age > 2.6 or born < 3.0:
			continue
		var st: Dictionary = director.hydraulic_state(born)
		var load: float = 0.35 + 0.65 * st.swash
		var drift = Vector2(-14 * age, -58 * age + 9 * age * age)
		var r = 5.0 + 16.0 * age
		var a = 0.20 * load * (1.0 - age / 2.6) * shade
		c.draw_circle(stack + drift + Vector2(sin(born * 7.0) * 4.0, 0), r, Color(0.32, 0.31, 0.30, a), true, -1, true)

# ---------------------------------------------------------------------- QA
func ground_check(f: Dictionary) -> Array:
	var errs = []
	var md: Dictionary = rig_cfg.mound
	var rig = director.rig
	for hp in rig_cfg.bucket_hull_px:
		var p: Vector2 = rig.bucket_point(Vector2(hp[0], hp[1]), f)
		var inside: bool = p.x > md.x0 and p.x < md.x1
		var limit = ground + (38.0 if inside else 1.5)
		if p.y > limit:
			errs.append("bucket below grade by %.1f px at x=%.0f" % [p.y - limit, p.x])
			break
	return errs
