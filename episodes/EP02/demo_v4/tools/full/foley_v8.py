"""Original synthetic Foley synced to the animated timeline, at 48 kHz."""
import wave

import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000


def _transition(t, start, span):
    u = np.clip((t - start) / span, 0, 1)
    return u * u * (3 - 2 * u)


def soundscape(scene, timing, duration, path, bumper=False):
    t = np.arange(round(duration * SR)) / SR
    rng = np.random.default_rng(80 + int(scene[2:]))
    marks = timing.get("marks", {})
    bed = np.zeros(t.size)
    mechanical = scene in {"SC01", "SC02", "SC03", "SC05", "SC06", "SC07", "SC08", "SC09", "SC11"}
    if mechanical:
        if scene == "SC01":
            start = 2.65 if bumper else 3.92
            level = 0.50 * _transition(t, start, 0.52)
            load = 0.75 * _transition(t, marks["dig.s"], 1.5) * (1 - _transition(t, marks["dig.s"] + 7, 1.2))
        else:
            level = 0.39
            load = 0.18 + 0.17 * np.sin(t * 0.66) ** 2
        firing = 47.0 + load * 25.0 + np.sin(t * 2.2) * 0.8
        phase = 2 * np.pi * np.cumsum(firing) / SR
        diesel = 0.025 * np.sin(phase) + 0.013 * np.sin(2 * phase + 0.6) + 0.009 * np.sin(4 * phase + 0.3)
        rasp = sosfilt(butter(2, [115, 600], fs=SR, btype="bandpass", output="sos"), rng.standard_normal(t.size))
        bed += level * (diesel + 0.022 * rasp)

    # Short bursts follow the relevant visible control/motion, not each sentence.
    # SC05's pilot lever keys were authored before the V6 holds and V7 voice
    # retime. Move the Foley on the same timeline as the lever and drawer.
    cue_times = [13.3, 17.2, 25.1]
    if scene == "SC05" and timing.get("retime_keys"):
        before, after = np.asarray(timing["retime_keys"]).T
        cue_times = np.interp(cue_times, before, after)
    events = {
        "SC01": [(marks.get("dig.s", 3.4), "scoop"), (marks.get("dig.s", 3.4) + 4.8, "hydraulic")],
        "SC05": list(zip(cue_times, ("lever", "hydraulic", "lever"))),
        "SC06": [(marks.get("boom.s", 4), "hydraulic"), (marks.get("arm.s", 12), "hydraulic"), (marks.get("bkt.s", 22), "hydraulic")],
        "SC08": [(marks.get("q.s", 2) + 0.65, "hydraulic"), (marks.get("motor.s", 9) + 0.45, "hydraulic")],
        "SC09": [(marks.get("trk.s", 18) + 0.2, "tracks"), (marks.get("top.s", 22) + 1.1, "tracks")],
    }
    for start, kind in events.get(scene, []):
        span = {"lever": 0.1, "hydraulic": 1.7, "scoop": 0.7, "tracks": 1.6}[kind]
        idx = max(0, round(start * SR))
        n = min(round(span * SR), t.size - idx)
        if n <= 0:
            continue
        u = np.arange(n) / SR
        if kind == "lever":
            hit = rng.standard_normal(n) * np.exp(-u * 66)
            event = 0.037 * sosfilt(butter(2, [280, 3200], fs=SR, btype="bandpass", output="sos"), hit)
        elif kind == "tracks":
            hits = np.exp(-42 * (u % 0.17))
            event = 0.035 * hits * sosfilt(butter(2, [200, 1700], fs=SR, btype="bandpass", output="sos"), rng.standard_normal(n))
            event *= np.sin(np.pi * u / span) ** 0.65
        else:
            noise = sosfilt(butter(2, [310, 1550], fs=SR, btype="bandpass", output="sos"), rng.standard_normal(n))
            event = 0.038 * noise * np.sin(np.pi * u / span) ** 1.2
            if kind == "hydraulic":
                event += 0.007 * np.sin(2 * np.pi * (210 * u + 23 * u * u)) * np.sin(np.pi * u / span)
        bed[idx:idx+n] += event
    # Lift the bed between lines, then bring it back under the next voice.
    duck = np.ones(t.size)
    for cue in timing.get("cues", []):
        start = max(0, round((cue["t0"] - 0.25) * SR))
        end = min(t.size, round((cue["t1"] + 0.25) * SR))
        u = t[start:end]
        speaking = _transition(u, cue["t0"] - 0.25, 0.25) * (1 - _transition(u, cue["t1"], 0.25))
        duck[start:end] = np.minimum(duck[start:end], 1 - 0.42 * speaking)
    fade = np.minimum(np.clip(t / 0.32, 0, 1), np.clip((duration - t) / 0.35, 0, 1))
    signal = 2.35 * bed * fade * duck
    if bumper and scene == 'SC01':
        # Short original three-note wood/metal station sound, no stock audio.
        for start, hz, gain in [(0.38, 349.23, 0.12), (0.56, 440.0, 0.13), (0.81, 523.25, 0.16)]:
            idx = round(start * SR)
            u = np.arange(round(0.70 * SR)) / SR
            envelope = np.minimum(u / 0.012, 1.0) * np.exp(-u * 8.5) * (1 - _transition(u, 0.55, 0.15))
            note = np.sin(2*np.pi*hz*u) + 0.26*np.sin(2*np.pi*2*hz*u)
            signal[idx:idx+u.size] += gain * envelope * note
    pcm = (np.clip(signal, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as f:
        f.setparams((2, 2, SR, 0, "NONE", "not compressed"))
        f.writeframes(np.repeat(pcm[:, None], 2, axis=1).tobytes())
