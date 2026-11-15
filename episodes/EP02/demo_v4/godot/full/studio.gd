@tool
extends Node2D
## Studio shot built around the owner-approved EP01 studio cels
## (local/studio-cels.png, 7 x 6 cels of 520 x 737, not in the public repo).
## The portrait cel sits centre-left; the 16:9 frame is completed by extending
## the cel's own edge pixels (wall/desk) and drawing a wall monitor on the
## right. The monitor is a HOLE in the studio layer: the world (machine) is
## framed behind it, so "the monitor turns on" and the push-in through the
## monitor is one continuous camera move, no cut.
##
## Talk: while Capy's line plays the cels advance through the EP01 talking
## sequence (cels 5..34) at 12 fps; idle uses the closed-mouth cels.

const CEL := Vector2(520, 737)
const COLS := 7
const TALK := [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34]
const IDLE := [0, 1, 2, 3, 4, 3, 2, 1, 35, 36, 37, 38, 39, 40, 41, 40, 39]
const MON := Rect2(1010, 150, 780, 439)     # 16:9 monitor (screen px at push 0)
const MouthD = preload("res://full/mouth.gd")
const FUR := Color(0.984, 0.68, 0.43)
const MOUTH := Vector2(276, 361)             # Capy's mouth in cel px (face is static across cels)

@export_range(0, 1) var studio_on := 1.0
@export_range(0, 1) var push := 0.0          # 0 = studio, 1 = monitor fills the frame
@export_range(0, 1) var monitor_on := 0.0    # screen glow / power-on
@export var focus := Vector2(170, -60)       # world point framed in the monitor
@export var focus_zoom := 0.62               # world zoom inside the monitor at push 0

var sheet: Texture2D
var img: Image
var layer: CanvasLayer
var canvas: Node2D
var talk := 0.0
var t := 0.0
var ok := false
var scale_cel := 1080.0 / 737.0
var cel_x := 0.0
var plate: Texture2D
var mouth_open := 0.0

func _ready() -> void:
	var p = ProjectSettings.globalize_path("res://local/studio-cels.png")
	if FileAccess.file_exists(p):
		img = Image.load_from_file(p)
		var im2 = img.duplicate()
		im2.generate_mipmaps()
		sheet = ImageTexture.create_from_image(im2)
		ok = true
	var pp = ProjectSettings.globalize_path("res://local/studio_plate.png")
	if FileAccess.file_exists(pp):
		plate = ImageTexture.create_from_image(Image.load_from_file(pp))
	layer = CanvasLayer.new()
	layer.layer = 2
	add_child(layer)
	canvas = Node2D.new()
	canvas.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	layer.add_child(canvas)
	canvas.draw.connect(_draw_studio)

func set_state(time: float, talking: float, mouth := 0.0) -> void:
	t = time
	talk = talking
	mouth_open = mouth
	canvas.queue_redraw()

## camera so that `focus` sits in the monitor, continuous with the push
func camera(cam: Camera2D) -> void:
	var S = _push_scale()
	var piv = _pivot(S)
	var mc = piv + (MON.get_center() - piv) * _s()
	var z = focus_zoom * _s()
	cam.zoom = Vector2.ONE * z
	cam.position = focus - (mc - Vector2(960, 540)) / z

func _push_scale() -> float:
	return 1920.0 / MON.size.x

func _pivot(S: float) -> Vector2:
	return S * MON.position / (S - 1.0)

func _s() -> float:
	var u = push * push * (3.0 - 2.0 * push)
	return lerpf(1.0, _push_scale(), u)

func _cel_index() -> int:
	if talk > 0.5:
		return TALK[int(t * 7.0) % TALK.size()]
	return IDLE[int(t * 3.0) % IDLE.size()]

func _draw_studio() -> void:
	if studio_on <= 0.001 or push >= 0.999:
		return
	var S = _push_scale()
	var piv = _pivot(S)
	var s = _s()
	canvas.draw_set_transform(piv - piv * s, 0.0, Vector2.ONE * s)
	var a = studio_on
	var i = _cel_index()
	var src = Rect2(Vector2(i % COLS, i / COLS) * CEL, CEL)
	var dst = Rect2(Vector2(cel_x, 0), CEL * scale_cel)
	if ok:
		canvas.draw_texture_rect_region(sheet, dst, src, Color(1, 1, 1, a))
		# lip-sync: own mouth over the cel's (fur patch, then smile or open mouth)
		var mp = dst.position + MOUTH * scale_cel
		var patch = PackedVector2Array()
		for k in 24:
			var ang = k * TAU / 24.0
			patch.append(mp + Vector2(cos(ang) * 30.0, 6.0 + sin(ang) * 17.0))
		canvas.draw_colored_polygon(patch, Color(FUR, a))
		if mouth_open < 0.06:
			var sm = PackedVector2Array()
			for k in 13:
				var u = k / 12.0
				sm.append(mp + Vector2(-20.0 + 40.0 * u, -4.0 + 7.0 * sin(PI * u)))
			canvas.draw_polyline(sm, Color(0.16, 0.11, 0.08, a), 3.0, true)
		else:
			MouthD.draw(canvas, mp + Vector2(0, -3), 19.0, mouth_open, Color(FUR, a))
	else:
		canvas.draw_rect(Rect2(0, 0, 1920, 1080), Color(0.1, 0.14, 0.26, a))
	if plate:
		canvas.draw_texture(plate, Vector2.ZERO, Color(1, 1, 1, a))
	_monitor(a)
	# The retained 2.81 s signature is the timing reference, no second voice.
	if t >= 0.8 and t <= 3.9 and get_parent().scene_tag == "SC01":
		var u = t - 0.8
		var words = ["KĨ", "SƯ", "ƠIIII!"]
		var starts = [0.0, 0.48, 1.15]
		for j in 3:
			var elapsed = u - starts[j]
			if elapsed < 0.0:
				continue
			var bounce = sin(elapsed * 10.0) * exp(-elapsed * 3.2) * 12.0
			var k = minf(elapsed / 0.12, 1.0) * clampf((3.9 - t) / 0.25, 0.0, 1.0)
			var pos = Vector2(1028 + j * 220, 410 + bounce)
			canvas.draw_string_outline(ThemeDB.fallback_font, pos, words[j], HORIZONTAL_ALIGNMENT_LEFT, -1, 64, 10, Color(0.04, 0.07, 0.13, k))
			canvas.draw_string(ThemeDB.fallback_font, pos, words[j], HORIZONTAL_ALIGNMENT_LEFT, -1, 64, Color(1, 0.84, 0.35, k))
	canvas.draw_set_transform(Vector2.ZERO)

func _monitor(a: float) -> void:
	var r = MON
	var frame = r.grow(16)
	# bezel drawn as 4 bars so the screen stays a hole onto the world
	var bez = Color(0.06, 0.07, 0.09, a)
	canvas.draw_rect(Rect2(frame.position, Vector2(frame.size.x, 16)), bez)
	canvas.draw_rect(Rect2(frame.position.x, r.end.y, frame.size.x, 16), bez)
	canvas.draw_rect(Rect2(frame.position, Vector2(16, frame.size.y)), bez)
	canvas.draw_rect(Rect2(r.end.x, frame.position.y, 16, frame.size.y), bez)
	canvas.draw_rect(frame, Color(0.25, 0.27, 0.3, a), false, 2.0)
	canvas.draw_rect(Rect2(r.get_center().x - 50, frame.end.y, 100, 40), Color(0.1, 0.11, 0.13, a))
	canvas.draw_circle(Vector2(r.end.x - 6, r.end.y + 8), 3.0, Color(0.3, 1.0, 0.5, a * monitor_on))
	# screen: dark until it powers on (power-on line opens vertically)
	var on = monitor_on
	if on < 1.0:
		var h = r.size.y * (1.0 - on)
		canvas.draw_rect(Rect2(r.position.x, r.get_center().y - h * 0.5, r.size.x, h), Color(0.02, 0.025, 0.035, a))
		if on > 0.0 and on < 1.0:
			canvas.draw_rect(Rect2(r.position.x, r.get_center().y - 2, r.size.x, 4), Color(0.8, 0.9, 1.0, a * (1.0 - on)))
	# glass reflection
	canvas.draw_colored_polygon(PackedVector2Array([r.position, r.position + Vector2(r.size.x * 0.35, 0), r.position + Vector2(r.size.x * 0.12, r.size.y), r.position + Vector2(0, r.size.y)]), Color(1, 1, 1, 0.05 * a))
	# screen edge rim shared with the world (frames the push-in)
	canvas.draw_rect(r, Color(0, 0, 0, 0.6 * a), false, 3.0)
