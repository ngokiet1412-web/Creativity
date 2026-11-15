@tool
extends Node2D
## One section of a closed-centre directional control valve (boom raise
## section), longitudinal cut. Generic 4-way spool: grooves T | A | P | B | T,
## lands with overlap (dead band), pilot chamber each end, centring springs.
## PC200-8 main control valve: 6-spool type with pressure compensation (CLSS),
## shop manual specification; port layout here is illustrative.
## spool > 0 (pilot pressure on the left end): P->A and B->T open.

const Kit = preload("res://cutaway/kit.gd")
const OVERLAP := 27.0
const G := {"T1": 170.0, "A": 290.0, "P": 450.0, "B": 610.0, "T2": 730.0}
const GW := 46.0
const BORE := 46.0

@export_range(-1, 1) var spool := 0.0: set = _set_spool
@export var travel_a := 0.0          # oil travel (px) in A / P passages
@export var travel_b := 0.0          # oil travel (px) in B / T passages
@export_range(0, 1) var pilot_left := 0.0
@export_range(0, 1) var holding := 1.0  # A side trapped under load when closed
@export var show_comp := true
@export var comp_throttle := -1.0      # -1 = follow opening; 0..1 = compensator closing (flow sharing)
@export var tag_text := ""
var font: Font

func _set_spool(v: float) -> void:
	spool = v
	queue_redraw()

func _ready() -> void:
	font = ThemeDB.fallback_font

func shift_px() -> float:
	return spool * 75.0

func open_pa() -> float:
	return maxf(shift_px() - OVERLAP, 0.0)

func open_bt() -> float:
	return maxf(shift_px() - OVERLAP, 0.0)

func _draw() -> void:
	var s = shift_px()
	var opa = open_pa()
	var obt = open_bt()
	# housing section
	var hous = PackedVector2Array([Vector2(0, -160), Vector2(900, -160), Vector2(900, 160), Vector2(0, 160)])
	Kit.cut(self, hous, Kit.CUT_FACE, 11.0, 2.6)
	# passages (drawn as oil-filled channels in the casting)
	var a_live: float = clampf(opa / 20.0, 0.0, 1.0)
	var b_live: float = clampf(obt / 20.0, 0.0, 1.0)
	var red_hold = Kit.RED.darkened(0.25) if holding > 0.5 else Color("#5b3a36")
	var col_a = Kit.RED if opa > 0.0 else red_hold
	var col_b = Kit.BLUE if obt > 0.0 else Kit.BLUE.darkened(0.35)
	_channel(PackedVector2Array([Vector2(G.A, -40), Vector2(G.A, -235)]), col_a, travel_a, 34, a_live)
	_channel(PackedVector2Array([Vector2(G.B, -235), Vector2(G.B, -40)]), col_b, travel_b, 34, b_live)
	# pump feed through the pressure-compensation valve into the P groove
	_channel(PackedVector2Array([Vector2(G.P, 235), Vector2(G.P, 40)]), Kit.RED, travel_a, 34, a_live)
	# tank gallery under the valve linking both T grooves
	_channel(PackedVector2Array([Vector2(G.T1, 40), Vector2(G.T1, 118), Vector2(G.T2, 118), Vector2(G.T2, 40)]), Kit.BLUE, -travel_b, 26, b_live)
	_channel(PackedVector2Array([Vector2(G.T2 + 40, 118), Vector2(880, 118), Vector2(880, 235)]), Kit.BLUE, travel_b, 26, b_live)
	# grooves (annular cavities) - colour follows what they are connected to
	var gcol = {"T1": Kit.BLUE.darkened(0.3), "A": col_a, "P": Kit.RED, "B": col_b, "T2": Kit.BLUE if obt > 0.0 else Kit.BLUE.darkened(0.3)}
	for k in G:
		var r = Rect2(G[k] - GW * 0.5, -78, GW, 156)
		draw_rect(r, gcol[k].darkened(0.1))
		draw_rect(r, Kit.INK, false, 1.8)
		Kit.label(self, font, Vector2(G[k] - 10 - (6 if k.length() > 1 else 0), 150), k, 22)
	# bore
	draw_rect(Rect2(70, -BORE * 0.5, 760, BORE), Color("#1a2028"))
	# oil in the bore where the spool necks connect grooves
	var necks = [[220.0 + s, 400.0 + s], [500.0 + s, 680.0 + s]]
	var ncol = [col_a, col_b]
	for i in 2:
		draw_rect(Rect2(necks[i][0], -BORE * 0.5 + 3, necks[i][1] - necks[i][0], BORE - 6), Color(ncol[i], 0.9))
	if opa > 0.0:
		draw_rect(Rect2(400.0 + s - opa, -BORE * 0.5 + 3, opa + 6, BORE - 6), Kit.RED.lightened(0.15))
	if obt > 0.0:
		draw_rect(Rect2(680.0 + s - obt, -BORE * 0.5 + 3, obt + 6, BORE - 6), Kit.BLUE.lightened(0.15))
	# spool: lands full diameter, necks reduced, metering notches on land edges
	var lands = [[95.0, 220.0], [400.0, 500.0], [680.0, 805.0]]
	Kit.cyl(self, Vector2(60 + s, 0), Vector2(840 + s, 0), 20, Kit.STEEL)
	for L in lands:
		Kit.cyl(self, Vector2(L[0] + s, 0), Vector2(L[1] + s, 0), BORE - 4, Kit.STEEL.lightened(0.05))
		for e in [L[0], L[1]]:
			var ex: float = e + s
			var dirn = 1.0 if e == L[0] else -1.0
			draw_colored_polygon(PackedVector2Array([Vector2(ex, -8), Vector2(ex + dirn * 14, -2), Vector2(ex, -2)]), Color(0.15, 0.17, 0.2))
	# end caps, pilot chambers, centring springs
	for side in [-1, 1]:
		var cx = 0.0 if side < 0 else 900.0
		var cap = Rect2(cx - (90 if side < 0 else 0), -100, 90, 200)
		Kit.body(self, Kit.rect_pts(cap), Kit.CAST)
		var ch = Rect2(cx - (70 if side < 0 else -5), -60, 65, 120)
		var pcol = Kit.ORANGE.darkened(0.55).lerp(Kit.ORANGE, pilot_left) if side < 0 else Kit.ORANGE.darkened(0.6)
		draw_rect(ch, pcol)
		draw_rect(ch, Kit.INK, false, 1.6)
		var a0 = Vector2(cx + side * 4 + (s if side < 0 else s), 0)
		var spring_end = Vector2(cx + side * 62, 0)
		Kit.spring(self, Vector2(60 + s if side < 0 else 840 + s, 0), spring_end, 7, 34)
		for k in 2:
			Kit.bolt(self, Vector2(cx + side * 45, -80 + k * 160), 6)
	Kit.label(self, font, Vector2(-150, -118), "Pi (pilot)", 21, Kit.ORANGE.lightened(0.3))
	if show_comp:
		_compensator(Vector2(G.P, 235))
	if tag_text != "":
		Kit.label(self, font, Vector2(20, -180), tag_text, 34, Color(1, 0.9, 0.6))

func _channel(pts: PackedVector2Array, col: Color, travel: float, w: float, live: float) -> void:
	Kit.pipe(self, pts, col, travel, w, live)

## Pressure-compensation valve in the feed (CLSS) - illustration of principle
func _compensator(c: Vector2) -> void:
	var r = Rect2(c.x - 80, c.y, 160, 90)
	Kit.cut(self, Kit.rect_pts(r), Kit.CUT_FACE.darkened(0.05), 8.0)
	draw_rect(Rect2(r.position.x + 12, c.y + 30, 136, 30), Color("#1a2028"))
	var bias = (clampf(open_pa() / 30.0, 0.0, 1.0) if comp_throttle < 0.0 else comp_throttle) * 26.0
	Kit.cyl(self, Vector2(r.position.x + 18 + bias, c.y + 45), Vector2(r.position.x + 92 + bias, c.y + 45), 26, Kit.STEEL)
	Kit.spring(self, Vector2(r.position.x + 92 + bias, c.y + 45), Vector2(r.end.x - 14, c.y + 45), 5, 22)
	Kit.label(self, font, Vector2(r.end.x + 12, c.y + 54), "van bù áp", 19)
