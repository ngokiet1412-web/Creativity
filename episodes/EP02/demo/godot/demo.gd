extends Node2D

const LENGTH = 42.0
const PROOF_LENGTH = 16.0
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
const PROOF_BEATS = [0.0, 3.0, 9.0, 13.0]

@export_range(0.0, 1.0) var lift_amount: float = 0.0
@export_range(0.0, 1.0) var pilot_amount: float = 0.0
@export_range(0.0, 1.0) var stick_amount: float = 0.5
@export_range(0.0, 1.0) var bucket_amount: float = 0.5

@onready var machine: Node2D = $Machine
@onready var characters: Node2D = $Characters
@onready var diagram_layer: Node2D = $DiagramLayer
@onready var animator: AnimationPlayer = $AnimationPlayer
@onready var field: Node2D = $Field
@onready var foreground: Node2D = $Foreground

var time: float = 0.0
var shot: int = 0
var proof_mode: bool = false
var active_length: float = LENGTH
var intro: ImageTexture
var cutaways_tex: ImageTexture
var worksite: ImageTexture

func _ready() -> void:
	intro = _local("studio-cels.png")
	cutaways_tex = _local("cutaways.png")
	var ws_path := ProjectSettings.globalize_path("res://art/worksite.png")
	if FileAccess.file_exists(ws_path):
		var ws_img := Image.load_from_file(ws_path)
		if ws_img != null:
			worksite = ImageTexture.create_from_image(ws_img)
	field.draw.connect(_draw_field)
	diagram_layer.draw.connect(_draw_diagrams)
	foreground.draw.connect(_draw_foreground)

	var args := OS.get_cmdline_user_args()
	proof_mode = args.has("--proof16")
	active_length = PROOF_LENGTH if proof_mode else LENGTH
	animator.play("proof_16s" if proof_mode else "sequence")
	animator.pause()

	if args.has("--qa"):
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
	if time >= active_length and not OS.has_feature("movie"):
		time = 0.0

func seek(value: float) -> void:
	time = value
	if proof_mode:
		for i in range(PROOF_BEATS.size()):
			if value >= PROOF_BEATS[i]:
				shot = i
		animator.seek(value, true)
		_apply_proof_state(value)
	else:
		for i in range(SCENES.size()):
			if value >= SCENES[i]:
				shot = i
		animator.seek(value, true)
		_apply_sequence_state(value)
	field.queue_redraw()
	diagram_layer.queue_redraw()
	foreground.queue_redraw()

func _apply_sequence_state(t: float) -> void:
	var scoop := 0.0
	if t >= 17.8:
		scoop = clampf((t - 17.8) / 5.5, 0.0, 1.0)
	machine.pose_full(lift_amount, stick_amount, bucket_amount, t, scoop)
	machine.visible = shot > 0

	# Camera cut in D05: close-up cylinder view (24.2..28.8s) -> wide kinematic view (28.8..35.8s)
	var is_closeup_d05 := (shot == 4 and t < 28.8)
	machine.show_pins_overlay = (shot == 4)
	if shot == 2 or shot == 3:
		machine.position = Vector2(1310, 706)
		machine.scale = Vector2.ONE * 1.04
	elif is_closeup_d05:
		machine.position = Vector2(1248, 768)
		machine.scale = Vector2.ONE * 1.26
	else:
		machine.position = Vector2(1184, 688)
		machine.scale = Vector2.ONE * 1.12

	# Multi-layered 2D Characters visibility & performance
	var show_chars := (shot == 1) or (shot == 4 and not is_closeup_d05) or (shot == 5)
	characters.visible = show_chars
	if show_chars:
		var capy_talk := (t >= 4.35 and t <= 7.05) or (t >= 36.0 and t <= 38.8)
		var eng_talk := (t >= 7.2 and t <= 10.05) or (t >= 29.0 and t <= 35.4) or (t >= 38.9 and t <= 41.8)
		var capy_exc := (t >= 29.2 and t <= 31.5) or (t >= 36.0 and t <= 38.8)
		var happy := (shot == 5)
		var point_deg := 0.0
		if shot == 1:
			# Sweep pointing arm from Engine (+10 deg) -> Pump (+4 deg) -> Valve (-3 deg) -> Boom Cylinders (-12 deg)
			point_deg = lerpf(10.0, -12.0, clampf((t - 7.0) / 2.8, 0.0, 1.0))
		elif shot == 4:
			point_deg = -13.0
		elif shot == 5:
			point_deg = -6.0 + sin(t * 2.5) * 4.0
		characters.apply_performance(t, capy_talk, eng_talk, point_deg, capy_exc, happy)

func _apply_proof_state(t: float) -> void:
	# 16s V3 QA Proof Clip:
	# Beat 0 (0..3s): Worksite idle + Capy asks question behind safety rail
	# Beat 1 (3..9s): Valve command -> cylinder extends -> boom & stick move + camera cut to cylinder close-up (6..9s)
	# Beat 2 (9..13s): Bucket curls & scoops soil mound with falling dirt particles + boom lifts loaded bucket
	# Beat 3 (13..16s): Capy reacts ("Àaa!") + hydraulic diagram chain highlights in sync
	var scoop := clampf((t - 9.1) / 3.1, 0.0, 1.0) if t >= 9.1 else 0.0
	machine.pose_full(lift_amount, stick_amount, bucket_amount, t, scoop)
	machine.visible = true
	var is_cyl_closeup := (t >= 6.0 and t < 9.0)
	machine.show_pins_overlay = (t >= 6.0 and t < 13.0)
	if is_cyl_closeup:
		machine.position = Vector2(1248, 768)
		machine.scale = Vector2.ONE * 1.26
	else:
		machine.position = Vector2(1210, 692)
		machine.scale = Vector2.ONE * 1.12

	characters.visible = not is_cyl_closeup
	if characters.visible:
		var capy_talk := (t >= 0.4 and t <= 2.7) or (t >= 13.1 and t <= 15.6)
		var eng_talk := (t >= 3.1 and t <= 5.9) or (t >= 9.2 and t <= 12.6)
		var capy_exc := (t >= 13.0)
		var happy := (t >= 13.0)
		var point_deg := lerpf(8.0, -12.0, clampf((t - 3.0) / 5.5, 0.0, 1.0))
		characters.apply_performance(t, capy_talk, eng_talk, point_deg, capy_exc, happy)

func _draw_field() -> void:
	field.draw_rect(Rect2(0, 0, WIDTH, HEIGHT), DARK)
	if not proof_mode and shot == 0:
		for i in range(9):
			var drift := fmod(time * 42.0, 240.0)
			var x := i * 240.0 - drift
			field.draw_line(Vector2(x, 0), Vector2(x - 160, 1080), Color("#1e3b47"), 3, true)
		for j in range(6):
			var y := 140.0 + j * 165.0
			field.draw_line(Vector2(0, y), Vector2(WIDTH, y), Color(0.14, 0.27, 0.33, 0.55), 2, true)
		return
	if worksite != null:
		var art_size := worksite.get_size()
		var gain := maxf(WIDTH / art_size.x, HEIGHT / art_size.y)
		var size := art_size * gain
		# Subtle camera parallax pan across worksite background
		var pan_x := sin(time * 0.45) * 8.0
		field.draw_texture_rect(worksite, Rect2((Vector2(WIDTH, HEIGHT) - size) * 0.5 + Vector2(pan_x, 0), size), false)
	# Animated drifting worksite clouds & wind dust motes so background is alive
	for c_idx in range(4):
		var cx := fmod(220.0 + c_idx * 460.0 + time * (18.0 + c_idx * 3.0), 2100.0) - 100.0
		var cy := 88.0 + (c_idx % 2) * 44.0
		field.draw_circle(Vector2(cx, cy), 34.0, Color(1.0, 0.98, 0.92, 0.16))
		field.draw_circle(Vector2(cx + 28.0, cy + 4.0), 26.0, Color(1.0, 0.98, 0.92, 0.14))

	var contact: Vector2 = machine.to_global(Vector2(-130, 247))
	_ground_shadow(contact + Vector2(4, 3), Vector2(325, 24), 0.17)
	_ground_shadow(contact, Vector2(305, 15), 0.30)
	var bucket_pos: Vector2 = machine.get_node("Upper/Boom/Stick/Bucket").to_global(Vector2(46, 66))
	var gap := maxf(0.0, contact.y - bucket_pos.y)
	_ground_shadow(Vector2(bucket_pos.x + gap * 0.15, contact.y + 2), Vector2(83 + gap * 0.13, 8 + gap * 0.025),
		0.19 - minf(0.11, gap * 0.00045))

func _ground_shadow(center: Vector2, radii: Vector2, opacity: float) -> void:
	var shadow := PackedVector2Array()
	for i in range(64):
		var angle := TAU * i / 64.0
		shadow.append(center + Vector2(cos(angle) * radii.x, sin(angle) * radii.y))
	field.draw_colored_polygon(shadow, Color(0.22, 0.14, 0.11, opacity))

func _text(layer: Node2D, p: Vector2, text: String, size: int, color := IVORY) -> void:
	layer.draw_string(ThemeDB.fallback_font, p, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, color)

func _rect(layer: Node2D, box: Rect2, color: Color) -> void:
	layer.draw_rect(box, color)

func _line(layer: Node2D, a: Vector2, b: Vector2, color: Color, width := 4.0) -> void:
	layer.draw_line(a, b, color, width, true)

func _circle(layer: Node2D, p: Vector2, r: float, color: Color) -> void:
	layer.draw_circle(p, r, color, true, -1.0, true)

func _panel(layer: Node2D, box: Rect2) -> void:
	_rect(layer, Rect2(box.position + Vector2(10, 11), box.size), Color(0.08, 0.12, 0.15, 0.72))
	_rect(layer, box, DARK)
	_rect(layer, box.grow(-4), PANEL)
	layer.draw_rect(box.grow(-4), Color("#385d6d"), false, 2.0)

func _label(kicker: String, title: String) -> void:
	_rect(foreground, Rect2(48, 36, 972, 112), Color(0.08, 0.17, 0.21, 0.94))
	foreground.draw_rect(Rect2(48, 36, 972, 112), GOLD, false, 2.5)
	_text(foreground, Vector2(72, 74), kicker, 22, GOLD)
	_text(foreground, Vector2(72, 122), title, 34, IVORY)

func _draw_diagrams() -> void:
	if proof_mode:
		_draw_proof_diagrams()
		return
	match shot:
		2: _draw_pump_diagram()
		3: _draw_valve_diagram()
		4: _draw_raise_diagram()
		5: _draw_hold_and_return_diagram()

func _draw_foreground() -> void:
	if proof_mode:
		_draw_proof_foreground()
		return
	match shot:
		0: _draw_studio()
		1: _draw_worksite_callouts()
		2: _label("D03 · ĐỘNG CƠ SAA6D107E-1 & BƠM PISTON", "Động cơ 110 kW quay bơm · Đĩa nghiêng đổi lưu lượng")
		3: _label("D04 · TAY TRANG PPC & VAN PHÂN PHỐI CLSS", "Mạch khiển mở con trượt · Gầu cuộn xúc đất")
		4:
			if time < 28.8:
				_label("D05a · CẬN CẢNH XI LANH NÂNG CẦN KÉP", "Dầu cấp vào khoang đáy · F = p · A đẩy ty đi ra")
			else:
				_label("D05b · QUỸ ĐẠO CƠ CẤU ĐA KHỚP PC200-8", "Cần, tay gầu và gầu đất phối hợp quanh chốt")
		5: _label("D06 · GIỮ TẢI, HỒI DẦU & TỔNG KẾT CHUỖI LỰC", "Van về giữa khóa dầu giữ cần · Dầu hồi qua lọc & làm mát")

	if shot >= 1:
		_draw_honesty_badge()

func _draw_honesty_badge() -> void:
	_rect(foreground, Rect2(1038, 36, 834, 44), Color(0.08, 0.17, 0.21, 0.92))
	foreground.draw_rect(Rect2(1038, 36, 834, 44), Color("#4f7586"), false, 2.0)
	_text(foreground, Vector2(1056, 66), "Sơ đồ giản lược · Chi tiết theo số sê-ri và cấu hình máy", 23, IVORY)

func _draw_studio() -> void:
	# Left studio frame with smooth 30fps breathing/bobbing & studio cel animation
	var studio_box := Rect2(76, 54, 680, 964)
	_panel(foreground, studio_box.grow(8))
	if intro != null:
		var cel_idx := mini(41, floori(time * 12.0))
		var source := Rect2((cel_idx % 7) * 520, floori(cel_idx / 7.0) * 737, 520, 737)
		var bob := sin(time * 6.5) * 3.5
		foreground.draw_texture_rect_region(intro, Rect2(76, 54 + bob, 680, 964 - bob), source)
	else:
		# Clean vector studio fallback
		_circle(foreground, Vector2(416, 480 + sin(time * 6.0) * 6.0), 140.0, Color("#f3a257"))
		_text(foreground, Vector2(290, 740), "CAPY BK STUDIO", 36, GOLD)

	# Right side: Animated Studio Blueprint Monitor & Signature Voice Visualizer
	_panel(foreground, Rect2(806, 54, 1038, 964))
	_rect(foreground, Rect2(842, 92, 966, 8), GOLD)
	_text(foreground, Vector2(842, 152), "CAPY BK   ·   TẬP 02   ·   KOMATSU PC200-8", 30, GOLD)
	var pulse := 1.0 + sin(time * 8.0) * 0.04
	_text(foreground, Vector2(842, 268), "KĨ SƯ ƠIII!", int(88 * pulse), IVORY)
	_text(foreground, Vector2(842, 348), "Giải mã hệ thống thủy lực máy đào PC200-8", 38, RETURN)

	# Animated 5-node hydraulic schematic preview on the studio monitor
	var mon := Rect2(842, 392, 966, 360)
	_rect(foreground, mon, Color("#10232b"))
	foreground.draw_rect(mon, Color("#2f5868"), false, 2.5)
	var nodes := [
		["SAA6D107E-1", "110 kW @ 2000 rpm", Vector2(935, 525), GOLD],
		["Bơm HPV95", "439 L/phút · CLSS", Vector2(1135, 525), PRESSURE],
		["Van PPC & CLSS", "Pilot 3.2 MPa · Bù áp", Vector2(1345, 525), PILOT],
		["Xi lanh Cần/Gầu", "Max 37.3 MPa", Vector2(1555, 525), RETURN],
		["Cơ cấu Cần-Gầu", "Đào & Nâng tải", Vector2(1730, 525), LS]
	]
	for idx in range(nodes.size() - 1):
		var a: Vector2 = nodes[idx][2]
		var b: Vector2 = nodes[idx + 1][2]
		flow_on(foreground, [a + Vector2(68, 0), b - Vector2(68, 0)], nodes[idx][3], true, time * 190.0)
	for idx in range(nodes.size()):
		var item: Array = nodes[idx]
		var center: Vector2 = item[2]
		var col: Color = item[3]
		var active_glow := 0.5 + 0.5 * sin(time * 5.5 - float(idx) * 0.9)
		var card := Rect2(center - Vector2(74, 58), Vector2(148, 116))
		_rect(foreground, card, Color("#1a3542").lightened(active_glow * 0.18))
		foreground.draw_rect(card, col, false, 3.0)
		_text(foreground, center + Vector2(-62, -10), item[0], 19, col)
		_text(foreground, center + Vector2(-62, 24), item[1], 15, IVORY)

	# Animated mini articulated boom-stick-bucket kinematic preview inside monitor lower strip
	var pivot_base := Vector2(1060, 710)
	var b_ang := -0.35 + sin(time * 2.8) * 0.22
	var s_ang := 0.55 + cos(time * 2.8) * 0.35
	var k_ang := -0.4 + sin(time * 5.6) * 0.45
	var p_elbow := pivot_base + Vector2(130, -55).rotated(b_ang)
	var p_wrist := p_elbow + Vector2(45, 95).rotated(b_ang + s_ang)
	var p_tip := p_wrist + Vector2(48, 12).rotated(b_ang + s_ang + k_ang)
	_line(foreground, pivot_base, p_elbow, GOLD, 10.0)
	_line(foreground, p_elbow, p_wrist, PILOT, 8.0)
	_line(foreground, p_wrist, p_tip, PRESSURE, 7.0)
	_circle(foreground, pivot_base, 7.0, IVORY)
	_circle(foreground, p_elbow, 6.0, IVORY)
	_circle(foreground, p_wrist, 5.0, IVORY)
	_text(foreground, Vector2(1265, 705), "Mô hình động học 2D tách lớp · Không biến dạng mesh", 22, GOLD)

	# Live audio waveform bars for Signature "Kĩ Sư Ơiii!" (active throughout 0..4.2s)
	_text(foreground, Vector2(842, 812), "VOICE TRACK · SIGNATURE INTRO: \"KĨ SƯ ƠIIII!\"", 24, GOLD)
	for b in range(36):
		var bx := 842.0 + b * 26.8
		var env := 0.35 + 0.65 * clampf(1.0 - absf(time - 2.4) / 1.5, 0.0, 1.0)
		var bh := (14.0 + 64.0 * absf(sin(time * 14.0 + float(b) * 0.55) * cos(time * 9.0 - float(b) * 0.3))) * env
		var bar_col := GOLD if (time >= 1.25 and time <= 4.1) else RETURN
		_rect(foreground, Rect2(bx, 915.0 - bh, 18.0, bh), bar_col)
	_text(foreground, Vector2(842, 965), "Chuỗi truyền công suất: Động cơ → Bơm → Van CLSS → Xi lanh → Cần", 26, IVORY)

func _draw_worksite_callouts() -> void:
	_label("D02 · CÔNG TRƯỜNG KOMATSU PC200-8", "Tay máy đào nặng hàng tấn lấy sức từ đâu?")
	# Sequential animated callout rings on the PC200-8 synced with the Engineer's pointing gesture
	var upper_node: Node2D = machine.get_node("Upper")
	var boom_node: Node2D = machine.get_node("Upper/Boom")
	var stick_node: Node2D = machine.get_node("Upper/Boom/Stick")
	var callouts := [
		["1. Động cơ SAA6D107E-1", upper_node.to_global(Vector2(-235, -55)), GOLD, 4.4],
		["2. Cụm bơm piston HPV95", upper_node.to_global(Vector2(-150, -35)), PRESSURE, 5.8],
		["3. Van phân phối CLSS", upper_node.to_global(Vector2(-35, -45)), PILOT, 7.2],
		["4. Xi lanh cần · tay gầu · gầu", boom_node.to_global(Vector2(180, -135)), RETURN, 8.4],
	]
	for idx in range(callouts.size()):
		var item: Array = callouts[idx]
		var label_text: String = item[0]
		var world_pt: Vector2 = item[1]
		var col: Color = item[2]
		var t_start: float = item[3]
		var appear := clampf((time - t_start) / 0.45, 0.0, 1.0)
		if appear <= 0.01:
			continue
		var pulse_r := (24.0 + sin(time * 7.0 + float(idx)) * 5.0) * appear
		foreground.draw_arc(world_pt, pulse_r, 0, TAU, 36, col, 4.0, true)
		_circle(foreground, world_pt, 6.0, IVORY)
		var tag_pos := Vector2(560, 210 + idx * 66)
		_line(foreground, tag_pos + Vector2(310, 22), world_pt, Color(col.r, col.g, col.b, 0.75 * appear), 3.0)
		var tag_box := Rect2(tag_pos, Vector2(310, 46))
		_rect(foreground, tag_box, Color(0.08, 0.17, 0.21, 0.92 * appear))
		foreground.draw_rect(tag_box, col, false, 2.5)
		_text(foreground, tag_pos + Vector2(14, 31), label_text, 22, col)

	# Also show live wrist/elbow pin rings on the articulating front attachment
	var elbow_pt := boom_node.to_global(RIG.ELBOW)
	var wrist_pt := stick_node.to_global(RIG.WRIST)
	foreground.draw_arc(elbow_pt, 20.0, 0, TAU, 32, RETURN, 2.5, true)
	foreground.draw_arc(wrist_pt, 18.0, 0, TAU, 32, RETURN, 2.5, true)

func _draw_pump_diagram() -> void:
	var box := Rect2(54, 182, 924, 710)
	_panel(diagram_layer, box)
	_text(diagram_layer, Vector2(88, 236), "1. ĐỘNG CƠ SAA6D107E-1 (110 kW)", 24, GOLD)
	_text(diagram_layer, Vector2(536, 236), "2. BƠM PISTON ĐĨA NGHIÊNG (439 L/p)", 24, PRESSURE)

	# 6-cylinder engine block & crank animation
	var shaft := Vector2(318, 462)
	var shaft_angle := time * 11.0
	_rect(diagram_layer, Rect2(88, 286, 408, 238), Color("#46656e"))
	_rect(diagram_layer, Rect2(104, 304, 376, 198), Color("#223c47"))
	var firing_order: Array[int] = [0, 4, 2, 5, 1, 3]
	for i in range(6):
		var x := 120.0 + i * 58.0
		var phase: float = shaft_angle + float(firing_order[i]) * TAU / 6.0
		var crank_pin := Vector2(x + 20, 456) + Vector2.from_angle(phase) * 15.0
		var lateral := crank_pin.x - (x + 20)
		var piston_pin := Vector2(x + 20, crank_pin.y - sqrt(maxf(100.0, 56.0 * 56.0 - lateral * lateral)))
		_rect(diagram_layer, Rect2(x, 322, 40, 102), Color("#597c84"))
		# Combustion flash at top dead center
		var comb := clampf((352.0 - piston_pin.y) / 14.0, 0.0, 1.0)
		if comb > 0.1:
			_rect(diagram_layer, Rect2(x + 3, 324, 34, 16), Color(1.0, 0.68, 0.22, comb * 0.85))
		_rect(diagram_layer, Rect2(x + 4, piston_pin.y - 15, 32, 22), Color("#c6d6cf"))
		_line(diagram_layer, piston_pin, crank_pin, IVORY, 6.0)
		_circle(diagram_layer, crank_pin, 4.5, GOLD)

	# Drive shaft coupling engine to main hydraulic pump
	_line(diagram_layer, Vector2(118, 462), Vector2(598, 462), GOLD, 12.0)
	for i in range(6):
		var dir := Vector2.from_angle(shaft_angle + i * TAU / 6.0)
		_line(diagram_layer, Vector2(496, 462) + dir * 20, Vector2(496, 462) + dir * 34, GOLD, 5.0)
	_circle(diagram_layer, Vector2(496, 462), 20.0, DARK)
	_circle(diagram_layer, Vector2(496, 462), 9.0, GOLD)

	# Variable swashplate axial piston pump with servo piston & LS feedback
	_rect(diagram_layer, Rect2(566, 304, 366, 226), Color("#3f5963"))
	_rect(diagram_layer, Rect2(582, 320, 334, 194), Color("#1d343e"))
	var tilt := lerpf(0.14, 0.46, 0.5 + 0.5 * sin((time - 10.2) * 1.35))
	var swash_top := Vector2(838.0 - 78.0 * tilt, 336.0)
	var swash_bot := Vector2(838.0 + 78.0 * tilt, 496.0)
	_line(diagram_layer, swash_top, swash_bot, GOLD, 14.0)
	_circle(diagram_layer, Vector2(838, 416), 9.0, IVORY)
	for i in range(5):
		var phase := shaft_angle + i * TAU / 5.0
		var y := 416.0 + sin(phase) * 62.0
		var shoe_x := 838.0 + (y - 416.0) * tilt
		_line(diagram_layer, Vector2(604, y), Vector2(726, y), Color("#2c4a57"), 18.0)
		_rect(diagram_layer, Rect2(shoe_x - 142, y - 6, 58, 13), IVORY)
		_line(diagram_layer, Vector2(shoe_x - 84, y), Vector2(shoe_x, y), Color("#9fb5b5"), 5.0)
		_circle(diagram_layer, Vector2(shoe_x, y), 5.0, GOLD)

	# High-pressure delivery line P and LS servo control line
	flow_on(diagram_layer, [Vector2(868, 365), Vector2(945, 365), Vector2(945, 595), Vector2(560, 595)], PRESSURE, true, time * 175.0)
	flow_on(diagram_layer, [Vector2(560, 642), Vector2(838, 642), Vector2(838, 502)], LS, true, time * 140.0)

	_text(diagram_layer, Vector2(88, 566), "Mô-men xoắn quay trục bơm @ 2000 vòng/phút", 22, GOLD)
	_text(diagram_layer, Vector2(88, 612), "Đỏ · Dầu cao áp P cấp tới van phân phối (Q max = 439 L/phút)", 22, PRESSURE)
	_text(diagram_layer, Vector2(88, 656), "Tím · Tín hiệu LS điều khiển góc đĩa nghiêng α theo nhu cầu tải", 22, LS)
	_rect(diagram_layer, Rect2(88, 694, 854, 168), Color("#152a33"))
	diagram_layer.draw_rect(Rect2(88, 694, 854, 168), GOLD, false, 2.0)
	_text(diagram_layer, Vector2(108, 736), "NGUYÊN LÝ VẬT LÝ BẮT BUỘC:", 23, GOLD)
	_text(diagram_layer, Vector2(108, 778), "• Bơm tạo LƯU LƯỢNG Q (quyết định tốc độ thao tác: v ≈ Q / A).", 22, IVORY)
	_text(diagram_layer, Vector2(108, 820), "• ÁP SUẤT p hình thành do sức cản của tải (đất, trọng lượng cần) & van giới hạn!", 21, RETURN)

	# Leader line to rear engine/pump bay on the PC200-8
	var pump_world: Vector2 = machine.get_node("Upper").to_global(Vector2(-175, -40))
	_line(diagram_layer, Vector2(978, 462), pump_world, GOLD, 3.5)
	diagram_layer.draw_arc(pump_world, 28.0 + sin(time * 6.0) * 4.0, 0, TAU, 36, GOLD, 4.0, true)

func _draw_valve_diagram() -> void:
	var box := Rect2(54, 182, 944, 718)
	_panel(diagram_layer, box)
	_text(diagram_layer, Vector2(88, 236), "3. TAY TRANG PPC (3.2 MPa)", 24, PILOT)
	_text(diagram_layer, Vector2(496, 236), "4. VAN PHÂN PHỐI CLSS & VAN BÙ ÁP", 24, IVORY)

	# Left: Operator PPC Joystick & Pilot Metering Valve
	var base := Vector2(228, 452)
	var handle := base + Vector2(-88.0 * pilot_amount, -132.0)
	_rect(diagram_layer, Rect2(142, 448, 172, 48), Color("#5c717a"))
	_line(diagram_layer, base, handle, DARK, 24.0)
	_line(diagram_layer, base, handle, IVORY, 13.0)
	_circle(diagram_layer, handle, 24.0, DARK)
	_circle(diagram_layer, handle - Vector2(0, 3), 17.0, PILOT)
	_text(diagram_layer, Vector2(118, 302), "Kéo tay trang: %.0f%%" % (pilot_amount * 100.0), 23, GOLD)

	# Right: 6-land CLSS Main Control Valve Spool + Pressure Compensator
	_rect(diagram_layer, Rect2(496, 336, 462, 162), Color("#55727b"))
	_rect(diagram_layer, Rect2(514, 364, 426, 106), DARK)
	var travel := 54.0 * pilot_amount
	for i in range(4):
		var x := 538.0 + i * 88.0 + travel
		_rect(diagram_layer, Rect2(x, 374, 40, 86), Color("#a9bdbc"))
	_line(diagram_layer, Vector2(522 + travel, 417), Vector2(898 + travel, 417), Color("#cad8d7"), 12.0)

	# Return spring on right end of spool
	for s in range(6):
		var sx := 898.0 + travel + float(s) * (38.0 - travel * 0.35) / 6.0
		_line(diagram_layer, Vector2(sx, 392), Vector2(sx + 4, 442), GOLD, 3.5)

	# Flow paths: Pilot (Orange), Main Supply P->A (Red), Return B->T (Blue), Load-Sensing LS (Purple)
	var active := pilot_amount > 0.04
	flow_on(diagram_layer, [Vector2(280, 476), Vector2(392, 476), Vector2(392, 417), Vector2(512, 417)], PILOT, active, time * 165.0)
	flow_on(diagram_layer, [Vector2(560, 560), Vector2(648, 560), Vector2(648, 470), Vector2(685, 336), Vector2(685, 285)], PRESSURE, active, time * 195.0)
	flow_on(diagram_layer, [Vector2(815, 285), Vector2(815, 336), Vector2(845, 470), Vector2(845, 560), Vector2(930, 560)], RETURN, active, time * 155.0)
	flow_on(diagram_layer, [Vector2(685, 315), Vector2(445, 315), Vector2(445, 595), Vector2(555, 595)], LS, active, time * 145.0)

	_text(diagram_layer, Vector2(88, 646), "Cam · Mạch khiển PPC (3.2 MPa) đẩy con trượt chính tỉ lệ với tay người lái", 22, PILOT)
	_text(diagram_layer, Vector2(88, 690), "Đỏ · Đường cấp P → A vào xi lanh    |    Xanh · Đường hồi B → T về thùng", 22, PRESSURE)
	_text(diagram_layer, Vector2(88, 734), "Tím · Nhánh cảm nhận tải LS + Van bù áp giữ chia lưu lượng ổn định khi phối hợp", 21, LS)

	# Live status of Stick & Bucket cylinders on the digging machine
	_rect(diagram_layer, Rect2(88, 768, 870, 104), Color("#152a33"))
	diagram_layer.draw_rect(Rect2(88, 768, 870, 104), RETURN, false, 2.0)
	_text(diagram_layer, Vector2(108, 806), "PHỐI HỢP THAO TÁC TRÊN MÁY (CLSS):", 22, GOLD)
	_text(diagram_layer, Vector2(108, 844), "Xi lanh tay gầu thu (L_arm = %.0f)  +  Xi lanh gầu duỗi cuộn đất (L_bkt = %.0f)" % [
		machine.stick_cylinder_length(), machine.bucket_cylinder_length()], 22, IVORY)

	# Leader line from valve cutaway to Bucket & Stick cylinders on the PC200-8
	var stick_node: Node2D = machine.get_node("Upper/Boom/Stick")
	var bkt_cyl_world := stick_node.to_global(machine.bucket_knuckle())
	_line(diagram_layer, Vector2(998, 417), bkt_cyl_world, PILOT, 3.5)
	diagram_layer.draw_arc(bkt_cyl_world, 24.0 + sin(time * 7.0) * 4.0, 0, TAU, 36, PILOT, 3.5, true)

func _draw_raise_diagram() -> void:
	var stroke: float = machine.stroke_ratio()
	var active := time >= 24.2 and time <= RAISE_END
	if time < 28.8:
		# Sub-shot D05a: Large high-detail double-acting cylinder cutaway on the left
		var box := Rect2(54, 182, 740, 718)
		_panel(diagram_layer, box)
		_text(diagram_layer, Vector2(82, 236), "XI LANH NÂNG CẦN KÉP (120 × 85 × 1334 mm)", 24, GOLD)
		var piston: float = 248.0 + 156.0 * stroke
		_rect(diagram_layer, Rect2(118, 326, 468, 128), Color("#7d8f8f"))
		_rect(diagram_layer, Rect2(134, 342, 436, 96), DARK)
		_rect(diagram_layer, Rect2(134, 344, piston - 134, 92), PRESSURE.darkened(0.38))
		_rect(diagram_layer, Rect2(piston, 344, 570 - piston, 92), RETURN.darkened(0.42))
		_rect(diagram_layer, Rect2(piston, 342, 18, 96), IVORY)
		_rect(diagram_layer, Rect2(piston + 18, 378, 290, 24), IVORY)
		_circle(diagram_layer, Vector2(piston + 308, 390), 14, Color("#afc4c2"))
		_rect(diagram_layer, Rect2(568, 326, 18, 52), Color("#7d8f8f"))
		_rect(diagram_layer, Rect2(568, 402, 18, 52), Color("#7d8f8f"))
		_text(diagram_layer, Vector2(134, 312), "Khoang đáy (Cấp P · A_đáy)", 20, PRESSURE)
		_text(diagram_layer, Vector2(418, 312), "Khoang ty (Hồi T · A_ty)", 20, RETURN)

		# Valve, Pump, Tank mini circuit below cylinder
		_rect(diagram_layer, Rect2(246, 558, 118, 76), Color("#667c81"))
		_circle(diagram_layer, Vector2(132, 586), 24, Color("#6f878c"))
		_rect(diagram_layer, Rect2(96, 656, 56, 36), Color("#6f878c"))
		flow_on(diagram_layer, [Vector2(156, 586), Vector2(246, 586), Vector2(384, 586),
			Vector2(384, 498), Vector2(176, 498), Vector2(176, 454)], PRESSURE, active, time * 185.0)
		flow_on(diagram_layer, [Vector2(542, 454), Vector2(542, 536), Vector2(416, 536),
			Vector2(416, 616), Vector2(226, 616), Vector2(226, 674), Vector2(152, 674)], RETURN, active, time * 120.0)
		flow_on(diagram_layer, [Vector2(302, 558), Vector2(302, 524), Vector2(132, 524),
			Vector2(132, 562)], LS, active, time * 150.0)
		_text(diagram_layer, Vector2(84, 742), "Lực đẩy: F = p · A_đáy   |   Tốc độ ty: v ≈ Q / A_đáy", 22, GOLD)
		_text(diagram_layer, Vector2(84, 786), "Áp suất giới hạn mạch công tác: 37.3 MPa (380 kgf/cm²)", 21, IVORY)
		_text(diagram_layer, Vector2(84, 830), "Khoảng cách chốt xi lanh cần: L_boom = %.1f (Hành trình: %.0f%%)" % [
			machine.length_at(machine.get_node("Upper/Boom").rotation), stroke * 100.0], 21, RETURN)
	else:
		# Sub-shot D05b: Compact telemetry HUD at top-center while Characters + Wide Machine are visible
		var hud := Rect2(538, 176, 748, 250)
		_panel(diagram_layer, hud)
		_text(diagram_layer, Vector2(564, 222), "ĐỘNG HỌC CƠ CẤU ĐA KHỚP · HÀNH TRÌNH XI LANH: %.0f%%" % (stroke * 100.0), 22, GOLD)
		var p_bar := 660.0 + 180.0 * stroke
		_rect(diagram_layer, Rect2(568, 248, 420, 48), DARK)
		_rect(diagram_layer, Rect2(572, 252, p_bar - 572, 40), PRESSURE.darkened(0.3))
		_rect(diagram_layer, Rect2(p_bar, 252, 984 - p_bar, 40), RETURN.darkened(0.35))
		_rect(diagram_layer, Rect2(p_bar, 250, 12, 44), IVORY)
		_rect(diagram_layer, Rect2(p_bar + 12, 266, 210, 12), IVORY)
		_text(diagram_layer, Vector2(564, 336), "L_boom = %.1f   |   L_arm = %.1f   |   L_bucket = %.1f" % [
			machine.length_at(machine.get_node("Upper/Boom").rotation),
			machine.stick_cylinder_length(),
			machine.bucket_cylinder_length()
		], 22, RETURN)
		_text(diagram_layer, Vector2(564, 382), "Các khâu giữ nguyên kích thước (scale = 1:1), chỉ quay quanh chốt!", 20, IVORY)

	# Highlight hinge & rod eye on the live machine
	var hinge: Vector2 = machine.to_global(RIG.BOOM_PIN)
	var rod_eye: Vector2 = machine.to_global(machine.eye())
	diagram_layer.draw_arc(hinge, 38, 0, TAU, 48, IVORY, 4, true)
	diagram_layer.draw_arc(rod_eye, 27, 0, TAU, 48, GOLD, 3, true)

func _draw_hold_and_return_diagram() -> void:
	# D06: Top-center animated Return/Cooler/Filter loop + 5-Stage Energy Chain (keeps screen lively while boom holds!)
	var box := Rect2(536, 174, 836, 356)
	_panel(diagram_layer, box)
	_text(diagram_layer, Vector2(566, 222), "GIỮ TẢI (VAN VỀ GIỮA) & MẠCH HỒI - LÀM MÁT - LỌC DẦU", 26, GOLD)

	# Animated return oil loop: Spool Neutral (Locked A/B) -> Oil Cooler -> Return Filter -> Hydraulic Tank
	var r_nodes := [
		["Van khóa giữ cần", "Cổng A/B đóng kín", Vector2(636, 298), GOLD],
		["Két làm mát dầu", "Hạ nhiệt dầu hồi", Vector2(836, 298), RETURN],
		["Lọc dầu hồi", "Giữ hạt mài kim loại", Vector2(1036, 298), RETURN],
		["Thùng dầu thủy lực", "Ổn định & cấp lại", Vector2(1246, 298), LS],
	]
	for i in range(r_nodes.size() - 1):
		var a: Vector2 = r_nodes[i][2]
		var b: Vector2 = r_nodes[i + 1][2]
		flow_on(diagram_layer, [a + Vector2(68, 0), b - Vector2(68, 0)], RETURN, true, time * 160.0)
	for i in range(r_nodes.size()):
		var n: Array = r_nodes[i]
		var c: Vector2 = n[2]
		var col: Color = n[3]
		var card := Rect2(c - Vector2(76, 42), Vector2(152, 84))
		_rect(diagram_layer, card, Color("#17313d"))
		diagram_layer.draw_rect(card, col, false, 2.5)
		_text(diagram_layer, c + Vector2(-64, -6), n[0], 18, col)
		_text(diagram_layer, c + Vector2(-64, 22), n[1], 15, IVORY)

	# 5-stage sweeping summary chain at bottom of panel
	var stages := ["1. Động cơ", "2. Bơm Piston", "3. Van CLSS", "4. Xi lanh", "5. Cần & Gầu"]
	var active_stage := int(floor(fmod(time - 35.8, 5.0)))
	for s in range(stages.size()):
		var sx := 566.0 + s * 158.0
		var is_hi := (s == active_stage)
		var sbox := Rect2(sx, 392, 144, 54)
		_rect(diagram_layer, sbox, Color("#295264") if is_hi else Color("#162c36"))
		diagram_layer.draw_rect(sbox, GOLD if is_hi else Color("#4a6e7d"), false, 3.0 if is_hi else 1.5)
		_text(diagram_layer, Vector2(sx + 12, 426), stages[s], 19, GOLD if is_hi else IVORY)
	_text(diagram_layer, Vector2(562, 496), "Cần giữ nguyên độ cao (L_boom = 318.2) nhờ van khóa kín dầu khoang đáy!", 20, IVORY)

	# Lock icon ring on the boom cylinder bottom chamber
	var rod_eye: Vector2 = machine.to_global(machine.eye())
	diagram_layer.draw_arc(rod_eye, 26.0 + sin(time * 8.0) * 4.0, 0, TAU, 36, GOLD, 4.0, true)

func _draw_proof_diagrams() -> void:
	if time >= 3.0 and time < 9.0:
		# Beat 2: Valve + Cylinder Cutaway
		var stroke: float = machine.stroke_ratio()
		var box := Rect2(54, 178, 720, 340) if time < 6.0 else Rect2(54, 178, 760, 520)
		_panel(diagram_layer, box)
		_text(diagram_layer, Vector2(82, 224), "VAN CLSS MỞ CẤP DẦU → XI LANH ĐẨY CẦN & TAY GẦU", 22, GOLD)
		var piston := 210.0 + 150.0 * stroke
		_rect(diagram_layer, Rect2(110, 266, 430, 96), Color("#7d8f8f"))
		_rect(diagram_layer, Rect2(124, 280, piston - 124, 68), PRESSURE.darkened(0.35))
		_rect(diagram_layer, Rect2(piston, 280, 526 - piston, 68), RETURN.darkened(0.4))
		_rect(diagram_layer, Rect2(piston, 278, 16, 72), IVORY)
		_rect(diagram_layer, Rect2(piston + 16, 304, 240, 20), IVORY)
		flow_on(diagram_layer, [Vector2(110, 440), Vector2(260, 440), Vector2(260, 362)], PRESSURE, true, time * 190.0)
		flow_on(diagram_layer, [Vector2(490, 362), Vector2(490, 440), Vector2(680, 440)], RETURN, true, time * 150.0)
		_text(diagram_layer, Vector2(110, 488), "F = p · A_đáy  |  L_boom = %.1f  |  L_arm = %.1f" % [
			machine.length_at(machine.get_node("Upper/Boom").rotation), machine.stick_cylinder_length()
		], 22, IVORY)
		if time >= 6.0:
			_text(diagram_layer, Vector2(110, 544), "CẬN CẢNH KHỚP CHỐT & XI LANH (6.0s – 9.0s):", 22, GOLD)
			_text(diagram_layer, Vector2(110, 586), "• Chốt cần (BOOM_PIN), chốt khuỷu (ELBOW), chốt cổ tay (WRIST)", 20, RETURN)
			_text(diagram_layer, Vector2(110, 624), "• Ty xi lanh trượt thẳng trong vỏ (Overlap > 9 đv, Scale = 1:1)", 20, IVORY)
	elif time >= 9.0 and time < 13.0:
		# Beat 3: Soil Scoop & Multi-Joint Digging HUD
		var hud := Rect2(536, 176, 740, 210)
		_panel(diagram_layer, hud)
		_text(diagram_layer, Vector2(564, 222), "BEAT 3 · XI LANH GẦU DUỖI → GẦU CUỘN XÚC ĐẤT & NÂNG TẢI", 21, GOLD)
		_text(diagram_layer, Vector2(564, 272), "L_bucket = %.1f  |  L_arm = %.1f  |  L_boom = %.1f" % [
			machine.bucket_cylinder_length(), machine.stick_cylinder_length(),
			machine.length_at(machine.get_node("Upper/Boom").rotation)
		], 22, RETURN)
		_text(diagram_layer, Vector2(564, 322), "Đất bị xén tại mũi gầu, hạt đất rơi theo trọng trường g và bụi bốc lên!", 20, IVORY)
	elif time >= 13.0:
		# Beat 4: Capy Reacts + Synchronized Hydraulic Power Chain Highlight
		_draw_hold_and_return_diagram()

func _draw_proof_foreground() -> void:
	if time < 3.0:
		_label("V3 PROOF · BEAT 1 (0–3s)", "Máy nổ chờ tại công trường · Capy hỏi anh kỹ sư")
	elif time < 6.0:
		_label("V3 PROOF · BEAT 2a (3–6s)", "Kéo tay trang PPC → Van mở dầu → Cần & tay gầu chuyển động")
	elif time < 9.0:
		_label("V3 PROOF · BEAT 2b (6–9s)", "Cắt cảnh cận: Xi lanh, đường dầu và chốt khớp cơ khí")
	elif time < 13.0:
		_label("V3 PROOF · BEAT 3 (9–13s)", "Gầu cuộn xúc đất có phản ứng đất rơi & nâng gầu đầy tải")
	else:
		_label("V3 PROOF · BEAT 4 (13–16s)", "Capy hiểu bài (\"Àaa!\") · Sơ đồ chuỗi thủy lực sáng đồng bộ")
	_draw_honesty_badge()

func flow_on(layer: Node2D, points: Array, hue: Color, running: bool, phase_val: float) -> void:
	var distances := PackedFloat32Array([0.0])
	for i in range(1, points.size()):
		var a: Vector2 = points[i - 1]
		var b: Vector2 = points[i]
		distances.append(distances[-1] + a.distance_to(b))
		_line(layer, a, b, hue.darkened(0.42) if running else IDLE, 9.0)
	if not running or distances[-1] <= 1.0:
		return
	var count := maxi(1, floori(distances[-1] / 85.0))
	for j in range(count):
		var pos_on_line := fposmod(phase_val + j * distances[-1] / count, distances[-1])
		for i in range(1, points.size()):
			if pos_on_line <= distances[i]:
				var a: Vector2 = points[i - 1]
				var b: Vector2 = points[i]
				var u := a.direction_to(b)
				var tip := a + u * (pos_on_line - distances[i - 1])
				layer.draw_colored_polygon(PackedVector2Array([
					tip + u * 9.5,
					tip - u * 8.5 + u.orthogonal() * 6.5,
					tip - u * 8.5 - u.orthogonal() * 6.5
				]), hue)
				break

func _verify() -> void:
	# 1. Verify full 42s sequence (1260 frames)
	proof_mode = false
	active_length = LENGTH
	animator.play("sequence")
	animator.pause()
	var last_extension := -1.0
	for frame in range(1260):
		seek(float(frame) / 30.0)
		var extension: float = machine.stroke_ratio()
		if not machine.verify_pose() or not characters.verify_characters() or extension + 0.00001 < last_extension:
			push_error("Rig/character geometry failed in 42s sequence at frame %d" % frame)
			get_tree().quit(1)
			return
		if ((frame <= 735 and absf(extension) > 0.00001)
				or (frame >= 1059 and absf(extension - 1.0) > 0.00001)):
			push_error("Hold state failed in 42s sequence at frame %d" % frame)
			get_tree().quit(1)
			return
		last_extension = extension

	# 2. Verify 16s V3 proof sequence (480 frames)
	proof_mode = true
	active_length = PROOF_LENGTH
	animator.play("proof_16s")
	animator.pause()
	for frame in range(480):
		seek(float(frame) / 30.0)
		if not machine.verify_pose() or not characters.verify_characters():
			push_error("Rig/character geometry failed in 16s proof at frame %d" % frame)
			get_tree().quit(1)
			return

	print("QA PASS: 1260 sequence poses + 480 V3 proof poses verified!")
	print("Boom ram pin distance: %.2f → %.2f illustration units" % [machine.length_at(RIG.LOWER), machine.length_at(RIG.UPPER)])
	print("Stick ram pin distance: %.2f → %.2f illustration units" % [
		RIG.ARM_BASE.distance_to(RIG.ELBOW + RIG.STICK_EAR.rotated(RIG.STICK_CROWD)),
		RIG.ARM_BASE.distance_to(RIG.ELBOW + RIG.STICK_EAR.rotated(RIG.STICK_REACH))
	])
	get_tree().quit()
