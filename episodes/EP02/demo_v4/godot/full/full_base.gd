@tool
extends "res://segments/segment_base.gd"
## EP02 full-episode scene base (V5 draft).
## Adds to segment_base:
##  - cue/marker timing from res://full/timing.json (written by
##    tools/full/build_full.py from the verbatim script lines), so motion is
##    keyed to the (estimated) dialogue and re-times when real VO arrives
##  - host talk motion while a host's line plays
##  - the director interface env.gd / crew.gd expect (World/Env, World/Machine,
##    World/Crew), so the approved V4 worksite, machine rig and field crew can
##    be reused unchanged in new scenes
##  - grid_alpha: blueprint grid over the worksite (x-ray transitions)

@export_range(0, 1) var grid_alpha := 1.0
@export_range(0, 1) var xray := 0.0
@export_range(0, 1) var cutaway := 0.0
@export var show_chip := true

var timing := {}
var cues: Array = []
var marks := {}
var rig = null            # World/Machine (rig.gd) if present
var bake_mound := false
var crumb_bursts: Array = []
var crew = null

func _ready() -> void:
	var js = JSON.parse_string(FileAccess.get_file_as_string("res://full/timing.json"))
	timing = js if js else {}
	if timing.has("scenes") and timing.scenes.has(scene_tag):
		cues = timing.scenes[scene_tag].cues
		marks = timing.scenes[scene_tag].marks
	rig = get_node_or_null("World/Machine")
	crew = get_node_or_null("World/Crew")
	super._ready()

func M(name: String) -> float:
	return float(marks.get(name, 0.0))

## 0..1 envelope of `who` speaking at time t ("CAPY" / "KS")
func speaking(who: String, time: float) -> float:
	var k = 0.0
	for c in cues:
		if c.who == who:
			var a = clampf((time - float(c.t0)) / 0.15, 0, 1) * clampf((float(c.t1) - time) / 0.2, 0, 1)
			k = maxf(k, a)
	return k

## pose at time s from the joint tracks (env.gd carves the mound with it)
func pose_at(s: float) -> Dictionary:
	if rig == null:
		return {}
	return rig.fk(sample("World/Machine:boom_deg", s), sample("World/Machine:arm_rel", s), sample("World/Machine:bucket_rel", s))

var mound_on := false          # machine on flat ground unless the scene digs
var mound_style := 1           # 1 = V5 heap drawing (env.gd)
var dig_window := Vector2(4.0, 9.4)
var crew_from := 0.0

func hydraulic_state(_born: float) -> Dictionary:
	return {"swash": exhaust_load}

var exhaust_load := 0.3

func _process(d: float) -> void:
	super._process(d)
	if crew:
		crew.mouth_capy = mouth("CAPY")
		crew.mouth_eng = mouth("KS")
		crew.appear_t = 0.0
		crew.modulate.a = clampf((t - crew_from) / 0.5, 0.0, 1.0)
		crew.set_state(t, capy_tilt)

func _draw() -> void:
	if grid_alpha <= 0.001:
		return
	var c = cam.position if cam else Vector2.ZERO
	var r = Rect2(c - Vector2(4000, 3000), Vector2(8000, 6000))
	draw_rect(r, Color(Color("#0c1524"), grid_alpha))
	var step = 60.0
	var x = floor(r.position.x / step) * step
	while x < r.end.x:
		draw_line(Vector2(x, r.position.y), Vector2(x, r.end.y), Color(0.35, 0.5, 0.75, 0.07 * grid_alpha), 1.0)
		x += step
	var y = floor(r.position.y / step) * step
	while y < r.end.y:
		draw_line(Vector2(r.position.x, y), Vector2(r.end.x, y), Color(0.35, 0.5, 0.75, 0.07 * grid_alpha), 1.0)
		y += step

func _draw_hud() -> void:
	if not show_chip:
		_hosts_only()
		return
	super._draw_hud()

func _hosts_only() -> void:
	for c in callouts:
		var a = clampf((t - float(c[4])) / 0.35, 0, 1) * clampf((float(c[5]) - t) / 0.3, 0, 1)
		if a > 0.0:
			_callout(c[0], c[1], to_screen(c[2]), c[3], a)
	draw_extra_hud(hud)
	_host(host_capy, capy_in, true, capy_tilt, capy_blinks, [[81, 84, 8, 11], [141, 102, 8.5, 11]])
	_host(host_eng, eng_in, false, 0.0, eng_blinks, [[135, 138, 7, 11], [185, 124, 6, 10]])
