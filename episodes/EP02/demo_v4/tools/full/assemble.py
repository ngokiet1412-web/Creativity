#!/usr/bin/env python3
"""Assemble the EP02 full draft (V5): per-scene H.264 + synthesised machine bed,
concatenated master, merged SRT, and a review copy with burned-in subtitles.

usage: assemble.py <render_dir> <out_dir>
render_dir holds sc01.avi .. sc14.avi (sc03/sc04 = approved segments,
sc05 = approved SC05 with the V4.2 cylinder). No voices are generated here:
VO stays pending the owner-approved ElevenLabs WAVs.
"""
import json
import os
import re
import subprocess
import sys
import wave

import numpy as np
from scipy.signal import butter, lfilter

HERE = os.path.dirname(os.path.abspath(__file__))
DEMO = os.path.join(HERE, "..", "..")
SR = 48000
ORDER = ["SC%02d" % i for i in range(1, 15)]
SEG_SRT = {"SC03": "segments_sc03_sc05/EP02_SC03_vi.srt", "SC04": "segments_sc03_sc05/EP02_SC04_vi.srt",
           "SC05": "segments_sc03_sc05/EP02_SC05_vi.srt"}
# scene -> (engine level, pump level, extra)
BED = {"SC01": (0.8, 0.5, "studio_in"), "SC02": (0.6, 0.3, ""), "SC06": (0.8, 0.7, ""), "SC07": (0.7, 0.6, ""),
       "SC08": (0.5, 0.4, "swing"), "SC09": (0.5, 0.4, "tracks"), "SC10": (0.3, 0.3, "flow"),
       "SC11": (0.9, 0.9, "relief"), "SC12": (0.2, 0.1, "hum"), "SC13": (0.4, 0.2, ""), "SC14": (0.0, 0.0, "studio")}


TIMING = json.load(open(os.path.join(DEMO, "godot", "full", "timing.json"), encoding="utf-8"))


def run(cmd):
    subprocess.run(cmd, check=True)


def dur(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True).stdout.strip())


def bed(scene, length, out):
    rng = np.random.default_rng(len(scene) * 7 + int(scene[2:]))
    n = int(length * SR)
    t = np.arange(n) / SR
    eng, pump, extra = BED.get(scene, (0.55, 0.3, ""))
    rpm = 1750 + 40 * np.sin(t * 0.7)
    ph = 2 * np.pi * np.cumsum(rpm / 60 * 3) / SR
    x = eng * sum((0.5 / k) * np.sin(k * ph + 0.6 * k) for k in range(1, 6))
    x += eng * 0.3 * lfilter(*butter(2, 220 / (SR / 2)), rng.standard_normal(n))
    pp = 2 * np.pi * np.cumsum(rpm / 60 * 9) / SR
    x += pump * 0.12 * (np.sin(pp) + 0.4 * np.sin(2 * pp))
    if extra == "swing":
        x += 0.25 * lfilter(*butter(2, [80 / (SR / 2), 300 / (SR / 2)], "band"), rng.standard_normal(n))
    if extra == "tracks":
        clank = np.zeros(n)
        for k in np.arange(0, length, 0.28):
            i = int(k * SR)
            m = min(int(0.04 * SR), n - i)
            clank[i:i + m] += rng.standard_normal(m) * np.exp(-np.arange(m) / (0.008 * SR))
        x += 0.5 * lfilter(*butter(2, 1800 / (SR / 2)), clank)
    if extra in ("flow", "relief"):
        x += 0.35 * lfilter(*butter(2, [900 / (SR / 2), 4000 / (SR / 2)], "band"), rng.standard_normal(n))
    if extra == "hum":
        x += 0.15 * np.sin(2 * np.pi * 120 * t)
    if extra.startswith("studio"):
        room = 0.05 * lfilter(*butter(2, 400 / (SR / 2)), rng.standard_normal(n))
        if extra == "studio_in":
            k = np.clip((t - 5.0) / 3.0, 0, 1)   # machine heard once the monitor is on
            x = x * k + room
        else:
            x = room
    rms = np.sqrt((x ** 2).mean()) + 1e-9
    x *= 0.03 / rms                     # -30 dBFS rms bed, sits under VO
    x = 0.5 * np.tanh(x / 0.5)
    fade = np.clip(t / 0.3, 0, 1) * np.clip((length - t) / 0.3, 0, 1)
    x *= fade
    st = (np.clip(np.stack([x, x], 1), -1, 1) * 32767).astype("<i2")
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(st.tobytes())


def parse_srt(path):
    out = []
    for blk in open(path, encoding="utf-8").read().strip().split("\n\n"):
        lines = blk.strip().split("\n")
        if len(lines) < 3:
            continue
        a, b = lines[1].split(" --> ")
        f = lambda s: int(s[:2]) * 3600 + int(s[3:5]) * 60 + int(s[6:8]) + int(s[9:]) / 1000
        out.append((f(a), f(b), " ".join(lines[2:])))
    return out


def ts(x):
    ms = int(round(x * 1000))
    return "%02d:%02d:%02d,%03d" % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)


def main(rdir, out):
    os.makedirs(out, exist_ok=True)
    parts, srt, offset = [], [], 0.0
    machine_audio = {"SC03": "audio/SC03_MACHINE.wav", "SC04": "audio/SC04_MACHINE.wav", "SC05": "audio/SC05_V42_MACHINE.wav"}
    for sc in ORDER:
        src = os.path.join(rdir, sc.lower() + ".avi")
        L = dur(src)
        wav = os.path.join(out, f"{sc}_bed.wav")
        if sc in machine_audio and os.path.exists(os.path.join(rdir, machine_audio[sc])):
            run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(rdir, machine_audio[sc]), "-af", "volume=0.5", "-t", str(L), wav])
        else:
            bed(sc, L, wav)
        voices = TIMING["scenes"].get(sc, {}).get("voices", [])
        if voices:      # owner VO on top of the bed (bed ducked 6 dB under speech scenes)
            mix = os.path.join(out, f"{sc}_mix.wav")
            cmd = ["ffmpeg", "-v", "error", "-y", "-i", wav]
            flt = "[0]volume=0.5[b];"
            for k, v in enumerate(voices):
                cmd += ["-i", os.path.join(DEMO, "godot", v["file"])]
                flt += "[%d]aresample=48000,aformat=channel_layouts=stereo,adelay=%d:all=1[v%d];" % (k + 1, int(v["t0"] * 1000), k)
            flt += "[b]" + "".join("[v%d]" % k for k in range(len(voices))) + "amix=inputs=%d:normalize=0:duration=first[m]" % (len(voices) + 1)
            run(cmd + ["-filter_complex", flt, "-map", "[m]", mix])
            wav = mix
        mp4 = os.path.join(out, f"{sc}.mp4")
        run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", wav, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
             "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", mp4])
        parts.append(mp4)
        srt_path = os.path.join(DEMO, SEG_SRT[sc]) if sc in SEG_SRT else os.path.join(DEMO, "full_v5", f"EP02_{sc}_vi.srt")
        for a, b, txt in parse_srt(srt_path):
            srt.append((a + offset, b + offset, txt))
        offset += dur(mp4)
        print(sc, round(L, 2), "->", round(offset, 2))
    lst = os.path.join(out, "concat.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    master = os.path.join(out, "EP02_FULL_V6_DRAFT.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", master])
    sp = os.path.join(out, "EP02_FULL_V6_vi.srt")
    with open(sp, "w", encoding="utf-8") as f:
        for i, (a, b, txt) in enumerate(srt, 1):
            f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{txt}\n\n")
    review = os.path.join(out, "EP02_FULL_V6_DRAFT_review_subs.mp4")
    style = "FontName=Inter,FontSize=15,PrimaryColour=&H00FFFFFF,OutlineColour=&H00101010,BorderStyle=3,Outline=1,Shadow=0,BackColour=&H90101010,MarginV=22"
    run(["ffmpeg", "-v", "error", "-y", "-i", master, "-vf", f"subtitles={sp}:force_style='{style}'", "-c:v", "libx264",
         "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", review])
    print("total", round(dur(master), 1), "s")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
