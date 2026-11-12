"""Synthesised machine bed for the SC03/SC04/SC05 segment clips (no samples, no voices).

Driven by the telemetry CSV that each segment's Godot --qa pass writes, so the
engine note, pump whine, valve clicks and oil hiss follow what is on screen.
The bed sits at -24 dBFS rms (peaks soft-limited to -6 dBFS) and sits under the (still pending) ElevenLabs VO.

usage: python3 make_foley_segments.py SC03|SC04|SC05 telemetry.csv OUT.wav
"""
import csv
import sys
import wave

import numpy as np
from scipy.signal import butter, lfilter

seg, tel, out = sys.argv[1:4]
SR = 48000
rows = list(csv.DictReader(open(tel)))
T = np.array([float(r["t"]) for r in rows])
LEN = T[-1] + 1 / 30
N = int(SR * LEN)
t = np.arange(N) / SR
rng = np.random.default_rng(7)


def col(k):
    return np.interp(t, T, np.array([float(r[k]) for r in rows]))


def raw(k):
    return np.array([float(r[k]) for r in rows])


def band(x, lo, hi):
    return lfilter(*butter(2, [lo / (SR / 2), hi / (SR / 2)], "band"), x)


def lowp(x, f):
    return lfilter(*butter(2, f / (SR / 2)), x)


def engine_note(rpm, load):
    ph = 2 * np.pi * np.cumsum(rpm / 60 * 3) / SR          # 6-cyl 4-stroke firing freq
    e = sum((0.55 / k) * np.sin(k * ph + 0.7 * k) for k in range(1, 7))
    e *= 0.75 + 0.25 * np.sin(ph * 0.5) ** 2
    e += 0.35 * lowp(rng.standard_normal(N), 260)
    return e * 0.16 * (0.7 + 0.45 * load)


def pump_whine(rpm, disp, press):
    ph = 2 * np.pi * np.cumsum(rpm / 60 * 9) / SR          # 9 pistons per rev
    w = np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)
    return w * 0.04 * np.clip(disp, 0, 1) ** 1.2 * (0.6 + 0.6 * press)


def clicks_at(times, gain=0.45):
    c = np.zeros(N)
    L = int(0.05 * SR)
    for tc in times:
        i = int(tc * SR)
        if i >= N:
            continue
        b = lfilter(*butter(2, 2500 / (SR / 2), "high"), rng.standard_normal(L)) * np.exp(-np.arange(L) / (0.006 * SR))
        c[i:i + L] += gain * b[: N - i]
    return c


def crossings(x, thr):
    return [T[i] for i in range(1, len(x)) if (abs(x[i - 1]) < thr) != (abs(x[i]) < thr)]


hiss_src = band(rng.standard_normal(N), 900, 4200)

if seg == "SC03":
    n = col("rpm")                                           # on-screen speed 1.2 -> 1.9
    rpm = 1450 + (n - 1.2) / 0.7 * 450
    disp = 0.5 * (col("swash_f") + col("swash_r"))
    mix = engine_note(rpm, disp) + pump_whine(rpm, disp, 0.3) + hiss_src * 0.012 * col("q")
elif seg == "SC04":
    rpm = np.full(N, 1800.0)
    pp, q = col("p_pump"), col("q")
    mix = engine_note(rpm, np.clip(pp * q / 0.62, 0, 1)) + pump_whine(rpm, col("swash"), pp)
    mix += hiss_src * 0.028 * q
    mix += clicks_at(crossings(raw("boom"), 0.08) + crossings(raw("arm"), 0.08))
    pc = col("pc")                                           # low strain when the PC valve limits power
    mix += band(rng.standard_normal(N), 90, 400) * 0.05 * pc
elif seg == "SC05":
    rpm = np.full(N, 1700.0)
    op = col("open_pa")
    ext = raw("ext")
    v = np.interp(t, T, np.abs(np.gradient(ext, T)))
    mix = engine_note(rpm, 0.3 + 0.5 * np.clip(op / 48, 0, 1)) + pump_whine(rpm, 0.2 + 0.8 * np.clip(op / 48, 0, 1), 0.5)
    mix += hiss_src * 0.03 * np.clip(v / 30, 0, 1)
    mix += clicks_at(crossings(raw("open_pa"), 0.01), 0.35)
    mix += clicks_at(crossings(raw("pilot"), 0.03), 0.18)    # pilot pressure step: softer tick
else:
    sys.exit("unknown segment " + seg)

fade = np.clip(t / 0.4, 0, 1) * np.clip((LEN - t) / 0.4, 0, 1)
mix *= fade
mix *= 0.06 / np.sqrt((mix ** 2).mean())        # same loudness bed in every clip (-24 dBFS rms)
mix = 0.5 * np.tanh(mix / 0.5)                   # soft limit valve clicks to -6 dBFS
st = np.stack([mix, mix], 1)
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((np.clip(st, -1, 1) * 32767).astype("<i2").tobytes())
print("%s %.1fs peak %.2f rms %.3f" % (seg, LEN, np.abs(mix).max(), np.sqrt((mix ** 2).mean())))
