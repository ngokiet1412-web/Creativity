@tool
extends Node2D
## Capy + engineer behind the safety barrier (EP01 still "field-reply", local).
## Layers: base (engineer, barrier, Capy body), Capy head on a neck pivot,
## collar overlay above the head seam. Head turns rigidly; blinks are drawn
## eyelids in fur colour. No mouth layers exist yet -> no lip-sync (blocker).

const SCALE := 1.2
const ORIGIN := Vector2(-835, -405)     # world position of the still's top-left
var CAPY_BLINKS: Array = []
var ENG_BLINKS: Array = []

var cfg := {}
var base: Texture2D
var head: Texture2D
var collar: Texture2D
var t := 0.0
var tilt := 0.0
var available := false

func _ready() -> void:
	z_index = 20
	z_as_relative = false
	var dir = ProjectSettings.globalize_path("res://local/")
	if not FileAccess.file_exists(dir + "crew_base.png"):
		return
	cfg = JSON.parse_string(FileAccess.get_file_as_string("res://local/crew.json"))
	base = _tex(dir + "crew_base.png")
	head = _tex(dir + "capy_head.png")
	collar = _tex(dir + "capy_collar.png")
	available = true

func _tex(p: String) -> Texture2D:
	var img = Image.load_from_file(p)
	img.generate_mipmaps()
	return ImageTexture.create_from_image(img)

func set_state(time: float, capy_tilt: float) -> void:
	var d = get_parent().get_parent()
	CAPY_BLINKS = d.capy_blinks
	ENG_BLINKS = d.eng_blinks
	t = time
	tilt = capy_tilt
	queue_redraw()

const MouthD = preload("res://full/mouth.gd")
const CapyDetails = preload("res://full/capy_details.gd")
var mouth_capy := 0.0
var mouth_eng := 0.0
var appear_t := 2.9

func _blink(times: Array) -> float:
	for b in times:
		var d: float = t - b
		if d >= 0.0 and d < 0.17:
			return 1.0 if d >= 0.05 and d < 0.12 else 0.55
	return 0.0

func _draw() -> void:
	if not available or t < appear_t:
		return
	texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	draw_set_transform(ORIGIN, 0.0, Vector2.ONE * SCALE)
	draw_texture(base, Vector2.ZERO)
	_eyes(cfg.engineer_eyes, _blink(ENG_BLINKS), Color(cfg.fur[0] / 255.0, cfg.fur[1] / 255.0, cfg.fur[2] / 255.0))
	var furc = Color(cfg.fur[0] / 255.0, cfg.fur[1] / 255.0, cfg.fur[2] / 255.0)
	MouthD.draw(self, Vector2(177, 407), 9.0, mouth_eng, furc, -0.3)
	var pv := Vector2(cfg.capy_head_pivot[0], cfg.capy_head_pivot[1])
	var breathe = 0.6 * sin(t * TAU * 0.35)
	draw_set_transform(ORIGIN + (pv + Vector2(0, breathe * 0.0)) * SCALE, deg_to_rad(tilt + breathe * 0.4), Vector2.ONE * SCALE)
	draw_texture(head, -pv)
	_eyes(cfg.capy_eyes, _blink(CAPY_BLINKS), Color(cfg.fur[0] / 255.0, cfg.fur[1] / 255.0, cfg.fur[2] / 255.0), -pv)
	var pupil_a := Vector2(cfg.capy_eyes[0][0], cfg.capy_eyes[0][1]) - pv
	var pupil_b := Vector2(cfg.capy_eyes[1][0], cfg.capy_eyes[1][1]) - pv
	CapyDetails.glasses(self, pupil_a, pupil_b)
	MouthD.draw(self, Vector2(390, 490) - pv, 9.0, mouth_capy, furc, 0.25)
	draw_set_transform(ORIGIN, 0.0, Vector2.ONE * SCALE)
	draw_texture(collar, Vector2.ZERO)
	CapyDetails.badge(self, Vector2(415, 605))
	draw_set_transform(Vector2.ZERO)

func _eyes(eyes: Array, close: float, fur: Color, off := Vector2.ZERO) -> void:
	## close 0.55 = half lid, 1.0 = shut (fur-coloured lid + lash line)
	if close <= 0.0:
		return
	for e in eyes:
		var c = Vector2(e[0], e[1]) + off
		var rx: float = e[2] + 1.8
		var ry: float = e[3] + 1.8
		var pts = PackedVector2Array()
		var full = close > 0.8
		var n = 24
		for k in n + 1:
			var ang = PI + k * (PI if not full else TAU) / n
			pts.append(c + Vector2(cos(ang) * rx, sin(ang) * ry))
		if not full:
			pts.append(c + Vector2(-rx, 0))
		draw_colored_polygon(pts, fur)
		var lash = PackedVector2Array()
		for k in 11:
			var x = -rx * 0.95 + k * rx * 0.19
			var y = (ry * 0.2 if full else 0.0) + (2.5 if full else 0.0) * (1.0 - pow(x / rx, 2.0))
			lash.append(c + Vector2(x, y))
		draw_polyline(lash, Color("#2a1d14"), 2.2, true)
