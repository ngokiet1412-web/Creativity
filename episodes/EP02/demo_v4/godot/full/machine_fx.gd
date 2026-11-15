@tool
extends Node2D
## Overlays on the shared machine rig (child of World, next to World/Machine):
##  - soil load heaped in the bucket opening (load 0..1)
##  - highlight glow on cylinders / pins / links (for SC02, SC06, SC07)
##  - force arrows along a cylinder axis and rotation arcs about a joint pin
## Everything is computed from rig.current() each frame, so overlays stay
## glued to the moving links.

const SOIL := Color("#b8743d")
const SOIL_DARK := Color("#7d4a24")
const SOIL_LIGHT := Color("#d79a5c")

@export_range(0, 1) var soil := 0.0
@export_range(0, 1) var hi_boom := 0.0
@export_range(0, 1) var hi_arm := 0.0
@export_range(0, 1) var hi_bucket := 0.0
@export_range(0, 1) var force_arrows := 0.0
@export_range(0, 1) var pins := 0.0
@export var hi_color := Color(0.45, 0.92, 1.0)

var rig

func _ready() -> void:
	z_index = 11
	z_as_relative = false
	rig = get_parent().get_node_or_null("Machine")

func _process(_d: float) -> void:
	queue_redraw()

func _draw() -> void:
	if rig == null or not rig.ready_done:
		return
	var f: Dictionary = rig.current()
	var xf: Transform2D = rig.transform
	draw_set_transform_matrix(xf)
	if soil > 0.01:
		_soil(f)
	for item in [[hi_boom, f.Bb, f.Eb], [hi_arm, f.Ab, f.Ea], [hi_bucket, f.C, f.J]]:
		var k: float = item[0]
		if k > 0.01:
			_glow(item[1], item[2], k)
		if force_arrows > 0.01:
			_arrow(item[1], item[2], force_arrows)
	if pins > 0.01:
		for p in [Vector2.ZERO, f.W1, f.W2, f.Bb, f.Eb, f.Ab, f.Ea, f.C, f.J, f.S, f.K]:
			draw_circle(p, 9.0, Color(1, 1, 1, 0.0), false, 2.0)
			draw_arc(p, 11.0, 0, TAU, 20, Color(hi_color, 0.9 * pins), 2.5, true)
	draw_set_transform(Vector2.ZERO)

func _glow(a: Vector2, b: Vector2, k: float) -> void:
	for w in [30.0, 20.0, 12.0]:
		draw_line(a, b, Color(hi_color, 0.16 * k), w, true)
	draw_line(a, b, Color(1, 1, 1, 0.7 * k), 3.0, true)

func _arrow(a: Vector2, b: Vector2, k: float) -> void:
	var d = (b - a).normalized()
	var tip = b + d * 50.0
	var c = Color(1.0, 0.3, 0.2, k)
	draw_line(b - d * 30.0, tip, Color(0.1, 0.05, 0.05, 0.6 * k), 11.0, true)
	draw_line(b - d * 30.0, tip, c, 7.0, true)
	var n = Vector2(-d.y, d.x)
	draw_colored_polygon(PackedVector2Array([tip + d * 20.0, tip + n * 13.0, tip - n * 13.0]), c)

## soil heaped over the bucket opening: lip (teeth) -> back plate, bulging outwards
func _soil(f: Dictionary) -> void:
	var lip: Vector2 = rig.bucket_point(Vector2(-318, 186), f)
	var back: Vector2 = rig.bucket_point(Vector2(-40, 18), f)
	var mid: Vector2 = rig.bucket_point(Vector2(-150, 60), f)
	var inner: Vector2 = rig.bucket_point(Vector2(-120, 140), f)
	var n = (mid - inner).normalized()
	var pts = PackedVector2Array()
	var h = 46.0 * soil
	for i in 21:
		var u = i / 20.0
		var p = lip.lerp(back, u) + n * (h * sin(PI * u) * (1.0 + 0.12 * sin(u * 23.0)))
		pts.append(p)
	pts.append(inner)
	if not Geometry2D.triangulate_polygon(pts).is_empty():
		draw_colored_polygon(pts, SOIL.darkened(0.05))
	var crest = PackedVector2Array()
	for i in 21:
		crest.append(pts[i] - n * 5.0)
	draw_polyline(crest, Color(SOIL_LIGHT, 0.8), 4.0, true)
	draw_polyline(pts.slice(0, 21), SOIL_DARK.darkened(0.25), 2.6, true)
	var rng = RandomNumberGenerator.new()
	rng.seed = 11
	for i in 14:
		var u = rng.randf_range(0.08, 0.92)
		var p = lip.lerp(back, u) + n * (h * sin(PI * u) * rng.randf_range(0.2, 0.85))
		var r = rng.randf_range(3.0, 6.5)
		draw_circle(p, r, Color(SOIL_DARK, 0.6), true, -1, true)
		draw_circle(p - Vector2(1, 1), r * 0.45, Color(SOIL_LIGHT, 0.6), true, -1, true)
