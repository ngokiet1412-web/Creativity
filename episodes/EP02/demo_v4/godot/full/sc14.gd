@tool
extends "res://full/full_base.gd"
## SC14 - Kết và kéo sang tập 3. Pull back from the system map into the studio
## monitor; branches light up as Capy sums up; end card.

@onready var studio = $Studio
@onready var smap = $World/Map

func setup() -> void:
	callouts = []

func update(time: float) -> void:
	studio.set_state(time, mouth("CAPY"), mouth("KS"), speaking("KS", time) > 0.0)
	studio.camera(cam)
	smap.chain_travel = time * 120.0
	if rig:
		rig.housing_alpha = 0.35
	show_chip = false
	exhaust_load = 0.2

func _draw_hud() -> void:
	var k = clampf((t - M("bye.s")) / 0.5, 0, 1)
	if k <= 0.0:
		return
	var h := hud
	var r = Rect2(550, 215, 820, 332)
	h.draw_rect(r, Color(0.05, 0.08, 0.13, 0.94 * k))
	h.draw_rect(Rect2(r.position, Vector2(r.size.x, 6)), Color(1, 0.78, 0.25, k))
	h.draw_string(bold, r.position + Vector2(40, 91), "KĨ SƯ ƠIII! · TẬP 3", HORIZONTAL_ALIGNMENT_LEFT, -1, 42, Color(1, 0.85, 0.4, k))
	h.draw_string(bold, r.position + Vector2(40, 173), "CLSS điều khiển bơm thế nào?", HORIZONTAL_ALIGNMENT_LEFT, -1, 39, Color(1, 1, 1, k))
	h.draw_string(font, r.position + Vector2(40, 242), "Vì sao máy có lúc bị ì?", HORIZONTAL_ALIGNMENT_LEFT, -1, 34, Color(0.85, 0.9, 0.95, k))
