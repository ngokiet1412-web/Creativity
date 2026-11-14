@tool
extends "res://full/full_base.gd"
## SC10 - Dầu hồi: lọc và làm mát (concept circuit).
@onready var rc = $Return
@export var flow := 1.0

func setup() -> void:
	callouts = [
		["Một đường hồi minh họa — không phải mọi dòng đều đi qua cùng một thứ tự", "NGUYÊN LÝ", Vector2(-300, 220), Vector2(-420, 160), M("ks.s") + 3.0, M("end")],
	]

func update(time: float) -> void:
	rc.travel = integrate(func(s): return sample(".:flow", s), time) * 90.0
	rc.fan = time * 7.0
	rc.caught = clampf((time - M("ks.s")) / 12.0, 0.0, 1.0)

func draw_extra_hud(h: Node2D) -> void:
	var k = clampf((t - M("fuel.s")) / 0.4, 0, 1) * clampf((M("roles.s") + 0.2 - t) / 0.4, 0, 1)
	if k > 0.0:
		var r = Rect2(560, 760, 800, 110)
		h.draw_rect(r, Color(0.05, 0.08, 0.13, 0.92 * k))
		h.draw_rect(Rect2(r.position, Vector2(6, r.size.y)), Color(1, 0.4, 0.3, k))
		h.draw_string(bold, r.position + Vector2(30, 66), "Dầu thủy lực ≠ nhiên liệu đốt trong xi lanh", HORIZONTAL_ALIGNMENT_LEFT, -1, 34, Color(1, 1, 1, k))
	var cards = [["Truyền năng lượng", Kit.RED], ["Bôi trơn", Color(0.9, 0.8, 0.4)], ["Tản nhiệt", Color(0.55, 0.85, 1.0)], ["→ Độ sạch & nhiệt độ quan trọng", Color(0.5, 0.95, 0.6)]]
	var x = 290.0
	for i in cards.size():
		var a = clampf((t - M("roles.s") - i * 1.1) / 0.4, 0, 1)
		if a <= 0.0:
			continue
		var w = bold.get_string_size(cards[i][0], HORIZONTAL_ALIGNMENT_LEFT, -1, 28).x + 40
		h.draw_rect(Rect2(x, 790, w, 70), Color(0.05, 0.08, 0.13, 0.92 * a))
		h.draw_rect(Rect2(x, 790, w, 5), Color(cards[i][1], a))
		h.draw_string(bold, Vector2(x + 20, 837), cards[i][0], HORIZONTAL_ALIGNMENT_LEFT, -1, 28, Color(1, 1, 1, a))
		x += w + 16
