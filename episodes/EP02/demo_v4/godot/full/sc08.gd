@tool
extends "res://full/full_base.gd"
## SC08 - Quay toa bằng mô tơ thủy lực (top view). Only the upper structure
## swings; the tracks stay put. Inset: swing pinion rolling in the fixed ring.

@onready var top = $Top

func setup() -> void:
	callouts = [
		["Nhìn từ trên xuống", "", Vector2(-200, -330), Vector2(-260, -60), 0.6, M("ks.s") + 2.0],
		["Mô tơ quay toa + bộ giảm tốc (trên thân trên)", "NGUYÊN LÝ", Vector2(40, 70), Vector2(-620, 250), M("motor.s"), M("ring.s") + 1.0],
		["Vòng quay toa", "NGUYÊN LÝ", Vector2(-80, 60), Vector2(-520, 340), M("ring.s"), M("brake.s")],
		["Hãm & giữ quay theo thiết kế", "NGUYÊN LÝ", Vector2(40, 70), Vector2(-560, 300), M("brake.s"), M("ok.s")],
		["Gầm xích đứng yên", "", Vector2(-120, 119), Vector2(-420, 380), M("ok.s"), M("end")],
		["Thân trên quay", "", Vector2(300, 0), Vector2(100, -330), M("ok.s"), M("end")],
	]

func update(_time: float) -> void:
	var rotation_rad: float = deg_to_rad(-top.swing_deg)
	callouts[1][2] = Vector2(40, 70).rotated(rotation_rad)
	callouts[3][2] = callouts[1][2]
	callouts[5][2] = Vector2(300, 0).rotated(rotation_rad)

func qa(time: float) -> void:
	# undercarriage must never turn: tracks are drawn in the fixed frame, and
	# the swing must stay inside the planned range
	if absf(top.swing_deg) > 181.0:
		qa_report.append("t=%.2f swing out of range" % time)
	if absf(top.track_l) > 0.001 or absf(top.track_r) > 0.001:
		qa_report.append("t=%.2f tracks moved during swing" % time)
	var rotation_rad: float = deg_to_rad(-top.swing_deg)
	# Landmarks on the two ends of the illustrated bucket shell.
	for p in [Vector2(2172, 195), Vector2(2172, 610)]:
		var screen := to_screen(((p - Vector2(430, 380)) * 0.44).rotated(rotation_rad))
		if not Rect2(30, 90, 1860, 900).has_point(screen):
			qa_report.append("t=%.2f bucket outside the safe frame" % time)
