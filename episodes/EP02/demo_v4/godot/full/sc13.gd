@tool
extends "res://full/full_base.gd"
## SC13 - Tại sao máy lại chậm / yếu? Four hypothesis groups with small
## animations, then "compare the symptom across functions" and the safety
## rule: measure per procedure, don't swap the pump because the machine is slow.

func update(_time: float) -> void:
	if rig:
		rig.housing_alpha = 1.0
	exhaust_load = 0.15

func _card(h: Node2D, r: Rect2, title: String, a: float, idx: int) -> void:
	h.draw_rect(Rect2(r.position + Vector2(6, 8), r.size), Color(0, 0, 0, 0.35 * a))
	h.draw_rect(r, Color(0.05, 0.08, 0.13, 0.94 * a))
	h.draw_rect(Rect2(r.position, Vector2(r.size.x, 6)), Color(1, 0.78, 0.25, a))
	h.draw_string(bold, r.position + Vector2(18, 44), title, HORIZONTAL_ALIGNMENT_LEFT, r.size.x - 30, 24, Color(1, 1, 1, a))
	var c = r.position + Vector2(r.size.x * 0.5, 150)
	var tt = t * 1.0
	match idx:
		0:  # engine power: tach needle sagging under load
			h.draw_arc(c, 60, PI * 0.8, PI * 2.2, 32, Color(1, 1, 1, a), 3.0, true)
			var v = 0.75 - 0.25 * (0.5 + 0.5 * sin(tt * 1.6))
			var an = PI * 0.8 + PI * 1.4 * v
			h.draw_line(c, c + Vector2(cos(an), sin(an)) * 52, Color(1, 0.4, 0.3, a), 5.0, true)
			h.draw_string(font, c + Vector2(-40, 40), "vòng/phút", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color(0.85, 0.9, 0.95, a))
		1:  # pump control: swash plate tilting + LS signal wave
			var ang = 0.25 * sin(tt * 1.3)
			var d = Vector2(cos(ang + PI * 0.5), sin(ang + PI * 0.5)) * 55
			h.draw_line(c - d, c + d, Color(0.85, 0.87, 0.9, a), 12.0, true)
			var pts = PackedVector2Array()
			for i in 40:
				pts.append(c + Vector2(-90 + i * 4.5, 70 + sin(i * 0.5 + tt * 4.0) * 8))
			h.draw_polyline(pts, Color(Kit.PURPLE, a), 3.0, true)
		2:  # valve / pilot / internal leakage: spool with drip
			h.draw_rect(Rect2(c + Vector2(-90, -24), Vector2(180, 48)), Color(0.7, 0.74, 0.8, a))
			h.draw_rect(Rect2(c + Vector2(-60 + 12 * sin(tt), -16), Vector2(120, 32)), Color(0.45, 0.5, 0.56, a))
			var dy = fposmod(tt * 60.0, 70.0)
			h.draw_circle(c + Vector2(40, 30 + dy), 6, Color(Kit.RED, a * (1.0 - dy / 70.0)))
		3:  # oil / filter / temperature / mechanical friction
			h.draw_rect(Rect2(c + Vector2(-80, -60), Vector2(22, 110)), Color(1, 1, 1, 0.3 * a))
			var lv = 0.5 + 0.4 * (0.5 + 0.5 * sin(tt * 0.9))
			h.draw_rect(Rect2(c + Vector2(-76, 46 - 100 * lv), Vector2(14, 100 * lv)), Color(1, 0.35, 0.2, a))
			h.draw_circle(c + Vector2(-69, 56), 14, Color(1, 0.35, 0.2, a))
			h.draw_rect(Rect2(c + Vector2(10, -50), Vector2(70, 100)), Color(0.9, 0.85, 0.6, a))
			for k in 8:
				h.draw_line(c + Vector2(16 + k * 8, -44), c + Vector2(16 + k * 8, 44), Color(0.3, 0.2, 0.1, a), 2.0)
			for k in 12:
				h.draw_circle(c + Vector2(14 + (k * 23) % 60, -40 + (k * 37) % 84), 3, Color(0.15, 0.1, 0.05, a))

func draw_extra_hud(h: Node2D) -> void:
	var titles = ["Động cơ thiếu công suất", "Bơm / điều khiển bơm / LS", "Van, pilot, rò rỉ bên trong", "Dầu, lọc, nhiệt độ, ma sát"]
	var k_all = clampf((M("cmp.s") + 0.3 - t) / 0.4, 0, 1)
	for i in 4:
		var a = clampf((t - M("h.s") - i * 1.6) / 0.4, 0, 1) * k_all
		if a > 0.0:
			_card(h, Rect2(150 + i * 410, 150, 390, 250), titles[i], a, i)
	var kc = clampf((t - M("cmp.s")) / 0.4, 0, 1) * clampf((M("rule.s") + 0.3 - t) / 0.4, 0, 1)
	if kc > 0.0:
		var r = Rect2(330, 140, 1260, 330)
		h.draw_rect(r, Color(0.05, 0.08, 0.13, 0.94 * kc))
		h.draw_string(bold, r.position + Vector2(24, 44), "So sánh biểu hiện giữa các chức năng", HORIZONTAL_ALIGNMENT_LEFT, -1, 28, Color(1, 1, 1, kc))
		var funcs = ["Nâng cần", "Co tay gầu", "Quay toa", "Chạy xích"]
		for i in 4:
			var x = r.position.x + 30 + i * 300
			h.draw_rect(Rect2(x, r.position.y + 80, 280, 110), Color(0.12, 0.17, 0.25, kc))
			h.draw_string(bold, Vector2(x + 18, r.position.y + 124), funcs[i], HORIZONTAL_ALIGNMENT_LEFT, -1, 26, Color(1, 1, 1, kc))
			var bar = 0.35 + 0.6 * (0.5 + 0.5 * sin(t * 1.2 + i * 1.7))
			h.draw_rect(Rect2(x + 18, r.position.y + 150, 240 * bar, 18), Color(0.55, 0.85, 1.0, kc))
		h.draw_string(font, r.position + Vector2(30, 240), "Cùng chậm ở mọi chức năng → nghĩ tới phần dùng chung (động cơ, bơm, điều khiển)", HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Color(0.9, 0.93, 0.97, kc))
		h.draw_string(font, r.position + Vector2(30, 284), "Chỉ một chức năng chậm → nghĩ tới nhánh / cơ cấu đó  (gợi ý khoanh vùng, phải đo)", HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Color(0.9, 0.93, 0.97, kc))
	var kr = clampf((t - M("rule.s")) / 0.4, 0, 1)
	if kr > 0.0:
		var r = Rect2(430, 170, 1060, 190)
		h.draw_rect(r, Color(0.05, 0.08, 0.13, 0.95 * kr))
		h.draw_rect(Rect2(r.position, Vector2(6, r.size.y)), Color(0.4, 0.9, 0.5, kr))
		h.draw_string(bold, r.position + Vector2(30, 70), "✓ Đo & đối chiếu theo quy trình an toàn", HORIZONTAL_ALIGNMENT_LEFT, -1, 34, Color(1, 1, 1, kr))
		h.draw_string(bold, r.position + Vector2(30, 140), "✗ Không thay bơm chỉ vì thấy máy chậm", HORIZONTAL_ALIGNMENT_LEFT, -1, 34, Color(1, 0.6, 0.55, kr))
