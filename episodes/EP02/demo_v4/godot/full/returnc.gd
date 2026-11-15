@tool
extends Node2D
## SC10 return circuit (concept): actuator -> control valve -> oil cooler ->
## return filter -> tank -> pump suction. Contaminant particles ride the
## return oil and stop at the filter element; air bubbles separate in the tank;
## the oil colour cools after the cooler. The order shown is ONE illustrative
## path (labelled), not the only route every return flow takes.

const Kit = preload("res://cutaway/kit.gd")
@export var travel := 0.0
@export var fan := 0.0
@export_range(0, 1) var live := 1.0
@export_range(0, 1) var caught := 0.0     # dirt accumulated on the element

const WARM := Color("#3a7fc4")   # warm return oil (blue; heat shown by the orange edge)
const COOL := Color("#3d93dc")

var path_pts := PackedVector2Array([Vector2(-760, -120), Vector2(-520, -120), Vector2(-520, -260), Vector2(-160, -260), Vector2(-160, -200)])

func _process(_d: float) -> void:
	queue_redraw()

func _draw() -> void:
	var font = ThemeDB.fallback_font
	# actuator (simplified cylinder) and control valve
	Kit.body(self, Kit.rect_pts(Rect2(-1080, -170, 300, 90)), Color("#e7a82b"), 2.4)
	Kit.cyl(self, Vector2(-780, -125), Vector2(-680, -125), 34, Kit.STEEL)
	Kit.label(self, font, Vector2(-1080, -200), "xi lanh / mô tơ", 26)
	Kit.body(self, Kit.rect_pts(Rect2(-600, -330, 170, 120)), Color("#b9c1c9"), 2.4)
	for k in 4:
		draw_rect(Rect2(-588 + k * 40, -318, 28, 96), Color("#8d98a4"))
	Kit.label(self, font, Vector2(-600, -350), "cụm van", 26)
	# return line -> cooler (warm: orange heat edge)
	for seg in [PackedVector2Array([Vector2(-780, -95), Vector2(-850, -95), Vector2(-850, 40), Vector2(-515, 40), Vector2(-515, -210)]), PackedVector2Array([Vector2(-430, -270), Vector2(-260, -270), Vector2(-260, -200)])]:
		draw_polyline(seg, Color(1, 0.55, 0.2, 0.35), 34.0, true)
	Kit.label(self, font, Vector2(-840, 90), "dầu hồi nóng", 24, Color(1, 0.75, 0.5))
	Kit.label(self, font, Vector2(-240, 230), "đã làm mát", 24, Color(0.7, 0.9, 1))
	Kit.pipe(self, PackedVector2Array([Vector2(-780, -95), Vector2(-850, -95), Vector2(-850, 40), Vector2(-515, 40), Vector2(-515, -210)]), WARM, travel, 18, live)
	Kit.pipe(self, PackedVector2Array([Vector2(-430, -270), Vector2(-260, -270), Vector2(-260, -200)]), WARM, travel, 18, live)
	# cooler with fins + fan
	var cr = Rect2(-330, -200, 140, 300)
	Kit.body(self, Kit.rect_pts(cr), Color("#9aa3ad"), 2.4)
	for k in 26:
		draw_line(Vector2(cr.position.x + 8, cr.position.y + 10 + k * 11), Vector2(cr.end.x - 8, cr.position.y + 10 + k * 11), Kit.INK, 1.4)
	var fc = Vector2(-130, -50)
	draw_circle(fc, 70, Color(0.1, 0.12, 0.15, 0.6))
	for b in 5:
		var a = fan + b * TAU / 5
		var blade = PackedVector2Array([fc, fc + Vector2(cos(a - 0.25), sin(a - 0.25)) * 64, fc + Vector2(cos(a + 0.2), sin(a + 0.2)) * 66])
		draw_colored_polygon(blade, Color("#5b6470"))
	draw_circle(fc, 12, Kit.INK)
	for k in 5:
		var y = -170 + k * 60 + fposmod(travel * 0.3, 60)
		draw_line(Vector2(-60, y), Vector2(-20, y - 10), Color(0.8, 0.9, 1, 0.5), 3.0)
	Kit.label(self, font, Vector2(-340, -230), "két làm mát dầu", 26)
	# cooler -> filter (oil now cool)
	Kit.pipe(self, PackedVector2Array([Vector2(-260, 100), Vector2(-260, 180), Vector2(80, 180), Vector2(80, 120)]), COOL, travel, 18, live)
	# filter canister (cutaway): pleated element, dirt caught on the outside
	var fr = Rect2(20, -200, 120, 320)
	Kit.cut(self, Kit.rect_pts(Rect2(fr.position.x, fr.position.y, 16, fr.size.y)), Kit.CUT_FACE, 8.0, 2.2)
	Kit.cut(self, Kit.rect_pts(Rect2(fr.end.x - 16, fr.position.y, 16, fr.size.y)), Kit.CUT_FACE, 8.0, 2.2)
	draw_rect(Rect2(fr.position.x + 16, fr.position.y, fr.size.x - 32, fr.size.y), Color(COOL, 0.55))
	for k in 12:
		var x = fr.position.x + 34 + k * 5.5
		draw_line(Vector2(x, fr.position.y + 30), Vector2(x, fr.end.y - 30), Color("#e9dfb4"), 3.0)
	var rng = RandomNumberGenerator.new()
	rng.seed = 3
	for i in int(caught * 40):
		draw_circle(Vector2(fr.position.x + 26 + rng.randf() * 8, fr.position.y + 40 + rng.randf() * 240), 3.0, Color(0.15, 0.1, 0.05))
	Kit.label(self, font, Vector2(-10, -230), "lọc dầu hồi", 26)
	# filter -> tank
	Kit.pipe(self, PackedVector2Array([Vector2(80, -200), Vector2(80, -290), Vector2(360, -290), Vector2(360, -200)]), COOL, travel, 18, live)
	# tank (cutaway): baffle, level, breather, suction strainer, bubbles rising
	var tr = Rect2(260, -200, 380, 380)
	draw_rect(tr, Color(0.07, 0.1, 0.16))
	var lvl = tr.position.y + 90 + sin(travel * 0.01) * 2.0
	draw_rect(Rect2(tr.position.x, lvl, tr.size.x, tr.end.y - lvl), Color(COOL, 0.85))
	draw_line(Vector2(tr.position.x, lvl), Vector2(tr.end.x, lvl), Color(1, 1, 1, 0.5), 2.0)
	draw_rect(Rect2(tr.position.x + 180, tr.position.y + 140, 14, tr.size.y - 140), Color("#8d98a4"))
	for i in 14:
		var ph = fposmod(travel * 0.02 + i * 0.37, 1.0)
		var bx = tr.position.x + 40 + (i * 53) % 130
		var by = lerpf(tr.end.y - 40, lvl + 4, ph)
		draw_arc(Vector2(bx + sin(ph * 9 + i) * 6, by), 4 + i % 3, 0, TAU, 12, Color(1, 1, 1, 0.7 * (1.0 - ph * 0.5)), 1.6, true)
	draw_rect(tr, Kit.INK, false, 4.0)
	draw_rect(Rect2(tr.end.x - 70, tr.position.y - 40, 36, 40), Color("#6a6e75"))
	Kit.label(self, font, Vector2(tr.end.x - 150, tr.position.y - 56), "thở", 22)
	Kit.label(self, font, Vector2(tr.position.x, tr.position.y - 20), "bình dầu", 26)
	Kit.label(self, font, Vector2(tr.position.x + 40, tr.end.y - 70), "bọt khí tách ra", 22, Color(1, 1, 1))
	# suction strainer + line to pump
	draw_rect(Rect2(tr.end.x - 120, tr.end.y - 70, 70, 40), Color("#b9a46a"))
	Kit.pipe(self, PackedVector2Array([Vector2(tr.end.x - 85, tr.end.y - 70), Vector2(tr.end.x - 85, tr.end.y + 60), Vector2(tr.end.x + 160, tr.end.y + 60), Vector2(tr.end.x + 160, -60)]), COOL, travel, 18, live)
	draw_circle(Vector2(tr.end.x + 160, -110), 50, Color("#c94a35"))
	draw_arc(Vector2(tr.end.x + 160, -110), 50, 0, TAU, 32, Kit.INK, 2.4, true)
	Kit.label(self, font, Vector2(tr.end.x + 100, -180), "bơm (hút)", 26)
	# contaminant particles riding the warm return line until the filter
	var line = PackedVector2Array([Vector2(-780, -95), Vector2(-850, -95), Vector2(-850, 40), Vector2(-515, 40), Vector2(-515, -210)])
	var L = 0.0
	for i in line.size() - 1:
		L += line[i].distance_to(line[i + 1])
	for i in 9:
		var d = fposmod(travel * 1.0 + i * L / 9.0, L)
		var acc = 0.0
		for j in line.size() - 1:
			var l = line[j].distance_to(line[j + 1])
			if d <= acc + l:
				draw_circle(line[j].lerp(line[j + 1], (d - acc) / l), 4.0, Color(0.15, 0.1, 0.05, 0.9 * live))
				break
			acc += l
