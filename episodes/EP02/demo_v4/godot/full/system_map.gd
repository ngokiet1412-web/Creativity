@tool
extends Node2D
## SC02 / SC14 system map drawn over the x-rayed machine (child of World).
## Component symbols sit at ILLUSTRATIVE relative positions (labelled
## "vị trí minh họa"), not a PC200-8 layout drawing. `step` lights them one by
## one; `chain` runs the energy chain engine -> pumps -> valve -> cylinder.

const Kit = preload("res://cutaway/kit.gd")

@export var step := -1.0
@export_range(0, 1) var chain := 0.0
@export_range(0, 1) var alpha := 1.0
@export var chain_travel := 0.0

var rig
var font: Font
var bold: FontVariation

# name, label, centre (machine px), kind, order, tag
var comps := [
	["engine", "Động cơ SAA6D107E-1", Vector2(-262, -62), "engine", 0, "K1 ✓"],
	["pumps", "2 bơm chính (HPV95+95)", Vector2(-150, -40), "pumps", 1, "K2 ✓"],
	["tank", "Bình dầu thủy lực", Vector2(-40, -112), "tank", 2, ""],
	["valve", "Cụm van điều khiển chính", Vector2(-62, -18), "valve", 3, "K2 ✓"],
	["cyl", "Xi lanh cần · tay gầu · gầu", Vector2(120, -120), "cyl", 4, ""],
	["swing", "Mô tơ quay toa", Vector2(-120, 30), "motor", 5, ""],
	["travel", "2 mô tơ di chuyển", Vector2(-350, 112), "motor", 6, ""],
	["cooler", "Két làm mát dầu", Vector2(-372, -76), "cooler", 7, ""],
	["filter", "Lọc dầu hồi", Vector2(-40, -150), "filter", 8, ""],
]

func _ready() -> void:
	z_index = 13
	z_as_relative = false
	rig = get_parent().get_node_or_null("Machine")
	font = ThemeDB.fallback_font
	bold = FontVariation.new()
	bold.base_font = font
	bold.variation_embolden = 0.7

func _process(_d: float) -> void:
	queue_redraw()

func pos(name: String) -> Vector2:
	for c in comps:
		if c[0] == name:
			return c[2]
	return Vector2.ZERO

func _draw() -> void:
	if alpha <= 0.01 or rig == null:
		return
	draw_set_transform_matrix(rig.transform)
	for c in comps:
		var lit = clampf(step - float(c[4]) + 1.0, 0.0, 1.0)
		if lit <= 0.0:
			continue
		var cur = clampf(1.0 - absf(step - float(c[4]) - 0.5) * 1.2, 0.0, 1.0)
		_symbol(c[3], c[2], lit * alpha, cur)
	_chain()
	# labels last (on top)
	for c in comps:
		var lit = clampf(step - float(c[4]) + 1.0, 0.0, 1.0)
		var cur = clampf(1.6 - absf(step - float(c[4]) - 0.5) * 1.1, 0.0, 1.0)
		if lit > 0.0 and cur > 0.0:
			_label(c[1], c[5], c[2], cur * alpha)
	draw_set_transform(Vector2.ZERO)

func _label(text: String, tag: String, p: Vector2, a: float) -> void:
	var size = 17
	var w = bold.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x + 16
	var tw = 0.0
	if tag != "":
		tw = bold.get_string_size(tag, HORIZONTAL_ALIGNMENT_LEFT, -1, 12).x + 12
	var bp = p + Vector2(-w * 0.5 - tw * 0.5, -70)
	draw_line(p + Vector2(0, -20), bp + Vector2((w + tw) * 0.5, 26), Color(1, 1, 1, 0.8 * a), 1.6, true)
	draw_rect(Rect2(bp, Vector2(w + tw, 26)), Color(0.05, 0.08, 0.13, 0.9 * a))
	draw_rect(Rect2(bp, Vector2(3, 26)), Color(1, 0.78, 0.25, a))
	draw_string(bold, bp + Vector2(9, 19), text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, Color(1, 1, 1, a))
	if tag != "":
		draw_rect(Rect2(bp + Vector2(w, 5), Vector2(tw - 4, 16)), Color(0.2, 0.62, 0.36, a))
		draw_string(bold, bp + Vector2(w + 5, 18), tag, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color(1, 1, 1, a))

func _glow(p: Vector2, r: float, a: float) -> void:
	for k in 4:
		draw_circle(p, r + k * 7.0, Color(1, 0.82, 0.3, 0.07 * a), true, -1, true)

func _symbol(kind: String, p: Vector2, a: float, cur: float) -> void:
	if cur > 0.0:
		_glow(p, 30.0, cur)
	var ink = Color(Kit.INK, a)
	match kind:
		"engine":
			var r = Rect2(p - Vector2(70, 34), Vector2(140, 68))
			draw_rect(r, Color(0.55, 0.58, 0.62, a))
			for i in 6:
				draw_rect(Rect2(r.position + Vector2(8 + i * 22, -14), Vector2(18, 16)), Color(0.4, 0.43, 0.48, a))
				draw_rect(Rect2(r.position + Vector2(8 + i * 22, -14), Vector2(18, 16)), ink, false, 1.5)
			draw_rect(r, ink, false, 2.0)
			draw_circle(r.position + Vector2(140, 44), 16, Color(0.35, 0.37, 0.4, a))
			draw_arc(r.position + Vector2(140, 44), 16, 0, TAU, 20, ink, 1.5, true)
		"pumps":
			for dx in [-16.0, 16.0]:
				var c = p + Vector2(dx, 0)
				draw_circle(c, 15, Color(0.75, 0.3, 0.25, a))
				draw_arc(c, 15, 0, TAU, 20, ink, 1.8, true)
				draw_colored_polygon(PackedVector2Array([c + Vector2(-7, 6), c + Vector2(7, 6), c + Vector2(0, -8)]), Color(1, 1, 1, a))
				draw_line(c + Vector2(-12, 12), c + Vector2(12, -12), Color(1, 1, 1, a), 1.5, true)
		"tank":
			var r = Rect2(p - Vector2(34, 38), Vector2(68, 76))
			draw_rect(r, Color(0.2, 0.32, 0.5, a))
			draw_rect(Rect2(r.position + Vector2(3, 26), Vector2(62, 47)), Color(Kit.BLUE, a))
			for k in 3:
				draw_line(r.position + Vector2(8 + k * 18, 32 + (k % 2) * 4), r.position + Vector2(18 + k * 18, 32 + (k % 2) * 4), Color(1, 1, 1, 0.5 * a), 1.5)
			draw_rect(r, ink, false, 2.0)
		"valve":
			var r = Rect2(p - Vector2(46, 22), Vector2(92, 44))
			draw_rect(r, Color(0.62, 0.66, 0.7, a))
			for i in 6:
				draw_rect(Rect2(r.position + Vector2(5 + i * 14.5, 6), Vector2(11, 32)), Color(0.42, 0.46, 0.52, a))
			draw_rect(r, ink, false, 2.0)
		"cyl":
			pass   # the machine_fx glow highlights the real cylinders
		"motor":
			draw_circle(p, 18, Color(0.45, 0.5, 0.58, a))
			draw_arc(p, 18, 0, TAU, 24, ink, 1.8, true)
			draw_arc(p, 10, -PI * 0.2, PI * 1.3, 16, Color(1, 1, 1, a), 2.0, true)
			var e = p + Vector2(cos(PI * 1.3), sin(PI * 1.3)) * 10
			draw_colored_polygon(PackedVector2Array([e + Vector2(-5, 0), e + Vector2(4, -4), e + Vector2(3, 5)]), Color(1, 1, 1, a))
		"cooler":
			var r = Rect2(p - Vector2(14, 44), Vector2(28, 88))
			draw_rect(r, Color(0.5, 0.55, 0.6, a))
			for k in 10:
				draw_line(r.position + Vector2(2, 6 + k * 8), r.position + Vector2(26, 6 + k * 8), ink, 1.2)
			draw_rect(r, ink, false, 2.0)
		"filter":
			var r = Rect2(p - Vector2(12, 20), Vector2(24, 40))
			draw_rect(r, Color(0.85, 0.8, 0.6, a))
			for k in 5:
				draw_line(r.position + Vector2(4 + k * 4, 3), r.position + Vector2(4 + k * 4, 37), Color(0.5, 0.4, 0.2, a), 1.2)
			draw_rect(r, ink, false, 2.0)

## energy chain: engine -> pumps -> valve -> boom cylinder (pulses on a path)
func _chain() -> void:
	if chain <= 0.01:
		return
	var f: Dictionary = rig.current()
	var pts = PackedVector2Array([pos("engine") + Vector2(70, 10), pos("pumps"), pos("valve"), Vector2(f.Bb), (Vector2(f.Bb) + Vector2(f.Eb)) * 0.5])
	var cols = [Color(0.6, 0.65, 0.7), Kit.RED, Kit.RED, Kit.RED]
	var total = 0.0
	for i in pts.size() - 1:
		total += pts[i].distance_to(pts[i + 1])
	var shown = total * chain
	var acc = 0.0
	for i in pts.size() - 1:
		var l = pts[i].distance_to(pts[i + 1])
		if acc >= shown:
			break
		var u = clampf((shown - acc) / l, 0, 1)
		var b = pts[i].lerp(pts[i + 1], u)
		draw_line(pts[i], b, Color(cols[i], 0.9 * alpha), 6.0, true)
		# pulses
		var d = fposmod(chain_travel, 30.0)
		while d < l * u:
			var q = pts[i].lerp(pts[i + 1], d / l)
			draw_circle(q, 4.0, Color(1, 1, 1, 0.8 * alpha), true, -1, true)
			d += 30.0
		acc += l
