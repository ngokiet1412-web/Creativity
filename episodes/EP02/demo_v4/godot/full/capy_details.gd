extends RefCounted
## Vector accessories shared by the studio, the corner host and the field rig.

static func glasses(c: CanvasItem, a: Vector2, b: Vector2) -> void:
	var rim := Color("#23354a")
	var along := (b - a).normalized()
	var up := Vector2(along.y, -along.x)
	var radius := 17.0
	c.draw_line(a - along * 15.0 + up * 4.0, a - along * 29.0 + up * 10.0, rim, 2.7, true)
	c.draw_line(b + along * 15.0 + up * 3.0, b + along * 26.0 + up * 8.0, rim, 2.7, true)
	c.draw_line(a + along * 16.0 + up * 2.0, b - along * 16.0 + up * 2.0, rim, 2.6, true)
	for p in [a, b]:
		c.draw_circle(p, radius, Color(0.64, 0.81, 0.95, 0.10), true, -1, true)
		c.draw_arc(p, radius, 0, TAU, 40, rim, 2.5, true)
		c.draw_arc(p, radius - 2.0, 3.65, 4.45, 12, Color(0.91, 0.98, 1.0, 0.72), 1.4, true)

static func _hex(c: CanvasItem, center: Vector2, radius: float, color: Color) -> void:
	var pts := PackedVector2Array()
	for i in 6:
		var angle := PI / 6.0 + i * TAU / 6.0
		pts.append(center + Vector2(cos(angle), sin(angle)) * radius)
	c.draw_colored_polygon(pts, color)

static func badge(c: CanvasItem, center: Vector2) -> void:
	# Reconstruct the original three blue lobes at a readable size, covering
	# the printed pixels of the old sprite. All corners stay on the polo.
	var patch := StyleBoxFlat.new()
	patch.bg_color = Color("#f4ebdf")
	patch.set_corner_radius_all(3)
	c.draw_style_box(patch, Rect2(center - Vector2(18.5, 18.0), Vector2(37, 37)))
	_hex(c, center + Vector2(0, -8), 10, Color("#187ed6"))
	_hex(c, center + Vector2(-8, 5), 10, Color("#0b54ad"))
	_hex(c, center + Vector2(8, 5), 10, Color("#0969c8"))
	_hex(c, center, 9, Color("#f4f9ff"))
	var font := ThemeDB.fallback_font
	var width := font.get_string_size("BK", HORIZONTAL_ALIGNMENT_LEFT, -1, 10).x
	c.draw_string(font, center + Vector2(-width / 2.0, 3.7), "BK", HORIZONTAL_ALIGNMENT_LEFT, -1, 10, Color("#073d85"))
