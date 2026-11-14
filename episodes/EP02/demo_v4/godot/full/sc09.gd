@tool
extends "res://full/full_base.gd"
## SC09 - Điều khiển hai bánh xích và khớp quay trung tâm.
## A: section with the centre swivel joint (upper turns, oil keeps flowing)
## B: one track from the side: sprocket, links on the loop, ground with no slip
## C: top view: both tracks forward = straight, opposite = pivot turn
##    (turn angle = (s_right - s_left) / track gauge)

const GAUGE := 238.0
@export var drive_s := 0.0      # straight travel (px)
@export var turn_d := 0.0       # pivot-turn differential (px per track)
@export var side_s := 0.0       # part B travel

@onready var sw = $Swivel
@onready var side = $Side
@onready var drive = $Drive
@onready var top = $Drive/Top

func setup() -> void:
	callouts = [
		["Khớp quay trung tâm (center swivel joint)", "NGUYÊN LÝ", Vector2(0, -260), Vector2(-320, -120), M("ks.s") + 0.2, M("trk.s")],
		["Mô tơ di chuyển + bộ truyền cuối", "NGUYÊN LÝ", Vector2(-300, 1400), Vector2(-520, -260), M("trk.s"), M("top.s")],
		["Hai xích cùng tiến → đi thẳng", "", Vector2(2480, -119), Vector2(-300, -300), M("top.s"), M("top.s") + 3.6],
		["Một bên tiến, một bên lùi → quay tại chỗ", "", Vector2(2700, 119), Vector2(-360, 300), M("top.s") + 3.8, M("q2.s")],
		["Bánh dẫn quay → mắt xích chạy theo vòng", "NGUYÊN LÝ", Vector2(-300, 1340), Vector2(-420, -300), M("ks2.s"), M("end")],
		["Mắt xích nằm trên đất không trượt → máy tiến", "NGUYÊN LÝ", Vector2(100, 1480), Vector2(-120, 200), M("ks2.s") + 2.0, M("end")],
	]

func update(time: float) -> void:
	var a = drive_s
	top.track_l = drive_s - turn_d
	top.track_r = drive_s + turn_d
	drive.position = Vector2(2300 + drive_s, 0)
	drive.rotation = -(2.0 * turn_d) / GAUGE
	side.s = side_s
	sw.travel = time * 70.0

func qa(time: float) -> void:
	# no-slip check for C: body rotation must equal track differential / gauge
	var expect = -(top.track_r - top.track_l) / GAUGE
	if absf(drive.rotation - expect) > 1e-4:
		qa_report.append("t=%.2f turn angle != (sR - sL)/gauge" % time)
