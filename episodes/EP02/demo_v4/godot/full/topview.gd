@tool
extends Node2D
## Top view of the excavator for SC08 (swing) and SC09 (travel), drawn in the
## same flat-paint + ink style as the cutaways. 100 px = 1 m, proportions are
## illustrative (no dimension is labelled).
##  - swing_deg rotates ONLY the upper structure about the swing centre; the
##    tracked undercarriage never rotates with it
##  - track_l / track_r: link travel (px) of each track (SC09), drawn as links
##    moving around the track loop
##  - gear: inset of the swing pinion meshing with the fixed internal ring
##    gear: pinion spin = swing * (1 - Z_ring / Z_pinion)  (rolling, no slip)

const Kit = preload("res://cutaway/kit.gd")
const Z_RING := 90
const Z_PIN := 14
const UPPER_V7 = preload("res://art/top_upper_v7.png")
const GROUND_V7 = preload("res://art/top_ground_v7.png")
const ART_SCALE := 0.44
const ART_PIVOT := Vector2(430, 380)

@export var swing_deg := 0.0
@export var track_l := 0.0
@export var track_r := 0.0
@export_range(0, 1) var hi_motor := 0.0
@export_range(0, 1) var hi_ring := 0.0
@export_range(0, 1) var hi_travel := 0.0
@export_range(0, 1) var gear := 0.0
@export var gear_pos := Vector2(820, 120)
@export_range(0, 1) var upper_alpha := 1.0

func _process(_d: float) -> void:
	queue_redraw()

@export var ground := true
@export var only_ground := false

func _draw() -> void:
	if ground or only_ground:
		_ground()
	if only_ground:
		return
	_undercarriage()
	_ring(hi_ring)
	_upper()
	if gear > 0.01:
		_gear_inset()

func _ground() -> void:
	var r = Rect2(Vector2(-1800, -1200), GROUND_V7.get_size() * 2.55)
	draw_texture_rect(GROUND_V7, r, false)

# ------------------------------------------------------------ undercarriage
func _undercarriage() -> void:
	for side in [-1.0, 1.0]:
		var y = side * 119.0
		var trav = track_l if side < 0 else track_r
		var r = Rect2(-222, y - 30, 444, 60)
		draw_rect(r.grow(4), Color(0, 0, 0, 0.35))
		draw_rect(r, Color("#3a3632"))
		# links: shoes moving with the track (top run moves opposite to bottom run;
		# from above we see the top run)
		var pitch = 19.0
		var off = fposmod(trav, pitch)
		var x = r.position.x + off
		while x < r.end.x:
			draw_rect(Rect2(x, r.position.y + 2, pitch - 3, r.size.y - 4), Color("#55504a"))
			draw_line(Vector2(x + 4, r.position.y + 4), Vector2(x + 4, r.end.y - 4), Color("#2a2622"), 2.0)
			x += pitch
		draw_rect(r, Kit.INK, false, 2.4)
		# sprocket end (rear) with travel motor
		var mp = Vector2(-205, y)
		var hk = hi_travel
		if hk > 0.0:
			for k in 4:
				draw_circle(mp, 26 + k * 7, Color(1, 0.82, 0.3, 0.08 * hk), true, -1, true)
		draw_circle(mp, 22, Color("#6a6e75"))
		draw_arc(mp, 22, 0, TAU, 24, Kit.INK, 2.0, true)
		draw_circle(mp, 9, Color("#3d4046"))
	# track frame / centre body (fixed)
	draw_rect(Rect2(-150, -88, 300, 176), Color("#4a4640"))
	draw_rect(Rect2(-150, -88, 300, 176), Kit.INK, false, 2.0)

func _ring(k: float) -> void:
	draw_circle(Vector2.ZERO, 92, Color("#5d6168"))
	draw_arc(Vector2.ZERO, 92, 0, TAU, 64, Kit.INK, 2.0, true)
	if k > 0.0:
		for i in 4:
			draw_arc(Vector2.ZERO, 92 + i * 6, 0, TAU, 64, Color(1, 0.82, 0.3, 0.25 * k), 5.0, true)

# ------------------------------------------------------------------- upper
func _upper() -> void:
	# A rigid painted superstructure. Rotation is around the turntable only.
	# No texture warping; front equipment is held fixed for this plan-view shot.
	draw_set_transform(Vector2(8, 12), deg_to_rad(-swing_deg), Vector2.ONE * ART_SCALE)
	draw_texture(UPPER_V7, -ART_PIVOT, Color(0, 0, 0, 0.22 * upper_alpha))
	draw_set_transform(Vector2.ZERO, deg_to_rad(-swing_deg), Vector2.ONE * ART_SCALE)
	draw_texture(UPPER_V7, -ART_PIVOT, Color(1, 1, 1, upper_alpha))
	draw_set_transform(Vector2.ZERO)
	var mp = Vector2(40, 70).rotated(deg_to_rad(-swing_deg))
	if hi_motor > 0.0:
		for k in 3:
			draw_arc(mp, 28 + k * 5, 0, TAU, 48, Color(1, 0.85, 0.4, hi_motor * 0.3), 3.0, true)
	if hi_ring > 0.0:
		draw_arc(Vector2.ZERO, 92, 0, TAU, 64, Color(1, 0.85, 0.35, hi_ring * 0.8), 4.0, true)

# ------------------------------------------------------------ gear inset
func _gear_inset() -> void:
	var c = gear_pos
	var R = 420.0            # ring pitch radius in the inset
	var rp = R * float(Z_PIN) / float(Z_RING)
	var k = gear
	var box = Rect2(c - Vector2(260, 200), Vector2(520, 400))
	draw_rect(box, Color(0.04, 0.07, 0.12, 0.94 * k))
	draw_rect(box, Color(0.4, 0.6, 0.9, 0.7 * k), false, 3.0)
	# the inset shows the mesh region: ring centre placed below the box
	var rc = c + Vector2(0, R - 20)
	var th = deg_to_rad(-swing_deg)
	# fixed internal ring (on the undercarriage): teeth point inwards
	var pts = PackedVector2Array()
	for i in Z_RING:
		var a0 = -PI * 0.5 + (i - Z_RING * 0.5) * TAU / Z_RING - th
		if absf(wrapf(a0 + PI * 0.5, -PI, PI)) > 0.5:
			continue
		var t0 = a0 - TAU / Z_RING * 0.22
		var t1 = a0 + TAU / Z_RING * 0.22
		var poly = PackedVector2Array([rc + Vector2(cos(t0 - 0.012), sin(t0 - 0.012)) * (R + 14), rc + Vector2(cos(t0), sin(t0)) * (R - 12),
			rc + Vector2(cos(t1), sin(t1)) * (R - 12), rc + Vector2(cos(t1 + 0.012), sin(t1 + 0.012)) * (R + 14)])
		draw_colored_polygon(poly, Color("#8a9099", k))
	draw_arc(rc, R + 14, -PI * 0.5 - 0.5, -PI * 0.5 + 0.5, 48, Color(Kit.INK, k), 2.0, true)
	Kit.label(self, ThemeDB.fallback_font, c + Vector2(-240, -170), "Vòng răng trong · gắn với gầm", 24, Color(1, 1, 1, k))
	# pinion carried by the upper: its centre turns with the swing angle,
	# its spin follows rolling inside the fixed ring
	# inset frame turns WITH the upper: pinion centre fixed, ring teeth pass by
	var cen = rc + Vector2(0, -1) * (R - rp)
	var spin = -th * float(Z_RING) / float(Z_PIN)
	var pp = PackedVector2Array()
	for i in Z_PIN * 4:
		var u = float(i) / (Z_PIN * 4)
		var ang = spin + u * TAU - PI * 0.5
		var tooth = fposmod(u * Z_PIN, 1.0)
		var rr = rp + (12.0 if tooth > 0.25 and tooth < 0.75 else -12.0)
		pp.append(cen + Vector2(cos(ang), sin(ang)) * rr)
	draw_colored_polygon(pp, Color("#c94a35", k))
	pp.append(pp[0])
	draw_polyline(pp, Color(Kit.INK, k), 2.0, true)
	draw_circle(cen, 12, Color(Kit.INK, k))
	var mark = cen + Vector2(cos(spin - PI * 0.5), sin(spin - PI * 0.5)) * (rp - 18)
	draw_circle(mark, 6, Color(1, 1, 1, k))
	Kit.label(self, ThemeDB.fallback_font, c + Vector2(-240, 155), "Bánh răng dẫn · gắn với thân trên", 24, Color(1, 0.85, 0.75, k))
