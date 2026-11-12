extends Node2D

const LENGTH = 42.0
const WIDTH = 1920
const HEIGHT = 1080
const DARK = Color("#142c36")
const PANEL = Color("#1d3946")
const IVORY = Color("#fff2d7")
const GOLD = Color("#ffcf69")
const PRESSURE = Color("#fa776c")
const RETURN = Color("#78c9ee")
const PILOT = Color("#ffb059")
const LS = Color("#d5a2f4")
const IDLE = Color("#48616b")
const RIG = preload("res://machine.gd")
const RAISE_START = 24.5
const RAISE_END = 35.3
const SCENES = [0.0, 4.2, 10.2, 17.4, 24.2, 35.8]

@export_range(0.0, 1.0) var lift_amount: float = 0.0
@export_range(0.0, 1.0) var pilot_amount: float = 0.0

@onready var machine: Node2D = $Machine
@onready var animator: AnimationPlayer = $AnimationPlayer
@onready var field: Node2D = $Field
@onready var foreground: Node2D = $Foreground

var time: float = 0
var shot: int = 0
var intro: ImageTexture
var guide: ImageTexture
var reply: ImageTexture
var clouds: Array[Vector2] = [Vector2(163, 261), Vector2(795, 174), Vector2(1457, 202)]
var ground_stones: PackedVector2Array

func _ready() -> void:
	intro = _local("studio-cels.png")
	guide = _local("field-hook.png")
	reply = _local("field-reply.png")
	var rng := RandomNumberGenerator.new()
	rng.seed = 2008
	for i in range(127):
		ground_stones.append(Vector2(rng.randf_range(0, WIDTH), rng.randf_range(540, HEIGHT)))
	field.draw.connect(_draw_field)
	foreground.draw.connect(_draw_foreground)
	animator.play("sequence")
	animator.pause()
	if OS.get_cmdline_user_args().has("--qa"):
		_verify()
		return
	seek(0.0)

func _local(filename: String) -> ImageTexture:
	var filename_full := ProjectSettings.globalize_path("res://local/" + filename)
	if not FileAccess.file_exists(filename_full):
		return null
	var art := Image.load_from_file(filename_full)
	return ImageTexture.create_from_image(art) if art else null

func _process(delta: float) -> void:
	seek(time)
	time += delta
	if time >= LENGTH and not OS.has_feature("movie"):
		time = 0.0

func seek(value: float) -> void:
	for i in range(SCENES.size()):
		if value >= SCENES[i]:
			shot = i
	animator.seek(value, true)
	machine.pose(lift_amount)
	machine.visible = shot > 0
	machine.position = Vector2(1210, 686) if shot != 2 else Vector2(1310, 722)
	var magnification := 1.15 if shot != 2 else 1.07
	machine.scale = Vector2.ONE * magnification
	field.queue_redraw()
	foreground.queue_redraw()

func _draw_field() -> void:
	field.draw_rect(Rect2(0, 0, WIDTH, HEIGHT), DARK)
	if shot == 0:
		for i in range(7):
			field.draw_line(Vector2(i * 240, 0), Vector2(i * 240 - 180, 1080), Color("#203e4a"), 3, true)
		return
	field.draw_rect(Rect2(0, 0, WIDTH, 630), Color("#b1ddd3"))
	for i in range(16):
		var y := float(i * 28)
		field.draw_rect(Rect2(0, y, WIDTH, 29), Color("#71aeba").lerp(Color("#c5e3ce"), float(i)/16))
	field.draw_circle(Vector2(1530, 202), 109, Color("#fff0b8"), true, -1, true)
	for p in clouds:
		var drift := Vector2(time * 1.4, 0)
		field.draw_rect(Rect2(p + drift, Vector2(197, 22)), Color("#f2e7cc"))
		for i in range(4):
			field.draw_circle(p + drift + Vector2(34 + i * 42, 4), 29 + 8 * (i % 2), Color("#f2e7cc"), true, -1, true)
	for i in range(22):
		var y := 458.0 + cos(float(i) * .53) * 42.0
		field.draw_circle(Vector2(i * 96, y), 129, Color("#80a99d"), true, -1, true)
	for i in range(46):
		var y := 530.0 + sin(float(i) * .8) * 35.0
		field.draw_circle(Vector2(i * 45, y), 58, Color("#577e6c"), true, -1, true)
	field.draw_colored_polygon(PackedVector2Array([Vector2(0, 604), Vector2(420, 546), Vector2(985, 582),
		Vector2(1380, 543), Vector2(WIDTH, 582), Vector2(WIDTH, HEIGHT), Vector2(0, HEIGHT)]), Color("#c58e59"))
	field.draw_colored_polygon(PackedVector2Array([Vector2(0, 814), Vector2(495, 761), Vector2(973, 845),
		Vector2(1380, 897), Vector2(WIDTH, 850), Vector2(WIDTH, HEIGHT), Vector2(0, HEIGHT)]), Color("#ddab71"))
	for p in ground_stones:
		if p.y > 610:
			var k := 1.0 + (p.y-610.0)/90.0
			field.draw_line(p, p+Vector2(k * 3.9, 0), Color("#b88454"), k*.62, true)
	for i in range(23):
		var x := float(i * 89)
		field.draw_line(Vector2(x, 577), Vector2(x, 636), Color("#77584a"), 9, true)
	field.draw_line(Vector2(0, 592), Vector2(1920, 592), Color("#edd197"), 8, true)
	field.draw_line(Vector2(0, 615), Vector2(1920, 615), Color("#edb970"), 6, true)
	var shadow := PackedVector2Array()
	for i in range(64):
		var angle := TAU * i / 64.0
		shadow.append(Vector2(1102 + cos(angle)*364.0, 966 + sin(angle)*15.0))
	field.draw_colored_polygon(shadow, Color("#9d764e"))

func _text(p: Vector2, text: String, size: int, color := IVORY) -> void:
	foreground.draw_string(ThemeDB.fallback_font, p, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, color)

func _rect(box: Rect2, color: Color) -> void:
	foreground.draw_rect(box, color)

func _line(a: Vector2, b: Vector2, color: Color, width := 4.0) -> void:
	foreground.draw_line(a, b, color, width, true)

func _circle(p: Vector2, r: float, color: Color) -> void:
	foreground.draw_circle(p, r, color, true, -1.0, true)

func _panel(box: Rect2) -> void:
	_rect(Rect2(box.position + Vector2(11, 12), box.size), Color("#3a3327"))
	_rect(box, DARK)
	_rect(box.grow(-4), PANEL)

func _label(kicker: String, title: String) -> void:
	_rect(Rect2(54, 48, 920, 127), DARK)
	_text(Vector2(82, 93), kicker, 25, GOLD)
	_text(Vector2(82, 148), title, 48)

func _draw_foreground() -> void:
	match shot:
		0: _studio()
		1: _observation(false)
		2: _pump()
		3: _valve()
		4: _raise()
		5: _observation(true)
	if shot >= 2:
		_rect(Rect2(1049, 48, 817, 42), DARK)
		_text(Vector2(1064, 78), "Sơ đồ giản lược · Chi tiết theo số sê-ri và cấu hình máy", 24, IVORY)

func _studio() -> void:
	if intro:
		var i := mini(41, floori(time * 10.0))
		var source := Rect2(i % 7 * 520, floori(i / 7.0) * 737, 520, 737)
		foreground.draw_texture_rect_region(intro, Rect2(90, 54, 680, 680.0 * 737.0 / 520.0), source)
	_rect(Rect2(831, 144, 944, 8), GOLD)
	_text(Vector2(831, 224), "CAPY BK   /   TẬP 02", 34, GOLD)
	_text(Vector2(831, 377), "KĨ SƯ ƠIII!", 99)
	_text(Vector2(838, 524), "Tay máy đào lấy đâu ra sức?", 51)
	_text(Vector2(838, 628), "KOMATSU PC200-8", 33, GOLD)
	_line(Vector2(838, 687), Vector2(1745, 687), IDLE, 3.0)

func _observation(holding: bool) -> void:
	if holding:
		_label("NÂNG CẦN · GIỮ VỊ TRÍ", "Cần giữ nguyên khi van về giữa")
	else:
		_label("CÔNG TRƯỜNG · PC200-8", "Tay máy lấy sức từ đâu?")
	var asset := reply if holding else guide
	if asset:
		var trim := 0.0 if holding else minf(1.0, maxf(0.0, (time-4.2)/6.0)) * 14.0
		var area := Rect2(0, 190 + trim, 520, 547 - trim)
		var target := Rect2(70, 265, 621, 621 * area.size.y / area.size.x)
		_panel(target.grow(5))
		foreground.draw_texture_rect_region(asset, target, area)
	if holding:
		_rect(Rect2(755, 191, 757, 58), DARK)
		_text(Vector2(779, 230), "Động cơ → bơm → van → xi lanh → cần", 29, GOLD)

func _pump() -> void:
	_label("KHOANG MÁY · TRUYỀN CÔNG SUẤT", "Động cơ quay bơm")
	_panel(Rect2(66, 260, 914, 596))
	_text(Vector2(104, 333), "SAA6D107E-1", 38)
	_text(Vector2(539, 333), "Bơm piston chính", 38)
	# A rotating crankshaft and piston bank illustrate the mechanical drive.
	var shaft := Vector2(328, 537)
	var shaft_angle := time * 9.0
	_rect(Rect2(109, 389, 357, 216), Color("#52737b"))
	_rect(Rect2(128, 412, 324, 171), Color("#284652"))
	for i in range(3):
		var x := 171.0 + i * 89.0
		var phase := shaft_angle + i * TAU / 3.0
		var crank_pin := Vector2(x + 26, 546) + Vector2.from_angle(phase) * 16.0
		var lateral := crank_pin.x - (x + 26)
		var piston_pin := Vector2(x + 26, crank_pin.y - sqrt(59.0 * 59.0 - lateral * lateral))
		_rect(Rect2(x, 429, 52, 103), Color("#63868b"))
		_rect(Rect2(x+6, piston_pin.y-16, 40, 23), Color("#b9ccc3"))
		_line(piston_pin, crank_pin, IVORY, 7.0)
	_line(Vector2(141, 552), Vector2(593, 552), GOLD, 12)
	for i in range(6):
		var direction := Vector2.from_angle(shaft_angle + i * TAU/6.0)
		_line(shaft+direction*28, shaft+direction*42, GOLD, 5.0)
	_circle(shaft, 27, DARK)
	_circle(shaft, 12, GOLD)
	_rect(Rect2(591, 411, 276, 194), Color("#49626b"))
	var tilt := lerpf(.12, .45, smoothstep(11.6, 15.1, time))
	_line(Vector2(827 - 76 * tilt, 429), Vector2(827 + 77 * tilt, 582), GOLD, 13)
	for i in range(4):
		var phase := shaft_angle + i * TAU / 4.0
		var y := 505.0 + sin(phase) * 59.0
		var shoe := 827.0 + (y - 505.0) * tilt
		_line(Vector2(626, y), Vector2(736, y), Color("#273f4a"), 21.0)
		_rect(Rect2(shoe-148, y-7, 61, 15), IVORY)
		_line(Vector2(shoe-87, y), Vector2(shoe, y), Color("#95acac"), 5.0)
		_circle(Vector2(shoe, y), 5, IVORY)
	flow([Vector2(867, 496), Vector2(922, 496), Vector2(922, 676), Vector2(773, 676)], PRESSURE, true)
	_text(Vector2(102, 737), "Trục truyền mô-men", 29, GOLD)
	_text(Vector2(532, 737), "Góc đĩa nghiêng đổi lưu lượng", 28, IVORY)
	_text(Vector2(102, 806), "Áp suất tăng theo tải và giới hạn của mạch.", 31)

func _valve() -> void:
	_label("JOYSTICK · ĐIỀU KHIỂN", "Pilot dịch chuyển con trượt")
	_panel(Rect2(66, 235, 972, 625))
	_text(Vector2(101, 312), "Tay điều khiển", 33, GOLD)
	_text(Vector2(539, 312), "Van phân phối", 33)
	var base := Vector2(242, 519)
	var handle := base + Vector2(-98.0 * pilot_amount, -140)
	_rect(Rect2(158, 515, 165, 50), Color("#61737b"))
	_line(base, handle, DARK, 24)
	_line(base, handle, IVORY, 13)
	_circle(handle, 24, DARK)
	_circle(handle-Vector2(0,4), 17, PILOT)
	_rect(Rect2(556, 437, 361, 154), Color("#5c7981"))
	_rect(Rect2(571, 464, 331, 100), DARK)
	var travel := 46.0 * pilot_amount
	for i in range(3):
		var x := 592.0 + i * 83.0 + travel
		_rect(Rect2(x, 474, 37, 79), Color("#a2b5b3"))
	_line(Vector2(580+travel, 513), Vector2(861+travel, 513), Color("#a2b5b3"), 10)
	flow([Vector2(301, 550), Vector2(385, 550), Vector2(385, 490), Vector2(551, 490)], PILOT, pilot_amount > 0.06)
	_text(Vector2(101, 696), "Cam · tín hiệu pilot", 29, PILOT)
	_text(Vector2(101, 741), "LS · phản hồi tải về bộ điều chỉnh bơm", 29, LS)
	_text(Vector2(101, 776), "Con trượt mở đường cấp và đường hồi cho xi lanh.", 30)

func _raise() -> void:
	_label("NÂNG CẦN · XI LANH TÁC ĐỘNG KÉP", "Ty đi ra, cần quay quanh chốt")
	var active := time > RAISE_START and time < RAISE_END
	_panel(Rect2(66, 258, 684, 628))
	_text(Vector2(102, 323), "Một xi lanh trong cặp nâng cần", 31)
	var stroke: float = machine.stroke_ratio()
	var piston: float = 302.0 + 108.0 * stroke
	_rect(Rect2(147, 410, 430, 123), Color("#7d8f8f"))
	_rect(Rect2(161, 425, 403, 93), DARK)
	_rect(Rect2(161, 427, piston - 161, 89), PRESSURE.darkened(0.45))
	_rect(Rect2(piston, 427, 564 - piston, 89), RETURN.darkened(0.48))
	_rect(Rect2(piston, 426, 17, 91), IVORY)
	_rect(Rect2(piston + 16, 462, 278, 20), IVORY)
	_circle(Vector2(piston+294, 472), 13, Color("#afc4c2"))
	_rect(Rect2(562, 410, 17, 50), Color("#7d8f8f"))
	_rect(Rect2(562, 482, 17, 51), Color("#7d8f8f"))
	_text(Vector2(171, 399), "Khoang đáy", 22, PRESSURE)
	_text(Vector2(465, 399), "Khoang ty", 22, RETURN)
	# The diagram folds the pump bank into one block and one cylinder.
	# Supply and return remain distinct through the valve body.
	_rect(Rect2(231, 627, 102, 73), Color("#667c81"))
	_circle(Vector2(125, 650), 21, Color("#6f878c"))
	_rect(Rect2(93, 719, 45, 31), Color("#6f878c"))
	_rect(Rect2(99, 731, 33, 14), RETURN.darkened(.4))
	flow([Vector2(145, 650), Vector2(236, 650), Vector2(365, 650),
		Vector2(365, 570), Vector2(194, 570), Vector2(194, 530)], PRESSURE, active, stroke * 430.0)
	flow([Vector2(543, 531), Vector2(543, 614), Vector2(396, 614),
		Vector2(396, 678), Vector2(220, 678), Vector2(220, 735), Vector2(130, 735)], RETURN, active, stroke * 214.0)
	flow([Vector2(282, 627), Vector2(282, 603), Vector2(126, 603),
		Vector2(126, 628)], LS, active)
	_text(Vector2(165, 593), "LS · tải", 20, LS)
	_text(Vector2(241, 722), "Van", 23)
	_text(Vector2(95, 692), "Bơm", 23)
	_text(Vector2(94, 769), "Thùng dầu", 23)
	_text(Vector2(104, 837), "Đỏ · cấp dầu    Xanh · hồi    Tím · LS", 25)
	var hinge: Vector2 = machine.to_global(RIG.BOOM_PIN)
	foreground.draw_arc(hinge, 38, 0, TAU, 48, IVORY, 4, true)
	var rod_eye: Vector2 = machine.to_global(machine.eye())
	foreground.draw_arc(rod_eye, 27, 0, TAU, 48, GOLD, 3, true)

func flow(points: Array, hue: Color, running: bool, travel := -1.0) -> void:
	var distances := PackedFloat32Array([0.0])
	for i in range(1, points.size()):
		var a: Vector2 = points[i-1]
		var b: Vector2 = points[i]
		distances.append(distances[-1] + a.distance_to(b))
		_line(a, b, hue.darkened(.43) if running else IDLE, 9.0)
	if not running:
		return
	var count := maxi(1, floori(distances[-1] / 91.0))
	for j in range(count):
		var phase := time * 124.0 if travel < 0.0 else travel
		var position_on_line := fposmod(phase + j * distances[-1] / count, distances[-1])
		for i in range(1, points.size()):
			if position_on_line < distances[i]:
				var a: Vector2 = points[i-1]
				var b: Vector2 = points[i]
				var u := a.direction_to(b)
				var tip := a + u * (position_on_line - distances[i-1])
				foreground.draw_colored_polygon(PackedVector2Array([tip+u*9,
					tip-u*9+u.orthogonal()*6, tip-u*9-u.orthogonal()*6]), hue)
				break

func _verify() -> void:
	var last_extension := -1.0
	for frame in range(1260):
		seek(float(frame)/30.0)
		var extension: float = machine.stroke_ratio()
		if not machine.verify_pose() or extension + 0.00001 < last_extension:
			push_error("Rig geometry failed at frame %d" % frame)
			get_tree().quit(1)
			return
		if ((frame <= 735 and absf(extension) > 0.00001)
				or (frame >= 1059 and absf(extension-1.0) > 0.00001)):
			push_error("Hold state failed at frame %d" % frame)
			get_tree().quit(1)
			return
		last_extension = extension
	print("QA PASS: 1260 poses, constant layer scale, pin coincidence, barrel overlap, twin stroke and hold")
	print("Ram pin distance: %.2f → %.2f illustration units" % [machine.length_at(RIG.LOWER), machine.length_at(RIG.UPPER)])
	get_tree().quit()
