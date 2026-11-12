extends Node2D
## Side-view rig. Distances are illustration units, not factory dimensions.

const INK = Color("#272a34")
const LIGHT = Color("#ffd365")
const YELLOW = Color("#f3ad2a")
const SHADE = Color("#b87020")
const STEEL = Color("#8296a0")
const BOOM_PIN = Vector2(25, 47)
const ELBOW = Vector2(329, -164)
const WRIST = Vector2(88, 255)
const RAM_BASE = Vector2(15, 128)
const RAM_EYE = Vector2(213, -89)
const BARREL_LENGTH = 211.0
const ROD_LENGTH = 176.0
const LOWER = 0.18
const UPPER = -0.39

@onready var boom: Node2D = $Upper/Boom
@onready var stick: Node2D = $Upper/Boom/Stick
@onready var bucket: Node2D = $Upper/Boom/Stick/Bucket
@onready var near_ram: Node2D = $Upper/BoomRamNear
@onready var far_ram: Node2D = $Upper/BoomRamFar

var progress: float = 0.0

func _ready() -> void:
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
	layer.draw_circle(p, r + 3, INK, true, -1, true)
	layer.draw_circle(p, r, STEEL, true, -1, true)
	layer.draw_circle(p, r * 0.46, Color("#dae0d9"), true, -1, true)

func _draw_track() -> void:
	var layer: Node2D = $Track
	layer.draw_circle(Vector2(-317, 176), 62, Color("#2f373b"), true, -1, true)
	layer.draw_circle(Vector2(81, 176), 62, Color("#2f373b"), true, -1, true)
	layer.draw_rect(Rect2(-317, 114, 398, 124), Color("#2f373b"))
	layer.draw_circle(Vector2(-314, 188), 56, INK, true, -1, true)
	layer.draw_circle(Vector2(91, 188), 56, INK, true, -1, true)
	layer.draw_rect(Rect2(-314, 132, 405, 112), INK)
	layer.draw_circle(Vector2(-313, 188), 43, Color("#636568"), true, -1, true)
	layer.draw_circle(Vector2(90, 188), 43, Color("#636568"), true, -1, true)
	layer.draw_rect(Rect2(-313, 145, 403, 86), Color("#636568"))
	for i in range(17):
		for y in [137, 237]:
			var x: int = -317 + i * 25
			layer.draw_line(Vector2(x, y), Vector2(x + 19, y), Color("#a09b85"), 6, true)
	for i in range(9):
		_pin(layer, Vector2(-245 + 41 * i, 206), 13)
	_pin(layer, Vector2(-313, 187), 27)
	_pin(layer, Vector2(90, 187), 27)
	_form(layer, [Vector2(-265, 156), Vector2(51, 156), Vector2(29, 194), Vector2(-248, 194)], Color("#6d593e"))
	for x in [-230, -180, -130, -80, -30, 20]:
		layer.draw_circle(Vector2(x, 174), 4, Color("#b7a58a"), true, -1, true)

func _draw_upper() -> void:
	var layer: Node2D = $Upper
	layer.draw_rect(Rect2(-247, 106, 310, 43), Color("#454a4d"))
	layer.draw_rect(Rect2(-237, 118, 284, 12), STEEL)
	_form(layer, [Vector2(-358, 36), Vector2(-344, -13), Vector2(-281, -43), Vector2(-126, -43),
		Vector2(-99, -136), Vector2(5, -134), Vector2(44, -102), Vector2(62, 93),
		Vector2(13, 118), Vector2(-309, 118), Vector2(-351, 98)], YELLOW)
	_form(layer, [Vector2(-119, -104), Vector2(-96, -149), Vector2(2, -148), Vector2(36, -127),
		Vector2(47, 29), Vector2(-125, 29)], INK)
	_form(layer, [Vector2(-103, -105), Vector2(-84, -134), Vector2(-6, -134), Vector2(20, -118),
		Vector2(33, 14), Vector2(-109, 14)], Color("#446e78"), 3.0)
	layer.draw_line(Vector2(-43, -133), Vector2(-51, 14), INK, 9, true)
	layer.draw_line(Vector2(-96, -84), Vector2(-65, -121), Color("#79a5a4"), 6, true)
	layer.draw_rect(Rect2(-348, 70, 395, 29), SHADE)
	layer.draw_line(Vector2(-330, 28), Vector2(-153, 28), LIGHT, 8, true)
	for i in range(4):
		layer.draw_line(Vector2(-322, -13 + 10 * i), Vector2(-286, -13 + 10 * i), INK, 4, true)
	layer.draw_rect(Rect2(-328, 40, 122, 33), INK)
	layer.draw_string(ThemeDB.fallback_font, Vector2(-316, 64), "PC200-8", HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color("#ffdd86"))
	_pin(layer, BOOM_PIN, 19)

func _draw_boom() -> void:
	_form(boom, [Vector2(-26, -24), Vector2(95, -139), Vector2(238, -191), Vector2(329, -188),
		Vector2(351, -160), Vector2(335, -142), Vector2(250, -134),
		Vector2(239, -89), Vector2(213, -72), Vector2(192, -102), Vector2(129, -71),
		Vector2(22, 27), Vector2(-20, 23)], YELLOW)
	boom.draw_polyline(PackedVector2Array([Vector2(3, -19), Vector2(111, -121), Vector2(246, -173),
		Vector2(310, -173)]), LIGHT, 8, true)
	_pin(boom, Vector2.ZERO, 18)
	_pin(boom, RAM_EYE, 12)
	_pin(boom, ELBOW, 15)
	# Passive arm actuator. Both anchors follow their owning links.
	var arm_eye := ELBOW + Vector2(32, 73).rotated(stick.rotation)
	_draw_cylinder_between(boom, Vector2(184, -161), arm_eye, 132, 111, 7, STEEL)

func _draw_stick() -> void:
	_form(stick, [Vector2(-19, -15), Vector2(25, -17), Vector2(52, 47), Vector2(105, 247),
		Vector2(91, 272), Vector2(67, 264), Vector2(22, 133), Vector2(-17, 35)], YELLOW)
	stick.draw_line(Vector2(17, 10), Vector2(86, 247), LIGHT, 6, true)
	_pin(stick, Vector2.ZERO, 14)
	_pin(stick, WRIST, 12)
	# Bucket assembly stays parked relative to the stick during this lift.
	_draw_cylinder_between(stick, Vector2(19, 48), Vector2(81, 205), 120, 90, 6, STEEL)
	stick.draw_line(Vector2(81, 205), WRIST + Vector2(27, -14).rotated(bucket.rotation), INK, 9, true)
	_pin(stick, Vector2(81, 205), 8)

func _draw_bucket() -> void:
	_form(bucket, [Vector2(-19, -19), Vector2(30, -25), Vector2(67, 3), Vector2(85, 32),
		Vector2(124, 36), Vector2(128, 50), Vector2(108, 55), Vector2(95, 70),
		Vector2(39, 77), Vector2(-2, 61), Vector2(-22, 26)], Color("#aa6e31"))
	bucket.draw_polyline(PackedVector2Array([Vector2(2, 3), Vector2(23, 46),
		Vector2(51, 56), Vector2(99, 50)]), Color("#dca154"), 8, true)
	_pin(bucket, Vector2.ZERO, 11)
	_pin(bucket, Vector2(27, -14), 8)
	_form(bucket, [Vector2(15, 45), Vector2(39, 23), Vector2(60, 31), Vector2(77, 27),
		Vector2(96, 49), Vector2(42, 57)], Color("#80553e"), 3)

func _draw_cylinder_between(layer: Node2D, a: Vector2, b: Vector2, barrel: float,
		rod: float, width: float, color: Color) -> void:
	var unit := a.direction_to(b)
	var sleeve_end := a + unit * barrel
	# The fixed rod continues inside the barrel and is occluded by it.
	layer.draw_line(b - unit * rod, b, INK, width + 5, true)
	layer.draw_line(b - unit * rod, b, Color("#dce6e4"), width, true)
	layer.draw_line(a, sleeve_end, INK, width + 16, true)
	layer.draw_line(a, sleeve_end, color, width + 10, true)
	layer.draw_line(sleeve_end - unit * 8, sleeve_end + unit * 3, INK, width + 13, true)
	_pin(layer, a, width + 1)
	_pin(layer, b, width - 1)

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
