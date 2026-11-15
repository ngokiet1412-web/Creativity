@tool
extends RefCounted
## Drawn mouth for lip-sync. `open` 0..1 comes from full/mouth.json (per-frame
## envelope: real VO loudness when the WAVs exist, else one bump per syllable
## of the script line). Closed: nothing is drawn, the original art shows.

static func draw(c: CanvasItem, p: Vector2, w: float, open: float, fur: Color, rot := 0.0) -> void:
	if open < 0.06:
		return
	var o = clampf(open, 0.0, 1.0)
	var rx = w * (0.62 + 0.3 * o)
	var ry = w * (0.18 + 0.72 * o)
	var cen = p + Vector2(0, ry * 0.75).rotated(rot)
	_ell(c, p + Vector2(0, w * 0.25).rotated(rot), w * 1.25, w * 0.75, rot, fur)       # hide the drawn smile
	_ell(c, cen, rx + 2.0, ry + 2.0, rot, Color("#2a1d14"))
	_ell(c, cen, rx, ry, rot, Color("#6b2320"))
	if o > 0.3:
		_ell(c, cen + Vector2(0, ry * 0.45).rotated(rot), rx * 0.62, ry * 0.5, rot, Color("#f08a8a"))

static func _ell(c: CanvasItem, cen: Vector2, rx: float, ry: float, rot: float, col: Color) -> void:
	var pts = PackedVector2Array()
	for i in 24:
		var a = i * TAU / 24.0
		pts.append(cen + Vector2(cos(a) * rx, sin(a) * ry).rotated(rot))
	c.draw_colored_polygon(pts, col)
