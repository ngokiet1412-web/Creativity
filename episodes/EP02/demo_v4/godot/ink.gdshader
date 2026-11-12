shader_type canvas_item;
// 2.5D technical-illustration look for the painted machine layers:
// warm ink contour + soft tone banding, keeps the painted detail but drops the
// glossy render feel. Colour only - geometry and UVs are untouched (no warp).
uniform float outline_px = 3.0;          // contour width in texture pixels
uniform vec4 ink : source_color = vec4(0.16, 0.11, 0.07, 1.0);
uniform float bands = 6.0;               // tone steps
uniform float band_mix = 0.45;           // 0 = painted, 1 = fully banded
uniform float detail_soften = 0.7;       // mip bias, calms photographic micro-texture
uniform vec3 grade = vec3(1.05, 1.0, 0.92);
uniform vec4 ghost : source_color = vec4(1.0);   // x-ray ghosting set by rig.gd

void fragment() {
	vec4 c = texture(TEXTURE, UV, detail_soften);
	vec2 px = TEXTURE_PIXEL_SIZE * outline_px;
	float a = 0.0;
	for (int i = 0; i < 12; i++) {
		float ang = float(i) * 0.5235988;
		a = max(a, texture(TEXTURE, UV + vec2(cos(ang), sin(ang)) * px).a);
	}
	float l = dot(c.rgb, vec3(0.299, 0.587, 0.114));
	float lq = (floor(l * bands) + smoothstep(0.35, 0.65, fract(l * bands))) / bands;
	vec3 toon = c.rgb * (lq / max(l, 0.002));
	vec3 col = clamp(mix(c.rgb, toon, band_mix) * grade, 0.0, 1.0);
	// darken a thin inner rim so parts read as cut-out plates
	float inner = 1.0;
	for (int i = 0; i < 8; i++) {
		float ang = float(i) * 0.7853982;
		inner = min(inner, texture(TEXTURE, UV + vec2(cos(ang), sin(ang)) * px * 0.6).a);
	}
	col = mix(ink.rgb, col, mix(0.45, 1.0, inner));
	float alpha = max(c.a, a * ink.a);
	COLOR = vec4(mix(ink.rgb, col, c.a), alpha) * ghost;
}
