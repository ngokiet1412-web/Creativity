@tool
extends Node2D
## Work-equipment PPC valve under a joystick, vertical section (principle).
## PC200-8 uses PPC (pilot pressure control) valves for work equipment and
## swing; pilot circuit relief 3.2 MPa (brochure). Internal layout: lever ->
## disc -> plunger -> metering spring -> reducing spool; output pressure is
## proportional to lever stroke. Illustration, not a Komatsu part drawing.

const Kit = preload("res://cutaway/kit.gd")

@export_range(-1, 1) var lever := 0.0: set = _set_lever
@export var travel := 0.0
var font: Font

func _set_lever(v: float) -> void:
	lever = v
	queue_redraw()

func _ready() -> void:
	font = ThemeDB.fallback_font

func output() -> float:
	## normalised pilot output on the active side (0..1), small dead band
	return clampf((absf(lever) - 0.08) / 0.92, 0.0, 1.0)

func _draw() -> void:
	var ang = deg_to_rad(20.0 * lever)
	var piv = Vector2(0, -150)
	# body (sectioned)
	var body = PackedVector2Array([Vector2(-170, -120), Vector2(170, -120), Vector2(170, 240), Vector2(-170, 240)])
	Kit.cut(self, body, Kit.CUT_FACE, 10.0, 2.4)
	# boot + lever + grip
	var u = Vector2(sin(ang), -cos(ang))
	var top = piv + u * 250
	Kit.body(self, PackedVector2Array([Vector2(-90, -120), Vector2(90, -120), piv + u * 70 + Vector2(30, 0), piv + u * 70 - Vector2(30, 0)]), Color("#2a2f36"))
	Kit.cyl(self, piv, top, 22, Kit.STEEL_DARK.lightened(0.2))
	# grip: rounded handle
	Kit.cyl(self, top - u * 60, top + u * 50, 64, Color("#2b2b2e"))
	draw_circle(top + u * 50, 32, Color("#2b2b2e"), true, -1, true)
	draw_arc(top + u * 50, 32, ang - PI, ang, 20, Kit.INK, 1.8, true)
	draw_circle(top + u * 40 + u.orthogonal() * 10, 7, Color(0.85, 0.3, 0.15), true, -1, true)
	# disc pushing the plungers
	var dhalf = Vector2(cos(ang), sin(ang)) * 110
	draw_line(piv - dhalf, piv + dhalf, Kit.INK, 16.0, true)
	draw_line(piv - dhalf, piv + dhalf, Kit.STEEL, 11.0, true)
	Kit.disc(self, piv, 14, Kit.STEEL)
	# two plunger/spool stacks
	for side in [-1, 1]:
		var x = side * 75.0
		var push = maxf((piv + dhalf * side).y - (piv - dhalf * side).y, 0.0) * 0.5 if side * lever > 0.0 else 0.0
		var active = push > 0.5
		var out = output() if active else 0.0
		draw_rect(Rect2(x - 22, -120, 44, 330), Color("#1a2028"))
		# output chamber + port to the main spool pilot chamber
		var oc = Color(Kit.ORANGE, 0.35 + 0.65 * out)
		draw_rect(Rect2(x - 20, 150, 40, 58), oc)
		Kit.pipe(self, PackedVector2Array([Vector2(x, 208), Vector2(x, 330)]), Kit.ORANGE, travel * (1.0 if active else 0.0), 22, out)
		# plunger
		Kit.cyl(self, Vector2(x, -150 + push), Vector2(x, -40 + push), 26, Kit.STEEL)
		# metering spring (compressed by the plunger)
		Kit.spring(self, Vector2(x, -40 + push), Vector2(x, 70), 6, 30)
		# reducing spool: lifts its land past the supply notch in proportion
		var sp = 70.0 + push * 0.35
		Kit.cyl(self, Vector2(x, sp), Vector2(x, sp + 80), 30, Kit.STEEL.lightened(0.1))
		Kit.label(self, font, Vector2(x - 26, 268 + 90), "P%d" % (1 if side < 0 else 2), 21, Kit.ORANGE.lightened(0.3))
	# pilot supply P (from the pilot pump, pressure-limited) and tank T
	Kit.pipe(self, PackedVector2Array([Vector2(-300, 120), Vector2(-20, 120)]), Kit.ORANGE, travel * 0.5, 18, 1.0)
	Kit.pipe(self, PackedVector2Array([Vector2(20, 40), Vector2(300, 40)]), Kit.BLUE, travel * 0.3, 16, absf(lever))
	Kit.label(self, font, Vector2(-300, 104), "P pilot", 20, Kit.ORANGE.lightened(0.3))
	Kit.label(self, font, Vector2(250, 26), "T", 20, Kit.BLUE.lightened(0.4))
