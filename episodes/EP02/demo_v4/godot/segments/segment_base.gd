@tool
extends Node2D
## Base director for EP02 script segments (SC03, SC04, ...).
## One AnimationPlayer clip "sequence" keys the component properties and the
## camera; this node steps time frame by frame, integrates oil travel, draws
## the blueprint background, callouts with evidence tags, host corners
## (Capy / engineer, local EP01 art) and runs --qa.

const Kit = preload("res://cutaway/kit.gd")
const FPS := 30.0

@export var scene_tag := "SC00"
@export var scene_title := ""
@export_range(0, 1) var capy_in := 0.0
@export_range(0, 1) var eng_in := 0.0
@export var capy_tilt := 0.0
@export var capy_blinks: Array = []
@export var eng_blinks: Array = []
@export_range(0, 1) var legend := 1.0
@export var cam_x := 0.0
@export var cam_y := 0.0
@export var cam_zoom := 1.0
## (base_time, inserted_seconds) pairs written by tools/segment_timing.py
@export var inserts: PackedVector2Array = PackedVector2Array()

var player: AnimationPlayer
var anim: Animation
var tracks := {}
var cam: Camera2D
var frame := 0
var t := 0.0
var length := 10.0
var qa_mode := false
var qa_report := []
var telemetry := []
var font: Font
var bold: FontVariation
var hud: Node2D
var host_capy: Texture2D
var host_eng: Texture2D
## [text, tag, world_anchor, screen_offset, t_in, t_out]
var callouts: Array = []

func _ready() -> void:
	font = ThemeDB.fallback_font
	bold = FontVariation.new()
	bold.base_font = font
	bold.variation_embolden = 0.7
	player = $AnimationPlayer
	cam = $Camera
	anim = player.get_animation("sequence")
	length = anim.length
	for i in anim.get_track_count():
		tracks[String(anim.track_get_path(i))] = i
	var layer = CanvasLayer.new()
	layer.layer = 3
	add_child(layer)
	hud = Node2D.new()
	layer.add_child(hud)
	hud.draw.connect(_draw_hud)
	for n in ["host_capy", "host_eng"]:
		var p = ProjectSettings.globalize_path("res://local/%s.png" % n)
		if FileAccess.file_exists(p):
			var img = Image.load_from_file(p)
			img.generate_mipmaps()
			set(n, ImageTexture.create_from_image(img))
	qa_mode = "--qa" in OS.get_cmdline_user_args()
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--start="):
			frame = int(round(float(arg.get_slice("=", 1)) * FPS))
	setup()
	for c in callouts:
		c[4] = warp(c[4])
		c[5] = warp(c[5])
	capy_blinks = capy_blinks.map(func(b): return warp(b))
	eng_blinks = eng_blinks.map(func(b): return warp(b))
	if not Engine.is_editor_hint():
		player.play("sequence")
		player.pause()

func setup() -> void:
	pass

## base-timeline seconds -> output seconds (same rule as tools/segment_timing.py)
func warp(bt: float) -> float:
	var out = bt
	for ins in inserts:
		if bt > ins.x:
			out += ins.y
	return out

func sample(path: String, time: float) -> float:
	return anim.value_track_interpolate(tracks[path], clampf(time, 0.0, length))

## integral of f(time) dt from 0 to `time` (deterministic, frame steps)
func integrate(f: Callable, time: float, step := 1.0 / 30.0) -> float:
	var acc = 0.0
	var s = 0.0
	while s < time:
		acc += f.call(s) * step
		s += step
	return acc

func _process(_d: float) -> void:
	if Engine.is_editor_hint():
		if player == null:
			return
		t = player.current_animation_position
	else:
		t = frame / FPS
		player.seek(t, true)
		frame += 1
	cam.position = Vector2(cam_x, cam_y)
	cam.zoom = Vector2.ONE * cam_zoom
	update(t)
	queue_redraw()
	hud.queue_redraw()
	if qa_mode and not Engine.is_editor_hint():
		qa(t)
		if frame >= int(length * FPS):
			_finish()

func update(_time: float) -> void:
	pass

func qa(_time: float) -> void:
	pass

func _finish() -> void:
	var out = FileAccess.open("res://../%s_qa.txt" % scene_tag, FileAccess.WRITE)
	out.store_line("frames=%d errors=%d" % [frame, qa_report.size()])
	for l in qa_report:
		out.store_line(l)
	out.close()
	var tel = FileAccess.open("res://../%s_telemetry.csv" % scene_tag, FileAccess.WRITE)
	for l in telemetry:
		tel.store_line(l)
	tel.close()
	print("QA %s frames=%d errors=%d" % [scene_tag, frame, qa_report.size()])
	get_tree().quit(1 if qa_report.size() > 0 else 0)

# ------------------------------------------------------------ background
func _draw() -> void:
	var c = cam.position if cam else Vector2.ZERO
	var r = Rect2(c - Vector2(4000, 3000), Vector2(8000, 6000))
	draw_rect(r, Color("#0c1524"))
	var step = 60.0
	var x0 = floor(r.position.x / step) * step
	var x = x0
	while x < r.end.x:
		draw_line(Vector2(x, r.position.y), Vector2(x, r.end.y), Color(0.35, 0.5, 0.75, 0.07), 1.0)
		x += step
	var y = floor(r.position.y / step) * step
	while y < r.end.y:
		draw_line(Vector2(r.position.x, y), Vector2(r.end.x, y), Color(0.35, 0.5, 0.75, 0.07), 1.0)
		y += step

# ------------------------------------------------------------------- HUD
func to_screen(p: Vector2) -> Vector2:
	return (p - cam.position) * cam.zoom.x + Vector2(960, 540)

func _draw_hud() -> void:
	# scene chip
	var title = "%s · %s" % [scene_tag, scene_title]
	var tw = bold.get_string_size(title, HORIZONTAL_ALIGNMENT_LEFT, -1, 22).x + 30
	hud.draw_rect(Rect2(36, 30, tw, 40), Color(0.05, 0.08, 0.12, 0.82))
	hud.draw_rect(Rect2(36, 30, 5, 40), Color(1, 0.78, 0.25))
	hud.draw_string(bold, Vector2(52, 58), title, HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color(1, 1, 1))
	var notice = "Mặt cắt minh họa nguyên lý · K1 ✓ brochure CEN00049-08 · K2 ✓ thông số shop manual PC200-8 · NGUYÊN LÝ = cấu tạo chung"
	var nw = font.get_string_size(notice, HORIZONTAL_ALIGNMENT_LEFT, -1, 18).x + 24
	hud.draw_rect(Rect2(1884 - nw, 30, nw, 32), Color(0.05, 0.08, 0.12, 0.78))
	hud.draw_string(font, Vector2(1896 - nw, 52), notice, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color(0.86, 0.94, 0.9))
	if legend > 0.01:
		var items = [[Kit.RED, "dầu áp lực"], [Kit.BLUE, "dầu hồi / hút"], [Kit.ORANGE, "pilot"], [Kit.PURPLE, "tín hiệu tải LS"]]
		var x = 1884.0
		for it in items:
			x -= font.get_string_size(it[1], HORIZONTAL_ALIGNMENT_LEFT, -1, 19).x + 50
		hud.draw_rect(Rect2(x - 12, 70, 1896 - x, 34), Color(0.05, 0.08, 0.12, 0.72 * legend))
		for it in items:
			hud.draw_line(Vector2(x, 87), Vector2(x + 26, 87), Color(it[0], legend), 7.0)
			hud.draw_string(font, Vector2(x + 34, 94), it[1], HORIZONTAL_ALIGNMENT_LEFT, -1, 19, Color(1, 1, 1, legend))
			x += font.get_string_size(it[1], HORIZONTAL_ALIGNMENT_LEFT, -1, 19).x + 50
	for c in callouts:
		var a = clampf((t - float(c[4])) / 0.35, 0, 1) * clampf((float(c[5]) - t) / 0.3, 0, 1)
		if a > 0.0:
			_callout(c[0], c[1], to_screen(c[2]), c[3], a)
	draw_extra_hud(hud)
	_host(host_capy, capy_in, true, capy_tilt, capy_blinks, [[69, 84, 8, 11], [128, 102, 8.5, 11]])
	_host(host_eng, eng_in, false, 0.0, eng_blinks, [[135, 138, 7, 11], [185, 124, 6, 10]])

func draw_extra_hud(_h: Node2D) -> void:
	pass

func _callout(text: String, tag: String, anchor: Vector2, offset: Vector2, a: float) -> void:
	var size = 24
	var tag_w = 0.0
	if tag != "":
		tag_w = bold.get_string_size(tag, HORIZONTAL_ALIGNMENT_LEFT, -1, 18).x + 18
	var w = bold.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x + 28 + tag_w
	var bp = anchor + offset
	bp.x = clampf(bp.x, 30, 1890 - w)
	bp.y = clampf(bp.y, 120, 900)
	var box = Rect2(bp, Vector2(w, 42))
	var join = Vector2(clampf(anchor.x, box.position.x + 10, box.end.x - 10), box.position.y + (42 if anchor.y > box.position.y + 21 else 0))
	hud.draw_line(anchor, join, Color(1, 1, 1, 0.85 * a), 2.0, true)
	hud.draw_circle(anchor, 5.0, Color(1, 0.86, 0.35, a), true, -1, true)
	hud.draw_rect(box, Color(0.05, 0.08, 0.13, 0.88 * a))
	hud.draw_rect(Rect2(box.position, Vector2(5, 42)), Color(1, 0.78, 0.25, a))
	hud.draw_string(bold, box.position + Vector2(15, 29), text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, Color(1, 1, 1, a))
	if tag != "":
		var verified = tag.begins_with("K")
		var tr = Rect2(Vector2(box.end.x - tag_w - 4, box.position.y + 8), Vector2(tag_w - 4, 26))
		hud.draw_rect(tr, Color(0.2, 0.62, 0.36, a) if verified else Color(0.42, 0.47, 0.55, a))
		hud.draw_string(bold, tr.position + Vector2(7, 20), tag, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color(1, 1, 1, a))

## Host corner: slides in from the bottom edge, rigid tilt, eyelid blinks.
func _host(tex: Texture2D, k: float, left: bool, tilt: float, blinks: Array, eyes: Array) -> void:
	if tex == null or k <= 0.001:
		return
	var e = 1.0 - pow(1.0 - k, 3.0)
	var sc = 1.25 if left else 1.0
	var size = tex.get_size() * sc
	var base = Vector2(70.0 if left else 1920.0 - size.x - 50.0, 1080.0 - size.y * e + 6.0)
	var pivot = base + Vector2(size.x * 0.5, size.y)
	var bob = sin(t * 2.1) * 1.5
	hud.draw_set_transform(pivot + Vector2(0, bob), deg_to_rad(tilt), Vector2.ONE * sc)
	var off = -Vector2(size.x * 0.5, size.y) / sc
	hud.draw_circle(off + tex.get_size() * Vector2(0.5, 0.75), tex.get_size().x * 0.6, Color(0.35, 0.55, 0.85, 0.18), true, -1, true)
	hud.draw_texture(tex, off)
	var close = 0.0
	for b in blinks:
		var d: float = t - float(b)
		if d >= 0.0 and d < 0.17:
			close = 1.0 if d >= 0.05 and d < 0.12 else 0.55
	if close > 0.0:
		for ey in eyes:
			var c = off + Vector2(ey[0], ey[1])
			var rx: float = ey[2] + 1.8
			var ry: float = ey[3] + 1.8
			var pts = PackedVector2Array()
			var n = 24
			for i in n + 1:
				var a = PI + i * (TAU if close > 0.8 else PI) / n
				pts.append(c + Vector2(cos(a) * rx, sin(a) * ry))
			hud.draw_colored_polygon(pts, Color(250 / 255.0, 172 / 255.0, 100 / 255.0))
			hud.draw_line(c + Vector2(-rx, ry * 0.2 if close > 0.8 else 0.0), c + Vector2(rx, ry * 0.2 if close > 0.8 else 0.0), Color("#2a1d14"), 2.2, true)
	hud.draw_set_transform(Vector2.ZERO)
