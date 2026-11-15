@tool
extends "res://full/full_base.gd"
## SC06 - Xi lanh cần, tay gầu và gầu. Stopped machine, one actuator at a
## time (rod length drives the joint), force arrows along the rod, pins lit;
## Capy's "rubber arm" shown crossed out vs rigid links on pins.

@onready var fx = $World/FX

func setup() -> void:
	callouts = [
		["2 xi lanh cần (cấu hình brochure)", "K1 ✓", Vector2(150, -95), Vector2(-360, -190), M("boom.s"), M("arm.s") - 0.2],
		["Xi lanh tay gầu", "", Vector2(430, -300), Vector2(-120, -170), M("arm.s"), M("bkt.s") - 0.2],
		["Xi lanh gầu + cơ cấu 4 khâu", "", Vector2(560, -60), Vector2(40, -200), M("bkt.s"), M("bkt.e") + 0.5],
		["Dầu vào một khoang tạo lực · khoang kia thoát dầu", "NGUYÊN LÝ", Vector2(150, -95), Vector2(-520, 150), M("oil.s"), M("pin.s") - 0.2],
		["Lực tịnh tiến → quay quanh chốt", "NGUYÊN LÝ", Vector2(0, 0), Vector2(-430, -260), M("pin.s"), M("q.s") - 0.2],
	]

func update(_time: float) -> void:
	if rig:
		rig.housing_alpha = 1.0
	exhaust_load = 0.2

func draw_extra_hud(h: Node2D) -> void:
	if rig == null:
		return
	var f: Dictionary = rig.current()
	var xf: Transform2D = rig.transform
	# Capy's rubber-arm question: a wobbly (wrong) arm crossed out
	var a = clampf((t - M("q.s")) / 0.4, 0, 1) * clampf((M("ks2.s") + 1.0 - t) / 0.4, 0, 1)
	if a > 0.0:
		var p0 = to_screen(xf * Vector2.ZERO)
		var p1 = to_screen(xf * Vector2(f.W2))
		var p2 = to_screen(xf * Vector2(f.T))
		var pts = PackedVector2Array()
		for i in 41:
			var u = i / 40.0
			var base = p0.lerp(p1, u * 2.0) if u < 0.5 else p1.lerp(p2, (u - 0.5) * 2.0)
			pts.append(base + Vector2(0, -150) + Vector2(sin(u * 12.0 + t * 3.0) * 26.0, cos(u * 9.0 + t * 2.0) * 18.0))
		h.draw_polyline(pts, Color(1, 0.6, 0.55, 0.85 * a), 16.0, true)
		var c = pts[20]
		h.draw_line(c + Vector2(-60, -60), c + Vector2(60, 60), Color(1, 0.2, 0.2, a), 10.0, true)
		h.draw_line(c + Vector2(-60, 60), c + Vector2(60, -60), Color(1, 0.2, 0.2, a), 10.0, true)
		h.draw_string(bold, c + Vector2(-170, -80), "SAI: tay máy không uốn cong như cao su", HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Color(1, 0.75, 0.7, a))
	# rigid-links answer: pin-to-pin length on each ram
	var b = clampf((t - M("ks2.s")) / 0.4, 0, 1)
	if b > 0.0:
		for pair in [[f.Bb, f.Eb], [f.Ab, f.Ea], [f.C, f.J]]:
			var s0 = to_screen(xf * Vector2(pair[0]))
			var s1 = to_screen(xf * Vector2(pair[1]))
			var n = (s1 - s0).normalized().orthogonal() * 30.0
			h.draw_line(s0 + n, s1 + n, Color(0.6, 0.9, 1.0, b), 2.0, true)
			h.draw_line(s0, s0 + n * 1.2, Color(0.6, 0.9, 1.0, b), 1.5, true)
			h.draw_line(s1, s1 + n * 1.2, Color(0.6, 0.9, 1.0, b), 1.5, true)
			h.draw_string(bold, (s0 + s1) * 0.5 + n * 1.6 - Vector2(10, 0), "L", HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Color(0.75, 0.95, 1.0, b))
		var txt = "ĐÚNG: khâu cứng quay quanh chốt · L xi lanh = khoảng cách chốt–chốt"
		var w = bold.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 24).x + 30
		h.draw_rect(Rect2(960 - w * 0.5, 880, w, 46), Color(0.05, 0.08, 0.13, 0.9 * b))
		h.draw_rect(Rect2(960 - w * 0.5, 880, 5, 46), Color(0.4, 0.9, 0.5, b))
		h.draw_string(bold, Vector2(975 - w * 0.5, 912), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Color(1, 1, 1, b))

func qa(time: float) -> void:
	if rig == null:
		return
	var f: Dictionary = rig.current()
	for e in rig.verify(f) if rig.has_method("verify") else []:
		qa_report.append("t=%.2f %s" % [time, e])
	if Vector2(f.T).y > 150.0:
		qa_report.append("t=%.2f bucket tip at/below grade" % time)
