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
const MON := Rect2(1210, 150, 608, 342)     # 16:9 monitor (screen px at push 0)

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
var cel_x := 300.0

func _ready() -> void:
	var p = ProjectSettings.globalize_path("res://local/studio-cels.png")
	if FileAccess.file_exists(p):
		img = Image.load_from_file(p)
		var im2 = img.duplicate()
		im2.generate_mipmaps()
		sheet = ImageTexture.create_from_image(im2)
		ok = true
	layer = CanvasLayer.new()
	layer.layer = 2
	add_child(layer)
	canvas = Node2D.new()
	canvas.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	layer.add_child(canvas)
	canvas.draw.connect(_draw_studio)

func set_state(time: float, talking: float) -> void:
	t = time
	talk = talking
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
		return TALK[int(t * 12.0) % TALK.size()]
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
		# edge extension: left and right columns of this cel stretched to the frame edges
		canvas.draw_texture_rect_region(sheet, Rect2(0, 0, cel_x + 2, 1080), Rect2(src.position, Vector2(2, CEL.y)), Color(0.82, 0.84, 0.9, a))
		var fr = MON.grow(16)
		var x0 = dst.end.x - 2
		for piece in [Rect2(x0, 0, 1920 - x0, fr.position.y), Rect2(x0, fr.end.y, 1920 - x0, 1080 - fr.end.y),
				Rect2(x0, fr.position.y, fr.position.x - x0, fr.size.y), Rect2(fr.end.x, fr.position.y, 1920 - fr.end.x, fr.size.y)]:
			if piece.size.x <= 0 or piece.size.y <= 0:
				continue
			var sy0 = piece.position.y / 1080.0 * CEL.y
			var sh = piece.size.y / 1080.0 * CEL.y
			canvas.draw_texture_rect_region(sheet, piece, Rect2(src.position + Vector2(CEL.x - 2, sy0), Vector2(2, sh)), Color(0.82, 0.84, 0.9, a))
	else:
		canvas.draw_rect(Rect2(0, 0, 1920, 1080), Color(0.1, 0.14, 0.26, a))
	_wall_details(a, dst)
	if ok:
		canvas.draw_texture_rect_region(sheet, dst, src, Color(1, 1, 1, a))
		# soft seams
		for k in 18:
			var w = 18.0 - k
			canvas.draw_rect(Rect2(dst.position.x - 1 + k, 0, 1, 1080), Color(0.08, 0.1, 0.18, 0.025 * w * a))
			canvas.draw_rect(Rect2(dst.end.x - k, 0, 1, 1080), Color(0.08, 0.1, 0.18, 0.025 * w * a))
	_monitor(a)
	canvas.draw_set_transform(Vector2.ZERO)

func _wall_details(a: float, dst: Rect2) -> void:
	var ink = Color(0.05, 0.07, 0.13, 0.55 * a)
	for x in [70.0, 190.0, 1160.0, 1870.0]:
		canvas.draw_line(Vector2(x, 0), Vector2(x, 840), ink, 3.0)
	canvas.draw_line(Vector2(0, 520), Vector2(dst.position.x, 520), ink, 3.0)
	canvas.draw_line(Vector2(dst.end.x, 600), Vector2(1920, 600), ink, 3.0)
	# shelf + books on the left (continues the cel's shelf line)
	var sy = 434.0
	canvas.draw_rect(Rect2(0, sy, dst.position.x + 4, 16), Color(0.45, 0.28, 0.16, a))
	canvas.draw_rect(Rect2(0, sy + 16, dst.position.x + 4, 6), Color(0.2, 0.12, 0.07, a))
	var cols = [Color("#2c4f8f"), Color("#c9822f"), Color("#3b6fb3"), Color("#d9d2c0"), Color("#20386b")]
	var x = 40.0
	for k in 9:
		var h = 70.0 + (k * 37 % 26)
		canvas.draw_rect(Rect2(x, sy - h, 22, h), Color(cols[k % cols.size()], a))
		canvas.draw_rect(Rect2(x, sy - h, 22, h), Color(0.03, 0.04, 0.08, a), false, 2.0)
		x += 26.0 if k != 4 else 60.0
	# desk continues the cel's desk top
	var dy = 880.0
	canvas.draw_rect(Rect2(0, dy, dst.position.x, 1080 - dy), Color(0.55, 0.32, 0.17, a))
	canvas.draw_rect(Rect2(dst.end.x, dy, 1920 - dst.end.x, 1080 - dy), Color(0.55, 0.32, 0.17, a))
	canvas.draw_line(Vector2(0, dy), Vector2(dst.position.x, dy), Color(0.75, 0.5, 0.3, a), 4.0)
	canvas.draw_line(Vector2(dst.end.x, dy), Vector2(1920, dy), Color(0.75, 0.5, 0.3, a), 4.0)

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
