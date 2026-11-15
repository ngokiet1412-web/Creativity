#!/usr/bin/env python3
"""EP02 full episode (V5 draft): timing + Godot scene writer.

* Dialogue is read VERBATIM from episodes/EP02/SCRIPT_YOUTUBE_PC200_8_FULL_V2.md
  (lines "**CAPY:** '...'" / "**ANH KỸ SƯ:** '...'"); nothing is retyped here.
* Each line becomes subtitle cues split at sentence punctuation. Spoken length
  is ESTIMATED (Vietnamese syllables / 4.2 per s + 0.25 s) until the
  owner-approved ElevenLabs WAVs exist; then replace est() by the WAV lengths
  and rebuild: every animation key below is placed on dialogue markers, so the
  picture re-times with the voice instead of the voice being sped up.
* Writes godot/full/timing.json, godot/full/scXX.tscn, subtitles/*.srt and
  audio_timing_full.csv.

Scene items:  ("beat", name, seconds)  visual-only time
              ("say", line_index, name) one script line of this scene
Markers: "<name>.s" / "<name>.e" for every item.
"""
import csv
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEMO = os.path.join(HERE, "..", "..")
GODOT = os.path.join(DEMO, "godot")
SCRIPT = os.path.join(DEMO, "..", "SCRIPT_YOUTUBE_PC200_8_FULL_V2.md")
sys.path.insert(0, os.path.join(HERE, ".."))
from kinematics import RIG, ik, fk  # noqa: E402

RATE = 4.2
WHO = {"CAPY": "CAPY", "ANH KỸ SƯ": "KS"}
SPOKEN = {"PC200-8": "pê xê hai trăm tám", "SAA6D107E-1": "ét a a sáu đê một trăm lẻ bảy e một",
          "CLSS": "xê eo ét ét", "LS/PC": "eo ét pê xê", "EPC": "e pê xê", "ECU": "e xê u", "LS": "eo ét"}


def script_lines():
    s = open(SCRIPT, encoding="utf-8").read()
    parts = re.split(r"\n## (SC\d\d) — ", s)
    out = {}
    for i in range(1, len(parts), 2):
        body = parts[i + 1].split("\n---")[0]
        out[parts[i]] = [(WHO[w], t) for w, t in re.findall(r"\*\*(CAPY|ANH KỸ SƯ):\*\* '(.+?)'\s*$", body, re.M)]
    return out


LINES = script_lines()


def syl(t):
    for k, v in SPOKEN.items():
        t = re.sub(r"(?<![\w-])" + re.escape(k) + r"(?![\w-])", v, t)
    return len(re.findall(r"[\wÀ-ỹ]+", t))


def est(text):
    return syl(text) / RATE + 0.25


VOICE = os.path.join(GODOT, "local", "voice")       # owner-approved VO, not in the public repo


def voice_file(scene, idx, who):
    """godot/local/voice/SC01_01_CAPY.wav (or .mp3): one file per script line"""
    for ext in ("wav", "mp3", "m4a"):
        p = os.path.join(VOICE, "%s_%02d_%s.%s" % (scene, idx + 1, who, ext))
        if os.path.exists(p):
            return p
    return None


def media_len(p):
    import subprocess
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout.strip())


def chunks(text, limit=88):
    """split at sentence ends; long sentences again at ';' / ',' (words untouched)"""
    sent = re.findall(r".+?(?:[.?!…]+(?=\s|$)|$)", text.strip())
    sent = [s.strip() for s in sent if s.strip()]
    out = []
    for s in sent:
        while len(s) > limit:
            cut = max(s.rfind("; ", 0, limit), s.rfind(", ", 0, limit), s.rfind(": ", 0, limit))
            if cut < 20:
                break
            out.append(s[:cut + 1].strip())
            s = s[cut + 1:].strip()
        out.append(s)
    return out


def timeline(scene, items, lead=0.6, tail=1.2):
    t = lead
    marks, cues, voices = {"start": 0.0}, [], []
    prev_who = None
    for it in items:
        if it[0] == "beat":
            marks[it[1] + ".s"] = round(t, 3)
            t += it[2]
            marks[it[1] + ".e"] = round(t, 3)
            prev_who = None
        else:
            who, text = LINES[scene][it[1]]
            if prev_who is not None:
                t += 0.75 if who != prev_who else 0.45
            marks[it[2] + ".s"] = round(t, 3)
            vf = voice_file(scene, it[1], who)
            chs = chunks(text)
            if vf:      # real VO: the line lasts as long as the recording; cues split by syllables
                total = media_len(vf)
                voices.append({"file": vf, "t0": round(t, 3), "who": who})
                w = [syl(c) for c in chs]
                for ch, wi in zip(chs, w):
                    d = total * wi / sum(w)
                    cues.append({"who": who, "t0": round(t, 3), "t1": round(t + d, 3), "text": ch, "line": it[1]})
                    t += d
            else:
                for k, ch in enumerate(chs):
                    if k:
                        t += 0.3
                    d = est(ch)
                    cues.append({"who": who, "t0": round(t, 3), "t1": round(t + d, 3), "text": ch, "line": it[1]})
                    t += d
            marks[it[2] + ".e"] = round(t, 3)
            prev_who = who
    t += tail
    marks["end"] = round(t, 3)
    used = sorted({it[1] for it in items if it[0] == "say"})
    assert used == list(range(len(LINES[scene]))), (scene, used, len(LINES[scene]))
    return {"length": round(t, 3), "marks": marks, "cues": cues, "voices": voices}


# ------------------------------------------------------------------ writer
def fmt(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    s = "%.6g" % v
    return s if any(ch in s for ch in ".e") else s + ".0"


def track(i, path, keys):
    keys = sorted(keys, key=lambda k: k[0])
    out, last = [], None
    for k in keys:
        tt, v = k[0], k[1]
        tr = k[2] if len(k) > 2 else -2.0
        v = last if v is None else v
        out.append((tt, v, tr))
        last = v
    return (f'tracks/{i}/type = "value"\ntracks/{i}/imported = false\ntracks/{i}/enabled = true\n'
            f'tracks/{i}/path = NodePath("{path}")\ntracks/{i}/interp = 1\ntracks/{i}/loop_wrap = false\n'
            f'tracks/{i}/keys = {{\n"times": PackedFloat32Array({", ".join(fmt(k[0]) for k in out)}),\n'
            f'"transitions": PackedFloat32Array({", ".join(fmt(k[2]) for k in out)}),\n"update": 0,\n'
            f'"values": [{", ".join(fmt(k[1]) for k in out)}]\n}}\n')


def write(name, script, length, nodes, keys, props):
    """nodes: (path, script_res or None, props_text); path 'World/Machine' -> parent 'World'"""
    body = "".join(track(i, p, k) for i, (p, k) in enumerate(keys.items()))
    ext = [f'[ext_resource type="Script" path="res://full/{script}" id="root"]']
    node_txt = []
    for j, (path, nscript, extra) in enumerate(nodes):
        parent = "." if "/" not in path else path.rsplit("/", 1)[0]
        nname = path.rsplit("/", 1)[-1]
        line = f'[node name="{nname}" type="Node2D" parent="{parent}"]\n'
        if nscript:
            ext.append(f'[ext_resource type="Script" path="{nscript}" id="c{j}"]')
            line += f'script = ExtResource("c{j}")\n'
        node_txt.append(line + (extra + "\n" if extra else ""))
    prop_txt = "".join(f"{k} = {v}\n" for k, v in props.items())
    scene = (f'[gd_scene format=3]\n\n' + "\n".join(ext) + '\n\n'
             f'[sub_resource type="Animation" id="seq"]\nresource_name = "sequence"\nlength = {fmt(length)}\n{body}\n'
             f'[sub_resource type="AnimationLibrary" id="lib"]\n_data = {{\n&"sequence": SubResource("seq")\n}}\n\n'
             f'[node name="{name.upper()}" type="Node2D"]\nscript = ExtResource("root")\n{prop_txt}\n'
             + "\n".join(node_txt) +
             f'\n[node name="Camera" type="Camera2D" parent="."]\n\n'
             f'[node name="AnimationPlayer" type="AnimationPlayer" parent="."]\nlibraries = {{\n&"": SubResource("lib")\n}}\n')
    os.makedirs(os.path.join(GODOT, "full"), exist_ok=True)
    open(os.path.join(GODOT, "full", f"{name}.tscn"), "w").write(scene)


def blinks(length, seed, every=3.4):
    import random
    r = random.Random(seed)
    out, t = [], 1.0
    while t < length - 0.5:
        out.append(round(t, 2))
        t += every * r.uniform(0.6, 1.4)
    return "[" + ", ".join(fmt(b) for b in out) + "]"


def hosts(tl, capy=True, eng=True, pad=0.5):
    """slide hosts in for their own lines (merged when lines are close)"""
    keys = {}
    for who, prop in (("CAPY", ".:capy_in"), ("KS", ".:eng_in")):
        if (who == "CAPY" and not capy) or (who == "KS" and not eng):
            continue
        spans = []
        for c in tl["cues"]:
            if c["who"] != who:
                continue
            a, b = c["t0"] - pad, c["t1"] + pad
            if spans and a - spans[-1][1] < 2.5:
                spans[-1][1] = b
            else:
                spans.append([a, b])
        k = [(0, 0)]
        for a, b in spans:
            a = max(a, 0.01)
            k += [(a, 0), (a + 0.45, 1), (b, 1), (b + 0.45, 0)]
        k.append((tl["length"], 0))
        keys[prop] = k
    return keys


EXTERIOR_NODES = [
    ("World", None, ""),
    ("World/Env", "res://env.gd", ""),
    ("World/Machine", "res://rig.gd", ""),
]
CREW_NODE = ("World/Crew", "res://crew.gd", "")


# =================================================================== scenes
SCENES = {}
from scenes_def import define, define2, define3, define4, define5, define6, define7, define8, define9, define10  # noqa: E402

define(SCENES, timeline, write, hosts, blinks, EXTERIOR_NODES, CREW_NODE, ik, fk, RIG)
define2(SCENES, timeline, write, hosts, blinks, EXTERIOR_NODES, CREW_NODE)
define3(SCENES, timeline, write, hosts, blinks, EXTERIOR_NODES, CREW_NODE)
define4(SCENES, timeline, write, hosts, blinks, EXTERIOR_NODES, CREW_NODE)
define5(SCENES, timeline, write, hosts, blinks)
define6(SCENES, timeline, write, hosts, blinks)
define7(SCENES, timeline, write, hosts, blinks)
define8(SCENES, timeline, write, hosts, blinks, EXTERIOR_NODES, CREW_NODE)
define9(SCENES, timeline, write, hosts, blinks)
define10(SCENES, timeline, write, hosts, blinks, EXTERIOR_NODES, CREW_NODE)


def mouth_env(tl):
    """per-frame mouth opening 0..1 for each speaker: VO loudness when the
    recording exists, otherwise one bump per syllable of the cue text"""
    import subprocess
    import numpy as np
    n = int(tl["length"] * 30) + 2
    env = {"CAPY": np.zeros(n), "KS": np.zeros(n)}
    voiced = set()
    for v in tl.get("voices", []):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", v["file"], "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True).stdout
        x = np.frombuffer(raw, "<i2").astype(float) / 32768.0
        hop = 16000 // 30
        rms = np.array([np.sqrt((x[i:i + hop] ** 2).mean()) for i in range(0, max(len(x) - hop, 1), hop)])
        if len(rms):
            rms = np.clip((rms / (np.percentile(rms, 95) + 1e-6) - 0.12) / 0.7, 0, 1)
            i0 = int(round(v["t0"] * 30))
            m = min(len(rms), n - i0)
            env[v["who"]][i0:i0 + m] = np.maximum(env[v["who"]][i0:i0 + m], rms[:m])
            voiced.add((v["who"], round(v["t0"], 1)))
    have_voice = bool(tl.get("voices"))
    for ci, c in enumerate(tl["cues"]):
        if have_voice and any(w == c["who"] and abs(c["t0"] - t0) < 60 for w, t0 in voiced) and "line" in c and \
                any(v["who"] == c["who"] and v["t0"] <= c["t0"] + 1e-3 for v in tl["voices"]):
            continue
        k = max(syl(c["text"]), 1)
        d = (c["t1"] - c["t0"]) / k
        for j in range(k):
            amp = 0.55 + 0.45 * (((j * 7 + ci * 3) % 5) / 4.0)
            a, b = c["t0"] + j * d, c["t0"] + (j + 0.85) * d
            for f in range(int(a * 30), min(int(b * 30) + 1, n)):
                u = (f / 30.0 - a) / (b - a)
                if 0 <= u <= 1:
                    env[c["who"]][f] = max(env[c["who"]][f], amp * math.sin(math.pi * u) ** 0.8)
    return {k: [round(float(x), 3) for x in v] for k, v in env.items()}


def seg_cues(tag):
    """SC03-SC05 keep their approved timing; cues come from their SRT files"""
    path = os.path.join(DEMO, "segments_sc03_sc05", "EP02_%s_vi.srt" % tag)
    cues = []
    for blk in open(path, encoding="utf-8").read().strip().split("\n\n"):
        ln = blk.strip().split("\n")
        a, b = ln[1].split(" --> ")
        f = lambda z: int(z[:2]) * 3600 + int(z[3:5]) * 60 + int(z[6:8]) + int(z[9:]) / 1000
        who, text = " ".join(ln[2:]).split(": ", 1)
        cues.append({"who": WHO[who], "t0": f(a), "t1": f(b), "text": text})
    voices = []
    for i, (who, text) in enumerate(LINES[tag]):     # VO for these scenes starts at the line's first cue
        vf = voice_file(tag, i, who)
        hit = [c for c in cues if text.startswith(c["text"])]
        if vf and hit:
            voices.append({"file": vf, "t0": hit[0]["t0"], "who": who})
    return {"length": cues[-1]["t1"] + 3.0, "marks": {}, "cues": cues, "voices": voices}


def srt_time(x):
    ms = int(round(x * 1000))
    return "%02d:%02d:%02d,%03d" % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)


if __name__ == "__main__":
    out = {"rate_syll_per_s": RATE, "scenes": {}}
    for sc, tl in SCENES.items():
        out["scenes"][sc] = tl
    mouth = {sc: mouth_env(tl) for sc, tl in SCENES.items()}
    for tag in ("SC03", "SC04", "SC05"):
        seg = seg_cues(tag)
        out["scenes"][tag] = seg
        mouth[tag] = mouth_env(seg)
    json.dump(out, open(os.path.join(GODOT, "full", "timing.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(mouth, open(os.path.join(GODOT, "full", "mouth.json"), "w"))
    sub = os.path.join(DEMO, "full_v5")
    os.makedirs(sub, exist_ok=True)
    with open(os.path.join(sub, "audio_timing_full.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["scene", "cue", "speaker", "start_s", "end_s", "est_s", "voice_file", "text"])
        for sc, tl in SCENES.items():
            with open(os.path.join(sub, f"EP02_{sc}_vi.srt"), "w", encoding="utf-8") as s:
                for i, c in enumerate(tl["cues"], 1):
                    s.write("%d\n%s --> %s\n%s: %s\n\n" % (i, srt_time(c["t0"]), srt_time(c["t1"]),
                            "CAPY" if c["who"] == "CAPY" else "ANH KỸ SƯ", c["text"]))
                    w.writerow([sc, i, c["who"], c["t0"], c["t1"], round(c["t1"] - c["t0"], 2),
                                "pending ElevenLabs (owner-approved)", c["text"]])
    # recording sheet for the VO (one file per script line, dropped in godot/local/voice/)
    with open(os.path.join(sub, "VOICE_SHEET.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["file_name", "scene", "speaker", "direction", "text"])
        for sc in sorted(LINES):
            for i, (who, text) in enumerate(LINES[sc]):
                base = "Capy: nhanh nhảu, tò mò, tinh nghịch" if who == "CAPY" else "Anh kỹ sư: ấm, điềm tĩnh, như đang chỉ tận tay"
                if text.rstrip().endswith("?"):
                    base += "; lên giọng thắc mắc thật sự"
                elif "!" in text:
                    base += "; hào hứng, nhấn chữ cuối"
                w.writerow(["%s_%02d_%s.wav" % (sc, i + 1, who), sc, "CAPY" if who == "CAPY" else "ANH KỸ SƯ", base, text])
    for sc, tl in SCENES.items():
        print("%s %.1fs  cues=%d voices=%d" % (sc, tl["length"], len(tl["cues"]), len(tl["voices"])))
