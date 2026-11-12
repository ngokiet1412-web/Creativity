@tool
extends Node2D
## Inline six-cylinder diesel, longitudinal section (crank axis horizontal).
## Proportions follow SAA6D107E-1: 6 cylinders, bore 107 mm, stroke 124 mm
## (6.69 L, Komatsu brochure CEN00049-08). 1 px = 1 mm * PX.
## Firing order 1-5-3-6-2-4 (inline-6 standard) - pairs 1/6, 2/5, 3/4 move together.
## In side view the crank pins move vertically; an end-view inset shows the
## slider-crank rotation of cylinder 1.

const Kit = preload("res://cutaway/kit.gd")
const PX := 0.9
const BORE := 107.0 * PX
const R := 62.0 * PX            # crank radius = stroke / 2
const ROD := 192.0 * PX         # con-rod centre distance (illustrative)
const PITCH := 128.0 * PX
const DECK := -300.0
const CRANK_Y := 0.0
const ORDER := [0.0, 480.0, 240.0, 600.0, 120.0, 360.0]   # cycle offset of cyl 1..6

@export var crank_deg := 0.0: set = _set_crank
@export var show_inset := true
@export var inset_pos := Vector2(140, 330)
@export_range(0, 1) var inset_alpha := 1.0
@export_range(0, 1) var ghost := 0.0          # fade for transitions

var font: Font

func _set_crank(v: float) -> void:
	crank_deg = v
	queue_redraw()

func _ready() -> void:
	font = ThemeDB.fallback_font

func cyl_x(i: int) -> float:
	return 70.0 + i * PITCH + BORE * 0.5

func piston_top(phase_deg: float) -> float:
	var th = deg_to_rad(phase_deg)
	return CRANK_Y - (R * cos(th) + sqrt(ROD * ROD - pow(R * sin(th), 2))) - 52.0

func _draw() -> void:
	var a = 1.0 - ghost
	modulate.a = a
	var x0 = 20.0
	var x1 = cyl_x(5) + BORE * 0.5 + 50.0
	# --- oil pan and crankcase background
	Kit.body(self, PackedVector2Array([Vector2(x0 + 20, 60), Vector2(x1 - 20, 60), Vector2(x1 - 60, 150), Vector2(x0 + 60, 150)]), Kit.CAST.darkened(0.2))
	draw_colored_polygon(PackedVector2Array([Vector2(x0 + 40, 105), Vector2(x1 - 40, 105), Vector2(x1 - 65, 144), Vector2(x0 + 65, 144)]), Color("#8a5a1c"))
	draw_rect(Rect2(x0, DECK, x1 - x0, 60.0 - DECK), Color("#1b222b"))
	# --- crankshaft (behind the cut block)
	var pins = []
	for i in 6:
		var ph: float = crank_deg - ORDER[i]
		var th = deg_to_rad(ph)
		pins.append([Vector2(cyl_x(i), CRANK_Y - R * cos(th)), sin(th)])
	Kit.cyl(self, Vector2(x0 + 10, CRANK_Y), Vector2(x1 + 30, CRANK_Y), 40.0, Kit.STEEL_DARK.lightened(0.2))
	for i in 6:
		var p: Vector2 = pins[i][0]
		var depth: float = pins[i][1]
		var shade = 0.25 * (1.0 - depth)
		var away = Vector2(0, CRANK_Y - p.y).normalized() if absf(CRANK_Y - p.y) > 0.5 else Vector2(0, 1)
		for side in [-1, 1]:
			var wx = cyl_x(i) + side * 30.0
			# crank web from journal to pin, counterweight lobe on the opposite side
			var web = PackedVector2Array([Vector2(wx - 9, p.y), Vector2(wx + 9, p.y),
				Vector2(wx + 9, CRANK_Y) + away * R * 0.55 + Vector2(6, 0), Vector2(wx - 9, CRANK_Y) + away * R * 0.55 - Vector2(6, 0)])
			Kit.body(self, web, Kit.STEEL_DARK.darkened(shade))
		Kit.cyl(self, Vector2(cyl_x(i) - 22, p.y), Vector2(cyl_x(i) + 22, p.y), 30.0, Kit.STEEL.darkened(shade))
	# --- pistons and rods
	for i in 6:
		var ph: float = crank_deg - ORDER[i]
		var top = piston_top(ph)
		var cx = cyl_x(i)
		var pin_y = top + 52.0
		var crank_pin: Vector2 = pins[i][0]
		# connecting rod (I-beam, side view)
		var rod = PackedVector2Array([Vector2(cx - 9, pin_y), Vector2(cx + 9, pin_y), Vector2(cx + 15, crank_pin.y - 14), Vector2(cx - 15, crank_pin.y - 14)])
		Kit.body(self, rod, Kit.STEEL)
		draw_line(Vector2(cx, pin_y + 6), Vector2(cx, crank_pin.y - 18), Kit.STEEL_DARK, 3.0, true)
		Kit.disc(self, Vector2(cx, crank_pin.y), 19, Kit.STEEL)
		# piston (half sectioned: left half cut, right half outside)
		var pr = Rect2(cx - BORE * 0.5 + 3, top, BORE - 6, 78)
		Kit.body(self, Kit.rect_pts(Rect2(pr.position + Vector2(pr.size.x * 0.5, 0), Vector2(pr.size.x * 0.5, pr.size.y))), Color("#b9c1c9"))
		Kit.cut(self, Kit.rect_pts(Rect2(pr.position, Vector2(pr.size.x * 0.5, pr.size.y))), Kit.CUT_FACE, 7.0)
		draw_rect(Rect2(pr.position + Vector2(10, -1), Vector2(pr.size.x - 20, 7)), Color("#6d757d"))   # bowl lip
		for k in 3:
			draw_line(Vector2(pr.position.x, top + 14 + k * 9), Vector2(pr.end.x, top + 14 + k * 9), Kit.INK, 2.0)
		Kit.disc(self, Vector2(cx, pin_y), 11, Kit.BRASS)
		# combustion: glow just after TDC on the power stroke (cycle phase 0-40 deg)
		var cyc = fposmod(ph, 720.0)
		if cyc < 45.0:
			var k2 = 1.0 - cyc / 45.0
			draw_rect(Rect2(cx - BORE * 0.5 + 4, DECK + 4, BORE - 8, top - DECK - 4), Color(1.0, 0.55, 0.15, 0.75 * k2))
			draw_circle(Vector2(cx, DECK + 14), 12 * k2 + 4, Color(1.0, 0.85, 0.4, 0.9 * k2), true, -1, true)
	# --- block: sectioned webs between the bores (cylinder region) + skirts
	var top_y = DECK
	var bot_y = -70.0
	var edges = [x0]
	for i in 6:
		edges.append(cyl_x(i) - BORE * 0.5 - 6.0)
		edges.append(cyl_x(i) + BORE * 0.5 + 6.0)
	edges.append(x1)
	for k in range(0, edges.size(), 2):
		var r = Rect2(edges[k], top_y, edges[k + 1] - edges[k], bot_y - top_y)
		if r.size.x > 1.0:
			Kit.cut(self, Kit.rect_pts(r), Kit.CUT_FACE, 11.0, 2.0)
			if r.size.x > 20.0:
				draw_rect(Rect2(r.position.x + r.size.x * 0.5 - 5, top_y + 18, 10, 150), Color("#3b6e8f"))
				draw_rect(Rect2(r.position.x + r.size.x * 0.5 - 5, top_y + 18, 10, 150), Kit.INK, false, 1.2)
	for i in 6:
		for side in [-1.0, 1.0]:
			var lx: float = cyl_x(i) + side * (BORE * 0.5 + 3.0)
			draw_rect(Rect2(lx - 3, top_y, 6, bot_y - top_y + 20), Color("#8a949e"))
	Kit.cut(self, Kit.rect_pts(Rect2(x0, bot_y, 26, 130)), Kit.CUT_FACE, 11.0)
	Kit.cut(self, Kit.rect_pts(Rect2(x1 - 26, bot_y, 26, 130)), Kit.CUT_FACE, 11.0)
	# --- cylinder head (sectioned) with valves and injectors
	var head = PackedVector2Array([Vector2(x0 + 6, DECK - 92), Vector2(x1 - 6, DECK - 92), Vector2(x1 - 6, DECK), Vector2(x0 + 6, DECK)])
	Kit.cut(self, head, Kit.CUT_FACE.darkened(0.05), 10.0)
	Kit.body(self, PackedVector2Array([Vector2(x0 + 20, DECK - 150), Vector2(x1 - 20, DECK - 150), Vector2(x1 - 10, DECK - 92), Vector2(x0 + 10, DECK - 92)]), Color("#3f4a56"))
	draw_string(font, Vector2(x0 + 40, DECK - 112), "SAA6D107E-1", HORIZONTAL_ALIGNMENT_LEFT, -1, 26, Color(0.85, 0.88, 0.92, 0.55))
	for i in 6:
		var cx = cyl_x(i)
		var cyc = fposmod(crank_deg - ORDER[i], 720.0)
		var ex_lift = _lift(cyc, 170.0, 380.0) * 12.0
		var in_lift = _lift(cyc, 350.0, 560.0) * 12.0
		for v in [[-24.0, ex_lift, Color("#c8743a")], [24.0, in_lift, Color("#7fa6c8")]]:
			var vx: float = cx + v[0]
			var lift: float = v[1]
			draw_line(Vector2(vx, DECK - 86), Vector2(vx, DECK - 6 + lift), Kit.STEEL, 5.0)
			draw_colored_polygon(PackedVector2Array([Vector2(vx - 14, DECK - 2 + lift), Vector2(vx + 14, DECK - 2 + lift),
				Vector2(vx + 4, DECK - 12 + lift), Vector2(vx - 4, DECK - 12 + lift)]), v[2])
			Kit.spring(self, Vector2(vx, DECK - 88), Vector2(vx, DECK - 52 + lift * 0.3), 4, 16)
		Kit.cyl(self, Vector2(cx, DECK - 95), Vector2(cx, DECK - 8), 12, Kit.BRASS)     # common-rail injector
	for i in 14:
		Kit.bolt(self, Vector2(x0 + 30 + i * (x1 - x0 - 60) / 13.0, DECK - 140), 5.5)
	# --- flywheel housing + flywheel (ring gear teeth scroll with rotation)
	var fx = x1 + 30.0
	Kit.cut(self, PackedVector2Array([Vector2(fx - 6, -230), Vector2(fx + 70, -250), Vector2(fx + 70, 170), Vector2(fx - 6, 150)]), Kit.CUT_FACE.darkened(0.08), 10.0)
	Kit.body(self, Kit.rect_pts(Rect2(fx + 8, -200, 46, 340)), Kit.STEEL_DARK)
	var tooth = fposmod(crank_deg * 1.2, 14.0)
	var y = -200.0 + tooth
	while y < 140.0:
		draw_line(Vector2(fx + 8, y), Vector2(fx + 54, y), Color(0.1, 0.12, 0.14, 0.7), 2.0)
		y += 14.0
	if show_inset and inset_alpha > 0.01:
		modulate.a = 1.0
		_inset(inset_pos)

func _lift(cyc: float, open_deg: float, close_deg: float) -> float:
	if cyc < open_deg or cyc > close_deg:
		return 0.0
	return sin(PI * (cyc - open_deg) / (close_deg - open_deg))

func _cut_with_holes(poly: PackedVector2Array, holes: Array, crank_y: float) -> void:
	# draw hatched block, then punch bores (dark cylinder walls + liners)
	Kit.cut(self, poly, Kit.CUT_FACE, 11.0, 2.4)
	for h: Rect2 in holes:
		draw_rect(h, Color("#232b34"))
		draw_rect(Rect2(h.position - Vector2(6, 0), Vector2(6, h.size.y)), Color("#8a949e"))
		draw_rect(Rect2(Vector2(h.end.x, h.position.y), Vector2(6, h.size.y)), Color("#8a949e"))
		draw_rect(Rect2(h.position - Vector2(6, 0), Vector2(h.size.x + 12, h.size.y)), Kit.INK, false, 1.8)
	# main bearing saddles
	draw_rect(Rect2(poly[0].x, crank_y - 26, poly[1].x - poly[0].x, 52), Color("#1b222b"))

## End view of cylinder 1: classic slider-crank, true rod angle
func _inset(c: Vector2) -> void:
	var rad = 170.0
	draw_circle(c, rad, Color(0.06, 0.09, 0.14, 0.94), true, -1, true)
	draw_arc(c, rad, 0, TAU, 60, Color(0.75, 0.85, 1.0, 0.8), 2.5, true)
	var th = deg_to_rad(crank_deg - ORDER[0])
	var s = 0.55
	var cc = c + Vector2(0, 60)
	var pin = cc + Vector2(sin(th), -cos(th)) * R * s
	var py = cc.y - (R * cos(th) + sqrt(ROD * ROD - pow(R * sin(th), 2))) * s
	var ppin = Vector2(cc.x, py)
	var bt = cc.y - (R + ROD) * s - 40
	var bb = cc.y - (ROD - R) * s + 16
	draw_rect(Rect2(cc.x - BORE * 0.5 * s - 6, bt, BORE * s + 12, bb - bt), Color("#8a949e"))
	draw_rect(Rect2(cc.x - BORE * 0.5 * s, bt, BORE * s, bb - bt), Color("#232b34"))
	draw_circle(cc, R * s + 14, Kit.STEEL_DARK, true, -1, true)
	draw_arc(cc, R * s, 0, TAU, 40, Color(1, 1, 1, 0.25), 1.5, true)
	draw_line(ppin, pin, Kit.INK, 12.0, true)
	draw_line(ppin, pin, Kit.STEEL, 8.0, true)
	draw_line(cc, pin, Kit.STEEL_DARK.lightened(0.3), 14.0, true)
	Kit.disc(self, pin, 8, Kit.STEEL)
	Kit.disc(self, cc, 10, Kit.STEEL)
	Kit.body(self, Kit.rect_pts(Rect2(ppin.x - BORE * 0.5 * s + 2, py - 18, BORE * s - 4, 30)), Color("#b9c1c9"))
	Kit.disc(self, ppin, 6, Kit.BRASS)
	Kit.label(self, font, c + Vector2(-112, rad - 20), "nhìn từ đầu máy · xi lanh 1", 18)
	if inset_alpha < 1.0:
		draw_circle(c, rad + 3, Color("#0c1524", 1.0 - inset_alpha), true, -1, true)
