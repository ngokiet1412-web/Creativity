@tool
extends Node2D
## Drives the whole proof from one AnimationPlayer ("sequence").
## Every keyed property lives on this node; derived quantities (cylinder
## speed, oil volume, pump swash, crumbs, mound bite) are computed from the
## keyed joint angles by sampling the Animation at other times, so the result
## is the same whether the clip is rendered, scrubbed in the editor or QA'd.

const FPS := 30.0
const LENGTH := 42.0

@export_group("Machine")
@export var boom_deg := 30.1
@export var arm_rel := 73.6
@export var bucket_rel := -2.9
@export_range(0, 1) var joystick := 0.0
@export_range(0, 1) var spool := 0.0
@export_group("Overlays")
@export_range(0, 1) var xray := 0.0
@export_range(0, 1) var cutaway := 0.0
@export_range(0, 1) var flow_overlay := 0.0
@export_range(0, 1) var legend := 0.0
@export var label_set := 0
@export_range(0, 5) var chain := 0.0
@export_range(0, 1) var intro := 1.0
@export_group("Camera")
@export var cam_x := 110.0
@export var cam_y := -131.0
@export var cam_zoom := 1.0
@export_range(0, 1) var cam_follow := 0.0
@export_group("Crew")
@export var capy_tilt := 0.0

@onready var player: AnimationPlayer = $AnimationPlayer
@onready var rig = $World/Machine
@onready var cam: Camera2D = $Camera
var anim: Animation
var tracks := {}
var frame := 0
var t := 0.0
var qa_mode := false
var qa_report := []
var telemetry := ["t,Lb,v,swash,spool,p_pump,joystick,cam_zoom,La,Lk,xray"]
var state := {}

func _ready() -> void:
	anim = player.get_animation("sequence")
	for i in anim.get_track_count():
		tracks[String(anim.track_get_path(i)).get_slice(":", 1)] = i
	qa_mode = "--qa" in OS.get_cmdline_user_args()
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--start="):
			frame = int(round(float(arg.get_slice("=", 1)) * FPS))
	if not Engine.is_editor_hint():
		player.play("sequence")
		player.pause()
		player.seek(0.0, true)

func sample(prop: String, time: float) -> float:
	return anim.value_track_interpolate(tracks[prop], clampf(time, 0.0, LENGTH))

func pose_at(time: float) -> Dictionary:
	return rig.fk(sample("boom_deg", time), sample("arm_rel", time), sample("bucket_rel", time))

func _process(_delta: float) -> void:
	if Engine.is_editor_hint():
		if player == null or anim == null:
			return
		t = player.current_animation_position
	else:
		t = frame / FPS
		player.seek(t, true)
		frame += 1
	_apply()
	if qa_mode and not Engine.is_editor_hint():
		_qa_step()
		if frame >= int(LENGTH * FPS):
			_qa_finish()

func _apply() -> void:
	rig.boom_deg = boom_deg
	rig.arm_rel = arm_rel
	rig.bucket_rel = bucket_rel
	rig.cutaway = cutaway
	rig.housing_alpha = 1.0 - xray
	state = hydraulic_state(t)
	cam.position = Vector2(cam_x, cam_y)
	if cam_follow > 0.0:
		var f: Dictionary = rig.current()
		var mid: Vector2 = rig.to_global((f.Bb + f.Eb) * 0.5) + Vector2(cam_x, cam_y)
		cam.position = cam.position.lerp(mid, cam_follow)
	cam.zoom = Vector2.ONE * cam_zoom          # uniform zoom only
	for n in ["World/Env", "World/Machine/Hydraulics", "World/Crew", "HUD/Overlay", "Intro/Card"]:
		var node = get_node_or_null(n)
		if node:
			node.queue_redraw()
	var crew = get_node_or_null("World/Crew")
	if crew:
		crew.visible = cam_zoom < 1.45 and intro < 0.5
		crew.set_state(t, capy_tilt)

## Oil volumes follow the boom cylinder piston. A = bottom (bore 120 mm),
## annulus = A - rod (85 mm) -> ~0.50 A, from the brochure cylinder sizes.
func hydraulic_state(time: float) -> Dictionary:
	var h = 1.0 / FPS
	var bc: Dictionary = rig.rig.boom_cyl
	var L0: float = pose_at(time - h).Lb
	var L1: float = pose_at(time).Lb
	var L2: float = pose_at(time + h).Lb
	var v = (L2 - L0) / (2.0 * h)                        # px/s, + = extending
	var lead = maxf((pose_at(time + 0.18).Lb - pose_at(time + 0.18 - h).Lb) / h, 0.0)
	var vmax = 9.5
	var area_ratio = 1.0 - pow(85.0 / 120.0, 2.0)
	var stroke = L1 - float(bc.closed)
	var open = sample("spool", time)
	var demand = clampf(lead / vmax, 0.0, 1.0)
	var swash = lerpf(0.10, 1.0, maxf(demand, 0.22 * open))   # 0..1 of max angle
	var p_pump = lerpf(0.14, 0.78, smoothstep(0.15, 0.85, open))   # standby -> load + LS margin
	return {
		"v": v, "stroke": stroke, "open": open, "swash": swash, "p_pump": p_pump,
		"vol_bottom": stroke * 14.0, "vol_rod": stroke * 14.0 * area_ratio,
		"pilot_vol": sample("spool", time) * 46.0,
		"ls": open, "moving": absf(v) > 0.05,
	}

func ls_wave(time: float) -> float:
	## 0..1 progress of the load-sense pressure front travelling to the pump
	if _ls_start < 0.0:
		_ls_start = 0.0
		for i in 400:
			var s = 15.0 + i * 0.05
			if sample("spool", s) > 0.35:
				_ls_start = s
				break
	var start = _ls_start
	return clampf((time - start) / 0.55, 0.0, 1.0) if start > 0.0 else 0.0

# ------------------------------------------------------------------------- QA
var _prev := {}
var _ls_start := -1.0
func _qa_step() -> void:
	var f: Dictionary = rig.current()
	var errs: Array = rig.verify(f)
	var env = get_node_or_null("World/Env")
	if env:
		errs.append_array(env.ground_check(f))
	for e in errs:
		qa_report.append("t=%.3f %s" % [t, e])
	# cylinder lengths must follow pins smoothly (no pops above 6 px/frame)
	for k in ["Lb", "La", "Lk"]:
		if _prev.has(k) and absf(f[k] - _prev[k]) > 6.0:
			qa_report.append("t=%.3f %s jump %.2f" % [t, k, f[k] - _prev[k]])
		_prev[k] = f[k]
	# oil direction must agree with piston motion
	telemetry.append("%.4f,%.3f,%.3f,%.4f,%.4f,%.4f,%.3f,%.3f,%.3f,%.3f,%.3f" % [t, f.Lb, state.v, state.swash, state.open, state.p_pump, joystick, cam_zoom, f.La, f.Lk, xray])
	if t >= 9.6 and state.moving and state.v > 0.0 and state.open < 0.2:
		qa_report.append("t=%.3f boom extends while spool is closed" % t)

func _qa_finish() -> void:
	var out = FileAccess.open("res://../qa_geometry.txt", FileAccess.WRITE)
	out.store_line("frames=%d errors=%d" % [frame, qa_report.size()])
	for line in qa_report:
		out.store_line(line)
	out.close()
	var tel = FileAccess.open("res://../telemetry.csv", FileAccess.WRITE)
	for line in telemetry:
		tel.store_line(line)
	tel.close()
	print("QA frames=%d errors=%d" % [frame, qa_report.size()])
	get_tree().quit(1 if qa_report.size() > 0 else 0)
