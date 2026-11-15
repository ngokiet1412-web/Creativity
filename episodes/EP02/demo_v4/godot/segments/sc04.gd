@tool
extends "res://segments/segment_base.gd"
## SC04 - CLSS: closed centre + load sensing + pressure compensation (principle).
## PC200-8 pump regulator has an LS valve and a PC valve (shop manual index);
## behaviour shown here is the textbook CLSS logic, not measured values:
##   no lever: LS line vented -> LS valve destrokes pump -> standby flow, low p
##   lever: LS = highest working-port pressure (shuttle) -> pump keeps
##          p_pump = p_LS + dp_LS and swings the swash to meet demand
##   two levers: compensators throttle the lighter branch so each section's
##          flow follows its spool opening (flow sharing)
##   high load: PC valve caps p*Q (engine power) by reducing the swash angle

@export_range(0, 1) var boom := 0.0
@export_range(0, 1) var arm := 0.0
@export_range(0, 1) var load_boom := 0.55
@export_range(0, 1) var load_arm := 0.3
@onready var pump = $Pump
@onready var vb = $ValveBoom
@onready var va = $ValveArm
const DP_LS := 0.16
const QMAX := 1.0
const POWER := 0.62            # p*Q cap (normalised) for the PC valve
var st := {}
var boom_ext := 0.0
var arm_ext := 0.0

func setup() -> void:
	callouts = [
		["Tâm kín: con trượt ở giữa chặn đường P", "NGUYÊN LÝ", Vector2(1147, 150), Vector2(-120, 220), 7.4, 9.6],
		["Đường LS xả về thùng → bơm giữ lưu lượng chờ", "NGUYÊN LÝ", Vector2(760, 300), Vector2(-200, 120), 7.8, 9.6],
		["Van LS trên bơm", "K2 ✓", Vector2(380, 60), Vector2(-80, 150), 6.8, 15.8],
		["LS = áp cổng làm việc cao nhất (van con thoi)", "NGUYÊN LÝ", Vector2(860, 230), Vector2(-260, 150), 11.2, 15.8],
		["Áp bơm = áp LS + chênh áp LS", "NGUYÊN LÝ", Vector2(240, 105), Vector2(-300, 200), 12.6, 15.8],
		["Van bù áp tiết lưu nhánh tải nhẹ → chia dòng", "NGUYÊN LÝ", Vector2(1147, 670), Vector2(-160, 140), 17.8, 24.0],
		["Van PC: áp cao thì giảm góc đĩa nghiêng (giữ trong công suất động cơ)", "NGUYÊN LÝ", Vector2(320, -50), Vector2(250, -60), 31.6, 37.6],
	]
	capy_blinks = [1.2, 2.9, 25.6, 28.4]
	eng_blinks = [5.0, 11.0, 18.5, 33.0, 36.4]

func state_at(time: float) -> Dictionary:
	var b = sample(".:boom", time)
	var a = sample(".:arm", time)
	var lb = sample(".:load_boom", time)
	var la = sample(".:load_arm", time)
	var ob = maxf(b - 0.15, 0.0) / 0.85
	var oa = maxf(a - 0.15, 0.0) / 0.85
	var pls = maxf(lb if ob > 0.0 else 0.0, la if oa > 0.0 else 0.0)
	var demand = 0.55 * ob + 0.45 * oa
	var pp = pls + DP_LS
	var qcap = QMAX if pp * QMAX <= POWER else POWER / pp
	var q = minf(demand, qcap)
	var share = q / demand if demand > 0.001 else 0.0
	var pc_active = demand > qcap
	return {"ob": ob, "oa": oa, "pls": pls, "pp": pp, "q": q, "qb": 0.55 * ob * share, "qa": 0.45 * oa * share,
		"pc": pc_active, "swash": clampf(0.08 + q * 0.92, 0.08, 1.0),
		"comp_b": clampf((pls - lb) * 2.2, 0.0, 1.0) if ob > 0.0 else 0.0,
		"comp_a": clampf((pls - la) * 2.2, 0.0, 1.0) if oa > 0.0 else 0.0}

func update(time: float) -> void:
	# Retain the complete LS/pump/valve path instead of cutting the pump in half.
	cam.position = Vector2(850, 260)
	cam.zoom = Vector2.ONE * 0.66
	st = state_at(time)
	pump.shaft_deg = time * 430.0
	pump.swash_f = st.swash
	pump.flow_travel_f = integrate(func(s): return state_at(s).q, time) * 160.0
	vb.spool = st.ob * 0.85 + (0.15 if boom > 0.15 else boom)
	va.spool = st.oa * 0.85 + (0.15 if arm > 0.15 else arm)
	vb.pilot_left = boom
	va.pilot_left = arm
	vb.comp_throttle = st.comp_b
	va.comp_throttle = st.comp_a
	vb.travel_a = integrate(func(s): return state_at(s).qb, time) * 160.0
	va.travel_a = integrate(func(s): return state_at(s).qa, time) * 160.0
	vb.travel_b = vb.travel_a * 0.5
	va.travel_b = va.travel_a * 0.5
	boom_ext = minf(vb.travel_a * 0.9, 260.0)
	arm_ext = minf(va.travel_a * 0.9, 260.0)
	for n in [pump, vb, va]:
		n.queue_redraw()

func _draw() -> void:
	super._draw()
	if st.is_empty():
		return
	var lsc = Kit.PURPLE
	var live = 1.0 if st.pls > 0.0 else 0.0
	# LS line: working ports -> shuttle -> LS valve spring chamber (a signal, not a supply line)
	var sh = Vector2(860, 230)
	Kit.pipe(self, PackedVector2Array([Vector2(1059, -5), Vector2(860, -5), sh]), lsc, t * 40.0 * live, 10, live * (1.0 if st.ob > 0.0 else 0.25))
	Kit.pipe(self, PackedVector2Array([Vector2(1059, 365), Vector2(860, 365), sh]), lsc, t * 40.0 * live, 10, live * (1.0 if st.oa > 0.0 else 0.25))
	Kit.pipe(self, PackedVector2Array([sh, Vector2(620, 230), Vector2(620, 105), Vector2(560, 105)]), lsc, t * 40.0 * live, 10, live)
	if st.pls <= 0.0:
		Kit.pipe(self, PackedVector2Array([Vector2(740, 230), Vector2(740, 300), Vector2(800, 300)]), Kit.BLUE, t * 20.0, 8, 0.6)
		Kit.label(self, font, Vector2(690, 330), "LS → thùng", 20, Kit.BLUE.lightened(0.4))
	Kit.disc(self, sh, 16, Color("#8f7ab8"))
	Kit.label(self, font, sh + Vector2(-160, -18), "van con thoi", 19)
	_ls_valve(Vector2(200, 60))
	_pc_valve(Vector2(200, -90))
	var servo: Vector2 = pump.position + Vector2(150, -236) * pump.scale.x
	Kit.pipe(self, PackedVector2Array([Vector2(330, 150), Vector2(330, 300), Vector2(servo.x, 300), servo]), Kit.RED.darkened(0.3), t * 10.0, 10, 0.4)
	var out: Vector2 = pump.position + Vector2(372, -300) * pump.scale.x
	Kit.pipe(self, PackedVector2Array([out, Vector2(out.x, 270), Vector2(820, 270), Vector2(820, 350), Vector2(1147, 350), Vector2(1147, 329)]), Kit.RED, pump.flow_travel_f, 16, 0.25 + 0.75 * st.q)
	Kit.pipe(self, PackedVector2Array([Vector2(820, 350), Vector2(820, 760), Vector2(1147, 760), Vector2(1147, 699)]), Kit.RED, pump.flow_travel_f, 14, 0.25 + 0.75 * st.q)
	# actuators
	_actuator(Vector2(1500, -40), boom_ext, "xi lanh cần", st.ob > 0.0, Vector2(1059, 21), Vector2(1235, 21), vb)
	_actuator(Vector2(1500, 330), arm_ext, "xi lanh tay gầu", st.oa > 0.0, Vector2(1059, 391), Vector2(1235, 391), va)

func _ls_valve(p: Vector2) -> void:
	var r = Rect2(p, Vector2(360, 90))
	Kit.cut(self, Kit.rect_pts(r), Kit.CUT_FACE, 9.0)
	draw_rect(Rect2(p + Vector2(20, 30), Vector2(320, 30)), Color("#1a2028"))
	# left end: pump pressure; right end: LS pressure + spring
	draw_rect(Rect2(p + Vector2(20, 30), Vector2(60, 30)), Color(Kit.RED, 0.4 + 0.6 * clampf(st.pp, 0, 1)))
	draw_rect(Rect2(p + Vector2(260, 30), Vector2(80, 30)), Color(Kit.PURPLE, 0.25 + 0.75 * clampf(st.pls / 0.9, 0, 1)))
	# spool: standby (no LS) shifts right -> destroke; working -> balanced centre
	var x = 150.0 + (34.0 if st.pls <= 0.0 else 0.0)
	Kit.cyl(self, p + Vector2(x - 70, 45), p + Vector2(x + 50, 45), 26, Kit.STEEL)
	Kit.spring(self, p + Vector2(x + 50, 45), p + Vector2(338, 45), 6, 22)
	Kit.label(self, font, p + Vector2(4, -10), "van LS", 22, Color(1, 0.9, 0.6))
	Kit.label(self, font, p + Vector2(20, 82), "p bơm", 17, Kit.RED.lightened(0.4))
	Kit.label(self, font, p + Vector2(262, 82), "p LS + lò xo", 17, Kit.PURPLE.lightened(0.4))

func _pc_valve(p: Vector2) -> void:
	var r = Rect2(p, Vector2(240, 80))
	Kit.cut(self, Kit.rect_pts(r), Kit.CUT_FACE.darkened(0.05), 9.0)
	draw_rect(Rect2(p + Vector2(16, 26), Vector2(208, 28)), Color("#1a2028"))
	var x = 90.0 + (30.0 if st.pc else 0.0)
	draw_rect(Rect2(p + Vector2(16, 26), Vector2(50, 28)), Color(Kit.RED, 0.4 + 0.6 * clampf(st.pp, 0, 1)))
	Kit.cyl(self, p + Vector2(x - 40, 40), p + Vector2(x + 40, 40), 22, Kit.STEEL)
	Kit.spring(self, p + Vector2(x + 40, 40), p + Vector2(222, 40), 5, 20)
	Kit.label(self, font, p + Vector2(4, -10), "van PC", 22, Color(1, 0.9, 0.6) if not st.pc else Color(1, 0.55, 0.4))

func _actuator(p: Vector2, ext: float, name: String, on: bool, a_port: Vector2, b_port: Vector2, sec: Node2D) -> void:
	var L = 300.0
	draw_rect(Rect2(p, Vector2(L, 70)), Color("#e7a82b"))
	draw_rect(Rect2(p + Vector2(8, 8), Vector2(L - 16, 54)), Color("#1a2028"))
	var px = p.x + 20 + ext * 0.85
	draw_rect(Rect2(p + Vector2(8, 10), Vector2(px - p.x - 8, 50)), Kit.RED.darkened(0.1))
	draw_rect(Rect2(Vector2(px + 16, p.y + 10), Vector2(p.x + L - 8 - px - 16, 50)), Kit.BLUE.darkened(0.15))
	Kit.cyl(self, Vector2(px + 10, p.y + 35), Vector2(px + 330, p.y + 35), 26, Kit.STEEL)
	Kit.body(self, Kit.rect_pts(Rect2(px, p.y + 6, 18, 58)), Color("#b9c1c9"))
	Kit.outline(self, Kit.rect_pts(Rect2(p, Vector2(L, 70))), 2.2)
	Kit.label(self, font, p + Vector2(0, -12), name, 21)
	Kit.pipe(self, PackedVector2Array([a_port, Vector2(a_port.x, p.y + 35), Vector2(p.x, p.y + 35)]), Kit.RED if on else Kit.RED.darkened(0.3), sec.travel_a, 12, 1.0 if on else 0.0)
	Kit.pipe(self, PackedVector2Array([Vector2(p.x + L - 30, p.y + 70), Vector2(p.x + L - 30, p.y + 90), Vector2(b_port.x, p.y + 90), b_port]), Kit.BLUE if on else Kit.BLUE.darkened(0.35), sec.travel_b, 12, 1.0 if on else 0.0)

func draw_extra_hud(h: Node2D) -> void:
	if st.is_empty():
		return
	var x = 56.0
	var y = 70.0
	h.draw_rect(Rect2(x - 20, y, 330, 230), Color(0.05, 0.08, 0.13, 0.86))
	h.draw_string(font, Vector2(x, y + 26), "minh họa định tính, không phải số đo", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(0.7, 0.78, 0.9))
	var rows = [["Áp bơm", st.pp, Kit.RED], ["Áp LS", st.pls, Kit.PURPLE], ["Lưu lượng bơm", st.q, Color(1, 0.8, 0.35)],
		["p·Q (trần PC)", st.pp * st.q / POWER, Color(1, 0.5, 0.4) if st.pc else Color(0.8, 0.85, 0.9)]]
	for i in rows.size():
		var yy = y + 62 + i * 42
		h.draw_string(font, Vector2(x, yy), rows[i][0], HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color(1, 1, 1))
		h.draw_rect(Rect2(x + 150, yy - 14, 150, 14), Color(1, 1, 1, 0.12))
		h.draw_rect(Rect2(x + 150, yy - 14, 150 * clampf(rows[i][1], 0, 1), 14), rows[i][2])

func qa(time: float) -> void:
	var s = state_at(time)
	if s.pls <= 0.0 and s.q > 0.0001:
		qa_report.append("t=%.2f pump delivers working flow with no LS demand" % time)
	if s.pp * s.q > POWER + 1e-4:
		qa_report.append("t=%.2f p*Q above PC cap" % time)
	if s.ob > 0.0 and s.oa > 0.0 and absf(s.qb / maxf(s.qa, 1e-6) - (0.55 * s.ob) / (0.45 * s.oa)) > 1e-3:
		qa_report.append("t=%.2f flow split does not follow spool openings" % time)
	if telemetry.is_empty():
		telemetry.append("t,boom,arm,p_pump,p_ls,q,pc,swash")
	telemetry.append("%.4f,%.3f,%.3f,%.4f,%.4f,%.4f,%d,%.4f" % [time, boom, arm, s.pp, s.pls, s.q, 1 if s.pc else 0, s.swash])
