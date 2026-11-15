@tool
extends RefCounted
## Drawing kit for EP02 technical cutaways (2.5D illustration style).
## Every helper draws on the CanvasItem passed as `c`, in that item's local
## space. Conventions: cut (sectioned) metal = light face + 45° hatch,
## un-cut round parts = cylinder shading, all outlines in warm ink.

const INK := Color("#1d1712")
const STEEL := Color("#9aa5b1")
const STEEL_DARK := Color("#5d6873")
const CAST := Color("#56606b")
const CUT_FACE := Color("#c9d0d8")
const HATCH := Color("#7c8794")
const BRASS := Color("#c9a35a")
const RED := Color("#e4472f")
const BLUE := Color("#3d93dc")
const ORANGE := Color("#f39a1e")
const PURPLE := Color("#a46be0")
const OIL_DARK := Color("#7a2a1d")

static func outline(c: CanvasItem, pts: PackedVector2Array, w := 2.0, col := INK) -> void:
	var p := pts.duplicate()
	p.append(pts[0])
	c.draw_polyline(p, col, w, true)

static func rect_pts(r: Rect2) -> PackedVector2Array:
	return PackedVector2Array([r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y)])

static func rounded(r: Rect2, rad: float, seg := 5) -> PackedVector2Array:
	var pts := PackedVector2Array()
	rad = minf(rad, minf(r.size.x, r.size.y) * 0.5)
	var cs := [r.position + Vector2(rad, rad), Vector2(r.end.x - rad, r.position.y + rad),
		r.end - Vector2(rad, rad), Vector2(r.position.x + rad, r.end.y - rad)]
	for k in 4:
		for i in seg + 1:
			var a: float = PI + k * PI * 0.5 + i * PI * 0.5 / seg
			pts.append(cs[k] + Vector2(cos(a), sin(a)) * rad)
	return pts

## Body with top-lit vertical gradient (painted casting look)
static func body(c: CanvasItem, pts: PackedVector2Array, base: Color, w := 2.2, light := 0.18) -> void:
	var miny := INF
	var maxy := -INF
	for p in pts:
		miny = minf(miny, p.y)
		maxy = maxf(maxy, p.y)
	var cols := PackedColorArray()
	for p in pts:
		var k := (p.y - miny) / maxf(maxy - miny, 1.0)
		cols.append(base.lightened(light * (1.0 - k)).darkened(light * k))
	c.draw_polygon(pts, cols)
	outline(c, pts, w)

## Sectioned face: flat light face + 45° hatch clipped to the polygon
static func cut(c: CanvasItem, pts: PackedVector2Array, face := CUT_FACE, spacing := 9.0, w := 2.0) -> void:
	c.draw_colored_polygon(pts, face)
	var r := Rect2(pts[0], Vector2.ZERO)
	for p in pts:
		r = r.expand(p)
	var d := r.size.x + r.size.y
	var s := -r.size.y
	while s < r.size.x:
		var a := Vector2(r.position.x + s, r.end.y)
		var b := a + Vector2(d, -d)
		for seg in Geometry2D.intersect_polyline_with_polygon(PackedVector2Array([a, b]), pts):
			if seg.size() >= 2:
				c.draw_line(seg[0], seg[1], HATCH, 1.2, true)
		s += spacing
	outline(c, pts, w)

## Round part seen from the side (shaft, piston, rod): banded metallic shading
static func cyl(c: CanvasItem, a: Vector2, b: Vector2, width: float, base := STEEL, ink := true) -> void:
	var u := a.direction_to(b)
	var n := u.orthogonal()
	var bands := [[-0.5, -0.32, base.darkened(0.35)], [-0.32, -0.1, base.lightened(0.15)],
		[-0.1, 0.06, base.lightened(0.45)], [0.06, 0.3, base], [0.3, 0.5, base.darkened(0.3)]]
	for bd in bands:
		var o0: Vector2 = n * width * float(bd[0])
		var o1: Vector2 = n * width * float(bd[1])
		c.draw_colored_polygon(PackedVector2Array([a + o0, b + o0, b + o1, a + o1]), bd[2])
	if ink:
		c.draw_line(a - n * width * 0.5, b - n * width * 0.5, INK, 1.8, true)
		c.draw_line(a + n * width * 0.5, b + n * width * 0.5, INK, 1.8, true)
		c.draw_line(a - n * width * 0.5, a + n * width * 0.5, INK, 1.8, true)
		c.draw_line(b - n * width * 0.5, b + n * width * 0.5, INK, 1.8, true)

static func disc(c: CanvasItem, p: Vector2, r: float, base := STEEL) -> void:
	c.draw_circle(p, r, base.darkened(0.25), true, -1, true)
	c.draw_circle(p - Vector2(r * 0.15, r * 0.18), r * 0.78, base, true, -1, true)
	c.draw_circle(p - Vector2(r * 0.3, r * 0.34), r * 0.3, base.lightened(0.35), true, -1, true)
	c.draw_arc(p, r, 0, TAU, 40, INK, 1.8, true)

static func bolt(c: CanvasItem, p: Vector2, r := 5.0) -> void:
	var pts := PackedVector2Array()
	for i in 6:
		var a := i * TAU / 6.0 + PI / 6.0
		pts.append(p + Vector2(cos(a), sin(a)) * r)
	c.draw_colored_polygon(pts, STEEL_DARK.lightened(0.15))
	outline(c, pts, 1.2)
	c.draw_circle(p, r * 0.35, STEEL_DARK.darkened(0.3), true, -1, true)

static func spring(c: CanvasItem, a: Vector2, b: Vector2, coils: int, width: float, col := Color("#b8c0c8")) -> void:
	var u := a.direction_to(b)
	var n := u.orthogonal()
	var L := a.distance_to(b)
	var pts := PackedVector2Array([a])
	var steps := coils * 2
	for i in steps:
		var s := (i + 0.5) / steps
		pts.append(a + u * L * s + n * width * 0.5 * (1.0 if i % 2 == 0 else -1.0))
	pts.append(b)
	c.draw_polyline(pts, INK, 4.2, true)
	c.draw_polyline(pts, col, 2.2, true)

## Oil-filled region; alpha pulses gently, specks drift along `flow` (px)
static func oil(c: CanvasItem, pts: PackedVector2Array, col: Color, travel: float, dir := Vector2.RIGHT, density := 0.0016) -> void:
	c.draw_colored_polygon(pts, Color(col.darkened(0.15), 0.92))
	var r := Rect2(pts[0], Vector2.ZERO)
	for p in pts:
		r = r.expand(p)
	var n := int(r.size.x * r.size.y * density)
	var rng := RandomNumberGenerator.new()
	rng.seed = int(r.position.x * 13 + r.position.y * 7)
	for i in n:
		var p := Vector2(rng.randf(), rng.randf())
		var q := r.position + Vector2(fposmod(p.x * r.size.x + dir.x * travel, r.size.x), fposmod(p.y * r.size.y + dir.y * travel, r.size.y))
		if Geometry2D.is_point_in_polygon(q, pts):
			c.draw_circle(q, 1.6, col.lightened(0.45), true, -1, true)

## Pipe along a polyline with oil dashes advected by `travel` (px)
static func pipe(c: CanvasItem, pts: PackedVector2Array, col: Color, travel: float, w := 9.0, live := 1.0) -> void:
	c.draw_polyline(pts, Color(0.01, 0.025, 0.047, 0.94), w + 5.0, true)
	c.draw_polyline(pts, col.darkened(0.37), w, true)
	c.draw_polyline(pts, Color(col.lightened(0.22), 0.68), maxf(w * 0.26, 1.0), true)
	if live <= 0.01:
		return
	var period := 52.0
	var dash := 16.0
	var acc := 0.0
	var off := fposmod(travel, period)
	for i in pts.size() - 1:
		var p0 := pts[i]
		var p1 := pts[i + 1]
		var seg := p0.distance_to(p1)
		var s := fposmod(off - acc, period)
		while s < seg:
			var e := minf(s + dash, seg)
			var front := p0.lerp(p1, e / seg)
			var start := p0.lerp(p1, s / seg)
			c.draw_line(start, front, Color(col.lightened(0.18), live * 0.55), maxf(w - 3.0, 2.0), true)
			c.draw_line(start, front, Color(col.lightened(0.57), live * 0.9), maxf(w * 0.34, 1.8), true)
			s += period
		acc += seg

static func arrow_head(c: CanvasItem, tip: Vector2, dir: Vector2, size: float, col: Color) -> void:
	var u := dir.normalized()
	var n := u.orthogonal()
	var pts := PackedVector2Array([tip, tip - u * size + n * size * 0.55, tip - u * size - n * size * 0.55])
	c.draw_colored_polygon(pts, col)
	outline(c, pts, 1.4)

static func label(c: CanvasItem, font: Font, p: Vector2, text: String, size := 22, col := Color(0.92, 0.95, 1.0)) -> void:
	c.draw_string_outline(font, p, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, 4, Color(0.03, 0.05, 0.09, 0.9))
	c.draw_string(font, p, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, col)
