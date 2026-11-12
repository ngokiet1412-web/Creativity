"""Render original mono machine ambience and two subtle control cues."""
import argparse
from array import array
from math import pi, sin, tau
from pathlib import Path
from random import Random
import sys
import wave


def gate(t, start, end, ramp):
    return max(0.0, min(1.0, (t - start) / ramp, (end - t) / ramp))


def render(path):
    rate = 48000
    samples = array("h")
    noise = Random(2008)
    lowpass = 0.0
    for sample in range(42 * rate):
        t = sample / rate
        wind = noise.uniform(-1, 1)
        lowpass += .12 * (wind - lowpass)
        bed = gate(t, 4.2, 42, .85)
        load = sin(pi * (t - 24.5) / 10.8) ** 2 if 24.5 < t < 35.3 else 0.0
        motor = .017 * sin(tau * 61 * t) + .013 * sin(tau * 122 * t)
        hydraulic = load * (.030 * lowpass + .009 * sin(tau * 194 * t))
        control = sum(.055 * gate(t, start, start + .14, .04)
                      * (.38 * wind + .62 * sin(tau * 420 * t))
                      for start in (21.82, 35.47))
        samples.append(round((bed * (motor + .015 * lowpass) + hydraulic + control) * 32767))
    if sys.byteorder != "little":
        samples.byteswap()
    with wave.open(str(path), "wb") as output:
        output.setparams((1, 2, rate, 0, "NONE", "not compressed"))
        output.writeframes(samples.tobytes())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wav", type=Path)
    render(parser.parse_args().wav)
