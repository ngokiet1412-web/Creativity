extends Node2D
## Multi-layered 2D character rig for Engineer & Capy BK behind the worksite safety barrier.
## All character part nodes maintain scale == Vector2.ONE (rigid transform + sprite switching only).

const PANEL_OFFSET = Vector2(0.0, 343.0) # Maps panel y=737 to screen y=1080

const REGIONS = {
	"safety_rail":       Rect2(0,   880, 520, 103),
	"eng_torso":         Rect2(0,     0, 245, 205),
	"eng_arm_l":         Rect2(260,   0, 148,  90),
	"eng_arm_r_point":   Rect2(420,   0, 160, 180),
	"eng_arm_r_open":    Rect2(590,   0, 160, 180),
	"eng_head":          Rect2(0,   220, 235, 224),
	"eng_brows":         Rect2(260, 220, 132,  50),
	"eng_eyelids_blink": Rect2(420, 220, 120,  70),
	"eng_eyelids_happy": Rect2(550, 220, 120,  70),
	"eng_mouth_closed":  Rect2(260, 310,  70,  70),
	"eng_mouth_half":    Rect2(340, 310,  70,  70),
	"eng_mouth_open":    Rect2(420, 310,  70,  70),
	"capy_torso":        Rect2(800,   0, 215, 110),
	"capy_paw_l_rail":   Rect2(1030,  0,  94,  70),
	"capy_paw_l_wave":   Rect2(1140,  0,  96, 125),
	"capy_paw_r_rail":   Rect2(1250,  0,  84,  66),
	"capy_head":         Rect2(800, 150, 200, 170),
	"capy_hat":          Rect2(1030,150, 165, 118),
	"capy_brows":        Rect2(1210,150, 110,  50),
	"capy_eyelids_blink":Rect2(1340,150, 120,  70),
	"capy_eyelids_happy":Rect2(1470,150, 120,  70),
	"capy_mouth_closed": Rect2(1030,290,  70,  70),
	"capy_mouth_small":  Rect2(1110,290,  70,  70),
	"capy_mouth_open":   Rect2(1190,290,  70,  70),
}

# Rest pivots in panel coordinates (0..520, 0..737)
const ENG_NECK_PIVOT = Vector2(135.0, 472.0)
const ENG_ARM_R_PIVOT = Vector2(185.0, 500.0)
const CAPY_NECK_PIVOT = Vector2(408.0, 552.0)
const CAPY_PAW_L_PIVOT = Vector2(338.0, 595.0)
const CAPY_HAT_PIVOT = Vector2(422.0, 435.0)

var atlas: ImageTexture

# Scene tree child nodes created deterministically in _ready()
var eng_root: Node2D
var eng_arm_r: Node2D
var eng_torso: Node2D
var eng_head: Node2D
var eng_brows: Node2D
var eng_eyelids: Node2D
var eng_mouth: Node2D
var eng_arm_l: Node2D

var capy_root: Node2D
var capy_torso: Node2D
var capy_paw_l_wave: Node2D
var capy_head: Node2D
var capy_brows: Node2D
var capy_eyelids: Node2D
var capy_mouth: Node2D
var capy_hat: Node2D
var capy_paw_l_rail: Node2D
var capy_paw_r_rail: Node2D

var safety_rail: Node2D

# Live animation state
var eng_mouth_state: String = "closed"
var eng_eye_state: String = "normal"
var capy_mouth_state: String = "closed"
var capy_eye_state: String = "normal"
var capy_waving: bool = false

func _ready() -> void:
	var path := ProjectSettings.globalize_path("res://local/character-layers.png")
	if FileAccess.file_exists(path):
		var img := Image.load_from_file(path)
		if img != null:
			atlas = ImageTexture.create_from_image(img)
	_build_hierarchy()
	apply_performance(0.0, false, false, 0.0, false, false)

func _make_node(parent: Node2D, node_name: String, pos: Vector2, draw_cb: Callable) -> Node2D:
	var n := Node2D.new()
	n.name = node_name
	n.position = pos
	n.draw.connect(draw_cb.bind(n))
	parent.add_child(n)
	return n

func _build_hierarchy() -> void:
	for c in get_children():
		c.queue_free()
	eng_root = _make_node(self, "Engineer", PANEL_OFFSET, _draw_noop)
	eng_arm_r = _make_node(eng_root, "ArmR", ENG_ARM_R_PIVOT, _draw_eng_arm_r)
	eng_torso = _make_node(eng_root, "Torso", Vector2(0, 440), _draw_eng_torso)
	eng_head = _make_node(eng_root, "Head", ENG_NECK_PIVOT, _draw_eng_head)
	eng_brows = _make_node(eng_head, "Brows", Vector2(80, 312) - ENG_NECK_PIVOT, _draw_eng_brows)
	eng_eyelids = _make_node(eng_head, "Eyelids", Vector2(95, 342) - ENG_NECK_PIVOT, _draw_eng_eyelids)
	eng_mouth = _make_node(eng_head, "Mouth", Vector2(145, 398) - ENG_NECK_PIVOT, _draw_eng_mouth)

	capy_root = _make_node(self, "Capy", PANEL_OFFSET, _draw_noop)
	capy_torso = _make_node(capy_root, "Torso", Vector2(290, 535), _draw_capy_torso)
	capy_paw_l_wave = _make_node(capy_root, "PawLWave", CAPY_PAW_L_PIVOT, _draw_capy_paw_l_wave)
	capy_head = _make_node(capy_root, "Head", CAPY_NECK_PIVOT, _draw_capy_head)
	capy_brows = _make_node(capy_head, "Brows", Vector2(360, 425) - CAPY_NECK_PIVOT, _draw_capy_brows)
	capy_eyelids = _make_node(capy_head, "Eyelids", Vector2(348, 442) - CAPY_NECK_PIVOT, _draw_capy_eyelids)
	capy_mouth = _make_node(capy_head, "Mouth", Vector2(355, 485) - CAPY_NECK_PIVOT, _draw_capy_mouth)
	capy_hat = _make_node(capy_head, "Hat", CAPY_HAT_PIVOT - CAPY_NECK_PIVOT, _draw_capy_hat)

	safety_rail = _make_node(self, "SafetyRail", PANEL_OFFSET + Vector2(0, 634), _draw_safety_rail)
	eng_arm_l = _make_node(self, "EngArmL", PANEL_OFFSET + Vector2(20, 572), _draw_eng_arm_l)
	capy_paw_l_rail = _make_node(self, "CapyPawLRail", PANEL_OFFSET + Vector2(292, 584), _draw_capy_paw_l_rail)
	capy_paw_r_rail = _make_node(self, "CapyPawRRail", PANEL_OFFSET + Vector2(416, 588), _draw_capy_paw_r_rail)

func apply_performance(t: float, capy_speaking: bool, eng_speaking: bool,
		eng_point_angle_deg: float, capy_excited: bool, happy_comprehension: bool) -> void:
	if eng_root == null:
		return
	# Breathing & subtle body weight shift (anticipation + reaction)
	var eng_breath := sin(t * 2.4) * 2.2
	var capy_breath := sin(t * 3.1 + 1.1) * 2.6 + (sin(t * 7.5) * 3.0 if capy_excited else 0.0)
	eng_root.position = PANEL_OFFSET + Vector2(0.0, eng_breath)
	capy_root.position = PANEL_OFFSET + Vector2(0.0, capy_breath)

	# Engineer head rotation & pointing arm rotation
	var eng_head_nod := (sin(t * 6.2) * 0.045 if eng_speaking else sin(t * 1.8) * 0.018)
	eng_head.rotation = deg_to_rad(eng_point_angle_deg * 0.25) + eng_head_nod
	var arm_wave := (sin(t * 4.2) * 2.5 if eng_speaking else sin(t * 1.6) * 0.8)
	eng_arm_r.rotation = deg_to_rad(eng_point_angle_deg + arm_wave)
	eng_brows.position = (Vector2(80, 312) - ENG_NECK_PIVOT) + Vector2(0.0, -2.5 if eng_speaking else 0.0)

	# Capy head rotation, secondary hat follow-through, and brow expression
	var capy_tilt_base := -0.05 if capy_speaking or capy_excited else 0.03 * sin(t * 2.0)
	var capy_nod := (sin(t * 7.4) * 0.055 if capy_speaking else 0.0)
	capy_head.rotation = capy_tilt_base + capy_nod
	var hat_bob := sin(t * 6.8 - 0.55) * (2.6 if (capy_speaking or capy_excited) else 1.0)
	capy_hat.position = (CAPY_HAT_PIVOT - CAPY_NECK_PIVOT) + Vector2(0.0, hat_bob)
	capy_hat.rotation = sin(t * 5.2 - 0.4) * (0.028 if (capy_speaking or capy_excited) else 0.008)
	capy_brows.position = (Vector2(360, 425) - CAPY_NECK_PIVOT) + Vector2(0.0, -3.8 if (capy_speaking or capy_excited) else -1.0 * sin(t * 2.2))

	# Capy waving / raising left paw
	capy_waving = capy_speaking or capy_excited or happy_comprehension
	capy_paw_l_wave.visible = capy_waving
	capy_paw_l_rail.visible = not capy_waving
	capy_paw_l_wave.rotation = sin(t * 7.2) * 0.11 if capy_waving else 0.0
	capy_paw_r_rail.position = PANEL_OFFSET + Vector2(416.0, 588.0 + sin(t * 4.5) * (2.2 if capy_waving else 0.6))
	eng_arm_l.position = PANEL_OFFSET + Vector2(20.0, 572.0 + sin(t * 3.2) * (1.8 if eng_speaking else 0.5))

	# Eyelid blinks & happy comprehension arcs
	var eng_blink := fmod(t + 0.7, 3.4) < 0.14
	var capy_blink := fmod(t + 1.9, 2.9) < 0.14
	if happy_comprehension and not eng_speaking:
		eng_eye_state = "happy"
	elif eng_blink:
		eng_eye_state = "blink"
	else:
		eng_eye_state = "normal"

	if happy_comprehension:
		capy_eye_state = "happy"
	elif capy_blink:
		capy_eye_state = "blink"
	else:
		capy_eye_state = "normal"

	# Multi-syllable lip sync visemes
	if eng_speaking:
		var syl := int(floor(t * 8.5)) % 4
		eng_mouth_state = "open" if (syl == 0 or syl == 2) else ("half" if syl == 1 else "closed")
	else:
		eng_mouth_state = "closed"

	if capy_speaking:
		var csyl := int(floor(t * 9.0)) % 4
		capy_mouth_state = "open" if (csyl == 0 or csyl == 2) else ("small" if csyl == 1 else "closed")
	elif capy_excited:
		capy_mouth_state = "open"
	else:
		capy_mouth_state = "closed"

	_queue_all_redraws(self)

func _queue_all_redraws(n: Node) -> void:
	if n is CanvasItem:
		(n as CanvasItem).queue_redraw()
	for c in n.get_children():
		_queue_all_redraws(c)

func _draw_region(node: Node2D, key: String, offset: Vector2) -> void:
	if atlas == null:
		return
	var r: Rect2 = REGIONS[key]
	node.draw_texture_rect_region(atlas, Rect2(offset, r.size), r)

func _draw_noop(_n: Node2D) -> void:
	pass

func _draw_safety_rail(n: Node2D) -> void:
	if atlas != null:
		_draw_region(n, "safety_rail", Vector2.ZERO)
	else:
		n.draw_rect(Rect2(0, 0, 520, 103), Color("#8c6239"))
		n.draw_rect(Rect2(0, 32, 520, 34), Color("#e2b024"))

func _draw_eng_arm_r(n: Node2D) -> void:
	# Pivot is at local (30, 135) inside the 160x180 region
	if atlas != null:
		_draw_region(n, "eng_arm_r_point", Vector2(-30, -135))
	else:
		n.draw_line(Vector2.ZERO, Vector2(95, -90), Color("#9eb8de"), 26.0, true)
		n.draw_circle(Vector2(105, -98), 14.0, Color("#f0a057"))

func _draw_eng_torso(n: Node2D) -> void:
	if atlas != null:
		_draw_region(n, "eng_torso", Vector2.ZERO)
	else:
		n.draw_rect(Rect2(20, 20, 200, 180), Color("#eb7a24"))

func _draw_eng_head(n: Node2D) -> void:
	# ENG_NECK_PIVOT = (135, 472); eng_head top-left in panel is (0, 260) -> offset (-135, -212)
	if atlas != null:
		_draw_region(n, "eng_head", Vector2(-135, -212))
	else:
		n.draw_circle(Vector2(-15, -80), 82.0, Color("#f0a057"))

func _draw_eng_brows(n: Node2D) -> void:
	if atlas != null:
		_draw_region(n, "eng_brows", Vector2.ZERO)

func _draw_eng_eyelids(n: Node2D) -> void:
	if atlas == null or eng_eye_state == "normal":
		return
	var key := "eng_eyelids_blink" if eng_eye_state == "blink" else "eng_eyelids_happy"
	_draw_region(n, key, Vector2.ZERO)

func _draw_eng_mouth(n: Node2D) -> void:
	if atlas != null:
		var key := "eng_mouth_" + eng_mouth_state
		_draw_region(n, key, Vector2.ZERO)
	else:
		n.draw_circle(Vector2(28, 20), 12.0 if eng_mouth_state == "open" else 5.0, Color("#271b16"))

func _draw_eng_arm_l(n: Node2D) -> void:
	if atlas != null:
		_draw_region(n, "eng_arm_l", Vector2.ZERO)
	else:
		n.draw_circle(Vector2(70, 45), 22.0, Color("#f0a057"))

func _draw_capy_torso(n: Node2D) -> void:
	if atlas != null:
		_draw_region(n, "capy_torso", Vector2.ZERO)
	else:
		n.draw_rect(Rect2(10, 15, 190, 95), Color("#f5eae1"))

func _draw_capy_paw_l_wave(n: Node2D) -> void:
	# CAPY_PAW_L_PIVOT = (338, 595); region top-left in panel is (270, 495) -> offset (-68, -100)
	if atlas != null:
		_draw_region(n, "capy_paw_l_wave", Vector2(-68, -100))
	else:
		n.draw_line(Vector2.ZERO, Vector2(-42, -75), Color("#f3a257"), 22.0, true)

func _draw_capy_head(n: Node2D) -> void:
	# CAPY_NECK_PIVOT = (408, 552); region top-left in panel is (308, 405) -> offset (-100, -147)
	if atlas != null:
		_draw_region(n, "capy_head", Vector2(-100, -147))
	else:
		n.draw_circle(Vector2(0, -65), 72.0, Color("#f3a257"))

func _draw_capy_brows(n: Node2D) -> void:
	if atlas != null:
		_draw_region(n, "capy_brows", Vector2.ZERO)

func _draw_capy_eyelids(n: Node2D) -> void:
	if atlas == null or capy_eye_state == "normal":
		return
	var key := "capy_eyelids_blink" if capy_eye_state == "blink" else "capy_eyelids_happy"
	_draw_region(n, key, Vector2.ZERO)

func _draw_capy_mouth(n: Node2D) -> void:
	if atlas != null:
		var key := "capy_mouth_" + capy_mouth_state
		_draw_region(n, key, Vector2.ZERO)
	else:
		n.draw_circle(Vector2(30, 22), 11.0 if capy_mouth_state == "open" else 4.0, Color("#271b16"))

func _draw_capy_hat(n: Node2D) -> void:
	# CAPY_HAT_PIVOT = (422, 435); region top-left in panel is (340, 372) -> offset (-82, -63)
	if atlas != null:
		_draw_region(n, "capy_hat", Vector2(-82, -63))
	else:
		n.draw_arc(Vector2(0, 0), 62.0, PI, TAU, 24, Color("#ffffff"), 22.0, true)

func _draw_capy_paw_l_rail(n: Node2D) -> void:
	if atlas != null:
		_draw_region(n, "capy_paw_l_rail", Vector2.ZERO)
	else:
		n.draw_circle(Vector2(45, 35), 20.0, Color("#f3a257"))

func _draw_capy_paw_r_rail(n: Node2D) -> void:
	if atlas != null:
		_draw_region(n, "capy_paw_r_rail", Vector2.ZERO)
	else:
		n.draw_circle(Vector2(42, 33), 20.0, Color("#f3a257"))

func verify_characters() -> bool:
	if eng_root == null or capy_root == null:
		return false
	return _check_unit_scale(self)

func _check_unit_scale(n: Node) -> bool:
	if n is Node2D:
		if (n as Node2D).scale != Vector2.ONE:
			return false
	for c in n.get_children():
		if not _check_unit_scale(c):
			return false
	return true
