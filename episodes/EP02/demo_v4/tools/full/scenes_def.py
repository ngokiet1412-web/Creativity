"""Scene definitions for the EP02 full episode (V5 draft). Imported by build_full.py."""
from motion import Motion, SCOOP, smooth, G
from kinematics import ik, fk

REST = (19.5, 99.9, 60.2)          # rig.gd default pose (bucket resting near grade)


def flat(keys, length, v):
    return [(0, v), (length, v)]


def define(SCENES, timeline, write, hosts, blinks, EXT, CREW, ik_, fk_, RIG):
    # ================================================================ SC01
    tl = timeline("SC01", [("say", 0, "q"), ("beat", "push", 2.4), ("say", 1, "ks"), ("beat", "hold", 1.2)], lead=0.8)
    SCENES["SC01"] = tl
    m, L = tl["marks"], tl["length"]
    mo = Motion(ik(SCOOP[0][1], SCOOP[0][2]))
    t_dig = m["q.s"] + 2.6
    m["dig.s"] = t_dig
    t_up = mo.path(t_dig, SCOOP) + 0.35
    t_top = mo.move(t_up, 4.1, {"boom_deg": 40.0}, ramp=0.24)
    mo.move(t_top + 0.2, 1.4, {"bucket_rel": 64.0}, ramp=0.4)
    mo.move(m["ks.s"] + 1.4, 2.7, {"boom_deg": 38.6, "bucket_rel": 66.2}, ramp=0.35)
    keys = mo.keys(L)
    keys.update({
        "Studio:studio_on": [(0, 1), (L, 1)],
        "Studio:monitor_on": [(0, 0), (m["q.s"] + 1.4, 0, -2), (m["q.s"] + 2.0, 1), (L, 1)],
        "Studio:push": [(0, 0), (m["push.s"], 0, -2), (m["push.e"], 1), (L, 1)],
        "World/FX:soil": [(0, 0), (t_dig + 1.5, 0, -2), (t_dig + 4.0, 0.62), (t_dig + 5.1, 0.69), (L, 0.69)],
        ".:pump_load": [(0, 0.1), (t_dig - 0.3, 0.1), (t_dig + 0.4, 0.7), (t_top, 0.9), (t_top + 0.8, 0.2), (L, 0.2)],
        ".:grid_alpha": flat(None, L, 0.0),
        ".:legend": flat(None, L, 0.0),
        ".:cam_x": [(0, 150), (m["push.e"], 150), (m["ks.s"] + 4, 175), (L, 185)],
        ".:cam_y": [(0, -165), (m["push.e"], -165), (m["ks.s"] + 4, -150), (L, -145)],
        ".:cam_zoom": [(0, 1.0), (m["push.e"], 1.0), (m["ks.s"] + 4, 1.08), (L, 1.1)],
        ".:capy_tilt": [(0, 0), (m["ks.s"], 0), (m["ks.s"] + 1.0, 4), (m["ks.e"], 2), (L, 0)],
    })
    write("sc01", "sc01.gd", L,
          EXT + [("World/FX", "res://full/machine_fx.gd", ""), CREW, ("Studio", "res://full/studio.gd", "focus = Vector2(150, -165)\nfocus_zoom = 0.40625")],
          keys,
          {"scene_tag": '"SC01"', "scene_title": '"Bí ẩn gầu đất"', "capy_blinks": blinks(L, 1), "eng_blinks": blinks(L, 2),
           "pump_load": "0.1"})


def cue_at(tl, needle, end=False):
    for c in tl["cues"]:
        if needle in c["text"]:
            return c["t1"] if end else c["t0"]
    raise KeyError(needle)


def define2(SCENES, timeline, write, hosts, blinks, EXT, CREW):
    # ================================================================ SC02
    tl = timeline("SC02", [("beat", "open", 1.6), ("say", 0, "q"), ("say", 1, "ks"), ("beat", "hold", 1.5)])
    SCENES["SC02"] = tl
    m, L = tl["marks"], tl["length"]
    ch = cue_at(tl, "lần theo")
    m["chain.s"] = ch
    x0, x1 = m["ks.s"] + 0.8, ch - 0.6
    keys = {
        ".:xray": [(0, 0), (m["q.e"] - 0.5, 0, -2), (x0, 1), (L - 0.8, 1, -2), (L, 0.6)],
        ".:grid_alpha": [(0, 0), (m["q.e"] - 0.5, 0, -2), (x0, 0.55), (L, 0.55)],
        "World/Map:step": [(0, -1), (x0, -1, 1), (x1, 9.0), (L, 9.0)],
        "World/Map:chain": [(0, 0), (ch, 0, 1), (ch + 6.5, 1), (L, 1)],
        "World/FX:hi_boom": [(0, 0), (x0 + (x1 - x0) * 4 / 10, 0, -2), (x0 + (x1 - x0) * 5 / 10, 1), (x0 + (x1 - x0) * 6 / 10, 0.35), (L, 0.35)],
        "World/FX:hi_arm": [(0, 0), (x0 + (x1 - x0) * 4.3 / 10, 0, -2), (x0 + (x1 - x0) * 5.2 / 10, 1), (x0 + (x1 - x0) * 6 / 10, 0.35), (L, 0.35)],
        "World/FX:hi_bucket": [(0, 0), (x0 + (x1 - x0) * 4.6 / 10, 0, -2), (x0 + (x1 - x0) * 5.4 / 10, 1), (x0 + (x1 - x0) * 6 / 10, 0.35), (L, 0.35)],
        ".:legend": [(0, 0), (ch - 0.5, 0, -2), (ch, 1), (L, 1)],
        ".:cam_x": [(0, 160), (m["q.e"], 140, -2), (x0, -190), (x0 + (x1 - x0) * 0.22, -170, -2), (x0 + (x1 - x0) * 0.36, 60), (ch, 70, -2), (L, 90)],
        ".:cam_y": [(0, -60), (m["q.e"], -60, -2), (x0, -50), (x0 + (x1 - x0) * 0.22, -50, -2), (x0 + (x1 - x0) * 0.36, -20), (ch, -20, -2), (L, -30)],
        ".:cam_zoom": [(0, 1.05), (m["q.e"], 1.08, -2), (x0, 2.6), (x0 + (x1 - x0) * 0.22, 2.6, -2), (x0 + (x1 - x0) * 0.36, 1.32), (ch, 1.32, -2), (L, 1.25)],
        ".:capy_tilt": [(0, 0), (m["q.s"], 2), (m["q.s"] + 1.5, -3), (m["q.e"], 4), (L, 0)],
    }
    keys.update(hosts(tl))
    write("sc02", "sc02.gd", L, EXT + [("World/FX", "res://full/machine_fx.gd", ""), ("World/Map", "res://full/system_map.gd", "")],
          keys, {"scene_tag": '"SC02"', "scene_title": '"Bản đồ cả hệ thống"', "capy_blinks": blinks(L, 3), "eng_blinks": blinks(L, 4)})


def define3(SCENES, timeline, write, hosts, blinks, EXT, CREW):
    from motion import Motion
    # ================================================================ SC06
    tl = timeline("SC06", [("beat", "open", 1.2), ("say", 0, "ks"), ("say", 1, "q"), ("say", 2, "ks2"), ("beat", "hold", 1.2)])
    SCENES["SC06"] = tl
    m, L = tl["marks"], tl["length"]
    m["boom.s"] = cue_at(tl, "Cần nâng hạ")
    m["arm.s"] = cue_at(tl, "tay gầu tiến lùi")
    m["bkt.s"] = cue_at(tl, "gầu cuộn hoặc mở")
    m["bkt.e"] = cue_at(tl, "gầu cuộn hoặc mở", True)
    m["oil.s"] = cue_at(tl, "Dầu vào một khoang")
    m["pin.s"] = cue_at(tl, "Qua các chốt")
    mo = Motion((28.0, 95.0, 45.0))
    t = mo.move(m["boom.s"] + 0.2, 2.0, {"boom_deg": 37.0})
    mo.move(t + 0.25, 1.6, {"boom_deg": 30.0})
    t = mo.move(m["arm.s"] + 0.2, 1.6, {"arm_rel": 74.0})
    mo.move(t + 0.25, 1.5, {"arm_rel": 94.0})
    t = mo.move(m["bkt.s"] + 0.2, 1.3, {"bucket_rel": 80.0})
    mo.move(t + 0.25, 1.2, {"bucket_rel": 50.0})
    t = mo.move(m["pin.s"] + 0.3, 3.0, {"boom_deg": 38.0, "bucket_rel": 70.0}, ramp=0.3)
    mo.move(m["ks2.s"] + 1.0, 3.2, {"boom_deg": 30.0, "arm_rel": 85.0, "bucket_rel": 55.0}, ramp=0.3)
    keys = mo.keys(L)
    def hi(a, b):
        return [(0, 0), (a - 0.3, 0, -2), (a + 0.2, 1), (b, 1, -2), (b + 0.4, 0.25), (L, 0.25)]
    keys.update({
        "World/FX:hi_boom": hi(m["boom.s"], m["arm.s"]),
        "World/FX:hi_arm": hi(m["arm.s"], m["bkt.s"]),
        "World/FX:hi_bucket": hi(m["bkt.s"], m["bkt.e"] + 0.3),
        "World/FX:force_arrows": [(0, 0), (m["oil.s"] - 0.3, 0, -2), (m["oil.s"] + 0.3, 1), (m["q.s"], 1, -2), (m["q.s"] + 0.4, 0), (L, 0)],
        "World/FX:pins": [(0, 0), (m["pin.s"] - 0.3, 0, -2), (m["pin.s"] + 0.3, 1), (m["q.s"], 1, -2), (m["q.s"] + 0.3, 0.3), (m["ks2.s"], 0.3, -2), (m["ks2.s"] + 0.4, 1), (L, 1)],
        ".:grid_alpha": [(0, 0), (L, 0)],
        ".:xray": [(0, 0), (L, 0)],
        ".:legend": [(0, 0), (L, 0)],
        ".:cam_x": [(0, 300), (m["boom.s"], 260), (m["arm.s"], 300, -2), (m["bkt.s"], 330), (m["q.s"], 300, -2), (L, 290)],
        ".:cam_y": [(0, -150), (m["boom.s"], -150), (m["q.s"], -160, -2), (L, -150)],
        ".:cam_zoom": [(0, 1.15), (m["boom.s"], 1.3), (m["bkt.s"], 1.4, -2), (m["q.s"], 1.22, -2), (L, 1.25)],
        ".:capy_tilt": [(0, 0), (m["q.s"], 3), (m["q.s"] + 1.2, -4), (m["q.e"], 5), (L, 0)],
    })
    keys.update(hosts(tl))
    write("sc06", "sc06.gd", L, EXT + [("World/FX", "res://full/machine_fx.gd", "")], keys,
          {"scene_tag": '"SC06"', "scene_title": '"Xi lanh cần, tay gầu và gầu"', "capy_blinks": blinks(L, 5), "eng_blinks": blinks(L, 6)})


def define4(SCENES, timeline, write, hosts, blinks, EXT, CREW):
    from motion import Motion
    # ================================================================ SC07
    tl = timeline("SC07", [("beat", "open", 1.0), ("say", 0, "q"), ("say", 1, "ks"), ("say", 2, "q2"), ("beat", "hold", 1.6)])
    SCENES["SC07"] = tl
    m, L = tl["marks"], tl["length"]
    m["f.s"] = cue_at(tl, "Với một khoang")
    m["v.s"] = cue_at(tl, "Muốn piston")
    m["lever.s"] = cue_at(tl, "Nhưng lực tới")
    mo = Motion((22.0, 95.0, 55.0))
    t = mo.move(m["v.s"] + 0.2, 4.6, {"boom_deg": 36.0}, ramp=0.25)
    mo.move(m["q2.s"] + 0.5, 3.5, {"boom_deg": 26.0}, ramp=0.3)
    keys = mo.keys(L)
    keys.update({
        ".:xray": [(0, 0.75), (L, 0.75)],
        ".:grid_alpha": [(0, 0.6), (L, 0.6)],
        ".:legend": [(0, 1), (L, 1)],
        ".:cam_x": [(0, -620), (m["f.s"], -640, -2), (m["lever.s"], -520, -2), (m["lever.s"] + 1.2, 60), (m["lever.s"] + 3.0, 60, -2), (m["lever.s"] + 4.2, 260), (m["q2.s"], 260, -2), (m["q2.s"] + 1.0, -420), (L, -420)],
        ".:cam_y": [(0, -60), (m["lever.s"], -60, -2), (m["lever.s"] + 1.2, -60), (m["lever.s"] + 3.0, -60, -2), (m["lever.s"] + 4.2, -80), (m["q2.s"], -80, -2), (m["q2.s"] + 1.0, -60), (L, -60)],
        ".:cam_zoom": [(0, 0.95), (m["f.s"], 0.98, -2), (m["lever.s"], 0.9, -2), (m["lever.s"] + 1.2, 1.7), (m["lever.s"] + 3.0, 1.7, -2), (m["lever.s"] + 4.2, 1.1), (m["q2.s"], 1.1, -2), (m["q2.s"] + 1.0, 0.82), (L, 0.82)],
        ".:capy_tilt": [(0, 0), (m["q.s"], 3), (m["q.e"], -2), (m["q2.s"], 4), (L, 0)],
    })
    keys.update(hosts(tl))
    write("sc07", "sc07.gd", L, EXT, keys,
          {"scene_tag": '"SC07"', "scene_title": '"Áp suất, lưu lượng và lực thật"', "capy_blinks": blinks(L, 7), "eng_blinks": blinks(L, 8)})


def define5(SCENES, timeline, write, hosts, blinks):
    from motion import trapezoid
    # ================================================================ SC08
    tl = timeline("SC08", [("beat", "open", 1.6), ("say", 0, "q"), ("say", 1, "ks"), ("beat", "demo", 3.0), ("beat", "hold", 1.0)])
    SCENES["SC08"] = tl
    m, L = tl["marks"], tl["length"]
    m["motor.s"] = cue_at(tl, "Dầu cấp đến")
    m["ring.s"] = cue_at(tl, "Dầu cấp đến") + 3.2
    m["brake.s"] = cue_at(tl, "Hệ thống có chức năng hãm")
    m["ok.s"] = cue_at(tl, "Ở hình này")
    sw = []
    def swing(t0, dur, a0, a1, n=40):
        for k in range(n + 1):
            u = k / n
            sw.append((t0 + dur * u, a0 + (a1 - a0) * trapezoid(u, 0.3), 1.0))
    sw.append((0, 0.0, 1.0))
    swing(m["q.s"] + 0.6, 3.6, 0.0, 70.0)
    swing(m["motor.s"] + 0.4, 4.4, 70.0, -40.0)
    swing(m["ok.s"] + 0.2, 5.0, -40.0, 120.0)
    swing(m["demo.s"] + 0.6, 2.4, 120.0, 0.0)
    sw.append((L, 0.0, 1.0))
    keys = {
        "Top:swing_deg": sw,
        "Top:hi_motor": [(0, 0), (m["motor.s"] - 0.3, 0, -2), (m["motor.s"] + 0.3, 1), (m["brake.s"], 1, -2), (m["brake.s"] + 0.5, 0.3), (L, 0.3)],
        "Top:hi_ring": [(0, 0), (m["ring.s"] - 0.3, 0, -2), (m["ring.s"] + 0.3, 1), (m["brake.s"], 1, -2), (m["brake.s"] + 0.5, 0.2), (L, 0.2)],
        "Top:gear": [(0, 0), (m["motor.s"] + 0.5, 0, -2), (m["motor.s"] + 1.2, 1), (m["ok.s"], 1, -2), (m["ok.s"] + 0.6, 0), (L, 0)],
        ".:legend": [(0, 0), (L, 0)],
        ".:cam_x": [(0, 200), (m["motor.s"], 200, -2), (m["motor.s"] + 1.0, 420), (m["ok.s"], 420, -2), (m["ok.s"] + 1.0, 240), (L, 240)],
        ".:cam_y": [(0, -85), (L, -85)],
        ".:cam_zoom": [(0, 0.60), (L, 0.60)],
        ".:capy_tilt": [(0, 0), (m["q.s"], 3), (m["q.e"], -3), (L, 0)],
    }
    keys.update(hosts(tl))
    write("sc08", "sc08.gd", L, [("Top", "res://full/topview.gd", "gear_pos = Vector2(1270, -425)")], keys,
          {"scene_tag": '"SC08"', "scene_title": '"Quay toa bằng mô tơ thủy lực"', "capy_blinks": blinks(L, 9), "eng_blinks": blinks(L, 10)})


def define6(SCENES, timeline, write, hosts, blinks):
    from motion import trapezoid
    # ================================================================ SC09
    tl = timeline("SC09", [("beat", "open", 1.0), ("say", 0, "q"), ("say", 1, "ks"), ("beat", "demo", 2.5), ("say", 2, "q2"), ("say", 3, "ks2"), ("beat", "hold", 2.0)])
    SCENES["SC09"] = tl
    m, L = tl["marks"], tl["length"]
    m["trk.s"] = cue_at(tl, "Mỗi bên xích")
    m["top.s"] = m["trk.s"] + 4.0
    def ramp(keys, t0, dur, v0, v1, n=30, r=0.25):
        for k in range(n + 1):
            u = k / n
            keys.append((t0 + dur * u, v0 + (v1 - v0) * trapezoid(u, r), 1.0))
    turn = [(0, 0.0, 1.0)]
    ramp(turn, m["q.s"] + 1.0, 4.0, 0.0, 120.0)
    ramp(turn, m["ks.s"] + 2.0, 5.0, 120.0, -60.0)
    turn.append((L, -60.0, 1.0))
    ds = [(0, 0.0, 1.0)]
    ramp(ds, m["top.s"] + 0.2, 3.2, 0.0, 380.0)
    ds.append((L, 380.0, 1.0))
    td = [(0, 0.0, 1.0)]
    ramp(td, m["top.s"] + 3.9, 3.4, 0.0, 170.0)
    td.append((L, 170.0, 1.0))
    ss = [(0, 0.0, 1.0)]
    ramp(ss, m["trk.s"] + 0.2, L - m["trk.s"] - 0.4, 0.0, 1700.0, n=120, r=0.08)
    keys = {
        "Swivel:turn": turn,
        "Swivel:noodle": [(0, 0), (m["q.s"] + 2.5, 0, -2), (m["q.s"] + 3.0, 1), (m["ks.s"] + 0.5, 1, -2), (m["ks.s"] + 1.0, 0), (L, 0)],
        "Side:hi_motor": [(0, 0), (m["trk.s"], 0, -2), (m["trk.s"] + 0.4, 1), (m["top.s"], 1), (L, 0.4)],
        "Side:wrong": [(0, 0), (m["q2.s"], 0, -2), (m["q2.s"] + 0.4, 1), (m["ks2.s"], 1, -2), (m["ks2.s"] + 0.4, 0), (L, 0)],
        ".:drive_s": ds, ".:turn_d": td, ".:side_s": ss,
        ".:legend": [(0, 1), (L, 1)],
        ".:cam_x": [(0, 0), (m["trk.s"] - 0.6, 0, -2), (m["trk.s"] + 0.4, 0), (m["top.s"] - 0.5, 0, -2), (m["top.s"] + 0.3, 2620), (m["top.s"] + 3.6, 2860), (m["q2.s"] - 0.6, 2860, -2), (m["q2.s"] + 0.2, 0), (L, 0)],
        ".:cam_y": [(0, -10), (m["trk.s"] - 0.6, -10, -2), (m["trk.s"] + 0.4, 1400), (m["top.s"] - 0.5, 1400, -2), (m["top.s"] + 0.3, 0), (m["q2.s"] - 0.6, 0, -2), (m["q2.s"] + 0.2, 1400), (L, 1400)],
        ".:cam_zoom": [(0, 1.15), (m["trk.s"] - 0.6, 1.2, -2), (m["trk.s"] + 0.4, 1.35), (m["top.s"] - 0.5, 1.35, -2), (m["top.s"] + 0.3, 0.92), (m["q2.s"] - 0.6, 0.92, -2), (m["q2.s"] + 0.2, 1.3), (L, 1.32)],
        ".:capy_tilt": [(0, 0), (m["q.s"], 3), (m["q.e"], -4), (m["q2.s"], 5), (L, 0)],
    }
    keys.update(hosts(tl))
    write("sc09", "sc09.gd", L, [("Swivel", "res://full/swivel.gd", ""), ("Side", "res://full/track_side.gd", "position = Vector2(0, 1400)"),
                                 ("TopGround", "res://full/topview.gd", "position = Vector2(2600, 0)\nonly_ground = true"),
                                 ("Drive", None, ""), ("Drive/Top", "res://full/topview.gd", "ground = false")], keys,
          {"scene_tag": '"SC09"', "scene_title": '"Hai bánh xích và khớp quay trung tâm"', "capy_blinks": blinks(L, 11), "eng_blinks": blinks(L, 12)})


def define7(SCENES, timeline, write, hosts, blinks):
    # ================================================================ SC10
    tl = timeline("SC10", [("beat", "open", 1.2), ("say", 0, "q"), ("say", 1, "ks"), ("beat", "hold", 2.0)])
    SCENES["SC10"] = tl
    m, L = tl["marks"], tl["length"]
    m["fuel.s"] = cue_at(tl, "không phải nhiên liệu")
    m["roles.s"] = cue_at(tl, "Nó truyền năng lượng")
    keys = {
        ".:flow": [(0, 1), (L, 1)],
        ".:legend": [(0, 1), (L, 1)],
        ".:cam_x": [(0, -620), (m["ks.s"], -560, -2), (m["ks.s"] + 4.0, -150), (m["fuel.s"], 100, -2), (m["roles.s"], 60), (L, 60)],
        ".:cam_y": [(0, -80), (m["ks.s"], -80, -2), (m["ks.s"] + 4.0, -40), (L, -40)],
        ".:cam_zoom": [(0, 1.15), (m["ks.s"], 1.1, -2), (m["ks.s"] + 4.0, 0.95), (m["fuel.s"], 0.92, -2), (m["roles.s"], 0.8), (L, 0.8)],
        ".:capy_tilt": [(0, 0), (m["q.s"], 4), (m["q.e"], -2), (L, 0)],
    }
    keys.update(hosts(tl))
    write("sc10", "sc10.gd", L, [("Return", "res://full/returnc.gd", "")], keys,
          {"scene_tag": '"SC10"', "scene_title": '"Dầu hồi: lọc và làm mát"', "capy_blinks": blinks(L, 13), "eng_blinks": blinks(L, 14)})


def define8(SCENES, timeline, write, hosts, blinks, EXT, CREW):
    from motion import Motion
    # ================================================================ SC11
    tl = timeline("SC11", [("beat", "open", 1.0), ("say", 0, "q"), ("say", 1, "ks"), ("say", 2, "q2"), ("beat", "hold", 1.5)])
    SCENES["SC11"] = tl
    m, L = tl["marks"], tl["length"]
    m["rv.s"] = cue_at(tl, "Hệ thống cần van")
    m["tab.s"] = cue_at(tl, "PC200-8 có các mạch")
    m["hold.s"] = cue_at(tl, "Ngoài ra còn có")
    m["warn.s"] = cue_at(tl, "Tuy nhiên đừng")
    mo = Motion((25.0, 100.0, 32.0))
    t_hit = mo.move(m["q.s"] + 0.4, 1.6, {"boom_deg": 22.15}, ramp=0.3)
    mo.move(m["warn.s"] + 0.5, 2.5, {"boom_deg": 28.0}, ramp=0.3)
    keys = mo.keys(L)
    keys.update({
        ".:p_mpa": [(0, 6.0), (t_hit, 9.0, -2), (t_hit + 2.2, 37.3, 1), (m["warn.s"] + 0.5, 37.3, -2), (m["warn.s"] + 2.0, 8.0), (L, 8.0)],
        ".:xray": [(0, 0), (m["rv.s"] - 0.5, 0, -2), (m["rv.s"], 0.55), (L, 0.55)],
        ".:grid_alpha": [(0, 0), (L, 0)],
        ".:legend": [(0, 0), (m["rv.s"], 0, -2), (m["rv.s"] + 0.4, 1), (L, 1)],
        ".:cam_x": [(0, 220), (m["q.s"], 240, -2), (t_hit, 300), (m["rv.s"], 300, -2), (m["rv.s"] + 0.6, 420), (L, 420)],
        ".:cam_y": [(0, -60), (m["rv.s"], -20, -2), (m["rv.s"] + 0.6, -120), (L, -120)],
        ".:cam_zoom": [(0, 1.1), (t_hit, 1.3, -2), (m["rv.s"], 1.3, -2), (m["rv.s"] + 0.6, 1.15), (L, 1.15)],
        ".:capy_tilt": [(0, 0), (m["q.s"], -4), (m["q.e"], 5), (m["q2.s"], 3), (L, 0)],
    })
    keys.update(hosts(tl))
    write("sc11", "sc11.gd", L, EXT + [("World/FX", "res://full/machine_fx.gd", "")], keys,
          {"scene_tag": '"SC11"', "scene_title": '"Van giới hạn áp và an toàn"', "capy_blinks": blinks(L, 15), "eng_blinks": blinks(L, 16)})


def define9(SCENES, timeline, write, hosts, blinks):
    # ================================================================ SC12
    tl = timeline("SC12", [("beat", "open", 1.2), ("say", 0, "q"), ("say", 1, "ks"), ("beat", "hold", 1.8)])
    SCENES["SC12"] = tl
    m, L = tl["marks"], tl["length"]
    m["sig.s"] = cue_at(tl, "Một số tín hiệu")
    m["epc.s"] = cue_at(tl, "Ở hệ CLSS")
    m["man.s"] = cue_at(tl, "Nhưng sơ đồ dây")
    keys = {
        "Elec:stage": [(0, 0), (m["sig.s"], 0, -2), (m["sig.s"] + 2.5, 1.0, -2), (m["epc.s"] - 1.0, 1.0, -2), (m["epc.s"], 2.0), (L, 2.0)],
        "Elec:hi_epc": [(0, 0), (m["epc.s"], 0, -2), (m["epc.s"] + 0.4, 1), (m["man.s"], 1, -2), (m["man.s"] + 0.5, 0), (L, 0)],
        "Elec:ecu_search": [(0, 0), (m["q.s"] + 2.0, 0, -2), (m["q.s"] + 2.5, 1), (m["sig.s"] + 3, 1, -2), (m["sig.s"] + 3.5, 0), (L, 0)],
        ".:legend": [(0, 1), (L, 1)],
        ".:cam_x": [(0, -260), (m["sig.s"], -260, -2), (m["epc.s"], -160, -2), (m["epc.s"] + 1.0, -160), (m["man.s"], -160, -2), (m["man.s"] + 1.0, -150), (L, -150)],
        ".:cam_y": [(0, -60), (m["man.s"], -60, -2), (m["man.s"] + 1.0, -140), (L, -140)],
        ".:cam_zoom": [(0, 0.95), (m["sig.s"], 0.9, -2), (m["epc.s"], 0.9, -2), (m["epc.s"] + 1.0, 1.05), (m["man.s"], 1.05, -2), (m["man.s"] + 1.0, 0.95), (L, 0.95)],
        ".:capy_tilt": [(0, 0), (m["q.s"], 5), (m["q.e"], -3), (L, 0)],
    }
    keys.update(hosts(tl))
    write("sc12", "sc12.gd", L, [("Elec", "res://full/elec.gd", "")], keys,
          {"scene_tag": '"SC12"', "scene_title": '"Điện tử có tham gia không?"', "capy_blinks": blinks(L, 17), "eng_blinks": blinks(L, 18)})


def define10(SCENES, timeline, write, hosts, blinks, EXT, CREW):
    from motion import Motion
    # ================================================================ SC13
    tl = timeline("SC13", [("beat", "open", 1.2), ("say", 0, "q"), ("say", 1, "ks"), ("beat", "hold", 2.0)])
    SCENES["SC13"] = tl
    m, L = tl["marks"], tl["length"]
    m["h.s"] = cue_at(tl, "Phải tách")
    m["cmp.s"] = cue_at(tl, "Quan trọng là")
    m["rule.s"] = cue_at(tl, "Đo và đối chiếu")
    keys = Motion((19.5, 99.9, 60.2)).keys(L)
    keys.update({
        ".:xray": [(0, 0), (m["h.s"] - 0.6, 0, -2), (m["h.s"], 0.65), (L, 0.65)],
        ".:grid_alpha": [(0, 0), (L, 0)],
        ".:legend": [(0, 0), (L, 0)],
        ".:cam_x": [(0, 60), (m["q.s"], 30, -2), (m["h.s"], 120), (L, 140)],
        ".:cam_y": [(0, -120), (L, -110)],
        ".:cam_zoom": [(0, 0.95), (m["q.s"], 1.0, -2), (m["h.s"], 1.0), (L, 1.02)],
        ".:capy_tilt": [(0, 0), (m["q.s"], 4), (m["q.e"], -3), (L, 0)],
    })
    write("sc13", "sc13.gd", L, EXT + [CREW], keys,
          {"scene_tag": '"SC13"', "scene_title": '"Tại sao máy lại chậm / yếu?"', "capy_blinks": blinks(L, 19), "eng_blinks": blinks(L, 20)})

    # ================================================================ SC14
    tl = timeline("SC14", [("beat", "back", 2.2), ("say", 0, "sum"), ("say", 1, "ks"), ("say", 2, "bye"), ("beat", "end", 3.0)], lead=0.4)
    SCENES["SC14"] = tl
    m, L = tl["marks"], tl["length"]
    s0, s1 = m["sum.s"] + 0.3, cue_at(tl, "Dầu còn phải về", True)
    keys = {
        "Studio:push": [(0, 1), (0.6, 1, -2), (m["back.e"], 0), (L, 0)],
        "Studio:monitor_on": [(0, 1), (L, 1)],
        "Studio:studio_on": [(0, 1), (L, 1)],
        "World/Map:step": [(0, 9), (m["back.e"], 9, 0), (s0, -1, 1), (s1, 9.5), (L, 9.5)],
        "World/Map:chain": [(0, 1), (L, 1)],
        ".:xray": [(0, 1), (L, 1)],
        ".:grid_alpha": [(0, 0.55), (L, 0.55)],
        ".:legend": [(0, 0), (L, 0)],
        ".:capy_tilt": [(0, 0), (L, 0)],
    }
    keys.update(hosts(tl, capy=False))
    write("sc14", "sc14.gd", L, EXT + [("World/FX", "res://full/machine_fx.gd", ""), ("World/Map", "res://full/system_map.gd", ""), ("Studio", "res://full/studio.gd", "focus = Vector2(60, -20)\nfocus_zoom = 0.53625")],
          keys, {"scene_tag": '"SC14"', "scene_title": '"Tổng kết"', "capy_blinks": blinks(L, 21), "eng_blinks": blinks(L, 22)})
