"""Synthesised machine bed for the EP02 V4 proof (generalised from V3) (no samples, no voices).
Driven by telemetry.csv written by the Godot QA pass, so engine load, pump
whine, valve clicks and oil hiss follow the rendered motion frame by frame.

usage: python3 make_foley_v4.py telemetry.csv SIGNATURE.wav OUT_DIR [signature_start_s]
"""
import csv, sys, wave
import numpy as np
tel, sig_path, out = sys.argv[1:4]
SR = 48000
rows0 = list(csv.DictReader(open(tel)))
LEN = round(float(rows0[-1]["t"]) + 1 / 30, 3)
SIG_AT = float(sys.argv[4]) if len(sys.argv) > 4 else 0.48
N = int(SR * LEN)
rows = list(csv.DictReader(open(tel)))
T = np.array([float(r["t"]) for r in rows])
def col(k): return np.interp(np.arange(N) / SR, T, np.array([float(r[k]) for r in rows]))
t = np.arange(N) / SR
swash, spool, v, zoom = col("swash"), col("spool"), col("v"), col("cam_zoom")
rng = np.random.default_rng(12)

def lp(x, a):   # one-pole low-pass
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc); y[i] = acc
    return y

def lp_fast(x, cutoff):
    a = 1 - np.exp(-2 * np.pi * cutoff / SR)
    from scipy.signal import lfilter
    return lfilter([a], [1, -(1 - a)], x)

on = np.clip((t - 3.0) / 0.12, 0, 1)
# engine: 6-cyl four-stroke, ~1800 rpm under load, 1650 at light load
rpm = 1650 + 220 * swash
phase = 2 * np.pi * np.cumsum(rpm / 60 * 3) / SR          # firing frequency
engine = sum((0.55 / k) * np.sin(k * phase + k * 0.7) for k in range(1, 7))
engine *= 0.75 + 0.25 * np.sin(phase * 0.5) ** 2
engine += 0.35 * lp_fast(rng.standard_normal(N), 260)
engine *= 0.16 * (0.75 + 0.35 * swash)
# pump: 9 pistons per rev, tonal whine scales with displacement
pph = 2 * np.pi * np.cumsum(rpm / 60 * 9) / SR
pump = (np.sin(pph) + 0.4 * np.sin(2 * pph) + 0.15 * np.sin(3 * pph)) * 0.045 * np.clip((swash - 0.1) / 0.9, 0, 1) ** 1.3
# oil hiss proportional to cylinder speed
from scipy.signal import butter, lfilter
b, a = butter(2, [900 / (SR / 2), 4200 / (SR / 2)], "band")
hiss = lfilter(b, a, rng.standard_normal(N)) * 0.03 * np.clip(np.abs(v) / 9.5, 0, 1)
# valve clicks when the spool leaves / returns to centre
clicks = np.zeros(N)
sp = np.array([float(r["spool"]) for r in rows])
cross = [T[i] for i in range(1, len(sp)) if (sp[i - 1] < 0.15) != (sp[i] < 0.15)]
for tc, g in zip(cross, [0.5, 0.4, 0.5, 0.4]):
    i = int(tc * SR); L = int(0.05 * SR)
    burst = lfilter(*butter(2, 2500 / (SR / 2), "high"), rng.standard_normal(L)) * np.exp(-np.arange(L) / (0.006 * SR))
    clicks[i:i + L] += g * burst
# bucket scrape in the mound and falling clods
scrape = np.zeros(N)
# soil grinding inside the bucket while it curls (12.9-14.3 s)
m = (t > 12.9) & (t < 14.4)
env = np.clip((t - 12.9) / 0.3, 0, 1) * np.clip((14.4 - t) / 0.4, 0, 1)
scrape += lfilter(*butter(2, [150 / (SR / 2), 1200 / (SR / 2)], "band"), rng.standard_normal(N)) * 0.06 * env * m
for k in range(16):
    tc = rng.uniform(4.9, 6.8) if k < 5 else rng.uniform(13.3, 15.2)
    i = int(tc * SR); L = int(0.07 * SR)
    thud = lfilter(*butter(2, 500 / (SR / 2)), rng.standard_normal(L)) * np.exp(-np.arange(L) / (0.012 * SR))
    scrape[i:i + L] += rng.uniform(0.08, 0.2) * thud
machine = (engine + pump + hiss + clicks + scrape) * on
machine *= np.where(zoom > 1.5, 0.85, 1.0)        # slightly softer inside the x-ray shots
machine *= 0.55 / np.abs(machine).max()            # bed peaks at -5 dBFS, leaves room for voices

def write(path, x):
    x = np.clip(x, -1, 1)
    st = np.stack([x, x], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype("<i2").tobytes())

write(f"{out}/MACHINE.wav", machine)
# signature tag at 00:00.480
with wave.open(sig_path) as w:
    sr, ch, raw = w.getframerate(), w.getnchannels(), w.readframes(w.getnframes())
sig = np.frombuffer(raw, "<i2").astype(float) / 32768
sig = sig.reshape(-1, ch).mean(1)
if sr != SR:
    sig = np.interp(np.arange(int(len(sig) * SR / sr)) * sr / SR, np.arange(len(sig)), sig)
mix = machine.copy()
i0 = int(SIG_AT * SR); mix[i0:i0 + len(sig)] += sig[: N - i0]
peak = np.abs(mix).max(); mix *= 0.89 / peak if peak > 0.89 else 1.0
write(f"{out}/PREVIEW_MIX.wav", mix)
print("machine peak %.2f rms %.3f; mix peak %.2f" % (np.abs(machine).max(), np.sqrt((machine ** 2).mean()), np.abs(mix).max()))
