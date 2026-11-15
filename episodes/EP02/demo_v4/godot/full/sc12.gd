@tool
extends "res://full/full_base.gd"
## SC12 - Điện tử có tham gia không? Concept block diagram.
@onready var el = $Elec

func setup() -> void:
	callouts = [
		["Sơ đồ khối khái niệm — không phải sơ đồ dây theo serial", "NGUYÊN LÝ", Vector2(-300, 340), Vector2(-260, 120), M("ks.s"), M("end")],
		["LS / PC / EPC: đầu mối cần học kỹ", "NGUYÊN LÝ", Vector2(-160, -90), Vector2(260, 30), M("epc.s"), M("man.s")],
	]

func update(time: float) -> void:
	el.pulse = time

func draw_extra_hud(h: Node2D) -> void:
	var k = clampf((t - M("man.s")) / 0.4, 0, 1)
	if k <= 0.0:
		return
	var items = [["Shop manual đúng phiên bản / serial", true], ["Đoán theo một ảnh trên mạng", false]]
	for i in 2:
		var a = clampf((t - M("man.s") - i * 1.2) / 0.4, 0, 1)
		var r = Rect2(520, 130 + i * 80, 880, 68)
		h.draw_rect(r, Color(0.05, 0.08, 0.13, 0.94 * a))
		h.draw_rect(Rect2(r.position, Vector2(6, r.size.y)), Color(0.4, 0.9, 0.5, a) if items[i][1] else Color(1, 0.3, 0.25, a))
		h.draw_string(bold, r.position + Vector2(80, 46), items[i][0], HORIZONTAL_ALIGNMENT_LEFT, -1, 30, Color(1, 1, 1, a))
		h.draw_string(bold, r.position + Vector2(24, 50), "✓" if items[i][1] else "✗", HORIZONTAL_ALIGNMENT_LEFT, -1, 40, Color(0.4, 0.9, 0.5, a) if items[i][1] else Color(1, 0.3, 0.25, a))
