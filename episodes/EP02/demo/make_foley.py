"""Render original mono PC200-8 machine ambience, hydraulic pump whine, soil scoop crunch, and PPC valve cues."""
import argparse
from array import array
from math import pi, sin, tau
from pathlib import Path
from random import Random
import sys
import wave


def gate(t: float, start: float, end: float, ramp: float) -> float:
    return max(0.0, min(1.0, (t - start) / ramp, (end - t) / ramp))


def render(path: Path, proof16: bool = False) -> None:
    rate = 48000
    duration = 16 if proof16 else 42
    samples = array("h")
    noise = Random(2008)
    lowpass = 0.0
    crunch_lp = 0.0
    for sample in range(duration * rate):
        t = sample / rate
        wind = noise.uniform(-1.0, 1.0)
        lowpass += 0.12 * (wind - lowpass)
        crunch_lp += 0.28 * (wind - crunch_lp)

        if not proof16:
            bed = gate(t, 4.2, 42.0, 0.85)
            pump_whine = gate(t, 10.4, 35.5, 0.6) * (0.010 * sin(tau * 168 * t) + 0.006 * sin(tau * 336 * t))
            scoop_env = gate(t, 18.4, 23.8, 0.45)
            load = sin(pi * (t - 24.5) / 10.8) ** 2 if 24.5 < t < 35.3 else 0.0
            clicks = (17.52, 21.62, 35.47)
        else:
            bed = gate(t, 0.0, 16.0, 0.35)
            pump_whine = gate(t, 3.0, 13.0, 0.35) * (0.011 * sin(tau * 172 * t) + 0.006 * sin(tau * 344 * t))
            scoop_env = gate(t, 9.1, 12.6, 0.35)
            load = sin(pi * (t - 3.2) / 9.6) ** 2 if 3.2 < t < 12.8 else 0.0
            clicks = (3.05, 9.05, 13.05)

        motor = 0.018 * sin(tau * 61 * t) + 0.013 * sin(tau * 122 * t) + 0.006 * sin(tau * 183 * t)
        hydraulic = load * (0.030 * lowpass + 0.011 * sin(tau * (194 + 22 * load) * t))
        soil_crunch = scoop_env * (0.028 * crunch_lp + 0.012 * sin(tau * 88 * t) * wind)
        control = sum(
            0.055 * gate(t, start, start + 0.14, 0.04) * (0.38 * wind + 0.62 * sin(tau * 420 * t))
            for start in clicks
        )
        val = (bed * (motor + 0.015 * lowpass) + pump_whine + hydraulic + soil_crunch + control)
        val = max(-0.98, min(0.98, val))
        samples.append(round(val * 32767))

    if sys.byteorder != "little":
        samples.byteswap()
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as output:
        output.setparams((1, 2, rate, 0, "NONE", "not compressed"))
        output.writeframes(samples.tobytes())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wav", type=Path)
    parser.add_argument("--proof16", action="store_true")
    args = parser.parse_args()
    render(args.wav, proof16=args.proof16)
