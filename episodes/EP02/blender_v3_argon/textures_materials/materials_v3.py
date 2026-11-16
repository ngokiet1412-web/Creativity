"""Procedural Industrial PBR Material Library for EP02 PC200-8 V3 Cinematic Render (Blender 5.3)."""

import bpy


def _lin(srgb):
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in srgb)


def _new_mat(name):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (650, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (320, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat, nt, bsdf, out


def _add_coord_noise(nt, scale=12.0, detail=6.0, roughness=0.55):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-750, 0)
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = (-500, 0)
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = detail
    noise.inputs["Roughness"].default_value = roughness
    nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
    return tc, noise


def _add_bump(nt, height_socket, strength=0.05, distance=0.002):
    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (80, -240)
    bump.inputs["Strength"].default_value = strength
    bump.inputs["Distance"].default_value = distance
    nt.links.new(height_socket, bump.inputs["Height"])
    return bump


def build_materials_library():
    mats = {}

    # 1. Komatsu Industrial Amber-Yellow Enamel with subtle edge wear & orange-peel grain
    mat, nt, bsdf, _ = _new_mat("MAT_Komatsu_Industrial_Yellow")
    tc, noise_micro = _add_coord_noise(nt, scale=140.0, detail=6.0, roughness=0.6)
    noise_macro = nt.nodes.new("ShaderNodeTexNoise")
    noise_macro.location = (-500, 220)
    noise_macro.inputs["Scale"].default_value = 3.5
    noise_macro.inputs["Detail"].default_value = 5.0
    nt.links.new(tc.outputs["Object"], noise_macro.inputs["Vector"])

    # Base color blend between rich Komatsu amber-gold and deeper weathered ochre (tuned for AgX)
    mix_col = nt.nodes.new("ShaderNodeMix")
    mix_col.data_type = "RGBA"
    mix_col.location = (-160, 220)
    mix_col.inputs["A"].default_value = (*_lin((0.76, 0.44, 0.018)), 1.0)
    mix_col.inputs["B"].default_value = (*_lin((0.55, 0.30, 0.012)), 1.0)
    nt.links.new(noise_macro.outputs["Fac"], mix_col.inputs["Factor"])

    # Subtle edge/weld pointiness wear toward primer-steel
    geom = nt.nodes.new("ShaderNodeNewGeometry")
    geom.location = (-500, 420)
    ramp_edge = nt.nodes.new("ShaderNodeValToRGB")
    ramp_edge.location = (-260, 420)
    ramp_edge.color_ramp.elements[0].position = 0.525
    ramp_edge.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    ramp_edge.color_ramp.elements[1].position = 0.575
    ramp_edge.color_ramp.elements[1].color = (0.65, 0.65, 0.65, 1.0)
    nt.links.new(geom.outputs["Pointiness"], ramp_edge.inputs["Fac"])

    mix_wear = nt.nodes.new("ShaderNodeMix")
    mix_wear.data_type = "RGBA"
    mix_wear.location = (60, 260)
    nt.links.new(ramp_edge.outputs["Color"], mix_wear.inputs["Factor"])
    nt.links.new(mix_col.outputs["Result"], mix_wear.inputs["A"])
    mix_wear.inputs["B"].default_value = (*_lin((0.20, 0.19, 0.18)), 1.0)

    # Roughness variation (0.28 .. 0.46)
    map_r = nt.nodes.new("ShaderNodeMapRange")
    map_r.location = (40, 20)
    map_r.inputs["To Min"].default_value = 0.28
    map_r.inputs["To Max"].default_value = 0.46
    nt.links.new(noise_macro.outputs["Fac"], map_r.inputs["Value"])

    # Metallic subtle mix only at worn edges
    map_m = nt.nodes.new("ShaderNodeMapRange")
    map_m.location = (40, 120)
    map_m.inputs["To Min"].default_value = 0.12
    map_m.inputs["To Max"].default_value = 0.72
    nt.links.new(ramp_edge.outputs["Color"], map_m.inputs["Value"])

    bump = _add_bump(nt, noise_micro.outputs["Fac"], strength=0.075, distance=0.0014)
    nt.links.new(mix_wear.outputs["Result"], bsdf.inputs["Base Color"])
    nt.links.new(map_m.outputs["Result"], bsdf.inputs["Metallic"])
    nt.links.new(map_r.outputs["Result"], bsdf.inputs["Roughness"])
    bsdf.inputs["Coat Weight"].default_value = 0.16
    bsdf.inputs["Coat Roughness"].default_value = 0.24
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    mat.diffuse_color = (*_lin((0.76, 0.44, 0.018)), 1.0)
    mats["yellow"] = mat

    # 2. Dark Structural / Forged Steel (Girders, Clevis Flanges, Cylinder Glands)
    mat, nt, bsdf, _ = _new_mat("MAT_Dark_Structural_Steel")
    tc, noise = _add_coord_noise(nt, scale=42.0, detail=7.0, roughness=0.65)
    mix_c = nt.nodes.new("ShaderNodeMix")
    mix_c.data_type = "RGBA"
    mix_c.location = (-120, 140)
    mix_c.inputs["A"].default_value = (*_lin((0.10, 0.115, 0.135)), 1.0)
    mix_c.inputs["B"].default_value = (*_lin((0.18, 0.195, 0.215)), 1.0)
    nt.links.new(noise.outputs["Fac"], mix_c.inputs["Factor"])
    map_r = nt.nodes.new("ShaderNodeMapRange")
    map_r.location = (40, -20)
    map_r.inputs["To Min"].default_value = 0.34
    map_r.inputs["To Max"].default_value = 0.54
    nt.links.new(noise.outputs["Fac"], map_r.inputs["Value"])
    bump = _add_bump(nt, noise.outputs["Fac"], strength=0.08, distance=0.0018)
    nt.links.new(mix_c.outputs["Result"], bsdf.inputs["Base Color"])
    bsdf.inputs["Metallic"].default_value = 0.88
    nt.links.new(map_r.outputs["Result"], bsdf.inputs["Roughness"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    mat.diffuse_color = (*_lin((0.14, 0.155, 0.175)), 1.0)
    mats["dark_steel"] = mat

    # 3. Hard Chrome Piston Rod (Mirror metallic with micro-honed sheen)
    mat, nt, bsdf, _ = _new_mat("MAT_Hard_Chrome_Rod")
    _, noise = _add_coord_noise(nt, scale=220.0, detail=4.0, roughness=0.4)
    map_r = nt.nodes.new("ShaderNodeMapRange")
    map_r.location = (40, -20)
    map_r.inputs["To Min"].default_value = 0.042
    map_r.inputs["To Max"].default_value = 0.082
    nt.links.new(noise.outputs["Fac"], map_r.inputs["Value"])
    bsdf.inputs["Base Color"].default_value = (*_lin((0.86, 0.89, 0.92)), 1.0)
    bsdf.inputs["Metallic"].default_value = 1.0
    nt.links.new(map_r.outputs["Result"], bsdf.inputs["Roughness"])
    mat.diffuse_color = (*_lin((0.86, 0.89, 0.92)), 1.0)
    mats["chrome"] = mat

    # 4. Machined Alloy Steel (Pivot Pins, Boss Collars, SAE Hydraulic Ports)
    mat, nt, bsdf, _ = _new_mat("MAT_Machined_Pin_Steel")
    _, noise = _add_coord_noise(nt, scale=95.0, detail=6.0, roughness=0.55)
    map_r = nt.nodes.new("ShaderNodeMapRange")
    map_r.location = (40, -20)
    map_r.inputs["To Min"].default_value = 0.20
    map_r.inputs["To Max"].default_value = 0.34
    nt.links.new(noise.outputs["Fac"], map_r.inputs["Value"])
    bump = _add_bump(nt, noise.outputs["Fac"], strength=0.04, distance=0.0008)
    bsdf.inputs["Base Color"].default_value = (*_lin((0.46, 0.48, 0.51)), 1.0)
    bsdf.inputs["Metallic"].default_value = 0.94
    nt.links.new(map_r.outputs["Result"], bsdf.inputs["Roughness"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    mat.diffuse_color = (*_lin((0.46, 0.48, 0.51)), 1.0)
    mats["machined_steel"] = mat

    # 5. Weathered Bucket Steel (Fine quarry dust patina + brushed manganese wear, non-camo)
    mat, nt, bsdf, _ = _new_mat("MAT_Weathered_Bucket_Steel")
    tc, noise = _add_coord_noise(nt, scale=36.0, detail=9.0, roughness=0.72)
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.location = (-500, 220)
    vor.inputs["Scale"].default_value = 65.0
    nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])

    ramp_dust = nt.nodes.new("ShaderNodeValToRGB")
    ramp_dust.location = (-220, 220)
    ramp_dust.color_ramp.elements[0].position = 0.50
    ramp_dust.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    ramp_dust.color_ramp.elements[1].position = 0.78
    ramp_dust.color_ramp.elements[1].color = (0.45, 0.45, 0.45, 1.0)
    nt.links.new(noise.outputs["Fac"], ramp_dust.inputs["Fac"])

    mix_col = nt.nodes.new("ShaderNodeMix")
    mix_col.data_type = "RGBA"
    mix_col.location = (50, 220)
    nt.links.new(ramp_dust.outputs["Color"], mix_col.inputs["Factor"])
    mix_col.inputs["A"].default_value = (*_lin((0.12, 0.13, 0.145)), 1.0)
    mix_col.inputs["B"].default_value = (*_lin((0.24, 0.19, 0.14)), 1.0)

    map_m = nt.nodes.new("ShaderNodeMapRange")
    map_m.location = (50, 60)
    map_m.inputs["To Min"].default_value = 0.88
    map_m.inputs["To Max"].default_value = 0.30
    nt.links.new(ramp_dust.outputs["Color"], map_m.inputs["Value"])

    map_r = nt.nodes.new("ShaderNodeMapRange")
    map_r.location = (50, -60)
    map_r.inputs["To Min"].default_value = 0.34
    map_r.inputs["To Max"].default_value = 0.76
    nt.links.new(ramp_dust.outputs["Color"], map_r.inputs["Value"])

    bump = _add_bump(nt, vor.outputs["Distance"], strength=0.10, distance=0.0018)
    nt.links.new(mix_col.outputs["Result"], bsdf.inputs["Base Color"])
    nt.links.new(map_m.outputs["Result"], bsdf.inputs["Metallic"])
    nt.links.new(map_r.outputs["Result"], bsdf.inputs["Roughness"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    mat.diffuse_color = (*_lin((0.14, 0.15, 0.16)), 1.0)
    mats["bucket_steel"] = mat

    # 6. Forged Bucket Teeth (Burnt heat-treated alloy + polished tip wear)
    mat, nt, bsdf, _ = _new_mat("MAT_Bucket_Forged_Teeth")
    _, noise = _add_coord_noise(nt, scale=35.0, detail=7.0, roughness=0.65)
    mix_c = nt.nodes.new("ShaderNodeMix")
    mix_c.data_type = "RGBA"
    mix_c.location = (-80, 160)
    mix_c.inputs["A"].default_value = (*_lin((0.24, 0.22, 0.20)), 1.0)
    mix_c.inputs["B"].default_value = (*_lin((0.46, 0.44, 0.41)), 1.0)
    nt.links.new(noise.outputs["Fac"], mix_c.inputs["Factor"])
    map_r = nt.nodes.new("ShaderNodeMapRange")
    map_r.location = (40, -20)
    map_r.inputs["To Min"].default_value = 0.24
    map_r.inputs["To Max"].default_value = 0.56
    nt.links.new(noise.outputs["Fac"], map_r.inputs["Value"])
    bump = _add_bump(nt, noise.outputs["Fac"], strength=0.12, distance=0.002)
    nt.links.new(mix_c.outputs["Result"], bsdf.inputs["Base Color"])
    bsdf.inputs["Metallic"].default_value = 0.84
    nt.links.new(map_r.outputs["Result"], bsdf.inputs["Roughness"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    mat.diffuse_color = (*_lin((0.35, 0.33, 0.30)), 1.0)
    mats["forged_teeth"] = mat

    # 7. Hydraulic Rubber Hose + Crimped Fittings
    mat, nt, bsdf, _ = _new_mat("MAT_Hydraulic_Rubber_Hose")
    _, noise = _add_coord_noise(nt, scale=180.0, detail=5.0, roughness=0.5)
    bump = _add_bump(nt, noise.outputs["Fac"], strength=0.16, distance=0.0012)
    bsdf.inputs["Base Color"].default_value = (*_lin((0.055, 0.058, 0.062)), 1.0)
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.76
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    mat.diffuse_color = (*_lin((0.06, 0.06, 0.065)), 1.0)
    mats["rubber_hose"] = mat

    # 8. Cutaway Section Wall & Phosphor-Bronze Piston Wear Band & Inner Cylinder Honed Wall
    mat, nt, bsdf, _ = _new_mat("MAT_Cutaway_Section_Face")
    bsdf.inputs["Base Color"].default_value = (*_lin((0.86, 0.26, 0.08)), 1.0)
    bsdf.inputs["Metallic"].default_value = 0.25
    bsdf.inputs["Roughness"].default_value = 0.36
    mat.diffuse_color = (*_lin((0.86, 0.26, 0.08)), 1.0)
    mats["cutaway_section"] = mat

    mat, nt, bsdf, _ = _new_mat("MAT_Bronze_Piston_Guide")
    bsdf.inputs["Base Color"].default_value = (*_lin((0.76, 0.50, 0.16)), 1.0)
    bsdf.inputs["Metallic"].default_value = 0.92
    bsdf.inputs["Roughness"].default_value = 0.24
    mat.diffuse_color = (*_lin((0.76, 0.50, 0.16)), 1.0)
    mats["bronze_guide"] = mat

    # 9. Semi-Transparent Hydraulic Fluid Shaders (Chrome Rod remains visible right inside Rod Chamber!)
    def make_fluid_mat(mname, rgb, alpha_mix=0.48, em_strength=0.55):
        m, mnt, _, mout = _new_mat(mname)
        mnt.nodes.clear()
        mout = mnt.nodes.new("ShaderNodeOutputMaterial")
        transp = mnt.nodes.new("ShaderNodeBsdfTransparent")
        transp.inputs["Color"].default_value = (*_lin(rgb), 1.0)
        glossy = mnt.nodes.new("ShaderNodeBsdfPrincipled")
        glossy.inputs["Base Color"].default_value = (*_lin(rgb), 1.0)
        glossy.inputs["Roughness"].default_value = 0.08
        glossy.inputs["Emission Color"].default_value = (*_lin(rgb), 1.0)
        glossy.inputs["Emission Strength"].default_value = em_strength
        mix = mnt.nodes.new("ShaderNodeMixShader")
        mix.inputs["Fac"].default_value = alpha_mix
        mnt.links.new(transp.outputs[0], mix.inputs[1])
        mnt.links.new(glossy.outputs[0], mix.inputs[2])
        mnt.links.new(mix.outputs[0], mout.inputs["Surface"])
        m.diffuse_color = (*_lin(rgb), alpha_mix)
        m.surface_render_method = "BLENDED"
        return m

    mats["oil_supply"] = make_fluid_mat("MAT_Hydraulic_Oil_Supply_Red", (0.94, 0.16, 0.04), alpha_mix=0.52, em_strength=0.72)
    mats["oil_return"] = make_fluid_mat("MAT_Hydraulic_Oil_Return_Blue", (0.06, 0.48, 0.92), alpha_mix=0.40, em_strength=0.45)

    mat_bg, bnt, _, _ = _new_mat("MAT_HUD_Backing_Glass")
    bnt.nodes.clear()
    bout = bnt.nodes.new("ShaderNodeOutputMaterial")
    btransp = bnt.nodes.new("ShaderNodeBsdfTransparent")
    bdiff = bnt.nodes.new("ShaderNodeBsdfPrincipled")
    bdiff.inputs["Base Color"].default_value = (*_lin((0.02, 0.03, 0.045)), 1.0)
    bdiff.inputs["Roughness"].default_value = 0.4
    bmix = bnt.nodes.new("ShaderNodeMixShader")
    bmix.inputs["Fac"].default_value = 0.78
    bnt.links.new(btransp.outputs[0], bmix.inputs[1])
    bnt.links.new(bdiff.outputs[0], bmix.inputs[2])
    bnt.links.new(bmix.outputs[0], bout.inputs["Surface"])
    mat_bg.surface_render_method = "BLENDED"
    mats["hud_backing"] = mat_bg

    # 10. Excavated Soil / Quarry Gravel Payload inside Bucket
    mat, nt, bsdf, _ = _new_mat("MAT_Excavated_Soil_Load")
    tc, noise = _add_coord_noise(nt, scale=18.0, detail=10.0, roughness=0.75)
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.location = (-500, 220)
    vor.inputs["Scale"].default_value = 26.0
    nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
    mix_c = nt.nodes.new("ShaderNodeMix")
    mix_c.data_type = "RGBA"
    mix_c.location = (-80, 140)
    mix_c.inputs["A"].default_value = (*_lin((0.20, 0.14, 0.09)), 1.0)
    mix_c.inputs["B"].default_value = (*_lin((0.36, 0.26, 0.17)), 1.0)
    nt.links.new(noise.outputs["Fac"], mix_c.inputs["Factor"])
    bump = _add_bump(nt, vor.outputs["Distance"], strength=0.65, distance=0.015)
    nt.links.new(mix_c.outputs["Result"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.92
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    mat.diffuse_color = (*_lin((0.28, 0.20, 0.13)), 1.0)
    mats["soil"] = mat

    # 11. Industrial Test-Bay Floor & Heavy Structural Datum Plinth
    mat, nt, bsdf, _ = _new_mat("MAT_Test_Bay_Floor")
    tc, noise = _add_coord_noise(nt, scale=1.8, detail=8.0, roughness=0.68)
    noise_fine = nt.nodes.new("ShaderNodeTexNoise")
    noise_fine.location = (-500, 220)
    noise_fine.inputs["Scale"].default_value = 18.0
    noise_fine.inputs["Detail"].default_value = 8.0
    nt.links.new(tc.outputs["Object"], noise_fine.inputs["Vector"])
    mix_c = nt.nodes.new("ShaderNodeMix")
    mix_c.data_type = "RGBA"
    mix_c.location = (-80, 140)
    mix_c.inputs["A"].default_value = (*_lin((0.065, 0.072, 0.082)), 1.0)
    mix_c.inputs["B"].default_value = (*_lin((0.115, 0.122, 0.135)), 1.0)
    nt.links.new(noise.outputs["Fac"], mix_c.inputs["Factor"])
    map_r = nt.nodes.new("ShaderNodeMapRange")
    map_r.location = (40, -20)
    map_r.inputs["To Min"].default_value = 0.52
    map_r.inputs["To Max"].default_value = 0.85
    nt.links.new(noise.outputs["Fac"], map_r.inputs["Value"])
    bump = _add_bump(nt, noise_fine.outputs["Fac"], strength=0.14, distance=0.008)
    nt.links.new(mix_c.outputs["Result"], bsdf.inputs["Base Color"])
    nt.links.new(map_r.outputs["Result"], bsdf.inputs["Roughness"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    mat.diffuse_color = (*_lin((0.075, 0.082, 0.095)), 1.0)
    mats["floor"] = mat

    mat, nt, bsdf, _ = _new_mat("MAT_Test_Stand_Slate")
    _, noise = _add_coord_noise(nt, scale=22.0, detail=5.0, roughness=0.5)
    bump = _add_bump(nt, noise.outputs["Fac"], strength=0.06, distance=0.002)
    bsdf.inputs["Base Color"].default_value = (*_lin((0.12, 0.14, 0.165)), 1.0)
    bsdf.inputs["Metallic"].default_value = 0.78
    bsdf.inputs["Roughness"].default_value = 0.44
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    mats["test_stand"] = mat

    # 12. Technical Annotation / Callout Flat Emission Ink & Backing
    mat, nt, bsdf, out = _new_mat("MAT_HUD_Text_Gold")
    nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*_lin((0.98, 0.68, 0.14)), 1.0)
    em.inputs["Strength"].default_value = 1.6
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    mats["hud_gold"] = mat

    mat, nt, bsdf, out = _new_mat("MAT_HUD_Text_White")
    nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*_lin((0.92, 0.95, 0.98)), 1.0)
    em.inputs["Strength"].default_value = 1.4
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    mats["hud_white"] = mat

    return mats
