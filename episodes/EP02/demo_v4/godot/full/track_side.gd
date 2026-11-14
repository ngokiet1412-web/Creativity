@tool
extends Node2D
## SC09 part B: one side of the undercarriage seen from the side.
## `s` = track travel (px) relative to the machine. The sprocket turns by
## s / r_sprocket, the chain links move around the closed loop (top run
## forward, bottom run backward), the ground scrolls backward at the same
## speed as the bottom run: the links on the ground do not slip.

const Kit = preload("res://cutaway/kit.gd")
const PITCH := 34.0
const RS := 62.0           # sprocket pitch radius (rear)
const RI := 62.0           # idler radius (front), same as the loop radius
const XS := -300.0
const XI := 300.0
const Y := 0.0

@export var s := 0.0
@export_range(0, 1) var hi_motor := 0.0
@export_range(0, 1) var wrong := 0.0     # Capy's rotating-rectangle gag

func _process(_d: float) -> void:
	queue_redraw()

func loop_len() -> float:
	return 2.0 * (XI - XS) + PI * RS + PI * RI

## point on the track loop at arc position u (px), counter-clockwise from the
## top of the sprocket going forward along the top run
func at(u: float) -> Array:
	var L = loop_len()
	u = fposmod(u, L)
	var top = XI - XS
	if u < top:
		return [Vector2(XS + u, Y - RS), 0.0]
	u -= top
	if u < PI * RI:
		var a = -PI * 0.5 + u / RI
		return [Vector2(XI, Y + (RS - RI) * 0.0) + Vector2(cos(a), sin(a)) * RI, a + PI * 0.5]
	u -= PI * RI
	if u < top:
		return [Vector2(XI - u, Y + RS), PI]
	u -= top
	var b = PI * 0.5 + u / RS
	return [Vector2(XS, Y) + Vector2(cos(b), sin(b)) * RS, b + PI * 0.5]

func _draw() -> void:
	var font = ThemeDB.fallback_font
	# ground (scrolls with the bottom run: no slip)
	var gy = Y + RS + 16
	draw_rect(Rect2(-900, gy, 1800, 220), Color("#8a6747"))
	var off = fposmod(-s, 60.0)
	var x = -900 + off - 60
	while x < 900:
		draw_rect(Rect2(x, gy + 6, 34, 8), Color(0.3, 0.2, 0.12, 0.35))
		draw_circle(Vector2(x + 20, gy + 40 + fmod(abs(x) * 0.37, 60)), 4, Color(0.35, 0.24, 0.15, 0.4))
		x += 60
	draw_line(Vector2(-900, gy), Vector2(900, gy), Kit.INK, 2.0)
	# track frame
	Kit.body(self, Kit.rect_pts(Rect2(XS + 40, Y - 34, XI - XS - 80, 68)), Color("#4a4640"), 2.2)
	# rollers (turn with the bottom run)
	for k in 5:
		var rx = XS + 110 + k * 95.0
		var rr = 20.0
		draw_circle(Vector2(rx, Y + RS - rr - 6), rr, Color("#6a6e75"))
		draw_arc(Vector2(rx, Y + RS - rr - 6), rr, 0, TAU, 20, Kit.INK, 2.0, true)
		var a = s / rr
		draw_line(Vector2(rx, Y + RS - rr - 6), Vector2(rx, Y + RS - rr - 6) + Vector2(cos(a), sin(a)) * rr * 0.8, Kit.INK, 2.0)
	# idler
	draw_circle(Vector2(XI, Y), RI - 10, Color("#6a6e75"))
	draw_arc(Vector2(XI, Y), RI - 10, 0, TAU, 32, Kit.INK, 2.2, true)
	draw_line(Vector2(XI, Y), Vector2(XI, Y) + Vector2(cos(s / RI), sin(s / RI)) * (RI - 16), Kit.INK, 3.0)
	# sprocket + travel motor / final drive
	if hi_motor > 0.0:
		for k in 4:
			draw_circle(Vector2(XS, Y), RS + 6 + k * 8, Color(1, 0.82, 0.3, 0.08 * hi_motor), true, -1, true)
	var sp = PackedVector2Array()
	var teeth = 11
	for i in teeth * 4:
		var u = float(i) / (teeth * 4)
		var a = s / RS + u * TAU
		var tooth = fposmod(u * teeth, 1.0)
		var rr = RS + (6.0 if tooth > 0.3 and tooth < 0.7 else -10.0)
		sp.append(Vector2(XS, Y) + Vector2(cos(a), sin(a)) * rr)
	draw_colored_polygon(sp, Color("#7c8088"))
	sp.append(sp[0])
	draw_polyline(sp, Kit.INK, 2.2, true)
	draw_circle(Vector2(XS, Y), 30, Color("#b23a2c"))
	draw_arc(Vector2(XS, Y), 30, 0, TAU, 24, Kit.INK, 2.0, true)
	draw_circle(Vector2(XS, Y), 8, Kit.INK)
	# chain links around the loop
	var L = loop_len()
	var n = int(L / PITCH)
	var pitch = L / n
	for i in n:
		var u = i * pitch + s
		var pa = at(u)
		var pb = at(u + pitch * 0.82)
		var p: Vector2 = pa[0]
		var q: Vector2 = pb[0]
		var d = (q - p)
		var nrm = d.normalized().orthogonal()
		# shoe on the outside of the loop
		var out = (p - Vector2((XS + XI) * 0.5, Y)).normalized()
		if nrm.dot(out) < 0:
			nrm = -nrm
		var shoe = PackedVector2Array([p, q, q + nrm * 14, p + nrm * 14])
		draw_colored_polygon(shoe, Color("#55504a"))
		shoe.append(shoe[0])
		draw_polyline(shoe, Kit.INK, 1.6, true)
		draw_circle(p, 4, Color("#9aa0a6"))
	if wrong > 0.01:
		var r = Rect2(XS - 80, Y - RS - 20, XI - XS + 160, 2 * RS + 40)
		var ang = s / 150.0
		draw_set_transform((r.position + r.end) * 0.5, ang, Vector2.ONE)
		draw_rect(Rect2(-r.size * 0.5, r.size), Color(0.2, 0.2, 0.2, 0.5 * wrong))
		draw_rect(Rect2(-r.size * 0.5, r.size), Color(1, 0.5, 0.5, wrong), false, 4.0)
		draw_set_transform(Vector2.ZERO)
		var c = (r.position + r.end) * 0.5
		draw_line(c + Vector2(-160, -120), c + Vector2(160, 120), Color(1, 0.2, 0.2, wrong), 12.0, true)
		draw_line(c + Vector2(-160, 120), c + Vector2(160, -120), Color(1, 0.2, 0.2, wrong), 12.0, true)
