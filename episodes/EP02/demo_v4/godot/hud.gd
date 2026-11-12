@tool
extends Node2D
## Screen-space graphics: component labels pinned to machine points, colour
## legend, simplified-diagram notice and the closing energy chain.
## Dialogue lives in the separate SRT, never in these frames.

const SAFE_BOTTOM := 905.0     # keep graphics above the subtitle band
var director: Node
var font: Font
var bold: FontVariation

const SETS := {
	1: [["Động cơ diesel SAA6D107E-1", Vector2(-308, -50), Vector2(-90, -110), 10.2],
		["Bơm piston thay đổi lưu lượng", Vector2(-214, 20), Vector2(60, 190), 12.2],
		["Đĩa nghiêng góc nhỏ = lưu lượng chờ", Vector2(-233, 8), Vector2(-520, 120), 13.4],
		["Áp bơm", Vector2(-180, -30), Vector2(-40, -150), 14.4],
		["Thùng dầu", Vector2(-159, -60), Vector2(120, -60), 15.2]],
	2: [["Tay điều khiển", Vector2(-44, -54), Vector2(50, -70), 16.9],
		["Dầu pilot đẩy con trượt", Vector2(-100, -10), Vector2(-120, -190), 18.4],
		["Van phân phối", Vector2(-91, 36), Vector2(60, 90), 19.6],
		["Tín hiệu tải LS về bơm", Vector2(-160, -22), Vector2(-330, -150), 21.3],
		["Đĩa nghiêng tăng góc", Vector2(-233, 8), Vector2(-260, 110), 22.1]],
	4: [["Ty dài ra · cần quay quanh chốt chân cần", Vector2(0, 0), Vector2(-260, -130), 27.8]],
	# ---- V4 proof: every label carries its evidence tag
	10: [["Van mở: dầu cấp (đỏ) vào xi lanh, dầu hồi (xanh) về van", Vector2(30, 45), Vector2(-120, 150), 4.7, "NGUYÊN LÝ"]],
	11: [["Động cơ SAA6D107E-1 quay bơm", Vector2(-308, -50), Vector2(-60, -120), 7.5, "K1 ✓"],
		["Bơm piston thay đổi lưu lượng", Vector2(-214, 20), Vector2(-330, 170), 7.9, "K1 ✓"],
		["Con trượt mở P→A, B→T", Vector2(-91, 36), Vector2(140, 150), 8.5, "NGUYÊN LÝ"]],
	13: [["Xi lanh gầu duỗi ra · gầu cuộn giữ đất", Vector2(380, -60), Vector2(-420, -150), 13.2, "NGUYÊN LÝ"]],
	5: [["Van về giữa: chặn đường A và B", Vector2(-56, 20), Vector2(-60, -120), 31.0],
		["Dầu giữ trong khoang đáy, cần đứng yên", Vector2(69, 39), Vector2(90, 160), 32.2]],
}

func _ready() -> void:
	director = get_parent().get_parent()
	font = ThemeDB.fallback_font
	bold = FontVariation.new()
	bold.base_font = font
	bold.variation_embolden = 0.7

func to_screen(machine_p: Vector2) -> Vector2:
	var cam: Camera2D = director.cam
	var w: Vector2 = director.rig.transform * machine_p
	return (w - cam.position) * cam.zoom.x + Vector2(960, 540)

func _draw() -> void:
	if director == null or director.cam == null:
		return
	var t: float = director.t
	var ls: int = director.label_set
	if SETS.has(ls):
		for item in SETS[ls]:
			var a = clampf((t - float(item[3])) / 0.35, 0.0, 1.0)
			if a > 0.0:
				_callout(item[0], to_screen(item[1]), item[2], a, item[4] if item.size() > 4 else "")
	if ls == 3:
		_cylinder_labels(t)
	if ls == 12:
		_cylinder_labels_v4(t)
	if ls >= 10:
		_evidence_key(clampf(director.legend, 0, 1))
	if director.legend > 0.01:
		_legend(director.legend)
		_notice(director.legend)
	if director.chain > 0.0:
		_chain(director.chain, t)
	if "--pins" in OS.get_cmdline_user_args():
		_pins()

## Diagnostic overlay: pins, cylinder axes and solved pin distances.
func _pins() -> void:
	var rig = director.rig
	var f: Dictionary = rig.current()
	var cyl = [["Lb", f.Bb, f.Eb, rig.rig.boom_cyl], ["La", f.Ab, f.Ea, rig.rig.arm_cyl], ["Lk", f.C, f.J, rig.rig.bucket_cyl]]
	for c in cyl:
		var a = to_screen(c[1])
		var b = to_screen(c[2])
		draw_line(a, b, Color(0, 1, 1, 0.9), 2.0, true)
		var s = float(f[c[0]]) - float(c[3].closed)
		draw_string(font, (a + b) * 0.5 + Vector2(12, -8), "%s %.0f px · hành trình %.0f/%.0f" % [c[0], f[c[0]], s, c[3].stroke], HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color(0, 1, 1))
	for k in ["W1", "W2", "K", "S", "C", "J", "Bb", "Eb", "Ab", "Ea"]:
		var p = to_screen(f[k])
		draw_arc(p, 9, 0, TAU, 20, Color(1, 0.2, 0.8), 2.5, true)
		draw_string(font, p + Vector2(10, 18), k, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color(1, 0.4, 0.9))
	var o = to_screen(Vector2.ZERO)
	draw_arc(o, 11, 0, TAU, 20, Color(1, 0.2, 0.8), 2.5, true)
	draw_string(font, Vector2(30, 140), "t = %.2f s   boom %.1f°  arm %.1f°  bucket %.1f°" % [director.t, director.boom_deg, director.arm_rel, director.bucket_rel], HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Color(1, 1, 1))

func _callout(text: String, anchor: Vector2, offset: Vector2, a: float, tag := "") -> void:
	var size = 25
	var tag_w = 0.0
	if tag != "":
		tag_w = bold.get_string_size(tag, HORIZONTAL_ALIGNMENT_LEFT, -1, 19).x + 18
	var w = bold.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x + 26 + tag_w
	var box_pos = anchor + offset
	box_pos.x = clampf(box_pos.x, 30, 1890 - w)
	box_pos.y = clampf(box_pos.y, 40, SAFE_BOTTOM - 46)
	var box = Rect2(box_pos, Vector2(w, 42))
	var join = Vector2(clampf(anchor.x, box.position.x + 10, box.end.x - 10), box.position.y + (42 if anchor.y > box.position.y + 21 else 0))
	draw_line(anchor, join, Color(1, 1, 1, 0.85 * a), 2.0, true)
	draw_circle(anchor, 5.0, Color(1, 0.86, 0.35, a), true, -1, true)
	draw_rect(box, Color(0.06, 0.09, 0.14, 0.86 * a))
	draw_rect(Rect2(box.position, Vector2(5, 42)), Color(1, 0.78, 0.25, a))
	draw_string(bold, box.position + Vector2(15, 29), text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, Color(1, 1, 1, a))
	if tag != "":
		var verified = tag.begins_with("K")
		var tr = Rect2(Vector2(box.end.x - tag_w - 4, box.position.y + 8), Vector2(tag_w - 4, 26))
		draw_rect(tr, Color(0.2, 0.62, 0.36, a) if verified else Color(0.42, 0.47, 0.55, a))
		draw_string(bold, tr.position + Vector2(7, 20), tag, HORIZONTAL_ALIGNMENT_LEFT, -1, 19, Color(1, 1, 1, a))

func _cylinder_labels(t: float) -> void:
	var rig = director.rig
	var f: Dictionary = rig.current()
	var u: Vector2 = f.Bb.direction_to(f.Eb)
	var piston = 22.0 + (f.Lb - float(rig.rig.boom_cyl.closed))
	var bottom_mid: Vector2 = f.Bb + u * (piston * 0.5)
	var rod_mid: Vector2 = f.Bb + u * ((piston + float(rig.rig.boom_cyl.closed) - 18.0) * 0.5)
	_callout("Khoang đáy: dầu áp lực vào", to_screen(bottom_mid), Vector2(60, 70), clampf((t - 23.9) / 0.35, 0, 1))
	_callout("Khoang ty: dầu bị đẩy về thùng", to_screen(rod_mid), Vector2(-120, -150), clampf((t - 25.2) / 0.35, 0, 1))

func _cylinder_labels_v4(t: float) -> void:
	var rig = director.rig
	var f: Dictionary = rig.current()
	var u: Vector2 = f.Bb.direction_to(f.Eb)
	var piston = 22.0 + (f.Lb - float(rig.rig.boom_cyl.closed))
	var bottom_mid: Vector2 = f.Bb + u * (piston * 0.5)
	var rod_mid: Vector2 = f.Bb + u * ((piston + float(rig.rig.boom_cyl.closed) - 18.0) * 0.5)
	_callout("Khoang đáy: dầu áp lực vào", to_screen(bottom_mid), Vector2(70, 60), clampf((t - 9.5) / 0.35, 0, 1), "NGUYÊN LÝ")
	_callout("Khoang ty: dầu bị đẩy về thùng", to_screen(rod_mid), Vector2(-560, -110), clampf((t - 10.2) / 0.35, 0, 1), "NGUYÊN LÝ")
	_callout("2 xi lanh nâng cần Ø120 mm · hành trình 1.334 mm", to_screen(f.Eb), Vector2(-700, -40), clampf((t - 10.9) / 0.35, 0, 1), "K1 ✓")

func _evidence_key(a: float) -> void:
	if a <= 0.01:
		return
	var text = "K1 ✓ đã đối chiếu brochure Komatsu PC200-8 CEN00049-08   ·   NGUYÊN LÝ = minh họa giản lược"
	var w = font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 19).x + 24
	draw_rect(Rect2(1880 - w, 74, w, 32), Color(0.05, 0.08, 0.12, 0.78 * a))
	draw_string(font, Vector2(1892 - w, 96), text, HORIZONTAL_ALIGNMENT_LEFT, -1, 19, Color(0.85, 0.95, 0.88, a))

func _legend(a: float) -> void:
	var items = [[Color("#e4472f"), "dầu áp lực"], [Color("#3d93dc"), "dầu hồi"], [Color("#f39a1e"), "pilot"], [Color("#a46be0"), "tín hiệu tải LS"]]
	var x = 40.0
	var y = 64.0
	var w = 0.0
	for it in items:
		w += font.get_string_size(it[1], HORIZONTAL_ALIGNMENT_LEFT, -1, 21).x + 52
	draw_rect(Rect2(x - 12, y - 25, w + 10, 40), Color(0.05, 0.08, 0.12, 0.78 * a))
	for it in items:
		draw_line(Vector2(x, y - 5), Vector2(x + 28, y - 5), Color(it[0], a), 7.0, true)
		draw_string(font, Vector2(x + 36, y + 2), it[1], HORIZONTAL_ALIGNMENT_LEFT, -1, 21, Color(1, 1, 1, a))
		x += font.get_string_size(it[1], HORIZONTAL_ALIGNMENT_LEFT, -1, 21).x + 52

func _notice(a: float) -> void:
	var text = "Sơ đồ giản lược · không phải sơ đồ cổng van theo số sê-ri"
	var w = font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 20).x + 24
	draw_rect(Rect2(1880 - w, 32, w, 36), Color(0.05, 0.08, 0.12, 0.78 * a))
	draw_string(font, Vector2(1892 - w, 57), text, HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color(0.92, 0.95, 1, a))

func _chain(c: float, t: float) -> void:
	var names = ["Động cơ", "Bơm", "Van", "Xi lanh", "Cần"]
	var appear = clampf((t - 34.6) / 0.4, 0, 1)
	var widths = []
	var total = 0.0
	for n in names:
		var w = bold.get_string_size(n, HORIZONTAL_ALIGNMENT_LEFT, -1, 30).x + 40
		widths.append(w)
		total += w
	total += 4 * 56
	var x = 960 - total * 0.5
	var y = 70.0
	for i in names.size():
		var lit = clampf(c - i, 0.0, 1.0)
		var pop = 1.0 + 0.08 * sin(clampf(c - i, 0, 1) * PI)
		var r = Rect2(x, y - 30 * pop, widths[i], 60 * pop)
		draw_rect(r, Color(0.06, 0.09, 0.14, 0.85 * appear))
		draw_rect(r, Color(1, 0.78, 0.25, appear * (0.25 + 0.75 * lit)), false, 3.0)
		draw_rect(Rect2(r.position, Vector2(r.size.x * lit, r.size.y)), Color(1, 0.78, 0.25, 0.22 * appear))
		draw_string(bold, Vector2(x + 20, y + 11), names[i], HORIZONTAL_ALIGNMENT_LEFT, -1, 30, Color(1, 1, 1, appear * (0.45 + 0.55 * lit)))
		x += widths[i]
		if i < names.size() - 1:
			var lit_arrow = clampf(c - i - 0.6, 0, 1)
			draw_line(Vector2(x + 10, y), Vector2(x + 44, y), Color(1, 0.78, 0.25, appear * (0.3 + 0.7 * lit_arrow)), 4.0, true)
			draw_colored_polygon(PackedVector2Array([Vector2(x + 46, y), Vector2(x + 34, y - 9), Vector2(x + 34, y + 9)]), Color(1, 0.78, 0.25, appear * (0.3 + 0.7 * lit_arrow)))
			x += 56
