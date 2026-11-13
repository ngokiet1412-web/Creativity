@tool
extends RefCounted
## V4.2 boom-cylinder section for SC05 (principle drawing, not a Komatsu part
## drawing). Drawn in the SAME envelope, position and scale as the approved
## V4 cylinder (sc05.gd: a0, 520 px barrel, 120 px outer, 84 px bore, 44 px
## rod, piston at a0.x + 40 + ext), so layout, camera and timing are unchanged.
##
## Technical fixes over V4 (see SC05_V42_REPORT.md):
##  - port A now opens through the end cap into the cap-side chamber; in V4 it
##    sat under the piston when the rod was fully retracted
##  - base pin is joined to the cap by a clevis and held in a fixed frame lug
##    (in V4 it floated next to the barrel)
##  - the rod ends in a rod eye + pin in a boom lug instead of a bare bar
##  - rod-side return flow = cap-side flow x (1 - d_rod^2 / D_bore^2) = 0.726,
##    not 0.5 (computed from the drawn 84 px bore and 44 px rod)
## Visual polish: hatched section walls, gland with guide bush, rod seal and
## wiper, piston seals + wear band + nut, chrome rod highlight, soft shadow
## from the shared upper-left key light, uniform 2.2 px ink.

const Kit = preload("res://cutaway/kit.gd")

const L := 520.0          # barrel length (as V4)
const RO := 60.0          # outer half height (as V4)
const RI := 42.0          # bore half height (as V4: 84 px)
const ROD := 22.0         # rod half width (as V4: 44 px)
const CAP := 40.0         # end cap thickness: chamber starts at a0.x + 40 (as V4 piston start)
const PIST := 30.0        # piston width
const GLAND := 490.0      # gland inner face, x from a0
const ROD_LEN := 600.0    # as V4 (rod drawn pist+20 .. pist+620)
const AREA_RATIO := 1.0 - (ROD * ROD) / (RI * RI)   # annulus / cap area = 0.726
const PAINT := Color("#e7a82b")
const W := 2.2


static func _soft_shadow(c: CanvasItem, r: Rect2, off := Vector2(8, 12)) -> void:
	for i in 5:
		var g = 4.0 + i * 4.0
		c.draw_rect(Rect2(r.position + off - Vector2(g, g) * 0.5, r.size + Vector2(g, g)), Color(0, 0, 0, 0.07))


## dashes travelling along a polyline (oil movement inside a chamber/passage)
static func _stream(c: CanvasItem, pts: PackedVector2Array, col: Color, travel: float, live: float, w := 5.0) -> void:
	if live <= 0.01:
		return
	var seglen = []
	var total = 0.0
	for i in range(pts.size() - 1):
		var l = pts[i].distance_to(pts[i + 1])
		seglen.append(l)
		total += l
	var step = 26.0
	var d = fposmod(travel, step)
	while d < total:
		var acc = 0.0
		for i in range(seglen.size()):
			if d <= acc + seglen[i]:
				var u = (d - acc) / seglen[i]
				var p = pts[i].lerp(pts[i + 1], u)
				var dir = (pts[i + 1] - pts[i]).normalized()
				c.draw_line(p - dir * 5.0, p + dir * 5.0, Color(col, 0.85 * live), w, true)
				break
			acc += seglen[i]
		d += step


## a0: cap-end centre line point (V4 a0). ext: rod travel px. state:
##   flow_a  0..1 current cap-side flow (piston speed / max speed)
##   travel_a, travel_b  integrated oil movement (same values the pipes use)
##   pressure 0..1  cap-side pressure (holding or moving: load pressure)
static func draw(c: CanvasItem, font: Font, a0: Vector2, ext: float, flow_a: float, travel_a: float, travel_b: float, pressure: float) -> void:
	var X = a0.x
	var Y = a0.y
	var pist = X + CAP + ext
	var rod_end = pist + 20.0 + ROD_LEN

	# --- shadows (key light upper-left)
	_soft_shadow(c, Rect2(X - 60, Y - RO, L + 72, RO * 2))
	_soft_shadow(c, Rect2(pist + 20, Y - ROD, rod_end - pist - 20, ROD * 2), Vector2(6, 9))

	# --- fixed frame lug + base pin (clevis on the cap)
	var lug = Kit.rounded(Rect2(X - 58, Y - 26, 44, 104), 14)
	Kit.cut(c, lug, Color("#8d98a4"), 8.0, W)
	for i in 7:                                       # fixed-support hatching
		var gx = X - 64 + i * 9.0
		c.draw_line(Vector2(gx, Y + 86), Vector2(gx - 8, Y + 96), Kit.INK, 1.6, true)
	c.draw_line(Vector2(X - 66, Y + 85), Vector2(X - 6, Y + 85), Kit.INK, W, true)
	Kit.body(c, Kit.rect_pts(Rect2(X - 36, Y - 17, 36, 34)), Kit.STEEL_DARK, W)   # clevis tongue
	_pin(c, Vector2(X - 30, Y), 14.0)

	# --- chambers (oil)
	var red = Kit.RED.darkened(0.25 - 0.18 * pressure)
	c.draw_rect(Rect2(X + CAP, Y - RI, pist - X - CAP, RI * 2), red)
	c.draw_rect(Rect2(pist + PIST, Y - RI, X + GLAND - pist - PIST, RI * 2), Kit.BLUE.darkened(0.15))
	# oil inside: inflow fans from port A into the cap side, outflow converges to port B
	var fa = clampf(flow_a, 0.0, 1.0)
	for k in [-1.0, 1.0]:
		var ya = Y + k * 18.0
		_stream(c, PackedVector2Array([Vector2(X + CAP + 6, Y + 24), Vector2(X + CAP + 22, ya), Vector2(pist - 6, ya)]),
			Color("#ffb3a3"), travel_a * 0.35, fa * clampf((pist - X - CAP) / 40.0, 0.0, 1.0), 3.0)
	for k in [-1.0, 1.0]:
		var yb = Y + k * 32.0
		_stream(c, PackedVector2Array([Vector2(pist + PIST + 4, yb), Vector2(X + 470, yb), Vector2(X + 478, Y + RI - 2)]),
			Color("#bfe2ff"), travel_b * 0.35, fa, 3.0)

	# --- barrel walls (section), end cap with drilled port A, port B boss
	var paint_face = PAINT.lightened(0.35)
	Kit.cut(c, Kit.rect_pts(Rect2(X + CAP, Y - RO, GLAND - CAP, RO - RI)), paint_face, 9.0, W)
	Kit.cut(c, Kit.rect_pts(Rect2(X + CAP, Y + RI, GLAND - CAP, RO - RI)), paint_face, 9.0, W)
	Kit.cut(c, Kit.rect_pts(Rect2(X, Y - RO, CAP, RO * 2)), paint_face, 9.0, W)
	c.draw_line(Vector2(X + 4, Y - RO + 3), Vector2(X + GLAND, Y - RO + 3), Color(1, 1, 1, 0.35), 2.0, true)   # rim light
	# port A: drilled up through the end cap into a pocket on the cap face, so
	# oil reaches the piston even when the rod is fully retracted (ext = 0)
	c.draw_rect(Rect2(X + CAP - 12, Y + 16, 12, RO - 16), red)
	c.draw_line(Vector2(X + CAP - 12, Y + RO), Vector2(X + CAP - 12, Y + 16), Kit.INK, 1.6, true)
	c.draw_line(Vector2(X + CAP - 12, Y + 16), Vector2(X + CAP, Y + 16), Kit.INK, 1.6, true)
	_stream(c, PackedVector2Array([Vector2(X + CAP - 6, Y + RO), Vector2(X + CAP - 6, Y + 24), Vector2(X + CAP + 6, Y + 24)]),
		Color("#ffb3a3"), travel_a * 0.35, fa, 3.0)
	# port B: drilled through the wall just inside the gland
	c.draw_rect(Rect2(X + L - 47, Y + RI, 14, RO - RI), Kit.BLUE.darkened(0.15))
	Kit.outline(c, Kit.rect_pts(Rect2(X + L - 47, Y + RI, 14, RO - RI)), 1.6)
	_boss(c, Vector2(X + CAP, Y + RO), "A")
	_boss(c, Vector2(X + L - 40, Y + RO), "B")

	# --- piston: seals, wear band, nut
	Kit.body(c, Kit.rect_pts(Rect2(pist, Y - RI, PIST, RI * 2)), Color("#b9c1c9"), W)
	for sx in [pist + 5.0, pist + PIST - 9.0]:
		c.draw_rect(Rect2(sx, Y - RI, 4, 7), Color("#26201c"))
		c.draw_rect(Rect2(sx, Y + RI - 7, 4, 7), Color("#26201c"))
	c.draw_rect(Rect2(pist + 11, Y - RI, PIST - 22, 5), Kit.BRASS)
	c.draw_rect(Rect2(pist + 11, Y + RI - 5, PIST - 22, 5), Kit.BRASS)

	# --- rod (chrome) through the gland
	Kit.cyl(c, Vector2(pist + 20, Y), Vector2(rod_end, Y), ROD * 2, Kit.STEEL)
	c.draw_line(Vector2(pist + 26, Y - 11), Vector2(rod_end - 30, Y - 11), Color(1, 1, 1, 0.55), 2.0, true)
	Kit.body(c, Kit.rect_pts(Rect2(pist + PIST, Y - 27, 12, 54)), Kit.STEEL_DARK, W)     # piston nut
	c.draw_line(Vector2(pist + PIST + 6, Y - 27), Vector2(pist + PIST + 6, Y + 27), Kit.INK, 1.2, true)

	# --- gland (rod guide): guide bush, rod seal, wiper, flange bolts
	var gface = Color("#c9d0d8")
	for s in [-1.0, 1.0]:
		var y0 = Y + s * ROD
		var y1 = Y + s * RO
		var r = Rect2(X + GLAND, minf(y0, y1), L - GLAND + 14, absf(y1 - y0))
		Kit.cut(c, Kit.rect_pts(r), gface, 7.0, W)
		var ys = Y + s * (ROD + 2.5)
		c.draw_rect(Rect2(X + GLAND + 4, ys - 2.5, 8, 5), Kit.BRASS)          # guide bush
		c.draw_rect(Rect2(X + GLAND + 16, ys - 3.0, 7, 6), Color("#26201c"))  # rod seal
		c.draw_rect(Rect2(X + L + 6, ys - 3.0, 7, 6), Color("#26201c"))       # wiper
		Kit.bolt(c, Vector2(X + L + 7, Y + s * 46.0), 4.5)

	# --- rod eye + pin in the boom lug (lug drawn cut free with a break line)
	var eye = Vector2(rod_end + 24, Y)
	Kit.body(c, Kit.rect_pts(Rect2(rod_end - 4, Y - 16, 14, 32)), Kit.STEEL_DARK, W)
	Kit.disc(c, eye, 26.0, Kit.STEEL)
	var bl = PackedVector2Array([eye + Vector2(-14, -40), eye + Vector2(40, -40), eye + Vector2(46, -20), eye + Vector2(36, 0),
		eye + Vector2(48, 20), eye + Vector2(40, 40), eye + Vector2(-14, 40)])
	c.draw_colored_polygon(bl, Color(PAINT, 0.55))
	Kit.outline(c, PackedVector2Array([bl[0], bl[1]]), W)
	Kit.outline(c, PackedVector2Array([bl[5], bl[6]]), W)
	c.draw_polyline(PackedVector2Array([bl[1], bl[2], bl[3], bl[4], bl[5]]), Kit.INK, 1.6, true)   # break line
	_pin(c, eye, 11.0)
	Kit.label(c, font, eye + Vector2(-30, -52), "tai cần", 18, Color(0.95, 0.85, 0.6))


static func _pin(c: CanvasItem, p: Vector2, r: float) -> void:
	c.draw_circle(p + Vector2(2, 3), r + 4, Color(0, 0, 0, 0.35))      # bushing shadow
	Kit.disc(c, p, r, Color("#c6ccd3"))
	c.draw_arc(p, r - 3, PI * 1.05, PI * 1.6, 8, Color(1, 1, 1, 0.7), 2.0, true)
	c.draw_circle(p, 3.0, Kit.INK)


static func _boss(c: CanvasItem, p: Vector2, tag: String) -> void:
	var r = Rect2(p.x - 15, p.y - 2, 30, 14)
	Kit.body(c, Kit.rect_pts(r), Color("#8d98a4"), W)
