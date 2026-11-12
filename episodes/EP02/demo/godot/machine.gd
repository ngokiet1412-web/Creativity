extends Node2D
## Side-view multi-joint PC200-8 rig. Distances are illustration units, not factory dimensions.
## Rigid links (Upper, Boom, Stick, Bucket, Cylinders) maintain scale == Vector2.ONE at all times.

const INK = Color("#272a34")
const STEEL = Color("#a3a4a0")
const BOOM_PIN = Vector2(25, 47)
const ELBOW = Vector2(329, -164)
const WRIST = Vector2(88, 255)
const RAM_BASE = Vector2(47, 120)
const RAM_EYE = Vector2(247.05, -113.27)
const BARREL_LENGTH = 233.0
const ROD_LENGTH = 176.0
const LOWER = 0.04
const UPPER = -0.41

# Stick (arm) cylinder constants on Boom -> Stick
const ARM_BASE = Vector2(179.06, -161.33)
const STICK_EAR = Vector2(32, 73)
const BARREL_STICK = 132.0
const ROD_STICK = 111.0
const STICK_REACH = -0.34
const STICK_CROWD = 0.34

# Bucket cylinder & 4-bar linkage constants on Stick -> Bucket
const BUCKET_RAM_BASE = Vector2(19, 48)
const BUCKET_EAR = Vector2(23, -8)
const BARREL_BUCKET = 120.0
const ROD_BUCKET = 90.0
const BUCKET_OPEN = 0.34
const BUCKET_CURL = -0.44

const BOOM_CLIP = [Vector2(835, 444), Vector2(829, 301), Vector2(996, 117),
	Vector2(1180, 59), Vector2(1430, 38), Vector2(1517, 38), Vector2(1517, 143),
	Vector2(1370, 163), Vector2(1354, 226), Vector2(1210, 266), Vector2(1094, 295),
	Vector2(990, 399), Vector2(941, 445)]

@onready var boom: Node2D = $Upper/Boom
@onready var stick: Node2D = $Upper/Boom/Stick
@onready var bucket: Node2D = $Upper/Boom/Stick/Bucket
@onready var near_ram: Node2D = $Upper/BoomRamNear
@onready var far_ram: Node2D = $Upper/BoomRamFar

var progress: float = 0.0
var stick_progress: float = 0.5
var bucket_progress: float = 0.5
var anim_time: float = 0.0
var scoop_progress: float = 0.0
var show_pins_overlay: bool = false
var highlight_part: String = ""
var atlas: ImageTexture

func _ready() -> void:
	var path := ProjectSettings.globalize_path("res://art/pc200-parts.png")
	if FileAccess.file_exists(path):
		var image := Image.load_from_file(path)
		if image != null:
			atlas = ImageTexture.create_from_image(image)
	$Track.draw.connect(_draw_track)
	$Upper.draw.connect(_draw_upper)
	boom.draw.connect(_draw_boom)
	stick.draw.connect(_draw_stick)
	bucket.draw.connect(_draw_bucket)
	near_ram.draw.connect(_draw_ram.bind(near_ram, false))
	far_ram.draw.connect(_draw_ram.bind(far_ram, true))
	boom.position = BOOM_PIN
	stick.position = ELBOW
	bucket.position = WRIST
	pose_full(0.0, 0.5, 0.5, 0.0, 0.0)

func pose(amount: float) -> void:
	pose_full(amount, stick_progress, bucket_progress, anim_time, scoop_progress)

func pose_full(boom_amt: float, stick_amt: float, bucket_amt: float, time_sec: float = 0.0, scoop_amt: float = -1.0) -> void:
	progress = clampf(boom_amt, 0.0, 1.0)
	stick_progress = clampf(stick_amt, 0.0, 1.0)
	bucket_progress = clampf(bucket_amt, 0.0, 1.0)
	anim_time = time_sec
	if scoop_amt >= 0.0:
		scoop_progress = clampf(scoop_amt, 0.0, 1.0)
	else:
		scoop_progress = clampf((bucket_progress - 0.35) / 0.65, 0.0, 1.0)
	boom.rotation = lerpf(LOWER, UPPER, progress)
	stick.rotation = lerpf(STICK_REACH, STICK_CROWD, stick_progress)
	bucket.rotation = lerpf(BUCKET_OPEN, BUCKET_CURL, bucket_progress)
	_update_ram(near_ram, RAM_BASE, eye())
	var offset := Vector2(-17, -16)
	_update_ram(far_ram, RAM_BASE + offset, eye() + offset)
	$Track.queue_redraw()
	$Upper.queue_redraw()
	boom.queue_redraw()
	stick.queue_redraw()
	bucket.queue_redraw()
	queue_redraw()

func eye() -> Vector2:
	return BOOM_PIN + RAM_EYE.rotated(boom.rotation)

func arm_eye() -> Vector2:
	return ELBOW + STICK_EAR.rotated(stick.rotation)

func bucket_knuckle() -> Vector2:
	var arc_angle := (bucket_progress - 0.5) * 0.92
	return WRIST + Vector2(-22.0, -18.0) + Vector2(15.0, -32.0).rotated(arc_angle)

func length_at(angle: float) -> float:
	return RAM_BASE.distance_to(BOOM_PIN + RAM_EYE.rotated(angle))

func stick_cylinder_length() -> float:
	return ARM_BASE.distance_to(arm_eye())

func bucket_cylinder_length() -> float:
	return BUCKET_RAM_BASE.distance_to(bucket_knuckle())

func stroke_ratio() -> float:
	return inverse_lerp(length_at(LOWER), length_at(UPPER), length_at(boom.rotation))

func stick_stroke_ratio() -> float:
	var l_min := ARM_BASE.distance_to(ELBOW + STICK_EAR.rotated(STICK_CROWD))
	var l_max := ARM_BASE.distance_to(ELBOW + STICK_EAR.rotated(STICK_REACH))
	return clampf(inverse_lerp(l_min, l_max, stick_cylinder_length()), 0.0, 1.0)

func bucket_stroke_ratio() -> float:
	var k_min := WRIST + Vector2(-22.0, -18.0) + Vector2(15.0, -32.0).rotated(-0.46)
	var k_max := WRIST + Vector2(-22.0, -18.0) + Vector2(15.0, -32.0).rotated(0.46)
	return clampf(inverse_lerp(BUCKET_RAM_BASE.distance_to(k_min), BUCKET_RAM_BASE.distance_to(k_max), bucket_cylinder_length()), 0.0, 1.0)

func _update_ram(ram: Node2D, start: Vector2, end: Vector2) -> void:
	ram.position = start
	ram.rotation = start.angle_to_point(end)
	ram.set_meta("pin_distance", start.distance_to(end))
	ram.queue_redraw()

func _form(layer: Node2D, points: Array, fill: Color, width := 5.0) -> void:
	var vertices := PackedVector2Array(points)
	layer.draw_colored_polygon(vertices, fill)
	vertices.append(vertices[0])
	layer.draw_polyline(vertices, INK, width, true)

func _pin(layer: Node2D, p: Vector2, r: float) -> void:
	layer.draw_circle(p, r + 2.0, Color("#302621"), true, -1, true)
	layer.draw_circle(p, r, Color("#7f7868"), true, -1, true)
	layer.draw_circle(p - Vector2(1, 1.5), r * .73, Color("#aea596"), true, -1, true)
	layer.draw_circle(p + Vector2(1, 2), r * .42, Color("#625e57"), true, -1, true)
	layer.draw_arc(p, r * .79, 3.65, 5.65, 18, Color("#e3d4a8"), 1.5, true)
	if show_pins_overlay:
		layer.draw_circle(p, r + 6.0, Color(0.15, 0.95, 0.98, 0.85), false, 2.0, true)
		layer.draw_line(p - Vector2(r + 9.0, 0), p + Vector2(r + 9.0, 0), Color("#26f7fd"), 1.6, true)
		layer.draw_line(p - Vector2(0, r + 9.0), p + Vector2(0, r + 9.0), Color("#26f7fd"), 1.6, true)

func _sprite(layer: Node2D, source: Rect2, origin: Vector2, destination: Vector2,
		magnification: float, angle := 0.0, tint := Color.WHITE) -> void:
	if atlas == null:
		return
	layer.draw_set_transform(destination, angle, Vector2.ONE * magnification)
	layer.draw_texture_rect_region(atlas, Rect2(source.position - origin, source.size), source, tint, false, true)
	layer.draw_set_transform(Vector2.ZERO)

func _draw_track() -> void:
	var layer: Node2D = $Track
	var source := Rect2(25, 691, 960, 293)
	_sprite(layer, source, source.position, Vector2(-415, 84), .55, 0.0, Color("#8a7a64"))
	_sprite(layer, source, source.position, Vector2(-397, 93), .55)
	_draw_dig_mound_and_dirt(layer)

func _draw_dig_mound_and_dirt(layer: Node2D) -> void:
	# Diggable earth trench & soil mound at the bucket work zone
	var carve := scoop_progress * 18.0
	var mound_back := PackedVector2Array([
		Vector2(255, 246), Vector2(315, 212), Vector2(385, 194 + carve * 0.5),
		Vector2(455, 188 + carve), Vector2(525, 198 + carve * 0.4),
		Vector2(590, 224), Vector2(635, 250), Vector2(255, 250)
	])
	layer.draw_colored_polygon(mound_back, Color("#6b4c2e"))
	layer.draw_polyline(mound_back, Color("#352618"), 3.5, true)
	var mound_front := PackedVector2Array([
		Vector2(280, 252), Vector2(345, 225), Vector2(418, 206 + carve * 0.7),
		Vector2(485, 202 + carve * 0.8), Vector2(555, 220), Vector2(615, 252), Vector2(280, 252)
	])
	layer.draw_colored_polygon(mound_front, Color("#87623d"))
	layer.draw_polyline(mound_front, Color("#3c2b1b"), 3.5, true)
	# Pebbles on soil mound
	for pebble in [Vector2(335, 236), Vector2(395, 226), Vector2(465, 228), Vector2(525, 234), Vector2(568, 240)]:
		layer.draw_circle(pebble, 4.5, Color("#523a23"), true, -1, true)
		layer.draw_circle(pebble - Vector2(1, 1), 2.5, Color("#a57d52"), true, -1, true)

	# Gravity-driven falling dirt clods & dust puffs when bucket curls / lifts soil
	var tip_world := bucket.to_global(Vector2(118, 42))
	var tip_local := layer.to_local(tip_world)
	var activity := clampf(scoop_progress * 1.3 - progress * 0.25, 0.0, 1.0)
	if activity > 0.05:
		var g := 390.0
		for i in range(14):
			var phase := fmod(anim_time * 1.55 + float(i) * 0.19, 1.0)
			var vx := -36.0 + float(i % 5) * 19.0 + sin(float(i) * 2.1) * 12.0
			var vy := -42.0 - float(i % 3) * 18.0
			var pos := tip_local + Vector2(vx * phase, vy * phase + 0.5 * g * phase * phase)
			pos.y = minf(pos.y, 244.0)
			var radius := (3.2 + float(i % 3) * 1.6) * (1.0 - phase * 0.35) * activity
			if radius > 0.8:
				layer.draw_circle(pos, radius + 1.2, Color("#2f2115"), true, -1, true)
				layer.draw_circle(pos, radius, Color("#7d5935") if i % 2 == 0 else Color("#9c7248"), true, -1, true)
		# Dust puffs near the dig contact
		for j in range(5):
			var d_phase := fmod(anim_time * 1.1 + float(j) * 0.21, 1.0)
			var dust_pos := Vector2(415.0 + float(j) * 28.0 + d_phase * 22.0, 218.0 - d_phase * 26.0)
			var alpha := (1.0 - d_phase) * 0.42 * activity
			layer.draw_circle(dust_pos, 10.0 + d_phase * 16.0, Color(0.84, 0.72, 0.54, alpha), true, -1, true)

func _draw_upper() -> void:
	var layer: Node2D = $Upper
	# Subtle diesel exhaust puffs from SAA6D107E-1 stack before drawing upper body
	for i in range(4):
		var p := fmod(anim_time * 0.85 + float(i) * 0.25, 1.0)
		var puff_pos := Vector2(-246.0 - p * 34.0 - sin(p * 4.5 + float(i)) * 6.0, -198.0 - p * 54.0)
		var puff_r := 7.0 + p * 16.0
		var puff_a := (1.0 - p) * 0.26
		layer.draw_circle(puff_pos, puff_r, Color(0.28, 0.31, 0.35, puff_a), true, -1, true)
	_sprite(layer, Rect2(64, 111, 708, 465), Vector2(725, 476), BOOM_PIN, .65)
	_form(layer, [Vector2(9, 67), Vector2(41, 69), Vector2(61, 100), Vector2(62, 128),
		Vector2(36, 135), Vector2(21, 114)], Color("#b97f30"), 3.0)
	layer.draw_line(Vector2(13, 70), Vector2(39, 73), Color("#fbc665"), 3.0, true)
	layer.draw_rect(Rect2(-248, 3, 95, 28), Color("#433529"))
	layer.draw_string(ThemeDB.fallback_font, Vector2(-243, 24), "PC200-8",
		HORIZONTAL_ALIGNMENT_LEFT, -1, 19, Color("#ffdf91"))

func _draw_boom() -> void:
	if atlas != null:
		var origin := Vector2(895, 391)
		var axis := Vector2(1471, 84) - origin
		var gain := ELBOW.length() / axis.length()
		var turn := ELBOW.angle() - axis.angle()
		var vertices := PackedVector2Array()
		var uvs := PackedVector2Array()
		for point: Vector2 in BOOM_CLIP:
			vertices.append((point - origin).rotated(turn) * gain)
			uvs.append(point / atlas.get_size())
		boom.draw_polygon(vertices, PackedColorArray([Color.WHITE]), uvs, atlas)
	else:
		_form(boom, [Vector2(-15, 20), Vector2(150, -145), ELBOW + Vector2(0, -20), ELBOW + Vector2(15, 20), Vector2(170, -95), Vector2(20, 30)], Color("#d89b2b"), 4.0)
	# Secondary motion on flexible hydraulic hose bundle along boom
	var flex := sin(anim_time * 5.0) * 1.8 + (stick_progress - 0.5) * 4.0
	var hose := PackedVector2Array([Vector2(1, -16), Vector2(31, -52 + flex * 0.4), Vector2(67, -96 + flex * 0.8),
		Vector2(100, -122 + flex), Vector2(138, -139 + flex * 0.7), Vector2(182, -152 + flex * 0.4), Vector2(223, -162),
		Vector2(274, -171 - flex * 0.5), Vector2(308, -171)])
	boom.draw_polyline(hose, Color("#3e3025"), 6, true)
	boom.draw_polyline(hose, Color("#6e5943"), 2, true)
	for i in [2, 4, 6]:
		boom.draw_line(hose[i] - Vector2(2, 5), hose[i] + Vector2(2, 5), Color("#a58f6d"), 4, true)
	_pin(boom, Vector2.ZERO, 10)
	# Active stick (arm) hydraulic cylinder: both anchors follow their owning rigid links
	var s_eye := arm_eye()
	_draw_cylinder_between(boom, ARM_BASE, s_eye, BARREL_STICK, ROD_STICK, 8, STEEL)
	if show_pins_overlay:
		var mid := (ARM_BASE + s_eye) * 0.5 + Vector2(0, -18)
		boom.draw_string(ThemeDB.fallback_font, mid, "L_arm=%.0f" % stick_cylinder_length(), HORIZONTAL_ALIGNMENT_CENTER, -1, 14, Color("#26f7fd"))

func _draw_stick() -> void:
	var axis := Vector2(1237, 640) - Vector2(1138, 353)
	if atlas != null:
		_sprite(stick, Rect2(1098, 314, 178, 365), Vector2(1138, 353), Vector2.ZERO,
			WRIST.length()/axis.length(), WRIST.angle()-axis.angle())
	else:
		_form(stick, [Vector2(-16, -15), Vector2(38, 68), WRIST + Vector2(12, 0), WRIST - Vector2(14, 0)], Color("#d89b2b"), 4.0)
	_pin(stick, Vector2.ZERO, 11)
	_pin(stick, STICK_EAR, 8)
	# Active bucket hydraulic cylinder & 4-bar linkage driving bucket curl
	var knuckle := bucket_knuckle()
	var bucket_ear_on_stick := WRIST + BUCKET_EAR.rotated(bucket.rotation)
	_draw_cylinder_between(stick, BUCKET_RAM_BASE, knuckle, BARREL_BUCKET, ROD_BUCKET, 6, STEEL)
	# Rocker link (WRIST -> knuckle) and power link (knuckle -> bucket ear)
	stick.draw_line(WRIST, knuckle, Color("#493829"), 11, true)
	stick.draw_line(WRIST, knuckle, Color("#b08442"), 5, true)
	stick.draw_line(knuckle, bucket_ear_on_stick, Color("#59432f"), 14, true)
	stick.draw_line(knuckle, bucket_ear_on_stick, Color("#c89a52"), 7, true)
	_pin(stick, knuckle, 7)
	if show_pins_overlay:
		var mid := (BUCKET_RAM_BASE + knuckle) * 0.5 + Vector2(-58, 0)
		stick.draw_string(ThemeDB.fallback_font, mid, "L_bkt=%.0f" % bucket_cylinder_length(), HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color("#26f7fd"))

func _draw_bucket() -> void:
	if atlas != null:
		_sprite(bucket, Rect2(1025, 682, 444, 313), Vector2(1112, 726), Vector2.ZERO, .375)
	else:
		_form(bucket, [Vector2(0, 0), Vector2(30, -10), Vector2(95, 35), Vector2(45, 78), Vector2(-18, 45)], Color("#7c6244"), 4.0)
	# Dynamic scooped earth heap inside bucket jaws as scoop_progress increases
	if scoop_progress > 0.05:
		var h := scoop_progress * 26.0
		var heap := PackedVector2Array([
			Vector2(28, 30), Vector2(48, 16 - h * 0.65), Vector2(76, 12 - h),
			Vector2(104, 22 - h * 0.55), Vector2(118, 42), Vector2(68, 52)
		])
		bucket.draw_colored_polygon(heap, Color("#7b5633"))
		bucket.draw_polyline(heap, Color("#382616"), 3.0, true)
		bucket.draw_circle(Vector2(66, 24 - h * 0.5), 6.0 * scoop_progress, Color("#9b7147"), true, -1, true)
		bucket.draw_circle(Vector2(88, 28 - h * 0.4), 5.0 * scoop_progress, Color("#5e4024"), true, -1, true)
	_form(bucket, [Vector2(-6, 1), Vector2(11, -16), Vector2(29, -17),
		Vector2(38, 0), Vector2(28, 12), Vector2(8, 13)], Color("#a37846"), 2.0)
	_pin(bucket, Vector2.ZERO, 7)
	_pin(bucket, BUCKET_EAR, 6)

func _draw_cylinder_between(layer: Node2D, a: Vector2, b: Vector2, barrel: float,
		rod: float, width: float, color: Color) -> void:
	var unit := a.direction_to(b)
	var across := unit.orthogonal()
	var sleeve_end := a + unit * barrel
	# The fixed rod continues inside the barrel and is occluded by it.
	var rod_inner := b - unit * rod
	layer.draw_line(rod_inner, b, Color("#332b24"), width + 5, true)
	layer.draw_line(rod_inner, b, Color("#8f999b"), width, true)
	layer.draw_line(rod_inner - across*2, b - across*2, Color("#e6ebe1"), width*.43, true)
	layer.draw_line(a, sleeve_end, Color("#342b26"), width + 16, true)
	layer.draw_line(a, sleeve_end, color, width + 10, true)
	layer.draw_line(a+unit*9-across*4, sleeve_end-unit*13-across*4, color.lightened(.30), 4, true)
	layer.draw_line(a+unit*11+across*4, sleeve_end-unit*11+across*4, color.darkened(.25), 4, true)
	layer.draw_line(sleeve_end - unit*12, sleeve_end + unit*3, Color("#504738"), width+13, true)
	layer.draw_line(sleeve_end - unit*8, sleeve_end - unit*4, Color("#968267"), width+10, true)
	_pin(layer, a, width+1)
	_pin(layer, b, width-1)

func _draw_ram(layer: Node2D, far: bool) -> void:
	var length: float = layer.get_meta("pin_distance", length_at(boom.rotation))
	var color := Color("#6c6c64") if far else Color("#b5853c")
	_draw_cylinder_between(layer, Vector2.ZERO, Vector2(length, 0), BARREL_LENGTH, ROD_LENGTH, 10, color)
	if show_pins_overlay and not far:
		layer.draw_string(ThemeDB.fallback_font, Vector2(length * 0.45, -18), "L_boom=%.0f" % length, HORIZONTAL_ALIGNMENT_CENTER, -1, 14, Color("#26f7fd"))

func verify_pose() -> bool:
	var distance := length_at(boom.rotation)
	var rod_inside := BARREL_LENGTH - (distance - ROD_LENGTH)
	var endpoint := near_ram.position + Vector2(distance, 0).rotated(near_ram.rotation)
	var far_distance: float = far_ram.get_meta("pin_distance")
	var s_len := stick_cylinder_length()
	var s_rod_inside := BARREL_STICK - (s_len - ROD_STICK)
	var b_len := bucket_cylinder_length()
	var b_rod_inside := BARREL_BUCKET - (b_len - ROD_BUCKET)
	var bucket_pin := stick.to_global(WRIST)
	var elbow_pin := boom.to_global(ELBOW)
	return (distance > BARREL_LENGTH + 4 and rod_inside > 9 and rod_inside < BARREL_LENGTH
		and s_len > BARREL_STICK + 4 and s_rod_inside > 9 and s_rod_inside < BARREL_STICK
		and b_len > BARREL_BUCKET + 4 and b_rod_inside > 9 and b_rod_inside < BARREL_BUCKET
		and endpoint.distance_to(eye()) < 0.01 and absf(far_distance - distance) < 0.01
		and stick.global_position.distance_to(elbow_pin) < 0.01
		and bucket.global_position.distance_to(bucket_pin) < 0.01
		and boom.scale == Vector2.ONE and stick.scale == Vector2.ONE and bucket.scale == Vector2.ONE
		and near_ram.scale == Vector2.ONE and far_ram.scale == Vector2.ONE)
