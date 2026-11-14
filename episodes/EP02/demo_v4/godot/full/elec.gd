@tool
extends Node2D
## SC12 concept block diagram: engine + hydraulics + electronics.
## Not a wiring diagram (labelled). Green dashed = electronic signal (editorial
## colour, not factory wire colour). `stage` reveals blocks in speaking order.

const Kit = preload("res://cutaway/kit.gd")
const SIG := Color(0.35, 0.95, 0.55)

@export var stage := 0.0
@export var pulse := 0.0
@export_range(0, 1) var hi_epc := 0.0
@export_range(0, 1) var ecu_search := 0.0

var font: Font
var bold: FontVariation

# name, label, rect, colour, stage, tag
var blocks := [
	["monitor", "Màn hình cabin", Rect2(-760, -420, 260, 150), Color("#2b3a55"), 1.0, ""],
	["ecu_e", "Bộ điều khiển động cơ", Rect2(-790, -120, 340, 120), Color("#26303e"), 1.0, ""],
	["ecu_p", "Bộ điều khiển bơm", Rect2(-320, -420, 300, 120), Color("#26303e"), 1.0, ""],
	["engine", "Động cơ", Rect2(-760, 170, 280, 150), Color("#7d848c"), 0.0, ""],
	["pump", "Bơm chính + LS/PC", Rect2(-300, 170, 280, 150), Color("#b04a3a"), 0.0, ""],
	["epc", "Van điện từ EPC", Rect2(-300, -90, 280, 100), Color("#2f6b4a"), 2.0, ""],
	["valve", "Cụm van chính", Rect2(160, 170, 280, 150), Color("#8d98a4"), 0.0, ""],
	["sens", "Cảm biến (tốc độ, áp suất…)", Rect2(140, -420, 370, 120), Color("#26303e"), 1.0, ""],
]

func _ready() -> void:
	font = ThemeDB.fallback_font
	bold = FontVariation.new()
	bold.base_font = font
	bold.variation_embolden = 0.7

func _process(_d: float) -> void:
	queue_redraw()

func R(n: String) -> Rect2:
	for b in blocks:
		if b[0] == n:
			return b[2]
	return Rect2()

func vis(n: String) -> float:
	for b in blocks:
		if b[0] == n:
			return clampf(stage - float(b[4]) + 1.0, 0, 1)
	return 0.0

func _draw() -> void:
	# hydraulic + mechanical links (always): engine -> pump shaft, pump -> valve oil
	_link(R("engine").get_center() + Vector2(140, 0), R("pump").get_center() + Vector2(-140, 0), Color(0.75, 0.78, 0.82), false, 1.0, 10.0)
	_link(R("pump").get_center() + Vector2(140, 0), R("valve").get_center() + Vector2(-140, 0), Kit.RED, false, 1.0, 12.0)
	# signals
	var a1 = vis("ecu_e")
	_link(R("sens").get_center() + Vector2(-150, 0), R("ecu_p").get_center() + Vector2(140, 0), SIG, true, a1)
	_link(R("ecu_e").get_center() + Vector2(0, 60), R("engine").get_center() + Vector2(0, -75), SIG, true, a1)
	_link(R("ecu_e").get_center() + Vector2(0, -60), R("monitor").get_center() + Vector2(0, 75), SIG, true, a1)
	_link(R("monitor").get_center() + Vector2(130, -30), R("ecu_p").get_center() + Vector2(-140, -30), SIG, true, a1)
	_link(R("ecu_e").get_center() + Vector2(140, -20), R("ecu_p").get_center() + Vector2(0, 60), SIG, true, a1)
	_link(R("valve").get_center() + Vector2(0, -75), R("sens").get_center() + Vector2(0, 60), SIG, true, a1)
	var a2 = vis("epc")
	_link(R("ecu_p").get_center() + Vector2(0, 60), R("epc").get_center() + Vector2(0, -50), SIG, true, a2)
	_link(R("epc").get_center() + Vector2(0, 50), R("pump").get_center() + Vector2(0, -75), Kit.ORANGE, false, a2, 8.0)
	for b in blocks:
		var a = vis(b[0])
		if a <= 0.0:
			continue
		var r: Rect2 = b[2]
		var glow = hi_epc if b[0] == "epc" else (ecu_search if b[0].begins_with("ecu") else 0.0)
		if glow > 0.0:
			for k in 4:
				draw_rect(r.grow(6 + k * 6), Color(1, 0.85, 0.3, 0.1 * glow), false, 6.0)
		draw_rect(Rect2(r.position + Vector2(8, 10), r.size), Color(0, 0, 0, 0.35 * a))
		draw_rect(r, Color(b[3], a))
		draw_rect(r, Color(Kit.INK, a), false, 3.0)
		draw_string(bold, r.position + Vector2(16, 40), b[1], HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Color(1, 1, 1, a))
		if b[0] == "monitor":
			var s = Rect2(r.position + Vector2(16, 56), Vector2(r.size.x - 32, 76))
			draw_rect(s, Color(0.1, 0.5, 0.6, a))
			for i in 3:
				draw_rect(Rect2(s.position + Vector2(10 + i * 74, 14), Vector2(60, 48)), Color(0.85, 0.95, 1.0, 0.6 * a), false, 2.0)
		if b[0].begins_with("ecu") or b[0] == "sens":
			for i in 8:
				draw_line(r.position + Vector2(20 + i * 30, r.size.y - 18), r.position + Vector2(20 + i * 30, r.size.y - 4), Color(0.8, 0.8, 0.6, a), 3.0)
		if b[0] == "epc":
			for i in 2:
				var c = r.position + Vector2(70 + i * 140, 70)
				draw_rect(Rect2(c - Vector2(30, 14), Vector2(60, 28)), Color(0.8, 0.5, 0.2, a))
				for k in 6:
					draw_line(c + Vector2(-26 + k * 10, -14), c + Vector2(-26 + k * 10, 14), Color(0.4, 0.2, 0.1, a), 2.0)
			draw_string(font, r.position + Vector2(40, 98), "LS-EPC        PC-EPC", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color(1, 1, 1, a))

func _link(a: Vector2, b: Vector2, col: Color, dashed: bool, k: float, w := 5.0) -> void:
	if k <= 0.01:
		return
	var mid = Vector2(a.x, (a.y + b.y) * 0.5) if absf(a.x - b.x) > 20 and absf(a.y - b.y) > 20 else a
	var pts = PackedVector2Array([a, mid, Vector2(b.x, mid.y), b]) if mid != a else PackedVector2Array([a, b])
	if dashed:
		for i in pts.size() - 1:
			draw_dashed_line(pts[i], pts[i + 1], Color(col, 0.9 * k), w, 14.0)
		# moving pulses
		var L = 0.0
		for i in pts.size() - 1:
			L += pts[i].distance_to(pts[i + 1])
		for j in 3:
			var d = fposmod(pulse * 160.0 + j * L / 3.0, L)
			var acc = 0.0
			for i in pts.size() - 1:
				var l = pts[i].distance_to(pts[i + 1])
				if d <= acc + l and l > 0:
					draw_circle(pts[i].lerp(pts[i + 1], (d - acc) / l), 6.0, Color(col.lightened(0.4), k))
					break
				acc += l
	else:
		draw_polyline(pts, Color(Kit.INK, k), w + 4, true)
		draw_polyline(pts, Color(col, k), w, true)
