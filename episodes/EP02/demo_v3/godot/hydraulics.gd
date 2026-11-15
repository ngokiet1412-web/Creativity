@tool
extends Node2D
## Simplified boom-raise circuit drawn in machine space (illustration, not a
## port-by-port PC200-8 drawing). Engine -> variable piston pump -> closed-centre
## spool -> boom cylinder bottom; rod side -> valve -> filter -> tank.
## Pilot (orange) shifts the spool, load-sense (purple) tells the pump regulator.
## Dash travel is proportional to oil volume moved by the piston.

const RED := Color("#e4472f")
const BLUE := Color("#3d93dc")
const ORANGE := Color("#f39a1e")
const PURPLE := Color("#a46be0")
const BODY := Color("#2c3a4a")
const EDGE := Color("#c9d6e3")

var director: Node
var rig

# layout (machine px; boom foot pin = origin)
const ENGINE := Rect2(-354, -50, 92, 66)
const CRANK_Y := 24.0
const PUMP := Rect2(-242, -14, 56, 44)
const REG := Rect2(-230, -32, 26, 14)
const TANK := Rect2(-178, -74, 38, 98)
const VALVE := Rect2(-126, 4, 70, 32)
const JOY := Vector2(-48, -32)
const FILTER := Vector2(-160, 44)
const MANIFOLD := Vector2(-6, 26)

func _ready() -> void:
	rig = get_parent()
	director = rig.get_parent().get_parent()
	z_index = 10
	z_as_relative = false

func _draw() -> void:
	if director == null or rig == null or not rig.ready_done:
		return
	var t: float = director.t
	var xr: float = director.xray
	var fo: float = maxf(director.flow_overlay, xr)
	if fo <= 0.01:
		return
	var st: Dictionary = director.hydraulic_state(t)
	var f: Dictionary = rig.current()
	var ports: Array = rig.port_points(f.Bb, f.Eb, rig.rig.boom_cyl)
	var a_port: Vector2 = ports[0]
	var b_port: Vector2 = ports[1]
	var supply_bottom: bool = st.v >= 0.0
	# ---- hoses to the cylinder (visible in x-ray and in wide flow overlay)
	var hose_a = PackedVector2Array([Vector2(VALVE.end.x, 13), Vector2(-30, 13), MANIFOLD + Vector2(0, -6),
		MANIFOLD + Vector2(18, 6), a_port.lerp(MANIFOLD, 0.45) + Vector2(4, 10), a_port])
	var u: Vector2 = f.Bb.direction_to(f.Eb)
	var n = u.orthogonal()
	var tube_end: Vector2 = b_port
	var tube_start: Vector2 = f.Bb + u * 30 - n * (rig.rig.boom_cyl.barrel_w * 0.5 + 6)
	var hose_b = PackedVector2Array([tube_end, tube_end - n * 5, tube_start, MANIFOLD + Vector2(14, 14),
		Vector2(-30, 27), Vector2(VALVE.end.x, 27)])
	var vb: float = st.vol_bottom
	var vr: float = st.vol_rod
	flow_line(hose_a, vb, RED if supply_bottom else BLUE, fo, 5.5)
	flow_line(hose_b, vr, BLUE if supply_bottom else RED, fo, 5.5)
	if xr <= 0.01:
		return
	var a = xr
	# ---- engine: inline six, slider-crank pistons
	var crank = t * TAU * 1.6
	_box(ENGINE, a, "")
	draw_rect(Rect2(ENGINE.position + Vector2(3, 3), Vector2(ENGINE.size.x - 6, 9)), Color(0.55, 0.22, 0.16, a))
	draw_circle(Vector2(ENGINE.position.x + 6, CRANK_Y), 5, Color(0.6, 0.62, 0.64, a), true, -1, true)
	for i in 6:
		var phase = crank + [0.0, 4.18879, 2.0944, 2.0944, 4.18879, 0.0][i]   # 1-5-3-6-2-4 pairs
		var cx = ENGINE.position.x + 9 + i * 14.6
		var r = 7.0
		var rod = 22.0
		var py = CRANK_Y - (r * cos(phase) + sqrt(rod * rod - pow(r * sin(phase), 2)))
		draw_rect(Rect2(cx - 5.6, ENGINE.position.y + 6, 11.2, 44), Color(0.1, 0.13, 0.17, a))
		var pin = Vector2(cx + r * sin(phase), CRANK_Y - r * cos(phase))
		draw_line(Vector2(cx, py + 4), pin, Color(0.75, 0.78, 0.8, a), 2.2, true)
		var sb = StyleBoxFlat.new()
		sb.bg_color = Color(0.86, 0.88, 0.89, a)
		sb.set_corner_radius_all(2)
		draw_style_box(sb, Rect2(cx - 5, py - 7, 10, 11))
		draw_line(Vector2(cx - 5, py - 4), Vector2(cx + 5, py - 4), Color(0.4, 0.42, 0.45, a), 1.0)
		draw_circle(pin, 2.2, Color(0.9, 0.7, 0.3, a), true, -1, true)
		var fire = pow(maxf(cos(phase * 0.5), 0.0), 18.0)
		if fire > 0.05:
			draw_circle(Vector2(cx, ENGINE.position.y + 9), 4.0, Color(1.0, 0.65, 0.2, a * fire), true, -1, true)
	draw_line(Vector2(ENGINE.position.x + 2, CRANK_Y), Vector2(PUMP.position.x, CRANK_Y), Color(0.7, 0.72, 0.74, a), 4.0, true)
	# rotating shaft marks + flywheel
	var fw = Vector2(ENGINE.end.x + 8, CRANK_Y - 10)
	draw_circle(fw, 15, Color(0.25, 0.3, 0.36, a), true, -1, true)
	draw_arc(fw, 15, 0, TAU, 32, Color(EDGE, a), 1.5, true)
	for k in 4:
		var ang = crank + k * PI * 0.5
		draw_line(fw, fw + Vector2(cos(ang), sin(ang)) * 13, Color(EDGE, a * 0.8), 2.0, true)
	# ---- pump: rotating cylinder block, stroke set by swash angle
	_box(PUMP, a, "")
	var sw: float = st.swash
	var alpha_deg = lerpf(3.0, 17.0, sw)
	var cxp = PUMP.position.x + 30
	var cyp = PUMP.position.y + PUMP.size.y * 0.5
	var plate_c = Vector2(PUMP.position.x + 9, cyp)
	var pd = Vector2(sin(deg_to_rad(alpha_deg)), cos(deg_to_rad(alpha_deg))) * 18
	draw_line(plate_c - pd, plate_c + pd, Color(0.95, 0.8, 0.35, a), 4.0, true)
	for k in 7:
		var ph = crank + k * TAU / 7.0
		var y = cyp + 14.0 * cos(ph)
		var depth = 0.45 + 0.55 * (0.5 + 0.5 * sin(ph))
		var ext = 6.0 + 16.0 * tan(deg_to_rad(alpha_deg)) * (1.0 + cos(ph)) * 1.6
		var bore_x = cxp - 6
		draw_rect(Rect2(bore_x - 2, y - 3, 22, 6), Color(0.08, 0.1, 0.13, a * depth))
		draw_rect(Rect2(bore_x - ext * 0.5, y - 2.4, 14, 4.8), Color(0.85, 0.87, 0.88, a * depth))
	draw_line(Vector2(cxp + 18, PUMP.position.y + 4), Vector2(cxp + 18, PUMP.end.y - 4), Color(EDGE, a * 0.6), 1.5)
	# regulator + load-sense line
	_box(REG, a, "")
	draw_line(Vector2(REG.position.x + 13, REG.end.y), plate_c + Vector2(0, -pd.y * 0.9), Color(PURPLE, a * 0.8), 2.0, true)
	var ls_path = PackedVector2Array([Vector2(VALVE.position.x + 34, VALVE.position.y), Vector2(VALVE.position.x + 34, -22),
		Vector2(REG.end.x + 4, -22), Vector2(REG.end.x, REG.position.y + 7)])
	signal_line(ls_path, director.ls_wave(t), PURPLE, a)
	# ---- pressure gauge on pump outlet
	var g = Vector2(PUMP.end.x + 6, PUMP.position.y - 16)
	draw_circle(g, 11, Color(0.92, 0.94, 0.95, a), true, -1, true)
	draw_arc(g, 11, 0, TAU, 28, Color(0.1, 0.1, 0.12, a), 1.6, true)
	draw_arc(g, 8, PI * 0.8, PI * 1.25, 10, Color(0.3, 0.7, 0.4, a), 2.5, true)
	draw_arc(g, 8, PI * 1.25, PI * 2.2, 18, Color(0.85, 0.3, 0.25, a), 2.5, true)
	var na = lerpf(PI * 0.8, PI * 2.2, st.p_pump)
	draw_line(g, g + Vector2(cos(na), sin(na)) * 9, Color(0.1, 0.1, 0.12, a), 1.8, true)
	draw_line(g + Vector2(0, 11), Vector2(g.x, PUMP.position.y), Color(EDGE, a), 1.5)
	# ---- tank, filter
	_box(TANK, a, "")
	var lvl = TANK.end.y - 46 - st.stroke * 0.05
	draw_rect(Rect2(TANK.position.x + 3, lvl, TANK.size.x - 6, TANK.end.y - lvl - 3), Color(BLUE, 0.55 * a))
	draw_circle(FILTER, 7, Color(0.25, 0.3, 0.36, a), true, -1, true)
	draw_arc(FILTER, 7, 0, TAU, 20, Color(EDGE, a), 1.4, true)
	for k in 3:
		draw_line(FILTER + Vector2(-4, -3 + k * 3), FILTER + Vector2(4, -3 + k * 3), Color(EDGE, a * 0.7), 1.0)
	# ---- main lines
	var p_line = PackedVector2Array([Vector2(PUMP.end.x, cyp + 8), Vector2(-150, cyp + 8), Vector2(-150, 42), Vector2(-112, 42), Vector2(-112, VALVE.end.y)])
	flow_line(p_line, vb, RED, a, 5.0, st.open < 0.05)
	var t_line = PackedVector2Array([Vector2(-70, VALVE.end.y), Vector2(-70, 50), FILTER + Vector2(8, 6), FILTER, Vector2(FILTER.x - 18, FILTER.y), Vector2(TANK.position.x + 18, TANK.end.y)])
	flow_line(t_line, vr, BLUE, a, 5.0)
	# ---- control valve with sliding spool (closed centre)
	_box(VALVE, a, "")
	var sp: float = st.open
	var shift = 11.0 * sp
	var sy = VALVE.position.y + VALVE.size.y * 0.5
	draw_rect(Rect2(VALVE.position.x + 4, sy - 4, VALVE.size.x - 8, 8), Color(0.08, 0.1, 0.13, a))
	for k in 4:
		var lx = VALVE.position.x + 9 + k * 16 + shift
		draw_rect(Rect2(lx, sy - 6, 9, 12), Color(0.82, 0.85, 0.87, a))
	draw_line(Vector2(VALVE.position.x + 4 + shift, sy), Vector2(VALVE.end.x - 4 + shift, sy), Color(0.82, 0.85, 0.87, a), 2.0)
	if sp > 0.05:
		# opened passages: P -> A (red), B -> T (blue)
		draw_line(Vector2(-112, VALVE.end.y - 3), Vector2(VALVE.end.x - 2, 13), Color(RED, a * sp), 3.0, true)
		draw_line(Vector2(VALVE.end.x - 2, 27), Vector2(-70, VALVE.end.y - 3), Color(BLUE, a * sp), 3.0, true)
	else:
		for p in [Vector2(VALVE.end.x - 2, 13), Vector2(VALVE.end.x - 2, 27)]:
			_lock(p + Vector2(10, 0), a * director.cutaway)
	# ---- joystick + pilot line
	var tilt = deg_to_rad(18.0 * director.joystick)
	var knob = JOY + Vector2(sin(tilt), -cos(tilt)) * 22
	draw_rect(Rect2(JOY.x - 8, JOY.y - 3, 16, 7), Color(0.2, 0.22, 0.25, a))
	draw_line(JOY, knob, Color(0.1, 0.1, 0.1, a), 4.0, true)
	draw_circle(knob, 4.5, Color(0.95, 0.4, 0.15, a), true, -1, true)
	var pilot = PackedVector2Array([JOY + Vector2(0, 4), Vector2(JOY.x, -10), Vector2(VALVE.position.x - 10, -10), Vector2(VALVE.position.x - 10, sy), Vector2(VALVE.position.x, sy)])
	flow_line(pilot, st.pilot_vol, ORANGE, a * (0.45 + 0.55 * director.joystick), 3.0)

func _box(r: Rect2, a: float, _label: String) -> void:
	var sb = StyleBoxFlat.new()
	sb.bg_color = Color(BODY, 0.94 * a)
	sb.border_color = Color(EDGE, a)
	sb.set_border_width_all(1)
	sb.set_corner_radius_all(4)
	sb.anti_aliasing = true
	draw_style_box(sb, r)

func _lock(p: Vector2, a: float) -> void:
	if a <= 0.01:
		return
	draw_circle(p, 6.5, Color(0.98, 0.85, 0.3, a), true, -1, true)
	draw_line(p + Vector2(-3, -3), p + Vector2(3, 3), Color(0.15, 0.1, 0.05, a), 2.0, true)
	draw_line(p + Vector2(3, -3), p + Vector2(-3, 3), Color(0.15, 0.1, 0.05, a), 2.0, true)

## Polyline with dashes advected by `volume` (px of oil travel). Static when
## the piston is static; reverses only if the piston reverses.
func flow_line(pts: PackedVector2Array, volume: float, col: Color, a: float, w: float, standby := false) -> void:
	draw_polyline(pts, Color(0.05, 0.06, 0.08, 0.85 * a), w + 3.0, true)
	draw_polyline(pts, Color(col.darkened(0.35), (0.55 if standby else 0.8) * a), w, true)
	var period = 22.0
	var dash = 9.0
	var total = 0.0
	var offs = fposmod(volume, period)
	for i in pts.size() - 1:
		var p0 = pts[i]
		var p1 = pts[i + 1]
		var seg = p0.distance_to(p1)
		var s = fposmod(offs - total, period)
		while s < seg:
			var e = minf(s + dash, seg)
			draw_line(p0.lerp(p1, s / seg), p0.lerp(p1, e / seg), Color(col.lightened(0.25), a), w - 1.0, true)
			s += period
		total += seg

func signal_line(pts: PackedVector2Array, progress: float, col: Color, a: float) -> void:
	draw_polyline(pts, Color(0.05, 0.06, 0.08, 0.8 * a), 4.5, true)
	draw_polyline(pts, Color(col.darkened(0.4), 0.7 * a), 2.2, true)
	if progress <= 0.0:
		return
	var length = 0.0
	for i in pts.size() - 1:
		length += pts[i].distance_to(pts[i + 1])
	var reach = length * progress
	var acc = 0.0
	for i in pts.size() - 1:
		var seg = pts[i].distance_to(pts[i + 1])
		if acc + seg <= reach:
			draw_line(pts[i], pts[i + 1], Color(col.lightened(0.2), a), 2.8, true)
		elif acc < reach:
			var tip = pts[i].lerp(pts[i + 1], (reach - acc) / seg)
			draw_line(pts[i], tip, Color(col.lightened(0.2), a), 2.8, true)
			if progress < 1.0:
				draw_circle(tip, 4.5, Color(col.lightened(0.45), a), true, -1, true)
		acc += seg
