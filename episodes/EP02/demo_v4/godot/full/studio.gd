@tool
extends Node2D
## Shared EP02 studio. The stage artwork is a local plate. A four-piece mask
## leaves the TV open to the live scene rendered by the world camera.

const SCREEN := Rect2(535, 142, 850, 478.125)
const VIEW := Vector2(1920, 1080)
const NAVY := Color("#151f34")
const MOUTH_D = preload("res://full/mouth.gd")

@export_range(0, 1) var studio_on := 1.0
@export_range(0, 1) var push := 0.0
@export_range(0, 1) var monitor_on := 0.0
@export var focus := Vector2(170, -60)
@export var focus_zoom := 0.62

var stage: Texture2D
var capy: Texture2D
var engineer: Texture2D
var canvas: Node2D
var t := 0.0
var capy_mouth := 0.0
var engineer_mouth := 0.0
var engineer_line := false

func _load_plate(name: String) -> Texture2D:
	var path := ProjectSettings.globalize_path("res://local/" + name)
	if not FileAccess.file_exists(path):
		return null
	var img := Image.load_from_file(path)
	img.generate_mipmaps()
	return ImageTexture.create_from_image(img)

func _ready() -> void:
	stage = _load_plate("studio_show_v8.png")
	capy = _load_plate("host_capy.png")
	engineer = _load_plate("host_eng.png")
	var layer := CanvasLayer.new()
	layer.layer = 2
	add_child(layer)
	canvas = Node2D.new()
	canvas.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	layer.add_child(canvas)
	canvas.draw.connect(_draw_studio)

func set_state(time: float, capy_open: float, engineer_open: float, listening: bool) -> void:
	t = time
	capy_mouth = capy_open
	engineer_mouth = engineer_open
	engineer_line = listening
	canvas.queue_redraw()

func _scale_factor() -> float:
	return lerpf(1.0, VIEW.x / SCREEN.size.x, smoothstep(0.0, 1.0, push))

func _pivot() -> Vector2:
	return SCREEN.position * (VIEW.x / (VIEW.x - SCREEN.size.x))

func camera(cam: Camera2D) -> void:
	var s := _scale_factor()
	var center := _pivot().lerp(SCREEN.get_center(), s)
	var zoom_factor := (SCREEN.size.x / VIEW.x) * s
	cam.zoom = Vector2.ONE * zoom_factor
	cam.position = focus - (center - VIEW * 0.5) / zoom_factor

func _tile(r: Rect2) -> void:
	if stage:
		var ratio := stage.get_size() / VIEW
		canvas.draw_texture_rect_region(stage, r, Rect2(r.position * ratio, r.size * ratio))
	else:
		canvas.draw_rect(r, NAVY)

func _foreground(coords: Array) -> void:
	if not stage:
		return
	var positions := PackedVector2Array()
	var uv := PackedVector2Array()
	for p: Vector2 in coords:
		var u := p / Vector2(1672, 941)
		positions.append(u * VIEW)
		uv.append(u)
	canvas.draw_polygon(positions, PackedColorArray([Color.WHITE]), uv, stage)

func _draw_studio() -> void:
	if studio_on <= 0.001 or push >= 0.999:
		return
	var s := _scale_factor()
	canvas.draw_set_transform(_pivot() * (1.0 - s), 0.0, Vector2.ONE * s)
	_tile(Rect2(0, 0, VIEW.x, SCREEN.position.y))
	_tile(Rect2(0, SCREEN.end.y, VIEW.x, VIEW.y - SCREEN.end.y))
	_tile(Rect2(0, SCREEN.position.y, SCREEN.position.x, SCREEN.size.y))
	_tile(Rect2(SCREEN.end.x, SCREEN.position.y, VIEW.x - SCREEN.end.x, SCREEN.size.y))
	_monitor()
	_people(s)
	canvas.draw_set_transform(_pivot() * (1.0 - s), 0.0, Vector2.ONE * s)
	# Foreground contours come from the same plate, so props occlude the hosts
	# naturally and the desktop edge keeps the two hosts in the same space.
	_foreground([Vector2(87,620), Vector2(286,625), Vector2(314,737), Vector2(419,755),
		Vector2(417,776), Vector2(328,802), Vector2(116,773)])
	_foreground([Vector2(435,694), Vector2(443,666), Vector2(496,597), Vector2(533,607),
		Vector2(529,632), Vector2(492,681), Vector2(496,749), Vector2(526,755),
		Vector2(523,777), Vector2(429,779), Vector2(428,758), Vector2(464,746),
		Vector2(462,707), Vector2(447,709)])
	_foreground([Vector2(1142,619), Vector2(1158,598), Vector2(1178,597), Vector2(1237,664),
		Vector2(1234,709), Vector2(1210,708), Vector2(1209,747), Vector2(1247,754),
		Vector2(1246,776), Vector2(1146,780), Vector2(1145,757), Vector2(1177,746),
		Vector2(1178,684)])
	canvas.draw_set_transform(Vector2.ZERO)

func _people(s: float) -> void:
	var stage_offset := _pivot() * (1.0 - s)
	if engineer:
		var d := Vector2(178, 842 + sin(t * 2.5) * 1.1)
		canvas.draw_set_transform(stage_offset + d * s, 0.012 * engineer_mouth, Vector2.ONE * s * 1.24)
		canvas.draw_texture(engineer, Vector2(0, -400))
		MOUTH_D.draw(canvas, Vector2(177, -223), 9.0, engineer_mouth, Color("#f8b263"), -0.3)
	if capy:
		var beat := fposmod(t + 0.20, 4.35)
		var nod := sin(PI * clampf((beat - 1.1) / 0.55, 0.0, 1.0)) if engineer_line else 0.0
		var seat := Vector2(1582, 845 + 1.1 * sin(t * 2.1))
		var q := 1.50 * s
		var left := -capy.get_width() / 2.0
		var w := capy.get_width()
		canvas.draw_set_transform(stage_offset + seat * s, 0.0, Vector2.ONE * q)
		canvas.draw_texture_rect_region(capy, Rect2(left, -80, w, 80), Rect2(0, 190, w, 80))
		var angle := -0.038 * nod + 0.017 * sin(t * 1.6)
		var neck := seat + Vector2(0, -80 * 1.5)
		canvas.draw_set_transform(stage_offset + neck * s, angle, Vector2.ONE * q)
		canvas.draw_texture_rect_region(capy, Rect2(left, -190, w, 194), Rect2(0, 0, w, 194))
		var blink := fposmod(t + 1.0, 3.65)
		if blink < 0.12:
			_lid(Vector2(left + 81, -106), 8, 11)
			_lid(Vector2(left + 141, -88), 9, 11)
		MOUTH_D.draw(canvas, Vector2(left + 103, -70), 9.0, capy_mouth, Color("#fbb166"), 0.22)

func _lid(center: Vector2, rx: float, ry: float) -> void:
	var shape := PackedVector2Array()
	for i in 24:
		var angle := TAU * i / 24.0
		shape.append(center + Vector2(rx * cos(angle), ry * sin(angle)))
	canvas.draw_colored_polygon(shape, Color("#fbb166"))
	canvas.draw_arc(center + Vector2(0, 2), rx - 1, 0.12, PI - 0.12, 16, Color("#39241a"), 1.8, true)

func _monitor() -> void:
	var bezel := SCREEN.grow(12)
	var color := Color("#090d14")
	canvas.draw_rect(Rect2(bezel.position, Vector2(bezel.size.x, 12)), color)
	canvas.draw_rect(Rect2(bezel.position.x, SCREEN.end.y, bezel.size.x, 12), color)
	canvas.draw_rect(Rect2(bezel.position, Vector2(12, bezel.size.y)), color)
	canvas.draw_rect(Rect2(SCREEN.end.x, bezel.position.y, 12, bezel.size.y), color)
	canvas.draw_rect(bezel, Color("#536078"), false, 2.0)
	canvas.draw_circle(Vector2(SCREEN.end.x - 14, SCREEN.end.y + 6), 2.0, Color("#70cfeb"))
	if monitor_on < 1.0:
		canvas.draw_rect(SCREEN, Color(0.028, 0.045, 0.075, 1.0 - monitor_on))
	if get_parent().scene_tag == "SC01" and t >= 0.78 and t <= 3.85:
		var font := ThemeDB.fallback_font
		var words := ["KĨ", "SƯ", "ƠIIII!"]
		var starts := [0.0, 0.48, 1.15]
		for j in 3:
			var elapsed := t - 0.78 - float(starts[j])
			if elapsed >= 0.0:
				var bounce := sin(elapsed * 10.0) * exp(-elapsed * 3.2) * 13.0
				var alpha := minf(elapsed / 0.12, 1.0) * clampf((3.85 - t) / 0.25, 0.0, 1.0)
				var pos := Vector2(680 + j * 170, 409 + bounce)
				canvas.draw_string(font, pos, words[j], HORIZONTAL_ALIGNMENT_LEFT, -1, 72, Color(1, 0.84, 0.35, alpha))
