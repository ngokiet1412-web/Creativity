@tool
extends "res://full/full_base.gd"
## SC07 - Áp suất, lưu lượng và lực thật. Section of the boom cylinder (same
## drawing as SC05 V4.2) whose rod travel IS the machine's boom-cylinder
## length change; F ≈ p·A, v ≈ Q/A, then the lever arm d about the boom foot
## pin (computed from the pins) and "force at the teeth ≠ piston force".

const CylV42 = preload("res://cutaway/cyl_v42.gd")
const A0 := Vector2(-1330, -330)
const L0 := 220.0          # boom cylinder closed length (rig.json)
const STROKE := 133.4

var over: Node2D

func setup() -> void:
	over = Node2D.new()
	over.z_index = 14
	over.z_as_relative = false
	add_child(over)
	over.draw.connect(_draw_over)
	callouts = [
		["Xi lanh lý tưởng: chưa tính ma sát, áp hồi, tổn thất", "NGUYÊN LÝ", A0 + Vector2(260, 70), Vector2(-120, 130), M("f.s"), M("lever.s")],
		["d = tay đòn quanh chốt chân cần (tính từ chốt)", "NGUYÊN LÝ", Vector2(0, 0), Vector2(-420, 190), M("lever.s") + 0.6, M("q2.s")],
	]

func ext() -> float:
	if rig == null:
		return 0.0
	return (float(rig.current().Lb) - L0) / STROKE * 300.0

func _draw() -> void:
	super._draw()
	var f = rig.current() if rig else {}
	var vel = 0.0
	if rig:
		var b0 = sample("World/Machine:boom_deg", t - 1.0 / 30.0)
		var b1 = sample("World/Machine:boom_deg", t)
		vel = clampf(absf(b1 - b0) * 30.0 / 4.0, 0.0, 1.0)
	var tr = integrate(func(s): return clampf(absf(sample("World/Machine:boom_deg", s) - sample("World/Machine:boom_deg", s - 1.0 / 30.0)) * 30.0 / 4.0, 0, 1), t) * 60.0
	var panel = Rect2(A0 + Vector2(-140, -140), Vector2(1020, 700))
	draw_rect(panel, Color(0.04, 0.07, 0.12, 0.92))
	draw_rect(panel, Color(0.4, 0.6, 0.9, 0.5), false, 3.0)
	var gx = panel.position.x + 40
	while gx < panel.end.x:
		draw_line(Vector2(gx, panel.position.y), Vector2(gx, panel.end.y), Color(0.35, 0.5, 0.75, 0.08), 1.0)
		gx += 40
	CylV42.draw(self, font, A0, ext(), vel, tr, tr * CylV42.AREA_RATIO, 0.9)
	Kit.label(self, font, A0 + Vector2(40, -86), "xi lanh cần (mặt cắt) — hành trình = xi lanh trên máy", 26)
	# port stubs with flow arrows
	Kit.pipe(self, PackedVector2Array([A0 + Vector2(40, 60), A0 + Vector2(40, 190), A0 + Vector2(-60, 190)]), Kit.RED, tr, 16, 1.0)
	Kit.pipe(self, PackedVector2Array([A0 + Vector2(480, 60), A0 + Vector2(480, 190), A0 + Vector2(600, 190)]), Kit.BLUE, tr * CylV42.AREA_RATIO, 16, 1.0)
	Kit.label(self, font, A0 + Vector2(-150, 236), "Q vào (từ van)", 22, Color(1, 0.75, 0.7))
	Kit.label(self, font, A0 + Vector2(500, 236), "dầu ra về thùng", 22, Color(0.7, 0.85, 1))
	# piston area A, end view
	var ka = clampf((t - M("f.s") - 1.0) / 0.5, 0, 1)
	if ka > 0.0:
		var c = A0 + Vector2(260, 420)
		draw_circle(c, 84, Color(Kit.RED, 0.85 * ka))
		draw_arc(c, 84, 0, TAU, 48, Color(1, 1, 1, ka), 3.0, true)
		for k in 9:
			var x = -70 + k * 17.5
			var h = sqrt(maxf(84 * 84 - x * x, 0))
			draw_line(c + Vector2(x, -h), c + Vector2(x + 30, h * 0.6), Color(1, 1, 1, 0.25 * ka), 1.5)
		Kit.label(self, bold, c + Vector2(110, 12), "A = diện tích piston (phía đáy)", 26, Color(1, 1, 1, ka))

func _draw_over() -> void:
	var f = rig.current() if rig else {}
	# lever arm about the boom foot pin
	var kl = clampf((t - M("lever.s")) / 0.5, 0, 1)
	if kl > 0.0 and rig:
		var xf: Transform2D = rig.transform
		var Bb = xf * Vector2(f.Bb)
		var Eb = xf * Vector2(f.Eb)
		var O = xf * Vector2.ZERO
		var dir = (Eb - Bb).normalized()
		var foot = Bb + dir * (O - Bb).dot(dir)
		over.draw_line(Bb - dir * 120, Eb + dir * 160, Color(1, 0.4, 0.3, 0.7 * kl), 3.0, true)
		over.draw_line(O, foot, Color(0.55, 0.92, 1.0, kl), 8.0, true)
		over.draw_circle(O, 9, Color(1, 0.85, 0.3, kl))
		over.draw_circle(foot, 6, Color(0.55, 0.92, 1.0, kl))
		Kit.label(over, bold, (O + foot) * 0.5 + Vector2(-46, 4), "d", 40, Color(0.6, 0.95, 1.0, kl))
		over.draw_arc(O, 70, -PI * 0.95, -PI * 0.35, 24, Color(1, 0.85, 0.3, kl), 7.0, true)
		var e = O + Vector2(cos(-PI * 0.35), sin(-PI * 0.35)) * 70
		over.draw_colored_polygon(PackedVector2Array([e + Vector2(10, 6), e + Vector2(-8, 10), e + Vector2(0, -12)]), Color(1, 0.85, 0.3, kl))
		Kit.label(over, bold, O + Vector2(-250, -100), "M = F · d", 38, Color(1, 0.9, 0.5, kl))
		var T = xf * Vector2(f.T)
		var kt = clampf((t - M("lever.s") - 3.0) / 0.5, 0, 1)
		if kt > 0.0:
			over.draw_line(T, T + Vector2(0, 70), Color(1, 0.6, 0.2, kt), 7.0, true)
			over.draw_colored_polygon(PackedVector2Array([T + Vector2(0, 92), T + Vector2(-12, 70), T + Vector2(12, 70)]), Color(1, 0.6, 0.2, kt))
			Kit.label(over, bold, T + Vector2(-420, 120), "lực tại răng gầu ≠ lực piston", 28, Color(1, 0.8, 0.5, kt))


func update(_time: float) -> void:
	over.queue_redraw()
	if rig:
		rig.housing_alpha = 1.0
	exhaust_load = 0.4

func draw_extra_hud(h: Node2D) -> void:
	var rows = [["F ≈ p · A", "lực do áp suất (khoang lý tưởng)", M("f.s") + 0.3, Kit.RED],
		["v ≈ Q / A", "tốc độ piston cần lưu lượng", M("v.s") + 0.2, Color(0.55, 0.85, 1.0)]]
	var y = 150.0
	for r in rows:
		var a = clampf((t - float(r[2])) / 0.4, 0, 1) * clampf((M("q2.s") - t) / 0.4, 0, 1)
		if a <= 0.0:
			continue
		h.draw_rect(Rect2(1180, y, 680, 86), Color(0.05, 0.08, 0.13, 0.9 * a))
		h.draw_rect(Rect2(1180, y, 6, 86), Color(r[3], a))
		h.draw_string(bold, Vector2(1205, y + 58), r[0], HORIZONTAL_ALIGNMENT_LEFT, -1, 44, Color(1, 1, 1, a))
		h.draw_string(font, Vector2(1430, y + 52), r[1], HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Color(0.85, 0.9, 0.95, a))
		y += 100.0
	var cards = [["Áp suất", "điều kiện tạo lực", Kit.RED], ["Lưu lượng", "liên quan tốc độ", Color(0.55, 0.85, 1.0)], ["Cơ cấu", "quyết định lực ra tới gầu", Color(1, 0.8, 0.3)]]
	for i in cards.size():
		var a = clampf((t - M("q2.s") - 0.4 - i * 1.4) / 0.4, 0, 1)
		if a <= 0.0:
			continue
		var x = 450.0 + i * 345.0
		h.draw_rect(Rect2(x, 760, 325, 130), Color(0.05, 0.08, 0.13, 0.92 * a))
		h.draw_rect(Rect2(x, 760, 325, 6), Color(cards[i][2], a))
		h.draw_string(bold, Vector2(x + 20, 820), cards[i][0], HORIZONTAL_ALIGNMENT_LEFT, -1, 34, Color(1, 1, 1, a))
		h.draw_string(font, Vector2(x + 20, 862), cards[i][1], HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color(0.85, 0.9, 0.95, a))
