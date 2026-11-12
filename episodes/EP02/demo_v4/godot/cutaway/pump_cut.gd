@tool
extends Node2D
## Tandem variable-displacement axial piston pump, section through the shaft.
## PC200-8: HPV95+95, two pumps on one shaft (shop manual specification).
## Internal arrangement is the generic swash-plate design (rotary group,
## swash plate + servo piston, valve plate with two crescent ports); it is an
## illustration, not a Komatsu part drawing.
## Kinematics: each piston shoe rides on the swash plane, so its axial position
## is x = plane(y); with y = Rb*cos(psi) the stroke is 2*Rb*tan(alpha).

const Kit = preload("res://cutaway/kit.gd")
const RB := 86.0            # pitch radius of the bores (px)
const N := 9
const PIST_L := 150.0
const A_MIN := 3.0
const A_MAX := 17.0

@export var shaft_deg := 0.0: set = _set_shaft
@export_range(0, 1) var swash_f := 0.1: set = _set_sf
@export_range(0, 1) var swash_r := 0.1: set = _set_sr
@export var flow_travel_f := 0.0
@export var flow_travel_r := 0.0
@export var show_rear := true
@export var show_valve_plate_inset := true
@export var show_stroke := false
@export_range(0, 1) var outlet_live := 1.0
var font: Font

func _set_shaft(v: float) -> void:
	shaft_deg = v
	queue_redraw()
func _set_sf(v: float) -> void:
	swash_f = v
	queue_redraw()
func _set_sr(v: float) -> void:
	swash_r = v
	queue_redraw()

func _ready() -> void:
	font = ThemeDB.fallback_font

func alpha_deg(s: float) -> float:
	return lerpf(A_MIN, A_MAX, s)

func _draw() -> void:
	# input shaft + coupling from the engine flywheel
	Kit.cyl(self, Vector2(-120, 0), Vector2(760.0 if show_rear else 470.0, 0), 34, Kit.STEEL)
	_spline_marks(Vector2(-120, 0), Vector2(40, 0))
	Kit.body(self, Kit.rect_pts(Rect2(-80, -120, 34, 240)), Color("#4a4f57"))     # damper disc
	for k in 6:
		Kit.bolt(self, Vector2(-63, -100 + k * 40), 5)
	_unit(1.0, 120.0, 200.0, swash_f, flow_travel_f)
	if show_rear:
		_unit(-1.0, 680.0, 600.0, swash_r, flow_travel_r)
	# centre valve block (sectioned) with outlets P1/P2 and common suction
	var vb = Rect2(345, -175, 110, 350)
	Kit.cut(self, Kit.rect_pts(vb), Kit.CUT_FACE.darkened(0.06), 9.0, 2.4)
	draw_rect(Rect2(vb.position.x + 14, -150, 26, 120), Color(Kit.RED, 0.9))       # P1 gallery
	draw_rect(Rect2(vb.position.x + 70, -150, 26, 120), Color(Kit.RED, 0.9))       # P2 gallery
	draw_rect(Rect2(vb.position.x + 20, 30, 70, 120), Color(Kit.BLUE, 0.85))       # suction
	Kit.pipe(self, PackedVector2Array([Vector2(372, -150), Vector2(372, -300)]), Kit.RED, -flow_travel_f, 22, outlet_live)
	if show_rear:
		Kit.pipe(self, PackedVector2Array([Vector2(428, -150), Vector2(428, -300)]), Kit.RED, -flow_travel_r, 22, outlet_live)
	Kit.pipe(self, PackedVector2Array([Vector2(400, 330), Vector2(400, 150)]), Kit.BLUE, (flow_travel_f + flow_travel_r) * 0.5, 30, outlet_live)
	Kit.label(self, font, Vector2(330, -312), "P1", 22)
	if show_rear:
		Kit.label(self, font, Vector2(420, -312), "P2", 22)
	if show_valve_plate_inset:
		_valve_plate(Vector2(400, 470) if not show_rear else Vector2(880, -10), swash_f)

## One pump unit. dir = +1 swash on the left, -1 mirrored on the right.
func _unit(dir: float, pivot_x: float, block_x: float, sw: float, travel: float) -> void:
	var al = deg_to_rad(alpha_deg(sw))
	var shell_x0 = pivot_x - dir * 70.0
	var shell = Rect2(minf(shell_x0, block_x + dir * 145.0), -190, absf(block_x + dir * 145.0 - shell_x0), 380)
	# casing (sectioned shell: top and bottom walls + end wall)
	Kit.cut(self, Kit.rect_pts(Rect2(shell.position.x, -190, shell.size.x, 26)), Kit.CUT_FACE, 9.0)
	Kit.cut(self, Kit.rect_pts(Rect2(shell.position.x, 164, shell.size.x, 26)), Kit.CUT_FACE, 9.0)
	var endx = shell_x0 - (26.0 if dir > 0 else 0.0)
	Kit.cut(self, Kit.rect_pts(Rect2(endx, -164, 26, 328)), Kit.CUT_FACE, 9.0)
	draw_rect(Rect2(shell.position.x + (26 if dir > 0 else 0), -164, shell.size.x - 26, 328), Color(0.13, 0.16, 0.2, 0.95))
	Kit.cyl(self, Vector2(shell.position.x, 0), Vector2(shell.end.x, 0), 34, Kit.STEEL)
	# swash plate on its cradle, tilted by alpha
	var piv = Vector2(pivot_x, 0)
	var t_dir = Vector2(sin(al) * dir, -cos(al))            # along the plate, upward
	var n_dir = Vector2(cos(al) * dir, sin(al))             # plate normal toward the block
	var plate = PackedVector2Array([piv - t_dir * 150 - n_dir * 14, piv + t_dir * 150 - n_dir * 14,
		piv + t_dir * 150 + n_dir * 14, piv - t_dir * 150 + n_dir * 14])
	Kit.body(self, PackedVector2Array([piv + Vector2(-dir * 40, -60), piv + Vector2(-dir * 40, 60), piv + Vector2(-dir * 14, 40), piv + Vector2(-dir * 14, -40)]), Kit.CAST)
	Kit.body(self, plate, Color("#7d8a96"))
	var face = plate[2]
	# rotary group: barrel, bores, pistons + shoes (sorted back to front)
	var bx0 = block_x
	var bx1 = block_x + dir * 125.0
	var barrel = Kit.rect_pts(Rect2(minf(bx0, bx1), -128, 125, 256))
	draw_colored_polygon(barrel, Color("#59636d"))
	var order = []
	for k in N:
		var psi = deg_to_rad(shaft_deg * dir) + k * TAU / N
		order.append([sin(psi), psi])
	order.sort_custom(func(p, q): return p[0] < q[0])
	var barrel_drawn = false
	for item in order:
		var z: float = item[0]
		var psi: float = item[1]
		if z >= 0.0 and not barrel_drawn:
			# translucent barrel between back-half and front-half pistons
			draw_colored_polygon(barrel, Color(0.66, 0.71, 0.76, 0.62))
			barrel_drawn = true
		var y = RB * cos(psi)
		var s_par = -y / maxf(cos(al), 0.2)
		var contact = piv + n_dir * 14 + t_dir * s_par
		var head_x = contact.x + dir * 14.0
		var end_x = head_x + dir * PIST_L
		var shade = 0.45 * (1.0 - (z * 0.5 + 0.5))
		var y2 = RB * cos(psi + dir * 0.02)
		var x2 = (piv + n_dir * 14 + t_dir * (-y2 / maxf(cos(al), 0.2))).x
		var discharging = dir * (x2 - contact.x) > 0.0
		var chamber_col = Kit.RED if discharging else Kit.BLUE
		var cha = Rect2(minf(end_x, bx1 - dir * 6), y - 11, absf(bx1 - dir * 6 - end_x), 22)
		draw_rect(cha, Color(chamber_col.darkened(0.1 + shade), 0.95))
		Kit.cyl(self, Vector2(head_x, y), Vector2(end_x, y), 22, Kit.STEEL.darkened(shade))
		var shoe = PackedVector2Array([contact + t_dir * 16, contact - t_dir * 16,
			contact - t_dir * 11 + n_dir * 12, contact + t_dir * 11 + n_dir * 12])
		Kit.body(self, shoe, Kit.BRASS.darkened(shade))
	if not barrel_drawn:
		draw_colored_polygon(barrel, Color(0.66, 0.71, 0.76, 0.62))
	# barrel end bands (sectioned) where the bores open to the valve plate
	Kit.cut(self, Kit.rect_pts(Rect2(minf(bx1, bx1 - dir * 16), -128, 16, 256)), Color("#aeb7c0"), 7.0, 1.6)
	Kit.outline(self, Kit.rect_pts(Rect2(minf(bx0, bx1), -128, 125, 256)), 2.4)
	# valve plate (thin disc) between barrel and centre block
	var vpx = bx1
	Kit.cut(self, Kit.rect_pts(Rect2(minf(vpx, vpx + dir * 14), -150, 14, 300)), Kit.BRASS.darkened(0.2), 5.0)
	_spline_marks(Vector2(minf(bx0, bx1), 0), Vector2(maxf(bx0, bx1), 0))
	# servo piston above: its position sets the swash angle through a link
	var top_pin = piv + t_dir * 140
	var servo_x = top_pin.x + dir * 26
	var sb = Rect2(minf(pivot_x - dir * 40, pivot_x + dir * 190), -262, 230, 52)
	Kit.cut(self, Kit.rect_pts(sb), Kit.CUT_FACE, 8.0)
	draw_rect(Rect2(sb.position.x + 14, -250, sb.size.x - 28, 28), Color("#1a2028"))
	draw_rect(Rect2(minf(servo_x, servo_x + dir * 90), -248, 90, 24), Color("#b9c1c9"))
	Kit.outline(self, Kit.rect_pts(Rect2(minf(servo_x, servo_x + dir * 90), -248, 90, 24)), 1.6)
	draw_line(Vector2(servo_x, -236), top_pin, Kit.INK, 8.0, true)
	draw_line(Vector2(servo_x, -236), top_pin, Kit.STEEL, 5.0, true)
	Kit.disc(self, top_pin, 7, Kit.STEEL)
	Kit.disc(self, piv, 9, Kit.STEEL_DARK)
	if show_stroke and dir > 0:
		_stroke_dim(piv, al, n_dir, t_dir, dir)

func _stroke_dim(piv: Vector2, al: float, n_dir: Vector2, t_dir: Vector2, dir: float) -> void:
	var y_top = -RB
	var y_bot = RB
	var xt = (piv + n_dir * 14 + t_dir * (-y_top / cos(al))).x
	var xb = (piv + n_dir * 14 + t_dir * (-y_bot / cos(al))).x
	var yy = -318.0
	draw_line(Vector2(xb, yy), Vector2(xt, yy), Color(1, 0.85, 0.3), 3.0, true)
	draw_line(Vector2(xb, yy - 10), Vector2(xb, yy + 10), Color(1, 0.85, 0.3), 3.0)
	draw_line(Vector2(xt, yy - 10), Vector2(xt, yy + 10), Color(1, 0.85, 0.3), 3.0)
	Kit.label(self, font, Vector2(minf(xb, xt) - 10, yy - 16), "hành trình piston", 20, Color(1, 0.88, 0.45))

func _spline_marks(a: Vector2, b: Vector2) -> void:
	var off = fposmod(shaft_deg * 0.35, 18.0)
	var x = a.x + off
	while x < b.x:
		draw_line(Vector2(x, -15), Vector2(x - 6, 15), Color(0.2, 0.24, 0.28, 0.55), 2.0)
		x += 18.0

## Valve plate seen end-on: two crescent ports, the 9 bores sweep over them.
func _valve_plate(c: Vector2, sw: float) -> void:
	var r = 120.0
	draw_circle(c, r + 20, Color(0.06, 0.09, 0.14, 0.95), true, -1, true)
	draw_arc(c, r + 20, 0, TAU, 64, Color(0.75, 0.85, 1.0, 0.8), 2.5, true)
	draw_circle(c, r, Kit.BRASS.darkened(0.25), true, -1, true)
	for half in [[0.12, PI - 0.12, Kit.RED], [PI + 0.12, TAU - 0.12, Kit.BLUE]]:
		var pts = PackedVector2Array()
		for i in 25:
			var a: float = lerpf(half[0], half[1], i / 24.0)
			pts.append(c + Vector2(sin(a), -cos(a)) * (RB * 0.95 + 14))
		for i in 25:
			var a: float = lerpf(half[1], half[0], i / 24.0)
			pts.append(c + Vector2(sin(a), -cos(a)) * (RB * 0.95 - 14))
		draw_colored_polygon(pts, half[2])
		Kit.outline(self, pts, 1.5)
	for k in N:
		var psi = deg_to_rad(shaft_deg) + k * TAU / N
		var p = c + Vector2(sin(psi), -cos(psi)) * RB * 0.95
		var col = Kit.RED if sin(psi) > 0.0 else Kit.BLUE
		draw_circle(p, 12, Color(0.05, 0.05, 0.06, 0.55), true, -1, true)
		draw_arc(p, 12, 0, TAU, 20, col.lightened(0.5), 2.2, true)
	Kit.disc(self, c, 18, Kit.STEEL)
	Kit.label(self, font, c + Vector2(-112, r + 52), "đĩa van · nhìn dọc trục", 19)
	Kit.label(self, font, c + Vector2(r * 0.55, -r * 0.8), "xả", 20, Kit.RED.lightened(0.4))
	Kit.label(self, font, c + Vector2(-r * 0.95, -r * 0.8), "hút", 20, Kit.BLUE.lightened(0.4))
