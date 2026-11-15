@tool
extends "res://segments/segment_base.gd"
## SC03 - Engine and tandem pump (script SCRIPT_YOUTUBE_PC200_8_FULL_V2.md).
## Crank and pump shaft turn together (direct drive). Pump delivery shown as
## Q ~ n * tan(alpha): bigger swash angle -> longer piston stroke -> more flow.

@export var rpm := 1.2              # visual rev/s (slowed for viewing)
@export_range(0, 1) var swash_f := 0.1
@export_range(0, 1) var swash_r := 0.1
@export_range(0, 1) var meters := 0.0
@export_range(0, 1) var chips := 0.0
@export_range(0, 1) var stroke_dim := 0.0
@onready var engine = $Engine
@onready var pump = $Pump
var crank := 0.0

func setup() -> void:
	var P = pump.position
	callouts = [
		["Động cơ diesel SAA6D107E-1 · 6 xi lanh · 6,69 L", "K1 ✓", Vector2(420, -470), Vector2(-120, -130), 1.2, 9.4],
		["Trục khuỷu quay → trục bơm quay theo", "NGUYÊN LÝ", Vector2(860, 0), Vector2(-260, 150), 6.8, 11.0],
		["Bơm HPV95+95: 2 bơm piston thay đổi lưu lượng", "K2 ✓", P + Vector2(400, -175), Vector2(-620, -120), 9.8, 16.5],
		["Lưu lượng tối đa của cụm bơm 439 L/phút", "K1 ✓", P + Vector2(372, -300), Vector2(60, -60), 11.0, 16.5],
		["Đĩa nghiêng", "NGUYÊN LÝ", P + Vector2(130, 120), Vector2(-260, 140), 14.6, 24.4],
		["Piston + guốc trượt quay theo khối xi lanh", "NGUYÊN LÝ", P + Vector2(260, 40), Vector2(-120, 190), 15.4, 24.4],
		["Piston servo đổi góc đĩa nghiêng", "NGUYÊN LÝ", P + Vector2(150, -236), Vector2(-560, 40), 16.4, 24.4],
		["Góc nhỏ → hành trình ngắn → lưu lượng ít", "NGUYÊN LÝ", P + Vector2(300, -318), Vector2(140, -20), 17.6, 20.6],
		["Góc lớn → hành trình dài → lưu lượng nhiều", "NGUYÊN LÝ", P + Vector2(300, -318), Vector2(140, -20), 20.8, 24.4],
	]
	capy_blinks = [26.2, 28.9, 33.5, 38.0]
	eng_blinks = [31.0, 35.2, 39.1]

func rate(time: float) -> float:
	return sample(".:rpm", time)

func update(time: float) -> void:
	crank = integrate(rate, time) * 360.0
	engine.crank_deg = crank
	pump.shaft_deg = crank
	pump.swash_f = swash_f
	pump.swash_r = swash_r
	pump.show_stroke = stroke_dim > 0.5
	var qf = func(s): return sample(".:rpm", s) * tan(deg_to_rad(lerpf(3.0, 17.0, sample(".:swash_f", s))))
	var qr = func(s): return sample(".:rpm", s) * tan(deg_to_rad(lerpf(3.0, 17.0, sample(".:swash_r", s))))
	pump.flow_travel_f = integrate(qf, time) * 420.0
	pump.flow_travel_r = integrate(qr, time) * 420.0
	pump.queue_redraw()
	engine.queue_redraw()

func q_now() -> float:
	return rpm * tan(deg_to_rad(lerpf(3.0, 17.0, swash_f)))

func draw_extra_hud(h: Node2D) -> void:
	if meters > 0.01:
		var a = meters
		var x = 1480.0
		var y = 190.0
		h.draw_rect(Rect2(x - 20, y - 50, 400, 190), Color(0.05, 0.08, 0.13, 0.86 * a))
		var rows = [["Tốc độ quay n", rpm / 2.0, Color(0.85, 0.85, 0.9)],
			["Góc đĩa nghiêng α", swash_f, Color(1, 0.8, 0.35)],
			["Lưu lượng Q ~ n·tan α", q_now() / (2.0 * tan(deg_to_rad(17.0))), Kit.RED]]
		for i in rows.size():
			var yy = y + i * 52
			h.draw_string(font, Vector2(x, yy - 12), rows[i][0], HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color(1, 1, 1, a))
			h.draw_rect(Rect2(x, yy - 4, 360, 14), Color(1, 1, 1, 0.12 * a))
			h.draw_rect(Rect2(x, yy - 4, 360 * clampf(rows[i][1], 0.0, 1.0), 14), Color(rows[i][2], a))
		h.draw_string(font, Vector2(x, y - 26), "minh họa định tính, không phải số đo", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(0.7, 0.78, 0.9, a))
	if chips > 0.01:
		var names = ["điều khiển bơm", "độ mở van", "tải", "giới hạn công suất"]
		var x2 = 470.0
		for i in names.size():
			var k = clampf((chips * 4.0) - i, 0.0, 1.0)
			var w = bold.get_string_size(names[i], HORIZONTAL_ALIGNMENT_LEFT, -1, 24).x + 34
			h.draw_rect(Rect2(x2, 900, w, 46), Color(0.05, 0.08, 0.13, 0.88 * k))
			h.draw_rect(Rect2(x2, 900, w, 46), Color(1, 0.78, 0.25, k), false, 2.5)
			h.draw_string(bold, Vector2(x2 + 17, 931), names[i], HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Color(1, 1, 1, k))
			x2 += w + 18
		h.draw_string(bold, Vector2(470, 888), "Lưu lượng tới cơ cấu còn phụ thuộc:", HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Color(1, 0.9, 0.6, chips))

func qa(time: float) -> void:
	# pump kinematics: shaft follows crank (direct drive), stroke = 2 Rb tan(alpha)
	if absf(pump.shaft_deg - engine.crank_deg) > 0.001:
		qa_report.append("t=%.2f pump shaft not synchronised" % time)
	telemetry.append("%.4f,%.4f,%.4f,%.4f,%.4f" % [time, rpm, swash_f, swash_r, q_now()])
	if telemetry.size() == 1:
		telemetry.insert(0, "t,rpm,swash_f,swash_r,q")
