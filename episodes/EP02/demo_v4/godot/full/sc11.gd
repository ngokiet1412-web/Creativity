@tool
extends "res://full/full_base.gd"
## SC11 - Van giới hạn áp và an toàn. Bucket stalls on a rock -> pressure
## rises to the relief setting and STOPS rising: the relief poppet lifts and
## the excess flow goes to tank. Brochure relief settings (K1), a concept
## load-holding check valve, and the safety warning.

@export var p_mpa := 5.0          # circuit pressure (MPa)
@onready var fx = $World/FX
const P_SET := 37.3
const ROCK := Vector2(452, 128)

var over: Node2D

func setup() -> void:
	over = Node2D.new()
	over.z_index = 13
	over.z_as_relative = false
	$World.add_child(over)
	over.draw.connect(_draw_rock)
	callouts = []

func update(_time: float) -> void:
	if rig:
		rig.housing_alpha = 1.0
	exhaust_load = clampf(p_mpa / P_SET, 0.2, 1.0)
	over.queue_redraw()

func _draw_rock() -> void:
	var pts = PackedVector2Array([ROCK + Vector2(-70, 30), ROCK + Vector2(-60, -10), ROCK + Vector2(-25, -30), ROCK + Vector2(30, -26), ROCK + Vector2(66, 0), ROCK + Vector2(72, 30)])
	over.draw_colored_polygon(pts, Color("#8b8f96"))
	over.draw_colored_polygon(PackedVector2Array([ROCK + Vector2(-50, -6), ROCK + Vector2(-22, -24), ROCK + Vector2(20, -20), ROCK + Vector2(-10, -4)]), Color("#b4b8be"))
	pts.append(pts[0])
	over.draw_polyline(pts, Kit.INK, 2.6, true)

func relief_lift() -> float:
	return clampf((p_mpa - (P_SET - 1.0)) / 1.0, 0.0, 1.0)

func draw_extra_hud(h: Node2D) -> void:
	var k = clampf((t - M("rv.s")) / 0.5, 0, 1) * clampf((M("warn.s") + 0.4 - t) / 0.5, 0, 1)
	# pressure gauge (always while the bucket is stalled)
	var g = clampf((t - M("q.s") - 1.0) / 0.4, 0, 1) * clampf((M("warn.s") + 0.4 - t) / 0.5, 0, 1)
	if g > 0.0:
		var c = Vector2(250, 300)
		h.draw_circle(c, 120, Color(0.05, 0.08, 0.13, 0.92 * g))
		h.draw_arc(c, 120, 0, TAU, 48, Color(1, 1, 1, g), 3.0, true)
		var a0 = PI * 0.75
		var a1 = PI * 2.25
		h.draw_arc(c, 100, a0 + (a1 - a0) * (P_SET / 45.0) - 0.05, a0 + (a1 - a0) * (P_SET / 45.0) + 0.05, 8, Color(1, 0.3, 0.2, g), 10.0)
		for i in 10:
			var a = a0 + (a1 - a0) * i / 9.0
			h.draw_line(c + Vector2(cos(a), sin(a)) * 104, c + Vector2(cos(a), sin(a)) * 116, Color(1, 1, 1, g), 2.0)
		var an = a0 + (a1 - a0) * clampf(p_mpa / 45.0, 0, 1)
		h.draw_line(c, c + Vector2(cos(an), sin(an)) * 92, Color(1, 0.85, 0.3, g), 5.0, true)
		h.draw_circle(c, 9, Color(1, 0.85, 0.3, g))
		h.draw_string(bold, c + Vector2(-58, 60), ("%.1f MPa" % p_mpa).replace(".", ","), HORIZONTAL_ALIGNMENT_LEFT, -1, 30, Color(1, 1, 1, g))
		h.draw_string(font, c + Vector2(-100, 160), "áp mạch công tác (minh họa)", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color(0.85, 0.9, 0.95, g))
	if k > 0.0:
		_relief(h, Rect2(1180, 130, 700, 380), k)
	var kt = clampf((t - M("tab.s")) / 0.4, 0, 1) * clampf((M("warn.s") + 0.4 - t) / 0.5, 0, 1)
	if kt > 0.0:
		var rows = [["Mạch công tác", "37,3 MPa"], ["Mạch di chuyển", "37,3 MPa"], ["Mạch quay toa", "28,9 MPa"], ["Mạch pilot", "3,2 MPa"]]
		var r = Rect2(1180, 525, 700, 205)
		h.draw_rect(r, Color(0.05, 0.08, 0.13, 0.94 * kt))
		h.draw_string(bold, r.position + Vector2(20, 36), "Áp cài đặt relief danh định — brochure PC200-8", HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color(1, 1, 1, kt))
		h.draw_rect(Rect2(r.end.x - 70, r.position.y + 14, 52, 26), Color(0.2, 0.62, 0.36, kt))
		h.draw_string(bold, Vector2(r.end.x - 62, r.position.y + 34), "K1 ✓", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color(1, 1, 1, kt))
		for i in rows.size():
			var y = r.position.y + 74 + i * 36
			h.draw_string(font, Vector2(r.position.x + 30, y), rows[i][0], HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Color(0.9, 0.93, 0.97, kt))
			h.draw_string(bold, Vector2(r.position.x + 380, y), rows[i][1], HORIZONTAL_ALIGNMENT_LEFT, -1, 26, Color(1, 0.85, 0.4, kt))
	var kh = clampf((t - M("hold.s")) / 0.4, 0, 1) * clampf((M("warn.s") + 0.4 - t) / 0.5, 0, 1)
	if kh > 0.0:
		_holding(h, Rect2(60, 520, 520, 300), kh)
	var kw = clampf((t - M("warn.s")) / 0.4, 0, 1)
	if kw > 0.0:
		var r = Rect2(460, 380, 1000, 200)
		h.draw_rect(r, Color(0.35, 0.05, 0.05, 0.92 * kw))
		h.draw_rect(r, Color(1, 0.8, 0.2, kw), false, 6.0)
		var tri = PackedVector2Array([r.position + Vector2(100, 40), r.position + Vector2(160, 150), r.position + Vector2(40, 150)])
		h.draw_colored_polygon(tri, Color(1, 0.8, 0.2, kw))
		h.draw_string(bold, r.position + Vector2(92, 135), "!", HORIZONTAL_ALIGNMENT_LEFT, -1, 70, Color(0.2, 0.05, 0.05, kw))
		h.draw_string(bold, r.position + Vector2(200, 86), "Không tự nới van relief", HORIZONTAL_ALIGNMENT_LEFT, -1, 40, Color(1, 1, 1, kw))
		h.draw_string(bold, r.position + Vector2(200, 146), "Không sờ đường dầu áp cao để thử", HORIZONTAL_ALIGNMENT_LEFT, -1, 40, Color(1, 1, 1, kw))

## direct-acting relief valve (principle): poppet held on its seat by the
## spring until p·A_seat exceeds the spring force; then it lifts and P -> T
func _relief(h: Node2D, r: Rect2, a: float) -> void:
	h.draw_rect(r, Color(0.04, 0.07, 0.12, 0.95 * a))
	h.draw_rect(r, Color(0.4, 0.6, 0.9, 0.7 * a), false, 3.0)
	h.draw_string(bold, r.position + Vector2(20, 36), "Van giới hạn áp (relief) — nguyên lý", HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Color(1, 1, 1, a))
	var o = r.position + Vector2(330, 230)
	var lift = relief_lift() * 22.0
	# body
	h.draw_rect(Rect2(o + Vector2(-120, -160), Vector2(240, 280)), Color(0.75, 0.78, 0.82, a))
	h.draw_rect(Rect2(o + Vector2(-120, -160), Vector2(240, 280)), Color(Kit.INK, a), false, 3.0)
	# P inlet (bottom, red) and T outlet (right, blue)
	h.draw_rect(Rect2(o + Vector2(-20, 40), Vector2(40, 80)), Color(Kit.RED, a))
	h.draw_rect(Rect2(o + Vector2(-60, -10), Vector2(120, 50)), Color(Kit.BLUE.darkened(0.2), a))
	h.draw_rect(Rect2(o + Vector2(60, -10), Vector2(130, 40)), Color(Kit.BLUE, a))
	h.draw_rect(Rect2(o + Vector2(-20, 40 - 4), Vector2(40, 4)), Color(Kit.RED, a * relief_lift()))
	# poppet (cone) on the seat
	var tip = o + Vector2(0, 40 - lift)
	h.draw_colored_polygon(PackedVector2Array([tip, tip + Vector2(-34, -40), tip + Vector2(34, -40)]), Color(0.85, 0.87, 0.9, a))
	h.draw_polyline(PackedVector2Array([tip, tip + Vector2(-34, -40), tip + Vector2(34, -40), tip]), Color(Kit.INK, a), 2.0, true)
	# spring
	var sp_top = o + Vector2(0, -150)
	var sp_bot = tip + Vector2(0, -40)
	var n = 9
	var pts = PackedVector2Array()
	for i in n * 2 + 1:
		var u = float(i) / (n * 2)
		pts.append(sp_top.lerp(sp_bot, u) + Vector2(26 if i % 2 else -26, 0))
	h.draw_polyline(pts, Color(0.75, 0.82, 0.9, a), 4.0, true)
	# adjusting screw + lock nut (with "do not touch")
	h.draw_rect(Rect2(o + Vector2(-16, -200), Vector2(32, 50)), Color(0.55, 0.58, 0.62, a))
	h.draw_rect(Rect2(o + Vector2(-30, -176), Vector2(60, 16)), Color(0.4, 0.42, 0.46, a))
	h.draw_string(font, o + Vector2(50, -170), "vít chỉnh áp — chỉ thợ có quy trình", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color(1, 0.8, 0.6, a))
	h.draw_string(bold, o + Vector2(-210, 100), "P", HORIZONTAL_ALIGNMENT_LEFT, -1, 30, Color(1, 0.6, 0.5, a))
	h.draw_string(bold, o + Vector2(200, 20), "T", HORIZONTAL_ALIGNMENT_LEFT, -1, 30, Color(0.6, 0.8, 1, a))
	var flow = relief_lift()
	if flow > 0.01:
		for i in 5:
			var u = fposmod(t * 2.0 + i * 0.2, 1.0)
			var p = o + Vector2(-10 + u * 190, 10)
			h.draw_circle(p, 5, Color(1, 1, 1, 0.9 * a * flow))
		h.draw_string(bold, o + Vector2(-200, -60), "mở → dầu dư về thùng", HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color(1, 0.9, 0.5, a * flow))
	else:
		h.draw_string(font, o + Vector2(-200, -60), "đóng (áp < cài đặt)", HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color(0.85, 0.9, 0.95, a))

## concept: check valve keeps the boom cylinder's bottom chamber from
## draining back when the spool is centred (anti-drift / load holding)
func _holding(h: Node2D, r: Rect2, a: float) -> void:
	h.draw_rect(r, Color(0.04, 0.07, 0.12, 0.95 * a))
	h.draw_rect(r, Color(0.4, 0.6, 0.9, 0.7 * a), false, 3.0)
	h.draw_string(bold, r.position + Vector2(16, 32), "Giữ tải / chống trôi cần — khái niệm", HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color(1, 1, 1, a))
	var o = r.position + Vector2(40, 90)
	h.draw_rect(Rect2(o, Vector2(260, 90)), Color(0.9, 0.62, 0.15, a))
	h.draw_rect(Rect2(o + Vector2(10, 12), Vector2(160, 66)), Color(Kit.RED, a))
	h.draw_rect(Rect2(o + Vector2(170, 12), Vector2(16, 66)), Color(0.8, 0.82, 0.85, a))
	h.draw_rect(Rect2(o + Vector2(186, 30), Vector2(170, 30)), Color(0.8, 0.82, 0.85, a))
	h.draw_rect(Rect2(o + Vector2(30, 90), Vector2(30, 70)), Color(Kit.RED, a))
	var bc = o + Vector2(45, 175)
	h.draw_circle(bc, 18, Color(0.9, 0.92, 0.95, a))
	h.draw_line(bc + Vector2(-26, 22), bc + Vector2(26, 22), Color(Kit.INK, a), 4.0)
	h.draw_string(font, o + Vector2(90, 190), "van một chiều giữ dầu khoang đáy", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color(0.9, 0.93, 0.97, a))
	h.draw_string(font, o + Vector2(200, 130), "tải (cần) không tự hạ", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color(1, 0.85, 0.5, a))
