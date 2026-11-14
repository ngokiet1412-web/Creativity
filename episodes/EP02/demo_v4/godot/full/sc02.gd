@tool
extends "res://full/full_base.gd"
## SC02 - Vẽ bản đồ cả hệ thống: x-ray of the stopped machine, components
## light up in order, then the energy chain engine -> pump -> valve -> actuator.

@onready var smap = $World/Map

func setup() -> void:
	callouts = [
		["Vị trí các bộ phận: minh họa tương đối, không phải bản vẽ bố trí của hãng", "NGUYÊN LÝ", Vector2(-150, 160), Vector2(-500, 120), M("ks.s") + 1.0, M("end")],
	]

func update(time: float) -> void:
	if rig:
		rig.housing_alpha = 1.0 - 0.7 * xray
	smap.chain_travel = time * 120.0
	exhaust_load = 0.25

func draw_extra_hud(h: Node2D) -> void:
	var k = clampf((t - M("chain.s")) / 0.4, 0, 1)
	if k <= 0.0:
		return
	var steps = ["Động cơ quay bơm", "Bơm đưa dầu vào hệ thống", "Van điều khiển dòng dầu", "Xi lanh / mô tơ tạo chuyển động"]
	var x = 110.0
	for i in steps.size():
		var a = clampf((t - M("chain.s") - i * 1.6) / 0.4, 0, 1) * k
		if a <= 0.0:
			continue
		var w = bold.get_string_size(steps[i], HORIZONTAL_ALIGNMENT_LEFT, -1, 20).x + 26
		h.draw_rect(Rect2(x, 880, w, 44), Color(0.05, 0.08, 0.13, 0.9 * a))
		h.draw_rect(Rect2(x, 880, w, 4), Color(Kit.RED, a) if i > 0 else Color(0.7, 0.75, 0.8, a))
		h.draw_string(bold, Vector2(x + 13, 910), steps[i], HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color(1, 1, 1, a))
		x += w + 18
		if i < steps.size() - 1:
			h.draw_string(bold, Vector2(x - 14, 910), "→", HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Color(1, 0.8, 0.3, a))
			x += 14
