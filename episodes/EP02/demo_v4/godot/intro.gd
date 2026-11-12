@tool
extends Node2D
## 0–4 s channel open: EP01 studio cels (local) at 10 fps + episode title.

var director: Node
var cels: Texture2D
var bold: FontVariation

func _ready() -> void:
	director = get_parent().get_parent()
	var p = ProjectSettings.globalize_path("res://local/studio-cels.png")
	if FileAccess.file_exists(p):
		var img = Image.load_from_file(p)
		img.generate_mipmaps()
		cels = ImageTexture.create_from_image(img)
	bold = FontVariation.new()
	bold.base_font = ThemeDB.fallback_font
	bold.variation_embolden = 0.8

func _draw() -> void:
	if director == null or director.intro <= 0.0:
		return
	var t: float = director.t
	var a: float = director.intro
	for k in 54:
		var c = Color("#0e1b2e").lerp(Color("#18304f"), k / 54.0)
		draw_rect(Rect2(0, k * 20, 1920, 20), Color(c, a))
	var panel = Rect2(170, 62, 676, 958)
	draw_rect(panel.grow(6), Color(0.95, 0.75, 0.3, a))
	if cels:
		var i = clampi(int(floor((t + director.cel_offset) * 10.0)), 0, 41)
		var src = Rect2((i % 7) * 520, (i / 7) * 737, 520, 737)
		texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
		draw_texture_rect_region(cels, panel, src, Color(1, 1, 1, a))
	else:
		draw_rect(panel, Color(0.1, 0.15, 0.22, a))
		draw_string(ThemeDB.fallback_font, panel.position + Vector2(40, 480), "local/studio-cels.png (EP01, cục bộ)", HORIZONTAL_ALIGNMENT_LEFT, -1, 26, Color(1, 1, 1, a))
	var rise = clampf((t - 0.3) / 0.5, 0, 1)
	var x = 940.0
	draw_line(Vector2(x, 330), Vector2(x + 760 * rise, 330), Color(0.95, 0.75, 0.3, a), 4.0)
	draw_string(bold, Vector2(x, 300), "CAPY BK  ·  TẬP 02", HORIZONTAL_ALIGNMENT_LEFT, -1, 34, Color(0.95, 0.78, 0.35, a * rise))
	var t2 = clampf((t - 0.6) / 0.5, 0, 1)
	draw_string(bold, Vector2(x, 440 + 20 * (1 - t2)), "KĨ SƯ ƠIII!", HORIZONTAL_ALIGNMENT_LEFT, -1, 104, Color(1, 1, 1, a * t2))
	var t3 = clampf((t - 1.4) / 0.5, 0, 1)
	draw_string(bold, Vector2(x, 540), "Tay máy đào lấy sức từ đâu?", HORIZONTAL_ALIGNMENT_LEFT, -1, 48, Color(1, 1, 1, a * t3))
	draw_string(ThemeDB.fallback_font, Vector2(x, 600), "Komatsu PC200-8 · demo thủy lực nâng cần", HORIZONTAL_ALIGNMENT_LEFT, -1, 32, Color(0.75, 0.85, 1, a * t3))
