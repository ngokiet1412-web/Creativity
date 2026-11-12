extends Node2D
## Side-view rig. Distances are illustration units, not factory dimensions.

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
const ARM_BASE = Vector2(179.06, -161.33)
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
var atlas: ImageTexture

func _ready() -> void:
	var image := Image.load_from_file(ProjectSettings.globalize_path("res://art/pc200-parts.png"))
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
	pose(0.0)

func pose(amount: float) -> void:
	progress = clampf(amount, 0.0, 1.0)
	boom.rotation = lerpf(LOWER, UPPER, progress)
	_update_ram(near_ram, RAM_BASE, eye())
	# Parallel second cylinder projected behind the near cylinder.
	var offset := Vector2(-17, -16)
	_update_ram(far_ram, RAM_BASE + offset, eye() + offset)

func eye() -> Vector2:
	return BOOM_PIN + RAM_EYE.rotated(boom.rotation)

func length_at(angle: float) -> float:
	return RAM_BASE.distance_to(BOOM_PIN + RAM_EYE.rotated(angle))

func stroke_ratio() -> float:
	return inverse_lerp(length_at(LOWER), length_at(UPPER), length_at(boom.rotation))

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

func _sprite(layer: Node2D, source: Rect2, origin: Vector2, destination: Vector2,
		magnification: float, angle := 0.0, tint := Color.WHITE) -> void:
	layer.draw_set_transform(destination, angle, Vector2.ONE * magnification)
	layer.draw_texture_rect_region(atlas, Rect2(source.position - origin, source.size), source, tint, false, true)
	layer.draw_set_transform(Vector2.ZERO)

func _draw_track() -> void:
	var layer: Node2D = $Track
	var source := Rect2(25, 691, 960, 293)
	_sprite(layer, source, source.position, Vector2(-415, 84), .55, 0.0, Color("#8a7a64"))
	_sprite(layer, source, source.position, Vector2(-397, 93), .55)

func _draw_upper() -> void:
	var layer: Node2D = $Upper
	_sprite(layer, Rect2(64, 111, 708, 465), Vector2(725, 476), BOOM_PIN, .65)
	_form(layer, [Vector2(9, 67), Vector2(41, 69), Vector2(61, 100), Vector2(62, 128),
		Vector2(36, 135), Vector2(21, 114)], Color("#b97f30"), 3.0)
	layer.draw_line(Vector2(13, 70), Vector2(39, 73), Color("#fbc665"), 3.0, true)
	layer.draw_rect(Rect2(-248, 3, 95, 28), Color("#433529"))
	layer.draw_string(ThemeDB.fallback_font, Vector2(-243, 24), "PC200-8",
		HORIZONTAL_ALIGNMENT_LEFT, -1, 19, Color("#ffdf91"))

func _draw_boom() -> void:
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
	var hose := PackedVector2Array([Vector2(1, -16), Vector2(31, -52), Vector2(67, -96),
		Vector2(100, -122), Vector2(138, -139), Vector2(182, -152), Vector2(223, -162),
		Vector2(274, -171), Vector2(308, -171)])
	boom.draw_polyline(hose, Color("#3e3025"), 6, true)
	boom.draw_polyline(hose, Color("#6e5943"), 2, true)
	for i in [2, 4, 6]:
		boom.draw_line(hose[i] - Vector2(2, 5), hose[i] + Vector2(2, 5), Color("#a58f6d"), 4, true)
	_pin(boom, Vector2.ZERO, 10)
	# Passive arm actuator. Both anchors follow their owning links.
	var arm_eye := ELBOW + Vector2(32, 73).rotated(stick.rotation)
	_draw_cylinder_between(boom, ARM_BASE, arm_eye, 132, 111, 8, STEEL)

func _draw_stick() -> void:
	var axis := Vector2(1237, 640) - Vector2(1138, 353)
	_sprite(stick, Rect2(1098, 314, 178, 365), Vector2(1138, 353), Vector2.ZERO,
		WRIST.length()/axis.length(), WRIST.angle()-axis.angle())
	_pin(stick, Vector2.ZERO, 11)
	_pin(stick, Vector2(32, 73), 8)
	# Bucket assembly stays parked relative to the stick during this lift.
	_draw_cylinder_between(stick, Vector2(19, 48), Vector2(81, 205), 120, 90, 6, STEEL)
	stick.draw_line(Vector2(81, 205), WRIST + Vector2(23, -8).rotated(bucket.rotation), Color("#59432f"), 14, true)
	stick.draw_line(Vector2(81, 205), WRIST + Vector2(23, -8).rotated(bucket.rotation), Color("#c89a52"), 7, true)
	_pin(stick, Vector2(81, 205), 7)

func _draw_bucket() -> void:
	_sprite(bucket, Rect2(1025, 682, 444, 313), Vector2(1112, 726), Vector2.ZERO, .375)
	_form(bucket, [Vector2(-6, 1), Vector2(11, -16), Vector2(29, -17),
		Vector2(38, 0), Vector2(28, 12), Vector2(8, 13)], Color("#a37846"), 2.0)
	_pin(bucket, Vector2.ZERO, 7)
	_pin(bucket, Vector2(23, -8), 6)

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
	var length: float = layer.get_meta("pin_distance")
	var color := Color("#6c6c64") if far else Color("#b5853c")
	_draw_cylinder_between(layer, Vector2.ZERO, Vector2(length, 0), BARREL_LENGTH, ROD_LENGTH, 10, color)

func verify_pose() -> bool:
	var distance := length_at(boom.rotation)
	var rod_inside := BARREL_LENGTH - (distance - ROD_LENGTH)
	var endpoint := near_ram.position + Vector2(distance, 0).rotated(near_ram.rotation)
	var far_distance: float = far_ram.get_meta("pin_distance")
	var bucket_pin := stick.to_global(WRIST)
	return (distance > BARREL_LENGTH + 4 and rod_inside > 9 and rod_inside < BARREL_LENGTH
		and endpoint.distance_to(eye()) < 0.01 and absf(far_distance - distance) < 0.01
		and bucket.global_position.distance_to(bucket_pin) < 0.01 and boom.scale == Vector2.ONE
		and stick.scale == Vector2.ONE and bucket.scale == Vector2.ONE)
