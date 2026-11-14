@tool
extends "res://full/full_base.gd"
## SC14 - Kết và kéo sang tập 3. Pull back from the system map into the studio
## monitor; branches light up as Capy sums up; end card.

@onready var studio = $Studio
@onready var smap = $World/Map

func setup() -> void:
	callouts = []

func update(time: float) -> void:
	studio.set_state(time, speaking("CAPY", time))
	studio.camera(cam)
	smap.chain_travel = time * 120.0
	if rig:
		rig.housing_alpha = 0.35
	show_chip = false
	exhaust_load = 0.2

func draw_extra_hud(h: Node2D) -> void:
	var k = clampf((t - M("bye.s")) / 0.5, 0, 1)
	if k <= 0.0:
		return
	var r = Rect2(1180, 620, 680, 220)
	h.draw_rect(r, Color(0.05, 0.08, 0.13, 0.94 * k))
	h.draw_rect(Rect2(r.position, Vector2(r.size.x, 6)), Color(1, 0.78, 0.25, k))
	h.draw_string(bold, r.position + Vector2(24, 60), "KĨ SƯ ƠIII! · Tập 3", HORIZONTAL_ALIGNMENT_LEFT, -1, 34, Color(1, 0.85, 0.4, k))
	h.draw_string(bold, r.position + Vector2(24, 116), "CLSS điều khiển bơm thế nào?", HORIZONTAL_ALIGNMENT_LEFT, -1, 32, Color(1, 1, 1, k))
	h.draw_string(font, r.position + Vector2(24, 166), "Vì sao máy có lúc bị ì?", HORIZONTAL_ALIGNMENT_LEFT, -1, 28, Color(0.85, 0.9, 0.95, k))
	h.draw_string(font, r.position + Vector2(24, 204), "Minh họa nguyên lý — chi tiết theo serial và cấu hình máy.", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color(0.75, 0.8, 0.85, k))
