@tool
extends "res://full/full_base.gd"
## SC01 - Bí ẩn gầu đất. Studio (EP01 cels) -> the wall monitor powers on with
## the PC200-8 scooping and raising a loaded bucket -> continuous push through
## the monitor to the worksite, where the engineer answers from the barrier.

@export var pump_load := 0.1
@onready var studio = $Studio

func setup() -> void:
	mound_on = true
	dig_window = Vector2(M("dig.s"), M("dig.s") + 5.2)
	crew_from = M("push.s") + 1.3
	callouts = [
		["Komatsu PC200-8 (ví dụ của tập)", "K1 ✓", Vector2(-120, -200), Vector2(-40, -120), M("ks.s") + 0.6, M("ks.s") + 6.5],
		["Thủy lực bên trong thân máy", "NGUYÊN LÝ", Vector2(-180, -60), Vector2(60, -170), M("ks.s") + 3.5, M("ks.e") + 0.4],
	]

func update(time: float) -> void:
	var move := smoothstep(M("ks.e") + 0.2, M("end") - 0.2, time)
	studio.push = move
	studio.monitor_on = smoothstep(3.92, 4.45, time)
	studio.set_state(time, mouth("CAPY"), mouth("KS"), speaking("KS", time) > 0.0)
	studio.camera(cam)
	show_chip = false
	if crew:
		crew.visible = false
	exhaust_load = 0.3 + 0.7 * sample(".:pump_load", time)

func _draw_hud() -> void:
	pass
