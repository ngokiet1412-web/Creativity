@tool
extends "res://segments/segment_base.gd"
## SC05 - Joystick -> PPC pilot -> main control valve spool -> boom cylinder.
## Chain of cause and effect, all derived from the keyed lever angle:
##   lever -> PPC output pressure (dead band, proportional)
##   pilot pressure -> spool shift against the centring spring (0.12 s lag)
##   spool shift - overlap -> P->A and B->T openings
##   opening -> oil volume -> piston travel in the cylinder (rod side out = 0.5x)

@export_range(-1, 1) var lever := 0.0
@export_range(0, 1) var compare := 0.0
@onready var ppc = $PPC
@onready var spool = $Spool
@onready var pump = $Pump
var pilot := 0.0
var shift := 0.0
var ext := 0.0
const STROKE := 300.0
const RATE := 0.6  # px of rod travel per (px of P->A opening * s); keeps the cylinder off its end stop

func setup() -> void:
	var S: Vector2 = spool.position
	callouts = [
		["Joystick đẩy piston van PPC", "NGUYÊN LÝ", Vector2(300, 230), Vector2(-280, -330), 6.2, 19.4],
		["Van PPC: áp pilot tỉ lệ hành trình cần gạt", "NGUYÊN LÝ", Vector2(375, 540), Vector2(-440, 140), 7.6, 19.4],
		["Áp pilot đẩy con trượt, nén lò xo định tâm", "NGUYÊN LÝ", S + Vector2(-40, 0), Vector2(-120, 200), 10.6, 19.4],
		["Van điều khiển chính loại 6 con trượt (vẽ 1 con)", "K2 ✓", S + Vector2(700, 160), Vector2(-60, 150), 12.2, 19.4],
		["P → A: dầu áp lực vào khoang đáy", "NGUYÊN LÝ", S + Vector2(290, -235), Vector2(-480, -60), 14.0, 19.4],
		["B → T: dầu khoang ty về thùng", "NGUYÊN LÝ", S + Vector2(610, -235), Vector2(70, -10), 15.0, 19.4],
	]
	capy_blinks = [1.6, 4.0, 20.6, 22.4]
	eng_blinks = [6.0, 12.4, 17.8, 25.0]

func pilot_at(time: float) -> float:
	var lv = sample(".:lever", time)
	return clampf((absf(lv) - 0.08) / 0.92, 0.0, 1.0) * signf(lv)

func open_at(time: float) -> float:
	var sh = pilot_at(time - 0.12) * 75.0
	return maxf(sh - 27.0, 0.0)

func update(time: float) -> void:
	ppc.lever = lever
	pilot = pilot_at(time)
	shift = pilot_at(time - 0.12)
	spool.spool = shift
	spool.pilot_left = absf(pilot)
	ppc.travel = integrate(func(s): return absf(pilot_at(s)), time) * 40.0
	var vol = integrate(open_at, time)              # px*s of opening
	spool.travel_a = vol * 9.0
	spool.travel_b = vol * 9.0 * 0.5
	ext = minf(vol * RATE, STROKE)
	pump.shaft_deg = time * 430.0
	pump.swash_f = clampf(0.12 + open_at(time) / 35.0, 0.12, 1.0)
	pump.flow_travel_f = vol * 9.0
	ppc.queue_redraw()
	spool.queue_redraw()
	pump.queue_redraw()

func _draw() -> void:
	super._draw()
	var S: Vector2 = spool.position
	# pilot line PPC P2 -> left pilot chamber of the spool
	Kit.pipe(self, PackedVector2Array([Vector2(375, 710), Vector2(375, 760), Vector2(640, 760), Vector2(640, S.y), Vector2(S.x - 70, S.y)]),
		Kit.ORANGE, ppc.travel, 14 + 12 * compare, absf(pilot))
	# boom cylinder fed from A (bottom) and B (rod side)
	var a0 = Vector2(980, -130)
	var bar_len = 520.0
	var pist = a0.x + 40 + ext
	draw_rect(Rect2(a0.x, a0.y - 60, bar_len, 120), Color("#e7a82b"))
	draw_rect(Rect2(a0.x + 12, a0.y - 46, bar_len - 24, 92), Color("#1a2028"))
	draw_rect(Rect2(a0.x + 12, a0.y - 42, pist - a0.x - 12, 84), Kit.RED.darkened(0.1))
	draw_rect(Rect2(pist + 24, a0.y - 42, a0.x + bar_len - 12 - pist - 24, 84), Kit.BLUE.darkened(0.15))
	Kit.cyl(self, Vector2(pist + 20, a0.y), Vector2(pist + 20 + 600, a0.y), 44, Kit.STEEL)
	Kit.body(self, Kit.rect_pts(Rect2(pist, a0.y - 44, 26, 88)), Color("#b9c1c9"))
	Kit.outline(self, Kit.rect_pts(Rect2(a0.x, a0.y - 60, bar_len, 120)), 2.6)
	Kit.disc(self, Vector2(a0.x - 30, a0.y), 22, Kit.STEEL)
	Kit.label(self, font, Vector2(a0.x + 40, a0.y - 78), "xi lanh nâng cần (mặt cắt)", 24)
	var opa = open_at(t)
	Kit.pipe(self, PackedVector2Array([S + Vector2(290, -235), Vector2(S.x + 290, 10), Vector2(a0.x + 40, 10), Vector2(a0.x + 40, a0.y + 60)]),
		Kit.RED if opa > 0.0 else Kit.RED.darkened(0.3), spool.travel_a, 24 - 10 * compare * 0, clampf(opa / 20.0, 0, 1))
	Kit.pipe(self, PackedVector2Array([Vector2(a0.x + bar_len - 40, a0.y + 60), Vector2(a0.x + bar_len - 40, 30), Vector2(S.x + 610, 30), S + Vector2(610, -235)]),
		Kit.BLUE if opa > 0.0 else Kit.BLUE.darkened(0.35), spool.travel_b, 24, clampf(opa / 20.0, 0, 1))
	# pump P1 -> compensator -> P groove; tank return
	var P: Vector2 = pump.position
	var ps: float = pump.scale.x
	Kit.pipe(self, PackedVector2Array([P + Vector2(372, -300) * ps, Vector2(P.x + 372 * ps, 700), Vector2(S.x + 450, 700), S + Vector2(450, 325)]),
		Kit.RED, spool.travel_a, 30 + 0 * compare, clampf(opa / 20.0, 0.15, 1.0))
	Kit.pipe(self, PackedVector2Array([S + Vector2(880, 235), Vector2(S.x + 880, 780), Vector2(S.x + 960, 780)]), Kit.BLUE, spool.travel_b, 24, clampf(opa / 20.0, 0, 1))
	Kit.body(self, Kit.rounded(Rect2(S.x + 940, 700, 180, 200), 18), Color("#33475e"))
	draw_rect(Rect2(S.x + 952, 780, 156, 108), Color(Kit.BLUE, 0.7))
	Kit.label(self, font, Vector2(S.x + 960, 760), "thùng dầu", 22)

func draw_extra_hud(h: Node2D) -> void:
	if compare > 0.01:
		var a = compare
		var rows = [["Mạch pilot (cần gạt → van)", "van an toàn 3,2 MPa", Kit.ORANGE, 0.12],
			["Mạch công tác (bơm → xi lanh)", "van an toàn 37,3 MPa", Kit.RED, 1.0]]
		h.draw_rect(Rect2(560, 880, 1010, 150), Color(0.05, 0.08, 0.13, 0.9 * a))
		for i in 2:
			var y = 920.0 + i * 58.0
			h.draw_string(bold, Vector2(580, y), rows[i][0], HORIZONTAL_ALIGNMENT_LEFT, -1, 23, Color(1, 1, 1, a))
			h.draw_rect(Rect2(930, y - 18, 280 * rows[i][3], 20), Color(rows[i][2], a))
			h.draw_string(font, Vector2(1226, y), rows[i][1], HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color(0.85, 0.95, 0.88, a))
		h.draw_rect(Rect2(1490, 896, 56, 28), Color(0.2, 0.62, 0.36, a))
		h.draw_string(bold, Vector2(1497, 917), "K1 ✓", HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color(1, 1, 1, a))

func qa(time: float) -> void:
	var opa = open_at(time)
	if opa > 0.0 and absf(sample(".:lever", time - 0.12)) < 0.08:
		qa_report.append("t=%.2f valve open inside joystick dead band" % time)
	if time > 0.2 and ext + 0.001 < minf(integrate(open_at, time - 1.0 / 30.0) * RATE, STROKE):
		qa_report.append("t=%.2f cylinder moved backwards while P->A open" % time)
	if telemetry.is_empty():
		telemetry.append("t,lever,pilot,shift,open_pa,ext")
	telemetry.append("%.4f,%.4f,%.4f,%.4f,%.4f,%.3f" % [time, lever, pilot, shift, opa, ext])
