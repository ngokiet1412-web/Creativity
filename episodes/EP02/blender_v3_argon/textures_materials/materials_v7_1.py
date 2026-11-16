"""V7.1 Cinematic Industrial PBR Material Library (Dual EEVEE + Cycles Compatible).

Replaces Cycles-only Pointiness with ShaderNodeAmbientOcclusion + LayerWeight Fresnel +
multi-scale anisotropic noise and directional quarry dust, plus animated hydraulic flow pulses.
"""

import bpy


def _lin(srgb):
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in srgb)


def _new_mat(name):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (820, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (460, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat, nt, bsdf, out


def _bump(nt, height_sock, strength=0.05, distance=0.0015, y=-260):
    b = nt.nodes.new("ShaderNodeBump")
    b.location = (220, y)
    b.inputs["Strength"].default_value = strength
    b.inputs["Distance"].default_value = distance
    nt.links.new(height_sock, b.inputs["Height"])
    return b


def build_v71_materials():
    mats = {}

    # 1. Komatsu Amber Enamel with Ambient Occlusion crevice grime + Pointiness edge wear
    mat, nt, bsdf, _ = _new_mat("MAT_Komatsu_Yellow_V71")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-900, 0)

    n_macro = nt.nodes.new("ShaderNodeTexNoise")
    n_macro.location = (-640, 220)
    n_macro.inputs["Scale"].default_value = 3.8
    n_macro.inputs["Detail"].default_value = 6.0
    n_macro.inputs["Roughness"].default_value = 0.58
    nt.links.new(tc.outputs["Object"], n_macro.inputs["Vector"])

    n_micro = nt.nodes.new("ShaderNodeTexNoise")
    n_micro.location = (-640, -160)
    n_micro.inputs["Scale"].default_value = 165.0
    n_micro.inputs["Detail"].default_value = 7.0
    n_micro.inputs["Roughness"].default_value = 0.60
    nt.links.new(tc.outputs["Object"], n_micro.inputs["Vector"])

    mix_paint = nt.nodes.new("ShaderNodeMix")
    mix_paint.data_type = "RGBA"
    mix_paint.location = (-360, 220)
    mix_paint.inputs["A"].default_value = (*_lin((0.75, 0.42, 0.015)), 1.0)
    mix_paint.inputs["B"].default_value = (*_lin((0.52, 0.27, 0.010)), 1.0)
    nt.links.new(n_macro.outputs["Fac"], mix_paint.inputs["Factor"])

    # AO darkening in joints, stiffener welds, bolt pockets (works in BOTH EEVEE & Cycles!)
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
    ao.location = (-360, 460)
    ao.samples = 8
    ao.inputs["Distance"].default_value = 0.16
    nt.links.new(mix_paint.outputs["Result"], ao.inputs["Color"])

    ramp_ao = nt.nodes.new("ShaderNodeValToRGB")
    ramp_ao.location = (-160, 460)
    ramp_ao.color_ramp.elements[0].position = 0.28
    ramp_ao.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    ramp_ao.color_ramp.elements[1].position = 0.80
    ramp_ao.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    nt.links.new(ao.outputs["AO"], ramp_ao.inputs["Fac"])

    mix_crevice = nt.nodes.new("ShaderNodeMix")
    mix_crevice.data_type = "RGBA"
    mix_crevice.location = (60, 380)
    nt.links.new(ramp_ao.outputs["Color"], mix_crevice.inputs["Factor"])
    mix_crevice.inputs["A"].default_value = (*_lin((0.19, 0.11, 0.025)), 1.0)
    nt.links.new(mix_paint.outputs["Result"], mix_crevice.inputs["B"])

    # Pointiness edge wear toward primer/steel for Cycles hero stills (0.5 constant in EEVEE -> zero washout)
    geom = nt.nodes.new("ShaderNodeNewGeometry")
    geom.location = (-360, 660)
    ramp_edge = nt.nodes.new("ShaderNodeValToRGB")
    ramp_edge.location = (-160, 660)
    ramp_edge.color_ramp.elements[0].position = 0.525
    ramp_edge.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    ramp_edge.color_ramp.elements[1].position = 0.575
    ramp_edge.color_ramp.elements[1].color = (0.60, 0.60, 0.60, 1.0)
    nt.links.new(geom.outputs["Pointiness"], ramp_edge.inputs["Fac"])

    mix_wear = nt.nodes.new("ShaderNodeMix")
    mix_wear.data_type = "RGBA"
    mix_wear.location = (240, 320)
    nt.links.new(ramp_edge.outputs["Color"], mix_wear.inputs["Factor"])
    nt.links.new(mix_crevice.outputs["Result"], mix_wear.inputs["A"])
    mix_wear.inputs["B"].default_value = (*_lin((0.22, 0.20, 0.18)), 1.0)

    map_r = nt.nodes.new("ShaderNodeMapRange")
    map_r.location = (180, -20)
    map_r.inputs["To Min"].default_value = 0.28
    map_r.inputs["To Max"].default_value = 0.45
    nt.links.new(n_macro.outputs["Fac"], map_r.inputs["Value"])

    map_m = nt.nodes.new("ShaderNodeMapRange")
    map_m.location = (180, 120)
    map_m.inputs["To Min"].default_value = 0.10
    map_m.inputs["To Max"].default_value = 0.55
    nt.links.new(ramp_edge.outputs["Color"], map_m.inputs["Value"])

    bump = _bump(nt, n_micro.outputs["Fac"], strength=0.068, distance=0.0013)
    nt.links.new(mix_wear.outputs["Result"], bsdf.inputs["Base Color"])
    nt.links.new(map_m.outputs["Result"], bsdf.inputs["Metallic"])
    nt.links.new(map_r.outputs["Result"], bsdf.inputs["Roughness"])
    bsdf.inputs["Coat Weight"].default_value = 0.18
    bsdf.inputs["Coat Roughness"].default_value = 0.22
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    mat.diffuse_color = (*_lin((0.75, 0.42, 0.015)), 1.0)
    mats["yellow"] = mat

    # 2. Dark Forged Structural Steel (Girders, I-beams, Glands, Gussets, Clamps)
    mat, nt, bsdf, _ = _new_mat("MAT_Dark_Forged_Steel_V71")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    n_steel = nt.nodes.new("ShaderNodeTexNoise")
    n_steel.inputs["Scale"].default_value = 46.0
    n_steel.inputs["Detail"].default_value = 8.0
    n_steel.inputs["Roughness"].default_value = 0.65
    nt.links.new(tc.outputs["Object"], n_steel.inputs["Vector"])

    ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
    ao.samples = 8
    ao.inputs["Distance"].default_value = 0.18

    mix_s = nt.nodes.new("ShaderNodeMix")
    mix_s.data_type = "RGBA"
    mix_s.inputs["A"].default_value = (*_lin((0.06, 0.07, 0.085)), 1.0)
    mix_s.inputs["B"].default_value = (*_lin((0.16, 0.18, 0.20)), 1.0)
    nt.links.new(ao.outputs["AO"], mix_s.inputs["Factor"])

    map_r = nt.nodes.new("ShaderNodeMapRange")
    map_r.inputs["To Min"].default_value = 0.28
    map_r.inputs["To Max"].default_value = 0.50
    nt.links.new(n_steel.outputs["Fac"], map_r.inputs["Value"])

    bump = _bump(nt, n_steel.outputs["Fac"], strength=0.09, distance=0.0018)
    nt.links.new(mix_s.outputs["Result"], bsdf.inputs["Base Color"])
    bsdf.inputs["Metallic"].default_value = 0.90
    nt.links.new(map_r.outputs["Result"], bsdf.inputs["Roughness"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    mat.diffuse_color = (*_lin((0.12, 0.135, 0.15)), 1.0)
    mats["dark_steel"] = mat

    # 3. Hard Chrome Piston Rod (Crisp industrial mirror with fine linear honing)
    mat, nt, bsdf, _ = _new_mat("MAT_Hard_Chrome_Rod_V71")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.5, 45.0, 45.0)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    n_hone = nt.nodes.new("ShaderNodeTexNoise")
    n_hone.inputs["Scale"].default_value = 14.0
    n_hone.inputs["Detail"].default_value = 5.0
    nt.links.new(mp.outputs["Vector"], n_hone.inputs["Vector"])
    map_r = nt.nodes.new("ShaderNodeMapRange")
    map_r.inputs["To Min"].default_value = 0.032
    map_r.inputs["To Max"].default_value = 0.062
    nt.links.new(n_hone.outputs["Fac"], map_r.inputs["Value"])
    bsdf.inputs["Base Color"].default_value = (*_lin((0.88, 0.91, 0.94)), 1.0)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Coat Weight"].default_value = 0.10
    bsdf.inputs["Coat Roughness"].default_value = 0.04
    nt.links.new(map_r.outputs["Result"], bsdf.inputs["Roughness"])
    mat.diffuse_color = (*_lin((0.88, 0.91, 0.94)), 1.0)
    mats["chrome"] = mat

    # 4. Machined Alloy Pin & Bolt Steel
    mat, nt, bsdf, _ = _new_mat("MAT_Machined_Pin_Steel_V71")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    n_turn = nt.nodes.new("ShaderNodeTexNoise")
    n_turn.inputs["Scale"].default_value = 110.0
    n_turn.inputs["Detail"].default_value = 6.0
    nt.links.new(tc.outputs["Object"], n_turn.inputs["Vector"])
    map_r = nt.nodes.new("ShaderNodeMapRange")
    map_r.inputs["To Min"].default_value = 0.18
    map_r.inputs["To Max"].default_value = 0.32
    nt.links.new(n_turn.outputs["Fac"], map_r.inputs["Value"])
    bump = _bump(nt, n_turn.outputs["Fac"], strength=0.045, distance=0.0008)
    bsdf.inputs["Base Color"].default_value = (*_lin((0.50, 0.52, 0.56)), 1.0)
    bsdf.inputs["Metallic"].default_value = 0.96
    nt.links.new(map_r.outputs["Result"], bsdf.inputs["Roughness"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    mat.diffuse_color = (*_lin((0.50, 0.52, 0.56)), 1.0)
    mats["machined_steel"] = mat

    # 5. Weathered Manganese Bucket Steel (Quarry dust Voronoi patina + Noise scrapes + AO recesses)
    mat, nt, bsdf, _ = _new_mat("MAT_Weathered_Bucket_V71")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.2, 4.5, 2.8)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])

    n_scrape = nt.nodes.new("ShaderNodeTexNoise")
    n_scrape.inputs["Scale"].default_value = 34.0
    n_scrape.inputs["Detail"].default_value = 9.0
    n_scrape.inputs["Roughness"].default_value = 0.72
    nt.links.new(mp.outputs["Vector"], n_scrape.inputs["Vector"])

    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 62.0
    nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])

    ramp_dust = nt.nodes.new("ShaderNodeValToRGB")
    ramp_dust.color_ramp.elements[0].position = 0.48
    ramp_dust.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    ramp_dust.color_ramp.elements[1].position = 0.76
    ramp_dust.color_ramp.elements[1].color = (0.45, 0.45, 0.45, 1.0)
    nt.links.new(n_scrape.outputs["Fac"], ramp_dust.inputs["Fac"])

    mix_b = nt.nodes.new("ShaderNodeMix")
    mix_b.data_type = "RGBA"
    nt.links.new(ramp_dust.outputs["Color"], mix_b.inputs["Factor"])
    mix_b.inputs["A"].default_value = (*_lin((0.12, 0.13, 0.145)), 1.0)
    mix_b.inputs["B"].default_value = (*_lin((0.24, 0.19, 0.14)), 1.0)

    ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
    ao.samples = 8
    ao.inputs["Distance"].default_value = 0.20

    ramp_bao = nt.nodes.new("ShaderNodeValToRGB")
    ramp_bao.color_ramp.elements[0].position = 0.25
    ramp_bao.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    ramp_bao.color_ramp.elements[1].position = 0.85
    ramp_bao.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    nt.links.new(ao.outputs["AO"], ramp_bao.inputs["Fac"])

    mix_b_ao = nt.nodes.new("ShaderNodeMix")
    mix_b_ao.data_type = "RGBA"
    nt.links.new(ramp_bao.outputs["Color"], mix_b_ao.inputs["Factor"])
    mix_b_ao.inputs["A"].default_value = (*_lin((0.16, 0.12, 0.085)), 1.0)
    nt.links.new(mix_b.outputs["Result"], mix_b_ao.inputs["B"])

    map_m = nt.nodes.new("ShaderNodeMapRange")
    map_m.inputs["To Min"].default_value = 0.88
    map_m.inputs["To Max"].default_value = 0.34
    nt.links.new(ramp_dust.outputs["Color"], map_m.inputs["Value"])

    map_r = nt.nodes.new("ShaderNodeMapRange")
    map_r.inputs["To Min"].default_value = 0.32
    map_r.inputs["To Max"].default_value = 0.72
    nt.links.new(ramp_dust.outputs["Color"], map_r.inputs["Value"])

    bump = _bump(nt, vor.outputs["Distance"], strength=0.11, distance=0.0018)
    nt.links.new(mix_b_ao.outputs["Result"], bsdf.inputs["Base Color"])
    nt.links.new(map_m.outputs["Result"], bsdf.inputs["Metallic"])
    nt.links.new(map_r.outputs["Result"], bsdf.inputs["Roughness"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    mat.diffuse_color = (*_lin((0.14, 0.15, 0.16)), 1.0)
    mats["bucket_steel"] = mat

    # 6. Forged Alloy Bucket Teeth (Burnished rock-polished tips)
    mat, nt, bsdf, _ = _new_mat("MAT_Forged_Teeth_V71")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    n_t = nt.nodes.new("ShaderNodeTexNoise")
    n_t.inputs["Scale"].default_value = 42.0
    n_t.inputs["Detail"].default_value = 8.0
    nt.links.new(tc.outputs["Object"], n_t.inputs["Vector"])
    mix_t = nt.nodes.new("ShaderNodeMix")
    mix_t.data_type = "RGBA"
    mix_t.inputs["A"].default_value = (*_lin((0.26, 0.23, 0.20)), 1.0)
    mix_t.inputs["B"].default_value = (*_lin((0.52, 0.50, 0.48)), 1.0)
    nt.links.new(n_t.outputs["Fac"], mix_t.inputs["Factor"])
    map_r = nt.nodes.new("ShaderNodeMapRange")
    map_r.inputs["To Min"].default_value = 0.22
    map_r.inputs["To Max"].default_value = 0.48
    nt.links.new(n_t.outputs["Fac"], map_r.inputs["Value"])
    bump = _bump(nt, n_t.outputs["Fac"], strength=0.12, distance=0.002)
    nt.links.new(mix_t.outputs["Result"], bsdf.inputs["Base Color"])
    bsdf.inputs["Metallic"].default_value = 0.88
    nt.links.new(map_r.outputs["Result"], bsdf.inputs["Roughness"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    mat.diffuse_color = (*_lin((0.38, 0.36, 0.34)), 1.0)
    mats["forged_teeth"] = mat

    # 7. Spiral-Braided Hydraulic Rubber Hose
    mat, nt, bsdf, _ = _new_mat("MAT_Hydraulic_Hose_V71")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    n_h = nt.nodes.new("ShaderNodeTexNoise")
    n_h.inputs["Scale"].default_value = 210.0
    n_h.inputs["Detail"].default_value = 6.0
    nt.links.new(tc.outputs["Object"], n_h.inputs["Vector"])
    bump = _bump(nt, n_h.outputs["Fac"], strength=0.18, distance=0.0014)
    bsdf.inputs["Base Color"].default_value = (*_lin((0.045, 0.048, 0.052)), 1.0)
    bsdf.inputs["Metallic"].default_value = 0.04
    bsdf.inputs["Roughness"].default_value = 0.72
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    mat.diffuse_color = (*_lin((0.05, 0.052, 0.056)), 1.0)
    mats["rubber_hose"] = mat

    # 8. Cutaway Engineering Faces & Multi-material Piston Internals
    mat, nt, bsdf, _ = _new_mat("MAT_Cutaway_Section_V71")
    bsdf.inputs["Base Color"].default_value = (*_lin((0.88, 0.26, 0.07)), 1.0)
    bsdf.inputs["Metallic"].default_value = 0.28
    bsdf.inputs["Roughness"].default_value = 0.32
    mat.diffuse_color = (*_lin((0.88, 0.26, 0.07)), 1.0)
    mats["cutaway_section"] = mat

    mat, nt, bsdf, _ = _new_mat("MAT_Bronze_WearBand_V71")
    bsdf.inputs["Base Color"].default_value = (*_lin((0.80, 0.52, 0.16)), 1.0)
    bsdf.inputs["Metallic"].default_value = 0.94
    bsdf.inputs["Roughness"].default_value = 0.20
    mat.diffuse_color = (*_lin((0.80, 0.52, 0.16)), 1.0)
    mats["bronze_guide"] = mat

    mat, nt, bsdf, _ = _new_mat("MAT_PTFE_Seal_V71")
    bsdf.inputs["Base Color"].default_value = (*_lin((0.12, 0.14, 0.16)), 1.0)
    bsdf.inputs["Metallic"].default_value = 0.05
    bsdf.inputs["Roughness"].default_value = 0.42
    mats["ptfe_seal"] = mat

    # 9. Animated Pulse Translucent Hydraulic Oils (phase controlled by Value node keyed per frame!)
    def make_animated_fluid(mname, base_rgb, pulse_rgb, alpha_mix=0.46, em_strength=0.38):
        m, mnt, _, _ = _new_mat(mname)
        mnt.nodes.clear()
        mout = mnt.nodes.new("ShaderNodeOutputMaterial")
        tc_f = mnt.nodes.new("ShaderNodeTexCoord")
        sep = mnt.nodes.new("ShaderNodeSeparateXYZ")
        mnt.links.new(tc_f.outputs["Object"], sep.inputs["Vector"])

        phase_val = mnt.nodes.new("ShaderNodeValue")
        phase_val.name = "FlowPhase"
        phase_val.outputs[0].default_value = 0.0

        add_p = mnt.nodes.new("ShaderNodeMath")
        add_p.operation = "SUBTRACT"
        mnt.links.new(sep.outputs["X"], add_p.inputs[0])
        mnt.links.new(phase_val.outputs[0], add_p.inputs[1])

        wave = mnt.nodes.new("ShaderNodeTexWave")
        wave.wave_type = "BANDS"
        wave.bands_direction = "X"
        wave.wave_profile = "SIN"
        wave.inputs["Scale"].default_value = 2.6
        wave.inputs["Distortion"].default_value = 0.35

        comb = mnt.nodes.new("ShaderNodeCombineXYZ")
        mnt.links.new(add_p.outputs[0], comb.inputs["X"])
        mnt.links.new(comb.outputs["Vector"], wave.inputs["Vector"])

        map_col = mnt.nodes.new("ShaderNodeMapRange")
        map_col.inputs["To Min"].default_value = 0.0
        map_col.inputs["To Max"].default_value = 0.65
        mnt.links.new(wave.outputs["Fac"], map_col.inputs["Value"])

        mix_em = mnt.nodes.new("ShaderNodeMix")
        mix_em.data_type = "RGBA"
        mix_em.inputs["A"].default_value = (*_lin(base_rgb), 1.0)
        mix_em.inputs["B"].default_value = (*_lin(pulse_rgb), 1.0)
        mnt.links.new(map_col.outputs["Result"], mix_em.inputs["Factor"])

        map_str = mnt.nodes.new("ShaderNodeMapRange")
        map_str.inputs["To Min"].default_value = max(0.15, em_strength - 0.12)
        map_str.inputs["To Max"].default_value = em_strength + 0.12
        mnt.links.new(wave.outputs["Fac"], map_str.inputs["Value"])

        transp = mnt.nodes.new("ShaderNodeBsdfTransparent")
        transp.inputs["Color"].default_value = (*_lin(base_rgb), 1.0)

        glossy = mnt.nodes.new("ShaderNodeBsdfPrincipled")
        mnt.links.new(mix_em.outputs["Result"], glossy.inputs["Base Color"])
        glossy.inputs["Roughness"].default_value = 0.08
        mnt.links.new(mix_em.outputs["Result"], glossy.inputs["Emission Color"])
        mnt.links.new(map_str.outputs["Result"], glossy.inputs["Emission Strength"])

        mix_sh = mnt.nodes.new("ShaderNodeMixShader")
        mix_sh.inputs["Fac"].default_value = alpha_mix
        mnt.links.new(transp.outputs[0], mix_sh.inputs[1])
        mnt.links.new(glossy.outputs[0], mix_sh.inputs[2])
        mnt.links.new(mix_sh.outputs[0], mout.inputs["Surface"])

        m.diffuse_color = (*_lin(base_rgb), alpha_mix)
        m.surface_render_method = "BLENDED"
        return m, phase_val, tc_f

    mats["oil_supply"], mats["oil_supply_phase"], mats["oil_supply_tc"] = make_animated_fluid(
        "MAT_Hydraulic_Oil_Supply_Red_V71", (0.85, 0.11, 0.04), (1.0, 0.28, 0.08), alpha_mix=0.48, em_strength=0.38
    )
    mats["oil_return"], mats["oil_return_phase"], mats["oil_return_tc"] = make_animated_fluid(
        "MAT_Hydraulic_Oil_Return_Blue_V71", (0.05, 0.38, 0.85), (0.16, 0.62, 1.00), alpha_mix=0.44, em_strength=0.36
    )

    # Solid non-transparent luminous oil arrow indicator
    for key, mname, col, strength in (
        ("arrow_red", "MAT_Arrow_Supply_Red_V71", (0.98, 0.22, 0.04), 2.2),
        ("arrow_blue", "MAT_Arrow_Return_Blue_V71", (0.12, 0.65, 1.0), 2.0),
        ("reticle_cyan", "MAT_Pin_Reticle_Cyan_V71", (0.28, 0.88, 1.0), 2.4),
        ("hud_gold", "MAT_HUD_Text_Gold_V71", (0.98, 0.68, 0.14), 1.8),
        ("hud_white", "MAT_HUD_Text_White_V71", (0.92, 0.96, 1.0), 1.6),
    ):
        m, mnt, _, _ = _new_mat(mname)
        mnt.nodes.clear()
        em = mnt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = (*_lin(col), 1.0)
        em.inputs["Strength"].default_value = strength
        mout = mnt.nodes.new("ShaderNodeOutputMaterial")
        mnt.links.new(em.outputs["Emission"], mout.inputs["Surface"])
        m.diffuse_color = (*_lin(col), 1.0)
        mats[key] = m

    # Dark Glass Callout Panel
    mbg, bnt, _, _ = _new_mat("MAT_HUD_Backing_V71")
    bnt.nodes.clear()
    bout = bnt.nodes.new("ShaderNodeOutputMaterial")
    btr = bnt.nodes.new("ShaderNodeBsdfTransparent")
    bpr = bnt.nodes.new("ShaderNodeBsdfPrincipled")
    bpr.inputs["Base Color"].default_value = (*_lin((0.015, 0.022, 0.032)), 1.0)
    bpr.inputs["Roughness"].default_value = 0.32
    bmix = bnt.nodes.new("ShaderNodeMixShader")
    bmix.inputs["Fac"].default_value = 0.84
    bnt.links.new(btr.outputs[0], bmix.inputs[1])
    bnt.links.new(bpr.outputs[0], bmix.inputs[2])
    bnt.links.new(bmix.outputs[0], bout.inputs["Surface"])
    mbg.surface_render_method = "BLENDED"
    mats["hud_backing"] = mbg

    # 10. Excavated Soil Load & Clods
    mat, nt, bsdf, _ = _new_mat("MAT_Excavated_Soil_V71")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    n_s = nt.nodes.new("ShaderNodeTexNoise")
    n_s.inputs["Scale"].default_value = 22.0
    n_s.inputs["Detail"].default_value = 10.0
    n_s.inputs["Roughness"].default_value = 0.78
    nt.links.new(tc.outputs["Object"], n_s.inputs["Vector"])
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 34.0
    nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
    mix_c = nt.nodes.new("ShaderNodeMix")
    mix_c.data_type = "RGBA"
    mix_c.inputs["A"].default_value = (*_lin((0.18, 0.12, 0.075)), 1.0)
    mix_c.inputs["B"].default_value = (*_lin((0.34, 0.24, 0.15)), 1.0)
    nt.links.new(n_s.outputs["Fac"], mix_c.inputs["Factor"])
    bump = _bump(nt, vor.outputs["Distance"], strength=0.72, distance=0.015)
    nt.links.new(mix_c.outputs["Result"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.94
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    mat.diffuse_color = (*_lin((0.26, 0.18, 0.12)), 1.0)
    mats["soil"] = mat

    # 11. Concrete Test Bay Floor, Structural I-Beam Stand, Distant Steel Architecture
    mat, nt, bsdf, _ = _new_mat("MAT_Industrial_Floor_V71")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    n_c1 = nt.nodes.new("ShaderNodeTexNoise")
    n_c1.inputs["Scale"].default_value = 1.6
    n_c1.inputs["Detail"].default_value = 8.0
    nt.links.new(tc.outputs["Object"], n_c1.inputs["Vector"])
    n_c2 = nt.nodes.new("ShaderNodeTexNoise")
    n_c2.inputs["Scale"].default_value = 22.0
    n_c2.inputs["Detail"].default_value = 8.0
    nt.links.new(tc.outputs["Object"], n_c2.inputs["Vector"])
    mix_f = nt.nodes.new("ShaderNodeMix")
    mix_f.data_type = "RGBA"
    mix_f.inputs["A"].default_value = (*_lin((0.055, 0.062, 0.072)), 1.0)
    mix_f.inputs["B"].default_value = (*_lin((0.105, 0.112, 0.122)), 1.0)
    nt.links.new(n_c1.outputs["Fac"], mix_f.inputs["Factor"])
    map_r = nt.nodes.new("ShaderNodeMapRange")
    map_r.inputs["To Min"].default_value = 0.45
    map_r.inputs["To Max"].default_value = 0.86
    nt.links.new(n_c1.outputs["Fac"], map_r.inputs["Value"])
    bump = _bump(nt, n_c2.outputs["Fac"], strength=0.14, distance=0.008)
    nt.links.new(mix_f.outputs["Result"], bsdf.inputs["Base Color"])
    nt.links.new(map_r.outputs["Result"], bsdf.inputs["Roughness"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    mat.diffuse_color = (*_lin((0.07, 0.078, 0.09)), 1.0)
    mats["floor"] = mat

    mat, nt, bsdf, _ = _new_mat("MAT_Test_Stand_V71")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    n_ts = nt.nodes.new("ShaderNodeTexNoise")
    n_ts.inputs["Scale"].default_value = 26.0
    n_ts.inputs["Detail"].default_value = 6.0
    nt.links.new(tc.outputs["Object"], n_ts.inputs["Vector"])
    bump = _bump(nt, n_ts.outputs["Fac"], strength=0.07, distance=0.002)
    bsdf.inputs["Base Color"].default_value = (*_lin((0.11, 0.128, 0.15)), 1.0)
    bsdf.inputs["Metallic"].default_value = 0.82
    bsdf.inputs["Roughness"].default_value = 0.42
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    mat.diffuse_color = (*_lin((0.11, 0.128, 0.15)), 1.0)
    mats["test_stand"] = mat

    mat, nt, bsdf, _ = _new_mat("MAT_Bay_Steel_Arch_V71")
    bsdf.inputs["Base Color"].default_value = (*_lin((0.055, 0.065, 0.080)), 1.0)
    bsdf.inputs["Metallic"].default_value = 0.65
    bsdf.inputs["Roughness"].default_value = 0.58
    mat.diffuse_color = (*_lin((0.055, 0.065, 0.080)), 1.0)
    mats["bay_arch"] = mat

    return mats
