@tool
extends Node2D
## SC09 part A: section through the upper/lower joint with the centre swivel
## joint (principle drawing). The outer body turns with the upper structure
## (its surface marks slide sideways as it turns), the inner shaft is tied to
## the undercarriage. Oil enters the body, rides in an annular groove that is
## open all the way round, goes down a drilled passage in the shaft and leaves
## to the travel motors - so the upper can turn without twisting hoses.

const Kit = preload("res://cutaway/kit.gd")

@export var turn := 0.0          # upper swing angle (deg) -> body surface marks
@export var travel := 0.0        # oil movement
@export_range(0, 1) var live := 1.0
@export_range(0, 1) var noodle := 0.0   # Capy's twisted-hose gag

func _process(_d: float) -> void:
	queue_redraw()

func _draw() -> void:
	var font = ThemeDB.fallback_font
	# upper frame (cut) and undercarriage centre frame (cut)
	Kit.cut(self, Kit.rect_pts(Rect2(-520, -330, 1040, 70)), Color("#e7c27a"), 10.0, 2.4)
	Kit.label(self, font, Vector2(-500, -350), "khung thân trên (quay)", 28)
	Kit.cut(self, Kit.rect_pts(Rect2(-520, 150, 1040, 70)), Color("#b9bec6"), 10.0, 2.4)
	Kit.label(self, font, Vector2(-500, 260), "khung gầm (đứng yên)", 28)
	# swing circle bearing (balls between two races)
	for side in [-1.0, 1.0]:
		var x = side * 360.0
		Kit.body(self, Kit.rect_pts(Rect2(x - 50, -260, 100, 40)), Color("#d0a24a"), 2.0)
		Kit.body(self, Kit.rect_pts(Rect2(x - 50, -220, 100, 40)), Color("#8b9098"), 2.0)
		for k in 3:
			var bx = x - 30 + fposmod(k * 30.0 + turn * 2.0 * side, 90.0) - 15
			draw_circle(Vector2(bx, -220), 9, Color("#e8ecef"))
			draw_arc(Vector2(bx, -220), 9, 0, TAU, 14, Kit.INK, 1.5, true)
		draw_line(Vector2(x, -180), Vector2(x, 150), Color(Kit.INK, 0.5), 2.0)
	Kit.label(self, font, Vector2(260, -300), "vòng quay toa", 26)
	# swivel body (turns with the upper): outer housing
	var body = Rect2(-110, -260, 220, 300)
	Kit.cut(self, Kit.rect_pts(Rect2(body.position.x, body.position.y, 50, body.size.y)), Color("#e7c27a"), 8.0, 2.2)
	Kit.cut(self, Kit.rect_pts(Rect2(body.end.x - 50, body.position.y, 50, body.size.y)), Color("#e7c27a"), 8.0, 2.2)
	# turning marks on the body front face (show the body rotating)
	for k in 8:
		var u = fposmod(k / 8.0 + turn / 360.0, 1.0)
		var x = -60 + 120 * (0.5 - 0.5 * cos(u * TAU))
		var vis = sin(u * TAU) > 0.0
		if vis:
			draw_line(Vector2(x, -255), Vector2(x, -232), Color(0.3, 0.2, 0.1, 0.7), 3.0)
	# inner shaft (tied to the undercarriage)
	var shaft = Rect2(-60, -250, 120, 420)
	Kit.body(self, Kit.rect_pts(shaft), Color("#a9b1ba"), 2.2)
	# Two isolated work passages A/B of ONE reversible travel motor.
	# Red supply / blue return show only the selected direction, not fixed ports.
	var ys = [-190.0, -110.0]
	var cols = [Kit.RED, Kit.BLUE]
	for i in 2:
		var y = ys[i]
		draw_rect(Rect2(-60, y - 14, 120, 28), cols[i].darkened(0.1))
		for sy in [y - 24, y + 20]:
			draw_rect(Rect2(-64, sy, 128, 5), Color("#26201c"))
		# ports in the body (from the valve, on the upper)
		var side = -1.0 if i == 0 else 1.0
		Kit.pipe(self, PackedVector2Array([Vector2(side * 520, y - 100), Vector2(side * 300, y - 100), Vector2(side * 300, y), Vector2(side * 60, y)]), cols[i], travel * (1 if i == 0 else -1), 16, live)
		# drilled passage down the shaft to the undercarriage
		var px = -24.0 if i == 0 else 24.0
		Kit.pipe(self, PackedVector2Array([Vector2(px, y), Vector2(px, 170), Vector2(px + side * 0.0, 230)]), cols[i], travel * (1 if i == 0 else -1), 12, live)
		Kit.pipe(self, PackedVector2Array([Vector2(px, 230), Vector2(px, 275), Vector2(side * 145, 275), Vector2(side * 145, 365), Vector2(side * 62, 365)]), cols[i], travel * (1 if i == 0 else -1), 16, live)
		draw_circle(Vector2(side * 145, 330), 19, Color("#142435"))
		Kit.label(self, font, Vector2(side * 145 - 9, 339), "A" if i == 0 else "B", 22, cols[i].lightened(0.45))
	Kit.label(self, font, Vector2(-520, -110), "từ cụm van (thân trên)", 26)
	Kit.disc(self, Vector2(0, 365), 62, Color("#556a79"))
	draw_circle(Vector2(0, 365), 39, Color("#273f51"))
	draw_arc(Vector2(0, 365), 28, turn * 0.08, turn * 0.08 + PI * 1.6, 30, Color("#ffd36d"), 5.0, true)
	Kit.label(self, font, Vector2(-195, 464), "A / B · cùng một mô tơ di chuyển", 24)
	Kit.label(self, font, Vector2(-235, 495), "Đổi chiều: cấp / hồi đổi vai · nhánh kia tương tự", 20)
	Kit.label(self, font, Vector2(130, -150), "rãnh vòng: dầu thông mọi góc quay", 26, Color(1, 0.9, 0.6))
	# noodle gag: hoses twisted round each other, crossed out
	if noodle > 0.01:
		var c = Vector2(0, -40)
		for k in 3:
			var pts = PackedVector2Array()
			for i in 40:
				var u = i / 39.0
				pts.append(c + Vector2(sin(u * 18.0 + k * 2.1) * 70.0, -200 + u * 400))
			draw_polyline(pts, Color(1, 0.85, 0.5, noodle), 10.0, true)
		draw_line(c + Vector2(-140, -140), c + Vector2(140, 140), Color(1, 0.2, 0.2, noodle), 12.0, true)
		draw_line(c + Vector2(-140, 140), c + Vector2(140, -140), Color(1, 0.2, 0.2, noodle), 12.0, true)
